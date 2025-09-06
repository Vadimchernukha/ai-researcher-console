# improved_analyzer.py
import logging
import json
import google.generativeai as genai
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import GOOGLE_API_KEY, GOOGLE_API_KEY2
import src.analyzers.prompts as classification_prompts
import src.analyzers.extraction_prompts as extraction_prompts
import asyncio
from typing import Optional, Dict, Any
import re

# Инициализация моделей с ротацией ключей
api_keys = [GOOGLE_API_KEY, GOOGLE_API_KEY2]
current_key_index = 0

def get_model():
    global current_key_index
    genai.configure(api_key=api_keys[current_key_index])
    generation_config = {"temperature": 0.1, "response_mime_type": "application/json"}
    return genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config=generation_config)

def get_model_pro():
    """Secondary model for high-precision validation/classification."""
    global current_key_index
    genai.configure(api_key=api_keys[current_key_index])
    generation_config = {"temperature": 0.0, "response_mime_type": "application/json"}
    return genai.GenerativeModel(model_name="gemini-1.5-pro-latest", generation_config=generation_config)

class DataExtractionValidator:
    """Валидация извлеченных данных для разных профилей (iso/software)"""

    @staticmethod
    def validate_extraction(data: dict, content_length: int, profile: str = None) -> dict:
        validation = {
            'is_valid': True,
            'confidence_score': 0,
            'issues': [],
            'completeness': 0
        }

        # Определяем профиль по переданному параметру или структуре данных
        if profile:
            is_iso_profile = profile == 'iso'
            is_edtech_profile = profile == 'edtech'
            is_software_profile = profile in ['software', 'telemedicine']
            is_pharma_profile = profile == 'pharma'
        else:
            is_iso_profile = 'fintech_services' in data or 'company_type_in_payments' in data
            is_software_profile = 'business_model' in data or 'software_name' in data
            is_pharma_profile = 'pharma_roles' in data or 'named_products' in data

        if is_iso_profile:
            required_fields = ['company_description', 'fintech_services', 'company_type_in_payments', 'target_audience']
            filled_fields = 0
            for field in required_fields:
                if field in data and data[field] and data[field] != "":
                    filled_fields += 1
                else:
                    validation['issues'].append(f'Missing or empty field: {field}')
            validation['completeness'] = (filled_fields / len(required_fields)) * 100

            description = data.get('company_description', '')
            if description:
                if len(description) < 20:
                    validation['issues'].append('Company description too short')
                elif len(description) > 500:
                    validation['issues'].append('Company description too long')
                else:
                    validation['confidence_score'] += 30
            services = data.get('fintech_services', [])
            if isinstance(services, list) and len(services) > 0:
                validation['confidence_score'] += 25
            company_type = data.get('company_type_in_payments', [])
            if isinstance(company_type, list) and len(company_type) > 0:
                validation['confidence_score'] += 25
            audience = data.get('target_audience', [])
            if isinstance(audience, list) and len(audience) > 0:
                validation['confidence_score'] += 20

        elif is_edtech_profile:
            # EdTech фокус на ПО + образование, бизнес-модель не важна
            required_fields = ['company_description']
            filled_fields = 0
            for field in required_fields:
                if field in data and data[field]:
                    filled_fields += 1
                else:
                    validation['issues'].append(f'Missing or empty field: {field}')
            validation['completeness'] = (filled_fields / len(required_fields)) * 100

            description = data.get('company_description', '')
            if description:
                if len(description) >= 10:
                    validation['confidence_score'] += 30
                else:
                    validation['issues'].append('Company description too short')
            
            # Проверка наличия ПО
            has_software = any([
                data.get('has_login_button'),
                data.get('has_pricing_page'), 
                data.get('software_name'),
                data.get('mentioned_products')
            ])
            if has_software:
                validation['confidence_score'] += 30
            else:
                validation['issues'].append('No software/platform evidence found')
            
            # EdTech специфичные бонусы
            audience = data.get('target_audience', '')
            edtech_indicators = data.get('edtech_indicators', [])
            company_type = data.get('company_type', '')
            
            if isinstance(audience, str) and any(keyword in audience.lower() for keyword in ['school', 'teacher', 'parent', 'student', 'education']):
                validation['confidence_score'] += 20
            if isinstance(edtech_indicators, list) and len(edtech_indicators) > 0:
                validation['confidence_score'] += min(20, len(edtech_indicators) * 5)
            if isinstance(company_type, str) and 'edtech' in company_type.lower():
                validation['confidence_score'] += 25

            if validation['confidence_score'] < 70:
                validation['is_valid'] = False

        elif is_software_profile:
            required_fields = ['company_description', 'business_model']
            filled_fields = 0
            for field in required_fields:
                if field in data and data[field]:
                    filled_fields += 1
                else:
                    validation['issues'].append(f'Missing or empty field: {field}')
            validation['completeness'] = (filled_fields / len(required_fields)) * 100

            description = data.get('company_description', '')
            if description:
                if len(description) >= 10:  # Снижен с 15 до 10
                    validation['confidence_score'] += 25
                else:
                    validation['issues'].append('Company description too short')
            business_model = data.get('business_model', '')
            if isinstance(business_model, str) and business_model:
                validation['confidence_score'] += 25
                if business_model.lower() in ['product', 'saas', 'paas', 'iaas', 'hybrid (product+service)']:
                    validation['confidence_score'] += 10
            software_name = data.get('software_name')
            if isinstance(software_name, str) and len(software_name) > 1:
                validation['confidence_score'] += 20
            software_purpose = data.get('software_purpose', '')
            if isinstance(software_purpose, str) and len(software_purpose) >= 5:  # Снижен с 10 до 5
                validation['confidence_score'] += 10
            audience = data.get('target_audience')
            if (isinstance(audience, list) and len(audience) > 0) or (isinstance(audience, str) and len(audience) > 0):
                validation['confidence_score'] += 10
        elif is_pharma_profile:
            required_fields = ['company_description']
            filled_fields = 0
            for field in required_fields:
                if field in data and data[field]:
                    filled_fields += 1
                else:
                    validation['issues'].append(f'Missing or empty field: {field}')
            validation['completeness'] = (filled_fields / len(required_fields)) * 100

            description = data.get('company_description', '')
            if description:
                if len(description) >= 10:  # Снижен с 15 до 10
                    validation['confidence_score'] += 30
                else:
                    validation['issues'].append('Company description too short')
            
            pharma_roles = data.get('pharma_roles', [])
            if isinstance(pharma_roles, list) and len(pharma_roles) > 0:
                validation['confidence_score'] += 25
            
            named_products = data.get('named_products', [])
            if isinstance(named_products, list) and len(named_products) > 0:
                validation['confidence_score'] += 20
            
            services = data.get('services', [])
            if isinstance(services, list) and len(services) > 0:
                validation['confidence_score'] += 15
        elif profile == 'edtech':
            # Strict EdTech: require explicit audience + features + GDPR + integration evidence
            required_fields = ['company_description', 'target_audience', 'platform_features', 'feature_flags', 'integrations', 'security_privacy']
            filled_fields = 0
            for field in required_fields:
                if field in data and data[field] not in (None, "", []):
                    filled_fields += 1
                else:
                    validation['issues'].append(f'Missing or empty field: {field}')
            validation['completeness'] = (filled_fields / len(required_fields)) * 100 if required_fields else 0

            audience = data.get('target_audience', [])
            features = data.get('platform_features', [])
            flags = data.get('feature_flags', {}) or {}
            integrations = data.get('integrations', {}) or {}
            privacy = data.get('security_privacy', {}) or {}

            has_required_audience = any(x.lower() in ['schools', 'kindergartens', 'k-12', 'teachers', 'parents'] for x in (audience or []))
            has_core_features = len([c for c in features if c in ['Class_Management','Parent_Communication','Scheduling_Tools']]) >= 2
            has_integration = bool(integrations.get('present')) or bool(integrations.get('types'))
            gdpr_claimed = bool(((privacy.get('gdpr_dsgvo') or {}).get('claimed')))

            if has_required_audience:
                validation['confidence_score'] += 20
            else:
                validation['issues'].append('Missing required audience (schools/kindergartens/teachers/parents)')

            if has_core_features:
                validation['confidence_score'] += 35
            else:
                validation['issues'].append('Requires at least two core features among Class_Management, Parent_Communication, Scheduling_Tools')

            if has_integration:
                validation['confidence_score'] += 20
            else:
                validation['issues'].append('Missing explicit integrations/SSO evidence')

            if gdpr_claimed:
                validation['confidence_score'] += 25
            else:
                validation['issues'].append('Missing explicit GDPR/DSGVO claim')

            if validation['confidence_score'] < 25:
                validation['is_valid'] = False
        else:
            validation['issues'].append('Unknown extraction profile')
            validation['is_valid'] = False

        # Снижаем порог валидации для software профиля
        if is_software_profile:
            if validation['confidence_score'] < 25:  # Снижен с 35 до 25
                validation['is_valid'] = False
        else:
            if validation['confidence_score'] < 35:
                validation['is_valid'] = False

        return validation


