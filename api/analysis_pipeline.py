"""
6-этапный pipeline анализа сайтов
Восстановленная логика из оригинального проекта
"""

import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup
import google.generativeai as genai
from enum import Enum


class ProcessingStage(Enum):
    """Этапы обработки"""
    CONTENT_EXTRACTION = "content_extraction"
    INITIAL_CLASSIFICATION = "initial_classification"
    DETAILED_ANALYSIS = "detailed_analysis"
    CONTEXT_VALIDATION = "context_validation"
    CONFIDENCE_ASSESSMENT = "confidence_assessment"
    FINAL_DECISION = "final_decision"


class ProcessingResult:
    """Результат обработки на каждом этапе"""
    def __init__(self, stage: ProcessingStage, success: bool, data: Dict[str, Any], error: Optional[str] = None):
        self.stage = stage
        self.success = success
        self.data = data
        self.error = error
        self.timestamp = time.time()


class EnhancedPipeline:
    """6-этапный pipeline анализа сайтов"""
    
    def __init__(self):
        self.gemini_model = None
        self.results: List[ProcessingResult] = []
    
    async def _get_gemini_model(self):
        """Получение модели Gemini"""
        if not self.gemini_model:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not set")
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        return self.gemini_model
    
    async def _extract_content(self, url: str) -> ProcessingResult:
        """Этап 1: Извлечение контента"""
        try:
            if not url.startswith("http"):
                url = f"https://{url}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Извлекаем ключевые элементы
                title = soup.find('title')
                title_text = title.get_text().strip() if title else ""
                
                # Удаляем скрипты и стили
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Получаем основной текст более агрессивно
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Если текст слишком короткий, пробуем альтернативные методы
                if len(text) < 100:
                    # Пробуем получить текст из body
                    body = soup.find('body')
                    if body:
                        text = body.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                
                # Если все еще короткий, используем весь HTML как fallback
                if len(text) < 100:
                    text = response.text[:5000]  # Первые 5000 символов HTML
                
                # Дополнительно извлекаем текст из всех элементов
                if len(text) < 200:
                    all_text_elements = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    additional_text = ' '.join([elem.get_text().strip() for elem in all_text_elements if elem.get_text().strip()])
                    if additional_text:
                        text = additional_text[:3000]
                
                # Извлекаем мета-теги
                meta_description = ""
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    meta_description = meta_desc.get('content', '')
                
                # Извлекаем заголовки
                headers = []
                for tag in ['h1', 'h2', 'h3']:
                    for header in soup.find_all(tag):
                        headers.append(header.get_text().strip())
                
                # Извлекаем ссылки
                links = []
                for link in soup.find_all('a', href=True):
                    href = link.get('href')
                    text = link.get_text().strip()
                    if href and text:
                        links.append({'url': href, 'text': text})
                
                content_data = {
                    'url': url,
                    'title': title_text,
                    'meta_description': meta_description,
                    'main_text': text[:5000],  # Ограничиваем размер
                    'headers': headers[:20],   # Первые 20 заголовков
                    'links': links[:50],       # Первые 50 ссылок
                    'content_length': len(text),
                    'status_code': response.status_code
                }
                
                return ProcessingResult(
                    stage=ProcessingStage.CONTENT_EXTRACTION,
                    success=True,
                    data=content_data
                )
                
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.CONTENT_EXTRACTION,
                success=False,
                data={},
                error=str(e)
            )
    
    async def _initial_classification(self, content_data: Dict[str, Any], profile_type: str) -> ProcessingResult:
        """Этап 2: Первичная классификация"""
        try:
            model = await self._get_gemini_model()
            
            # Создаем промпт для первичной классификации
            prompt = f"""
            Analyze this website content and determine if it matches the {profile_type} profile.
            
            Website Title: {content_data.get('title', '')}
            Meta Description: {content_data.get('meta_description', '')}
            Main Content: {content_data.get('main_text', '')[:2000]}
            Headers: {', '.join(content_data.get('headers', [])[:10])}
            
            Profile Types:
            - software: Software companies, SaaS platforms, development tools
            - fintech: Financial technology, payment systems, banking solutions
            - edtech: Educational technology, online learning platforms
            - healthtech: Healthcare technology, medical software, telemedicine
            
            Return JSON with:
            {{
                "relevance_score": 0-100,
                "primary_category": "category name",
                "key_indicators": ["indicator1", "indicator2"],
                "confidence": 0-100,
                "reasoning": "explanation"
            }}
            """
            
            response = await model.generate_content_async(prompt)
            raw_text = response.text.strip()
            
            # Парсим JSON ответ
            try:
                result = json.loads(raw_text)
            except:
                # Fallback parsing
                result = {
                    "relevance_score": 50,
                    "primary_category": "unknown",
                    "key_indicators": [],
                    "confidence": 50,
                    "reasoning": "Could not parse AI response"
                }
            
            return ProcessingResult(
                stage=ProcessingStage.INITIAL_CLASSIFICATION,
                success=True,
                data=result
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.INITIAL_CLASSIFICATION,
                success=False,
                data={},
                error=str(e)
            )
    
    async def _detailed_analysis(self, content_data: Dict[str, Any], initial_result: Dict[str, Any]) -> ProcessingResult:
        """Этап 3: Детальный анализ"""
        try:
            model = await self._get_gemini_model()
            
            prompt = f"""
            Perform detailed analysis of this website based on initial classification.
            
            Content: {content_data.get('main_text', '')[:3000]}
            Headers: {', '.join(content_data.get('headers', [])[:15])}
            Links: {len(content_data.get('links', []))} links found
            
            Initial Classification: {initial_result.get('primary_category', 'unknown')}
            Relevance Score: {initial_result.get('relevance_score', 0)}
            
            Analyze:
            1. Business model and value proposition
            2. Target audience and market segment
            3. Technology stack indicators
            4. Competitive positioning
            5. Growth stage indicators
            
            Return JSON:
            {{
                "business_model": "description",
                "target_audience": "description", 
                "technology_indicators": ["tech1", "tech2"],
                "market_position": "description",
                "growth_stage": "startup|growth|mature|enterprise",
                "detailed_score": 0-100
            }}
            """
            
            response = await model.generate_content_async(prompt)
            raw_text = response.text.strip()
            
            try:
                result = json.loads(raw_text)
            except:
                result = {
                    "business_model": "unknown",
                    "target_audience": "unknown",
                    "technology_indicators": [],
                    "market_position": "unknown", 
                    "growth_stage": "unknown",
                    "detailed_score": 50
                }
            
            return ProcessingResult(
                stage=ProcessingStage.DETAILED_ANALYSIS,
                success=True,
                data=result
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.DETAILED_ANALYSIS,
                success=False,
                data={},
                error=str(e)
            )
    
    async def _context_validation(self, content_data: Dict[str, Any], analysis_results: List[Dict[str, Any]]) -> ProcessingResult:
        """Этап 4: Валидация контекста"""
        try:
            model = await self._get_gemini_model()
            
            # Объединяем результаты предыдущих этапов
            combined_data = {
                'content': content_data,
                'initial': analysis_results[0] if analysis_results else {},
                'detailed': analysis_results[1] if len(analysis_results) > 1 else {}
            }
            
            prompt = f"""
            Validate the analysis results and check for consistency.
            
            Website: {content_data.get('title', '')}
            URL: {content_data.get('url', '')}
            
            Initial Classification: {combined_data['initial']}
            Detailed Analysis: {combined_data['detailed']}
            
            Check for:
            1. Consistency between initial and detailed analysis
            2. Red flags or inconsistencies
            3. Missing information that could affect classification
            4. Quality of evidence supporting the classification
            
            Return JSON:
            {{
                "is_consistent": true/false,
                "red_flags": ["flag1", "flag2"],
                "missing_info": ["info1", "info2"],
                "evidence_quality": "high|medium|low",
                "validation_score": 0-100
            }}
            """
            
            response = await model.generate_content_async(prompt)
            raw_text = response.text.strip()
            
            try:
                result = json.loads(raw_text)
            except:
                result = {
                    "is_consistent": True,
                    "red_flags": [],
                    "missing_info": [],
                    "evidence_quality": "medium",
                    "validation_score": 75
                }
            
            return ProcessingResult(
                stage=ProcessingStage.CONTEXT_VALIDATION,
                success=True,
                data=result
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.CONTEXT_VALIDATION,
                success=False,
                data={},
                error=str(e)
            )
    
    async def _confidence_assessment(self, all_results: List[ProcessingResult]) -> ProcessingResult:
        """Этап 5: Оценка уверенности"""
        try:
            # Анализируем результаты всех предыдущих этапов
            successful_stages = [r for r in all_results if r.success]
            failed_stages = [r for r in all_results if not r.success]
            
            # Базовый confidence score
            base_confidence = 100 if len(failed_stages) == 0 else max(0, 100 - len(failed_stages) * 20)
            
            # Анализируем качество данных
            content_result = next((r for r in successful_stages if r.stage == ProcessingStage.CONTENT_EXTRACTION), None)
            content_quality = 0
            if content_result:
                content_length = content_result.data.get('content_length', 0)
                if content_length > 1000:
                    content_quality = 100
                elif content_length > 500:
                    content_quality = 75
                elif content_length > 200:
                    content_quality = 50
                else:
                    content_quality = 25
            
            # Анализируем согласованность результатов
            consistency_score = 75  # Default
            validation_result = next((r for r in successful_stages if r.stage == ProcessingStage.CONTEXT_VALIDATION), None)
            if validation_result:
                consistency_score = validation_result.data.get('validation_score', 75)
            
            # Финальный confidence
            final_confidence = (base_confidence + content_quality + consistency_score) / 3
            
            assessment_data = {
                "base_confidence": base_confidence,
                "content_quality": content_quality,
                "consistency_score": consistency_score,
                "final_confidence": round(final_confidence, 1),
                "successful_stages": len(successful_stages),
                "failed_stages": len(failed_stages),
                "quality_factors": {
                    "content_length": content_result.data.get('content_length', 0) if content_result else 0,
                    "stages_completed": len(successful_stages),
                    "validation_passed": validation_result.data.get('is_consistent', True) if validation_result else True
                }
            }
            
            return ProcessingResult(
                stage=ProcessingStage.CONFIDENCE_ASSESSMENT,
                success=True,
                data=assessment_data
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.CONFIDENCE_ASSESSMENT,
                success=False,
                data={},
                error=str(e)
            )
    
    async def _final_decision(self, all_results: List[ProcessingResult], profile_type: str) -> ProcessingResult:
        """Этап 6: Финальное решение"""
        try:
            model = await self._get_gemini_model()
            
            # Собираем все данные для финального решения
            content_result = next((r for r in all_results if r.stage == ProcessingStage.CONTENT_EXTRACTION), None)
            initial_result = next((r for r in all_results if r.stage == ProcessingStage.INITIAL_CLASSIFICATION), None)
            detailed_result = next((r for r in all_results if r.stage == ProcessingStage.DETAILED_ANALYSIS), None)
            validation_result = next((r for r in all_results if r.stage == ProcessingStage.CONTEXT_VALIDATION), None)
            confidence_result = next((r for r in all_results if r.stage == ProcessingStage.CONFIDENCE_ASSESSMENT), None)
            
            # Подготавливаем сводку для AI
            summary = {
                "website": content_result.data.get('title', '') if content_result else '',
                "profile_type": profile_type,
                "initial_classification": initial_result.data if initial_result else {},
                "detailed_analysis": detailed_result.data if detailed_result else {},
                "validation": validation_result.data if validation_result else {},
                "confidence": confidence_result.data if confidence_result else {}
            }
            
            prompt = f"""
            Make final decision on website classification based on comprehensive 6-stage analysis.
            
            Target Profile: {profile_type}
            Website: {summary['website']}
            
            Analysis Summary:
            - Initial Classification: {summary['initial_classification']}
            - Detailed Analysis: {summary['detailed_analysis']}
            - Validation Results: {summary['validation']}
            - Confidence Assessment: {summary['confidence']}
            
            Make final decision considering:
            1. Overall relevance to {profile_type} profile
            2. Quality and consistency of analysis
            3. Confidence level
            4. Any red flags or concerns
            
            Return JSON:
            {{
                "final_classification": "specific classification",
                "relevance_score": 0-100,
                "confidence": 0-100,
                "decision": "ACCEPT|REJECT|REVIEW",
                "reasoning": "detailed explanation",
                "key_factors": ["factor1", "factor2"],
                "recommendations": ["rec1", "rec2"]
            }}
            """
            
            response = await model.generate_content_async(prompt)
            raw_text = response.text.strip()
            
            try:
                result = json.loads(raw_text)
            except:
                # Fallback decision
                confidence_data = confidence_result.data if confidence_result else {}
                final_confidence = confidence_data.get('final_confidence', 50)
                
                result = {
                    "final_classification": f"{profile_type} candidate",
                    "relevance_score": 50,
                    "confidence": final_confidence,
                    "decision": "REVIEW" if final_confidence < 70 else "ACCEPT",
                    "reasoning": "Analysis completed with fallback decision",
                    "key_factors": ["automated_analysis"],
                    "recommendations": ["manual_review_recommended"]
                }
            
            return ProcessingResult(
                stage=ProcessingStage.FINAL_DECISION,
                success=True,
                data=result
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=ProcessingStage.FINAL_DECISION,
                success=False,
                data={},
                error=str(e)
            )
    
    async def analyze_website(self, url: str, domain: str, profile_type: str) -> Dict[str, Any]:
        """Запуск полного 6-этапного анализа"""
        start_time = time.time()
        self.results = []
        
        try:
            # Этап 1: Извлечение контента
            content_result = await self._extract_content(url)
            self.results.append(content_result)
            
            if not content_result.success:
                raise Exception(f"Content extraction failed: {content_result.error}")
            
            # Этап 2: Первичная классификация
            initial_result = await self._initial_classification(content_result.data, profile_type)
            self.results.append(initial_result)
            
            # Этап 3: Детальный анализ
            detailed_result = await self._detailed_analysis(content_result.data, initial_result.data)
            self.results.append(detailed_result)
            
            # Этап 4: Валидация контекста
            analysis_results = [r.data for r in self.results[1:3] if r.success]
            validation_result = await self._context_validation(content_result.data, analysis_results)
            self.results.append(validation_result)
            
            # Этап 5: Оценка уверенности
            confidence_result = await self._confidence_assessment(self.results)
            self.results.append(confidence_result)
            
            # Этап 6: Финальное решение
            final_result = await self._final_decision(self.results, profile_type)
            self.results.append(final_result)
            
            processing_time = time.time() - start_time
            
            # Формируем итоговый результат
            final_data = final_result.data if final_result.success else {}
            
            return {
                "domain": domain,
                "url": url,
                "profile_type": profile_type,
                "classification": final_data.get("final_classification", "Unknown"),
                "confidence": final_data.get("confidence", 0),
                "relevance_score": final_data.get("relevance_score", 0),
                "decision": final_data.get("decision", "REVIEW"),
                "comment": final_data.get("reasoning", "Analysis completed"),
                "processing_time": round(processing_time, 2),
                "stages_completed": len([r for r in self.results if r.success]),
                "total_stages": 6,
                "raw_data": {
                    "pipeline_results": [r.data for r in self.results if r.success],
                    "stage_errors": [{"stage": r.stage.value, "error": r.error} for r in self.results if not r.success]
                }
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                "domain": domain,
                "url": url,
                "profile_type": profile_type,
                "classification": "Analysis Failed",
                "confidence": 0,
                "relevance_score": 0,
                "decision": "REJECT",
                "comment": f"Pipeline error: {str(e)}",
                "processing_time": round(processing_time, 2),
                "stages_completed": len([r for r in self.results if r.success]),
                "total_stages": 6,
                "raw_data": {
                    "error": str(e),
                    "pipeline_results": [r.data for r in self.results if r.success]
                }
            }
