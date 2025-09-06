# enhanced_pipeline.py
"""
Новый многоэтапный подход к классификации с повышенной точностью
"""

import asyncio
import csv
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time

from src.scrapers.content_scraper import smart_fetch_content
from src.analyzers.ai_analyzer import MultiStageAnalyzer
from src.validators.quality_monitor import QualityMonitor
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.settings import *
from tqdm import tqdm

class ProcessingStage(Enum):
    """Этапы обработки"""
    CONTENT_EXTRACTION = "content_extraction"
    CONTENT_VALIDATION = "content_validation"
    INITIAL_CLASSIFICATION = "initial_classification"
    DETAILED_ANALYSIS = "detailed_analysis"
    CROSS_VALIDATION = "cross_validation"
    FINAL_DECISION = "final_decision"

@dataclass
class ProcessingResult:
    """Результат обработки сайта"""
    domain: str
    stage: ProcessingStage
    success: bool
    confidence_score: float
    data: Dict[str, Any]
    processing_time: float
    error_details: str = ""

class EnhancedPipeline:
    """Улучшенный пайплайн обработки с многоэтапной валидацией"""
    
    def __init__(self, profile: str = "software"):
        self.profile = profile
        self.analyzer = MultiStageAnalyzer(profile=profile)
        self.quality_monitor = QualityMonitor()
        self.processed_domains = set()
        
    async def process_website_comprehensive(self, context, url: str) -> Optional[Dict[str, Any]]:
        """Комплексная обработка сайта через все этапы"""
        
        domain = self._extract_domain(url)
        # Убираем вывод в консоль, только в логи
        
        # Этап 1: Извлечение контента
        start_time = time.time()
        # Этапы 1-6: Все логирование только в файлы, без консольного вывода
        content_result = await self._stage_1_extract_content(context, url, domain)
        if not content_result.success:
            return None
            
        validation_result = await self._stage_2_validate_content(
            content_result.data["content"], domain
        )
        if not validation_result.success:
            return None
            
        initial_classification = await self._stage_3_initial_classification(
            validation_result.data, domain
        )
        if not initial_classification.success:
            return None
            
        # Этап 4: Детальный анализ (только для потенциальных совпадений)
        if initial_classification.data.get("potential_match", False):
            detailed_analysis = await self._stage_4_detailed_analysis(
                validation_result.data, initial_classification.data, domain
            )
            
            if detailed_analysis.success:
                cross_validation = await self._stage_5_cross_validation(
                    detailed_analysis.data, domain
                )
                
                if cross_validation.success:
                    final_decision = await self._stage_6_final_decision(
                        cross_validation.data, domain
                    )
                    
                    total_time = time.time() - start_time
                    
                    if final_decision.success and final_decision.data.get("is_match"):
                        return {
                            "domain": domain,
                            "classification": final_decision.data["classification"],
                            "comment": final_decision.data.get("reasoning", ""),
                            "confidence": final_decision.confidence_score,
                            "processing_time": total_time,
                            "stages_completed": 6
                        }
        return None
    
    async def _stage_1_extract_content(self, context, url: str, domain: str) -> ProcessingResult:
        """Этап 1: Извлечение контента с веб-сайта"""
        
        start_time = time.time()
        
        try:
            content = await smart_fetch_content(context, url)
            processing_time = time.time() - start_time
            
            if content and len(content) >= MIN_CONTENT_LENGTH:
                self.quality_monitor.log_extraction_attempt(
                    domain, len(content), True, 100, processing_time
                )
                
                return ProcessingResult(
                    domain=domain,
                    stage=ProcessingStage.CONTENT_EXTRACTION,
                    success=True,
                    confidence_score=100.0,
                    data={"content": content, "length": len(content)},
                    processing_time=processing_time
                )
            else:
                error_msg = f"Insufficient content: {len(content) if content else 0} chars"
                self.quality_monitor.log_extraction_attempt(
                    domain, len(content) if content else 0, False, 0, processing_time, error_msg
                )
                
                return ProcessingResult(
                    domain=domain,
                    stage=ProcessingStage.CONTENT_EXTRACTION,
                    success=False,
                    confidence_score=0.0,
                    data={},
                    processing_time=processing_time,
                    error_details=error_msg
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Content extraction error: {str(e)}"
            
            self.quality_monitor.log_extraction_attempt(
                domain, 0, False, 0, processing_time, error_msg
            )
            
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.CONTENT_EXTRACTION,
                success=False,
                confidence_score=0.0,
                data={},
                processing_time=processing_time,
                error_details=error_msg
            )
    
    async def _stage_2_validate_content(self, content: str, domain: str) -> ProcessingResult:
        """Этап 2: Валидация качества контента"""
        
        start_time = time.time()
        
        # Базовая валидация
        word_count = len(content.split())
        business_keywords = [
            'services', 'products', 'solutions', 'company', 'business',
            'about', 'contact', 'pricing', 'features', 'software', 'platform'
        ]
        
        keyword_matches = sum(1 for keyword in business_keywords if keyword in content.lower())
        
        # Скоринг качества
        quality_score = 0
        
        # Длина контента (40 баллов максимум)
        if len(content) >= 1000:
            quality_score += 40
        elif len(content) >= 500:
            quality_score += 30
        elif len(content) >= 200:
            quality_score += 20
        
        # Количество слов (30 баллов максимум)
        if word_count >= 200:
            quality_score += 30
        elif word_count >= 100:
            quality_score += 20
        elif word_count >= 50:
            quality_score += 10
        
        # Бизнес-ключевые слова (30 баллов максимум)
        quality_score += min(30, keyword_matches * 5)
        
        processing_time = time.time() - start_time
        
        if quality_score >= MIN_CONFIDENCE_SCORE:
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.CONTENT_VALIDATION,
                success=True,
                confidence_score=quality_score,
                data={
                    "content": content,
                    "quality_score": quality_score,
                    "word_count": word_count,
                    "keyword_matches": keyword_matches
                },
                processing_time=processing_time
            )
        else:
            # Ослабленный режим: всё равно пропускаем дальше, но с низкой уверенностью
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.CONTENT_VALIDATION,
                success=True,
                confidence_score=quality_score,
                data={
                    "content": content,
                    "quality_score": quality_score,
                    "word_count": word_count,
                    "keyword_matches": keyword_matches,
                    "note": "Low quality content, forced pass"
                },
                processing_time=processing_time
            )
    
    async def _stage_3_initial_classification(self, content_data: Dict, domain: str) -> ProcessingResult:
        """Этап 3: Первичная классификация (быстрая фильтрация)"""
        
        start_time = time.time()
        
        try:
            # Быстрый анализ на основе ключевых слов
            content = content_data["content"]
            
            # Индикаторы под профиль
            fintech_keywords = [
                'payment', 'merchant', 'pos', 'card', 'transaction', 'fintech',
                'financial', 'banking', 'credit', 'processing', 'gateway'
            ]
            software_keywords = [
                'saas', 'software', 'platform', 'cloud', 'app', 'application',
                'pricing', 'features', 'sign in', 'login', 'try for free'
            ]
            edtech_keywords = [
                'school', 'schools', 'schule', 'kindergarten', 'kita', 'k-12',
                'teacher', 'parent', 'student', 'classbook', 'gradebook',
                'timetable', 'schedule', 'lesson', 'homework', 'announcement',
                'sso', 'single sign', 'gdpr', 'dsgvo', 'microsoft 365', 'google workspace',
                # EdTech system types (broad recall)
                'learning experience platform', 'lxp',
                'digital learning platform',
                'learning ecosystem',
                'online training platform',
                'educational platform',
                'learning portal',
                'learning management system', 'lms',
                'student information system', 'sis',
                'academic management system',
                'school management system',
                'education management system',
                'microlearning platform',
                'skills development platform',
                'knowledge management system', 'kms',
                'assessment platform', 'testing platform',
                'digital academy',
                'course management system', 'cms',
                'virtual learning environment', 'vle',
                'online learning platform',
                'e-learning platform', 'elearning platform'
            ]
            
            # Исключающие индикаторы
            exclusion_keywords = [
                'hospital', 'clinic', 'doctor', 'medical', 'health', 'pharmacy',
                'restaurant', 'food', 'travel', 'hotel'
            ]
            
            text_l = content.lower()
            fintech_score = sum(1 for keyword in fintech_keywords if keyword in text_l)
            software_score = sum(1 for keyword in software_keywords if keyword in text_l)
            edtech_score = sum(1 for keyword in edtech_keywords if keyword in text_l)
            exclusion_score = sum(1 for keyword in exclusion_keywords if keyword in content.lower())
            
            # Логика принятия решения
            potential_match = False
            confidence = 0
            
            if self.profile == "software":
                profile_score = software_score
            elif self.profile == "iso":
                profile_score = fintech_score
            elif self.profile == "edtech":
                # Строгий фильтр для EdTech: нужно минимум 2 ключевых слова
                profile_score = edtech_score
                if edtech_score >= 1 and exclusion_score <= 1:
                    potential_match = True
                    confidence = min(85, edtech_score * 20)
                else:
                    potential_match = False
                    confidence = 90  # Высокая уверенность в исключении
            elif self.profile in ("pharma", "telemedicine"):
                # Для других доменных профилей пропускаем по эвристике
                profile_score = 1 if len(text_l) > 0 else 0
            else:
                profile_score = max(software_score, fintech_score)

            # Логика для не-edtech профилей
            if self.profile != "edtech":
                if profile_score >= 1 and exclusion_score <= profile_score:
                    potential_match = True
                    confidence = min(85, max(fintech_score * 12, software_score * 10, 40))
                elif self.profile == "iso" and fintech_score == 0 and exclusion_score > 2:
                    potential_match = False
                    confidence = 90  # Высокая уверенность в исключении
                else:
                    potential_match = True  # Неопределенность - отправляем на детальный анализ
                    confidence = 30
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.INITIAL_CLASSIFICATION,
                success=True,
                confidence_score=confidence,
                data={
                    "potential_match": potential_match,
                    "fintech_score": fintech_score,
                    "exclusion_score": exclusion_score,
                    "content_data": content_data
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.INITIAL_CLASSIFICATION,
                success=False,
                confidence_score=0.0,
                data={},
                processing_time=processing_time,
                error_details=str(e)
            )
    
    async def _stage_4_detailed_analysis(self, content_data: Dict, 
                                       initial_data: Dict, domain: str) -> ProcessingResult:
        """Этап 4: Детальный анализ с помощью LLM"""
        
        start_time = time.time()
        
        try:
            # Используем улучшенный анализатор
            extracted_data = await self.analyzer.extract_facts_with_validation(content_data["content"])
            
            if not extracted_data:
                processing_time = time.time() - start_time
                return ProcessingResult(
                    domain=domain,
                    stage=ProcessingStage.DETAILED_ANALYSIS,
                    success=False,
                    confidence_score=0.0,
                    data={},
                    processing_time=processing_time,
                    error_details="Failed to extract facts"
                )
            
            # Получаем оценку качества извлечения
            extraction_confidence = extracted_data.get('_validation', {}).get('confidence_score', 0)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.DETAILED_ANALYSIS,
                success=True,
                confidence_score=extraction_confidence,
                data={
                    "extracted_facts": extracted_data,
                    "extraction_confidence": extraction_confidence,
                    "initial_data": initial_data
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.DETAILED_ANALYSIS,
                success=False,
                confidence_score=0.0,
                data={},
                processing_time=processing_time,
                error_details=str(e)
            )
    
    async def _stage_5_cross_validation(self, detailed_data: Dict, domain: str) -> ProcessingResult:
        """Этап 5: Кросс-валидация результатов"""
        
        start_time = time.time()
        
        try:
            extracted_facts = detailed_data["extracted_facts"]
            
            # Классификация с помощью LLM
            classification_result = await self.analyzer.classify_with_confidence(extracted_facts)
            
            if not classification_result:
                processing_time = time.time() - start_time
                return ProcessingResult(
                    domain=domain,
                    stage=ProcessingStage.CROSS_VALIDATION,
                    success=False,
                    confidence_score=0.0,
                    data={},
                    processing_time=processing_time,
                    error_details="Classification failed"
                )
            
            # Сравнение с первичной классификацией
            initial_match = detailed_data["initial_data"]["potential_match"]

            def _is_positive(label: str) -> bool:
                if not isinstance(label, str):
                    return False
                lbl = label.strip()
                if self.profile == "pharma":
                    return lbl == "Relevant"
                return lbl == "Match"

            llm_match = _is_positive(classification_result.get("classification"))
            
            # Логика кросс-валидации
            cross_validation_score = 0
            consistency_bonus = 0
            
            if initial_match == llm_match:
                consistency_bonus = 20  # Бонус за согласованность
            
            extraction_confidence = detailed_data["extraction_confidence"]
            classification_confidence = 70 if llm_match else 30  # Базовая уверенность LLM
            
            cross_validation_score = (extraction_confidence + classification_confidence + consistency_bonus) / 3
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.CROSS_VALIDATION,
                success=True,
                confidence_score=cross_validation_score,
                data={
                    "cross_validation_score": cross_validation_score,
                    "classification_result": classification_result,
                    "initial_match": initial_match,
                    "llm_match": llm_match,
                    "consistency_bonus": consistency_bonus,
                    "detailed_data": detailed_data
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.CROSS_VALIDATION,
                success=False,
                confidence_score=0.0,
                data={},
                processing_time=processing_time,
                error_details=str(e)
            )
    
    async def _stage_6_final_decision(self, validation_data: Dict, domain: str) -> ProcessingResult:
        """Этап 6: Финальное решение на основе всех данных"""
        
        start_time = time.time()
        
        try:
            classification_result = validation_data["classification_result"]
            confidence_score = validation_data.get("cross_validation_score", 0)
            
            # Финальное решение
            def _is_positive(label: str) -> bool:
                if not isinstance(label, str):
                    return False
                lbl = label.strip()
                if self.profile == "pharma":
                    return lbl == "Relevant"
                return lbl == "Match"

            is_match = (
                _is_positive(classification_result.get("classification")) and
                confidence_score >= CLASSIFICATION_SETTINGS["confidence_threshold"] * 100
            )
            
            if is_match:
                # Универсальная нормализация итоговой метки
                final_output = classification_result.get("final_output", "")
                if isinstance(final_output, str) and final_output.startswith("+ Relevant"):
                    result_text = final_output.split('-', 1)[-1].strip()
                else:
                    base = classification_result.get("classification", "Relevant")
                    if self.profile == "pharma":
                        result_text = "Pharma Relevant"
                    elif self.profile == "iso":
                        result_text = "ISO/MSP Lead"
                    elif self.profile == "software":
                        result_text = "Software Lead"
                    elif self.profile == "edtech":
                        # Определяем тип EdTech компании из reasoning или classification_result
                        final_output = classification_result.get("final_output", "")
                        reasoning = classification_result.get("reasoning", "")
                        if "provider" in reasoning.lower() or "software provider" in final_output.lower():
                            result_text = "EdTech Software Provider"
                        else:
                            result_text = "EdTech Platform"
                    else:
                        result_text = base
            else:
                result_text = None
                
            processing_time = time.time() - start_time
            
            # Логирование результата классификации
            self.quality_monitor.log_classification_attempt(
                domain, is_match, result_text or "Not Relevant", processing_time
            )
            
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.FINAL_DECISION,
                success=True,
                confidence_score=confidence_score,
                data={
                    "is_match": is_match,
                    "classification": result_text,
                    "final_confidence": confidence_score,
                    "reasoning": classification_result.get("reasoning", "")
                },
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ProcessingResult(
                domain=domain,
                stage=ProcessingStage.FINAL_DECISION,
                success=False,
                confidence_score=0.0,
                data={},
                processing_time=processing_time,
                error_details=str(e)
            )
    
    def _extract_domain(self, url: str) -> str:
        """Извлечение домена из URL"""
        return url.replace("https://", "").replace("http://", "").split('/')[0].lower()
    
    def generate_quality_report(self):
        """Генерация отчета о качестве"""
        self.quality_monitor.print_report()
        return self.quality_monitor.generate_report()