class MultiStageAnalyzer:
    """Многоэтапный анализатор с валидацией"""
    
    def __init__(self, profile: str = "software"):
        self.profile = profile
        self.model = get_model()  # primary: flash
        self.model_pro = get_model_pro()  # secondary: pro for validation
        self.retry_count = 3
        
    async def extract_facts_with_validation(self, content: str) -> Optional[Dict[str, Any]]:
        """Извлечение фактов с валидацией и повторными попытками; пробует ISO, затем SOFTWARE"""

        # Восстанавливаем оригинальную логику, которая работала
        if self.profile == 'software':
            profiles = [('software', extraction_prompts.PROMPT_SOFTWARE_PRODUCT)]
        elif self.profile == 'iso':
            profiles = [('iso', extraction_prompts.PROMPT_EXTRACTION_ISO)]
        elif self.profile == 'pharma':
            profiles = [('pharma', extraction_prompts.PROMPT_DATA_EXTRACTION_PHARMA)]
        elif self.profile == 'telemedicine':
            profiles = [('telemedicine', extraction_prompts.PROMPT_DATA_EXTRACTION_TELEMEDICINE)]
        elif self.profile == 'edtech':
            profiles = [('edtech', extraction_prompts.PROMPT_DATA_EXTRACTION_EDTECH)]
        # Промпт для клиентов - Client Extraction Prompts
        elif self.profile == 'marketing':
            profiles = [('marketing', extraction_prompts.PROMPT_DATA_EXTRACTION_MARKETING)]
        elif self.profile == 'fintech':
            profiles = [('fintech', extraction_prompts.PROMPT_DATA_EXTRACTION_FINTECH)]
        elif self.profile == 'healthtech':
            profiles = [('healthtech', extraction_prompts.PROMPT_DATA_EXTRACTION_HEALTHTECH)]
        elif self.profile == 'elearning':
            profiles = [('elearning', extraction_prompts.PROMPT_DATA_EXTRACTION_ELEARNING)]
        elif self.profile == 'software_products':
            profiles = [('software_products', extraction_prompts.PROMPT_DATA_EXTRACTION_SOFTWARE_PRODUCTS)]
        elif self.profile in ['salesforce_partner', 'hubspot_partner', 'aws', 'shopify']:
            profiles = [(self.profile, extraction_prompts.PROMPT_DATA_EXTRACTION_PARTNER_ECOSYSTEM)]
        elif self.profile == 'ai_companies':
            profiles = [('ai_companies', extraction_prompts.PROMPT_DATA_EXTRACTION_AI_COMPANIES)]
        elif self.profile == 'mobile_app':
            profiles = [('mobile_app', extraction_prompts.PROMPT_DATA_EXTRACTION_MOBILE_APP)]
        elif self.profile == 'recruiting':
            profiles = [('recruiting', extraction_prompts.PROMPT_DATA_EXTRACTION_RECRUITING)]
        elif self.profile == 'banking':
            profiles = [('banking', extraction_prompts.PROMPT_DATA_EXTRACTION_BANKING)]
        elif self.profile == 'platforms':
            profiles = [('platforms', extraction_prompts.PROMPT_DATA_EXTRACTION_PLATFORMS)]
        else:
            profiles = [('software', extraction_prompts.PROMPT_SOFTWARE_PRODUCT)]

        for profile_name, prompt_template in profiles:
            # Pass 1: FLASH attempts
            for attempt in range(self.retry_count):
                try:
                    prompt_text = prompt_template.format(content=content)
                    response = await self.model.generate_content_async(prompt_text)
                    if profile_name == "edtech":
                        logging.error(f"[DEBUG EdTech] Raw response: {response.text[:800]}")
                    raw_data = self._parse_json_response(response.text)
                    if not raw_data:
                        logging.warning(f"[{profile_name}] Failed to parse JSON on attempt {attempt + 1}")
                        continue

                    validation = DataExtractionValidator.validate_extraction(raw_data, len(content), profile_name)
                    if validation['is_valid']:
                        raw_data['_validation'] = validation
                        raw_data['_profile'] = profile_name
                        return raw_data
                    else:
                        logging.warning(f"[{profile_name}] Data validation failed on attempt {attempt + 1}: {validation['issues']}")
                        if attempt < self.retry_count - 1:
                            enhanced_prompt = self._create_enhanced_prompt(content, validation['issues'])
                            response = await self.model.generate_content_async(enhanced_prompt)
                            raw_data = self._parse_json_response(response.text)
                            if raw_data:
                                validation = DataExtractionValidator.validate_extraction(raw_data, len(content), profile_name)
                                if validation['is_valid']:
                                    raw_data['_validation'] = validation
                                    raw_data['_profile'] = profile_name
                                    return raw_data
                except Exception as e:
                    logging.error(f"[{profile_name}] Error in extraction attempt {attempt + 1}: {e}")
                    # DEBUG: Логируем полный ответ для отладки
                    if profile_name == "edtech":
                        logging.error(f"[DEBUG EdTech] Full response: {response.text[:500]}...")
                    # Fail-fast для EdTech при ошибках парсинга JSON
                    if os.environ.get("FAIL_FAST") == "true" and profile_name == "edtech":
                        raise RuntimeError(f"FAIL-FAST: EdTech extraction failed on {e}")
                    global current_key_index
                    current_key_index = (current_key_index + 1) % len(api_keys)
                    self.model = get_model()
                    self.model_pro = get_model_pro()
                    await asyncio.sleep(2 ** attempt)
            # Pass 2: escalate to PRO if FLASH did not produce valid result
            try:
                prompt_text = prompt_template.format(content=content)
                response = await self.model_pro.generate_content_async(prompt_text)
                raw_data = self._parse_json_response(response.text)
                if raw_data:
                    validation = DataExtractionValidator.validate_extraction(raw_data, len(content), profile_name)
                    if validation['is_valid']:
                        raw_data['_validation'] = validation
                        raw_data['_profile'] = profile_name
                        raw_data['_reviewed_by'] = 'pro'
                        return raw_data
            except Exception as e:
                logging.error(f"[{profile_name}] PRO extraction attempt failed: {e}")

        return None
    
    def _create_enhanced_prompt(self, content: str, issues: list) -> str:
        """Создает улучшенный промпт на основе проблем"""
        additional_instructions = ""
        
        if any("company_description" in issue for issue in issues):
            additional_instructions += "\nPay special attention to extracting a comprehensive company description from about sections, homepage content, or mission statements."
            
        if any("fintech_services" in issue for issue in issues):
            additional_instructions += "\nLook carefully for any payment-related services, even if not explicitly listed as 'fintech services'."
            
        enhanced_prompt = f"""
{extraction_prompts.PROMPT_EXTRACTION_ISO.format(content=content)}

ADDITIONAL INSTRUCTIONS:
{additional_instructions}

CRITICAL: Make sure to fill all fields. If you cannot find specific information, provide your best interpretation based on available context.
"""
        return enhanced_prompt
    
    def _parse_json_response(self, response_text: str) -> Optional[dict]:
        """Улучшенный парсинг JSON ответов"""
        text = response_text.strip()
        # Удаляем коды и маркдаун ограды
        if text.startswith("```"):
            text = re.sub(r"```[a-zA-Z]*\n?|```", "", text)
        # Прямой парсинг
        try:
            return json.loads(text)
        except Exception:
            pass
        # Вырезаем первый валидный JSON-объект по скобочному балансу
        try:
            start = text.find('{')
            if start != -1:
                depth = 0
                for i in range(start, len(text)):
                    if text[i] == '{':
                        depth += 1
                    elif text[i] == '}':
                        depth -= 1
                        if depth == 0:
                            candidate = text[start:i+1]
                            return json.loads(candidate)
        except Exception:
            pass
        # Попытка поправить некавыченные ключи
        try:
            fixed = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', text)
            return json.loads(fixed)
        except Exception:
            logging.error(f"Failed to parse JSON response: {text[:200]}...")
            return None


    async def classify_with_confidence(self, facts_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Классификация с оценкой уверенности"""
        
        if not facts_data or '_validation' not in facts_data:
            logging.warning("No validated data for classification")
            return None
            
        validation_score = facts_data['_validation']['confidence_score']
        
        profile_name = facts_data.get('_profile', self.profile)
        for attempt in range(self.retry_count):
            try:
                facts_json = json.dumps(facts_data, ensure_ascii=False)
                if profile_name == 'software':
                    prompt_text = classification_prompts.PROMPT_SOFTWARE_CLASSIFICATION.format(structured_summary=facts_json)
                elif profile_name == 'iso':
                    prompt_text = classification_prompts.PROMPT_ISO_MSP_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'pharma':
                    prompt_text = classification_prompts.PROMPT_FINAL_CLASSIFICATION_PHARMA.format(structured_summary=facts_json)
                elif profile_name == 'telemedicine':
                    prompt_text = classification_prompts.PROMPT_TELEMEDICINE_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'edtech':
                    prompt_text = classification_prompts.PROMPT_CONCEPT_CLASSIFICATION_EDTECH.format(structured_summary=facts_json)
                # Промпт для клиентов - Client Classification Prompts
                elif profile_name == 'marketing':
                    prompt_text = classification_prompts.PROMPT_MARKETING_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'fintech':
                    prompt_text = classification_prompts.PROMPT_FINTECH_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'healthtech':
                    prompt_text = classification_prompts.PROMPT_HEALTHTECH_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'elearning':
                    prompt_text = classification_prompts.PROMPT_ELEARNING_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'software_products':
                    prompt_text = classification_prompts.PROMPT_SOFTWARE_PRODUCTS_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'salesforce_partner':
                    prompt_text = classification_prompts.PROMPT_SALESFORCE_PARTNER_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'hubspot_partner':
                    prompt_text = classification_prompts.PROMPT_HUBSPOT_PARTNER_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'aws':
                    prompt_text = classification_prompts.PROMPT_AWS_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'shopify':
                    prompt_text = classification_prompts.PROMPT_SHOPIFY_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'ai_companies':
                    prompt_text = classification_prompts.PROMPT_AI_COMPANIES_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'mobile_app':
                    prompt_text = classification_prompts.PROMPT_MOBILE_APP_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'recruiting':
                    prompt_text = classification_prompts.PROMPT_RECRUITING_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'banking':
                    prompt_text = classification_prompts.PROMPT_BANKING_CLASSIFIER.format(structured_summary=facts_json)
                elif profile_name == 'platforms':
                    prompt_text = classification_prompts.PROMPT_PLATFORMS_CLASSIFIER.format(structured_summary=facts_json)
                else:
                    prompt_text = classification_prompts.PROMPT_SOFTWARE_CLASSIFICATION.format(structured_summary=facts_json)
                
                response = await self.model.generate_content_async(prompt_text)
                classification_data = self._parse_json_response(response.text)
                
                if not classification_data:
                    continue
                    
                # Добавляем метаданные
                classification_data['_extraction_confidence'] = validation_score
                classification_data['_classification_attempt'] = attempt + 1
                
                # Проверяем качество классификации
                if self._is_classification_valid(classification_data):
                    # Gate to PRO for low-confidence cases
                    needs_pro = False
                    if profile_name == 'edtech':
                        needs_pro = validation_score < 70
                    else:
                        needs_pro = validation_score < 50

                    # Also escalate if negative with mid confidence to reduce false negatives
                    if classification_data.get('classification') == 'No Match' and 35 <= validation_score < 65:
                        needs_pro = True

                    if not needs_pro:
                        return classification_data

                    try:
                        pro_response = await self.model_pro.generate_content_async(prompt_text)
                        pro_cls = self._parse_json_response(pro_response.text)
                        if pro_cls and self._is_classification_valid(pro_cls):
                            pro_cls['_extraction_confidence'] = validation_score
                            pro_cls['_classification_reviewed_by'] = 'pro'
                            return pro_cls
                    except Exception as e:
                        logging.error(f"Classification PRO escalation error: {e}")
                    return classification_data
                    
            except Exception as e:
                logging.error(f"Classification error on attempt {attempt + 1}: {e}")
                await asyncio.sleep(1)
                
        # If FLASH attempts failed entirely, try single PRO pass
        try:
            facts_json = json.dumps(facts_data, ensure_ascii=False)
            if profile_name == 'software':
                prompt_text = classification_prompts.PROMPT_SOFTWARE_CLASSIFICATION.format(structured_summary=facts_json)
            elif profile_name == 'iso':
                prompt_text = classification_prompts.PROMPT_ISO_MSP_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'pharma':
                prompt_text = classification_prompts.PROMPT_FINAL_CLASSIFICATION_PHARMA.format(structured_summary=facts_json)
            elif profile_name == 'telemedicine':
                prompt_text = classification_prompts.PROMPT_TELEMEDICINE_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'edtech':
                prompt_text = classification_prompts.PROMPT_CONCEPT_CLASSIFICATION_EDTECH.format(structured_summary=facts_json)
            elif profile_name == 'marketing':
                prompt_text = classification_prompts.PROMPT_MARKETING_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'fintech':
                prompt_text = classification_prompts.PROMPT_FINTECH_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'healthtech':
                prompt_text = classification_prompts.PROMPT_HEALTHTECH_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'elearning':
                prompt_text = classification_prompts.PROMPT_ELEARNING_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'software_products':
                prompt_text = classification_prompts.PROMPT_SOFTWARE_PRODUCTS_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'salesforce_partner':
                prompt_text = classification_prompts.PROMPT_SALESFORCE_PARTNER_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'hubspot_partner':
                prompt_text = classification_prompts.PROMPT_HUBSPOT_PARTNER_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'aws':
                prompt_text = classification_prompts.PROMPT_AWS_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'shopify':
                prompt_text = classification_prompts.PROMPT_SHOPIFY_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'ai_companies':
                prompt_text = classification_prompts.PROMPT_AI_COMPANIES_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'mobile_app':
                prompt_text = classification_prompts.PROMPT_MOBILE_APP_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'recruiting':
                prompt_text = classification_prompts.PROMPT_RECRUITING_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'banking':
                prompt_text = classification_prompts.PROMPT_BANKING_CLASSIFIER.format(structured_summary=facts_json)
            elif profile_name == 'platforms':
                prompt_text = classification_prompts.PROMPT_PLATFORMS_CLASSIFIER.format(structured_summary=facts_json)
            else:
                prompt_text = classification_prompts.PROMPT_SOFTWARE_CLASSIFICATION.format(structured_summary=facts_json)

            pro_response = await self.model_pro.generate_content_async(prompt_text)
            pro_cls = self._parse_json_response(pro_response.text)
            if pro_cls and self._is_classification_valid(pro_cls):
                pro_cls['_extraction_confidence'] = validation_score
                pro_cls['_classification_reviewed_by'] = 'pro'
                return pro_cls
        except Exception as e:
            logging.error(f"Final PRO classification attempt failed: {e}")

        return None
    
    def _is_classification_valid(self, classification: dict) -> bool:
        """Проверяет валидность классификации"""
        required_fields = ['reasoning', 'classification', 'final_output']
        
        for field in required_fields:
            if field not in classification or not classification[field]:
                return False
                
        # Проверка формата классификации
        valid_classifications = ['Match', 'No Match']
        if classification['classification'] not in valid_classifications:
            return False
            
        return True


# Основные функции (совместимость с существующим кодом)
analyzer = MultiStageAnalyzer()

async def extract_facts(content):
    """Совместимая функция для извлечения фактов"""
    result = await analyzer.extract_facts_with_validation(content)
    if result:
        return json.dumps(result, ensure_ascii=False)
    return None

async def classify_facts(facts_json):
    """Совместимая функция для классификации"""
    try:
        facts_data = json.loads(facts_json) if isinstance(facts_json, str) else facts_json
        result = await analyzer.classify_with_confidence(facts_data)
        
        if result and result.get('final_output', '').startswith("+ Relevant"):
            return result['final_output'].split('-', 1)[-1].strip()
            
    except Exception as e:
        logging.error(f"Error in classify_facts: {e}")
        
    return None
