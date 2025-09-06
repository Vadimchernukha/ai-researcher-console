# quality_monitor.py
"""Система мониторинга качества обработки"""

import csv
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import statistics
from dataclasses import dataclass

@dataclass
class QualityMetrics:
    """Метрики качества обработки"""
    total_processed: int = 0
    successful_extractions: int = 0
    successful_classifications: int = 0
    avg_confidence_score: float = 0.0
    content_quality_scores: List[float] = None
    common_errors: Dict[str, int] = None
    processing_times: List[float] = None
    
    def __post_init__(self):
        if self.content_quality_scores is None:
            self.content_quality_scores = []
        if self.common_errors is None:
            self.common_errors = {}
        if self.processing_times is None:
            self.processing_times = []

class QualityMonitor:
    """Монитор качества обработки"""
    
    def __init__(self, log_file: str = "quality_report.csv"):
        # Гарантируем наличие каталога
        try:
            import os
            os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
        except Exception:
            pass
        self.log_file = log_file
        self.metrics = QualityMetrics()
        self.detailed_logs: List[Dict] = []
        self.setup_logging()
        
    def setup_logging(self):
        """Настройка логирования качества"""
        # Создаем файл отчета если не существует
        try:
            with open(self.log_file, 'x', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "domain", "stage", "status", "confidence_score", 
                    "content_length", "processing_time", "error_type", "details"
                ])
        except FileExistsError:
            pass  # Файл уже существует
            
    def log_extraction_attempt(self, domain: str, content_length: int, 
                             success: bool, confidence_score: float = 0, 
                             processing_time: float = 0, error_details: str = ""):
        """Логирование попытки извлечения данных"""
        
        self.metrics.total_processed += 1
        
        if success:
            self.metrics.successful_extractions += 1
            self.metrics.content_quality_scores.append(confidence_score)
            
        self.metrics.processing_times.append(processing_time)
        
        # Детальный лог
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "stage": "extraction",
            "status": "success" if success else "failure",
            "confidence_score": confidence_score,
            "content_length": content_length,
            "processing_time": processing_time,
            "error_type": "" if success else self._categorize_error(error_details),
            "details": error_details
        }
        
        self.detailed_logs.append(log_entry)
        self._write_log_entry(log_entry)
        
        # Подсчет ошибок
        if not success:
            error_type = self._categorize_error(error_details)
            self.metrics.common_errors[error_type] = self.metrics.common_errors.get(error_type, 0) + 1
            
    def log_classification_attempt(self, domain: str, success: bool, 
                                 classification_result: str = "", 
                                 processing_time: float = 0, 
                                 error_details: str = ""):
        """Логирование попытки классификации"""
        
        if success:
            self.metrics.successful_classifications += 1
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "stage": "classification",
            "status": "success" if success else "failure",
            "confidence_score": 0,  # Для классификации не применимо
            "content_length": 0,
            "processing_time": processing_time,
            "error_type": "" if success else self._categorize_error(error_details),
            "details": classification_result if success else error_details
        }
        
        self.detailed_logs.append(log_entry)
        self._write_log_entry(log_entry)
        
    def _categorize_error(self, error_details: str) -> str:
        """Категоризация ошибок"""
        error_lower = error_details.lower()
        
        if "timeout" in error_lower:
            return "timeout"
        elif "ssl" in error_lower or "cert" in error_lower:
            return "ssl_certificate"
        elif "content too short" in error_lower:
            return "insufficient_content"
        elif "json" in error_lower or "parse" in error_lower:
            return "json_parsing"
        elif "api" in error_lower or "quota" in error_lower:
            return "api_error"
        elif "network" in error_lower or "connection" in error_lower:
            return "network_error"
        else:
            return "other"
            
    def _write_log_entry(self, log_entry: Dict):
        """Запись записи в лог файл"""
        try:
            with open(self.log_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    log_entry["timestamp"],
                    log_entry["domain"],
                    log_entry["stage"],
                    log_entry["status"],
                    log_entry["confidence_score"],
                    log_entry["content_length"],
                    log_entry["processing_time"],
                    log_entry["error_type"],
                    log_entry["details"]
                ])
        except Exception as e:
            logging.error(f"Failed to write quality log entry: {e}")
            
    def generate_report(self) -> Dict[str, Any]:
        """Генерация отчета о качестве"""
        
        if self.metrics.content_quality_scores:
            self.metrics.avg_confidence_score = statistics.mean(self.metrics.content_quality_scores)
        
        extraction_success_rate = (self.metrics.successful_extractions / max(1, self.metrics.total_processed)) * 100
        classification_success_rate = (self.metrics.successful_classifications / max(1, self.metrics.successful_extractions)) * 100
        
        avg_processing_time = statistics.mean(self.metrics.processing_times) if self.metrics.processing_times else 0
        
        report = {
            "summary": {
                "total_processed": self.metrics.total_processed,
                "extraction_success_rate": round(extraction_success_rate, 2),
                "classification_success_rate": round(classification_success_rate, 2),
                "overall_success_rate": round((self.metrics.successful_classifications / max(1, self.metrics.total_processed)) * 100, 2),
                "avg_confidence_score": round(self.metrics.avg_confidence_score, 2),
                "avg_processing_time": round(avg_processing_time, 2)
            },
            "quality_distribution": self._analyze_quality_distribution(),
            "error_analysis": self.metrics.common_errors,
            "performance_stats": {
                "min_processing_time": min(self.metrics.processing_times) if self.metrics.processing_times else 0,
                "max_processing_time": max(self.metrics.processing_times) if self.metrics.processing_times else 0,
                "median_processing_time": statistics.median(self.metrics.processing_times) if self.metrics.processing_times else 0
            },
            "recommendations": self._generate_recommendations()
        }
        
        return report
        
    def _analyze_quality_distribution(self) -> Dict[str, int]:
        """Анализ распределения качества"""
        distribution = {"excellent": 0, "good": 0, "average": 0, "poor": 0}
        
        for score in self.metrics.content_quality_scores:
            if score >= 80:
                distribution["excellent"] += 1
            elif score >= 60:
                distribution["good"] += 1
            elif score >= 40:
                distribution["average"] += 1
            else:
                distribution["poor"] += 1
                
        return distribution
        
    def _generate_recommendations(self) -> List[str]:
        """Генерация рекомендаций по улучшению"""
        recommendations = []
        
        # Анализ успешности извлечения
        extraction_rate = (self.metrics.successful_extractions / max(1, self.metrics.total_processed)) * 100
        if extraction_rate < 70:
            recommendations.append("Consider improving web scraping strategy - low extraction success rate")
            
        # Анализ ошибок
        total_errors = sum(self.metrics.common_errors.values())
        if total_errors > 0:
            most_common_error = max(self.metrics.common_errors.items(), key=lambda x: x[1])
            if most_common_error[1] / total_errors > 0.3:
                recommendations.append(f"Focus on fixing '{most_common_error[0]}' errors - they account for {round(most_common_error[1]/total_errors*100)}% of failures")
                
        # Анализ качества контента
        if self.metrics.content_quality_scores:
            avg_quality = statistics.mean(self.metrics.content_quality_scores)
            if avg_quality < 50:
                recommendations.append("Content quality is low - consider improving extraction prompts")
                
        # Анализ производительности
        if self.metrics.processing_times:
            avg_time = statistics.mean(self.metrics.processing_times)
            if avg_time > 10:  # Больше 10 секунд на запрос
                recommendations.append("Processing is slow - consider optimizing concurrency or timeouts")
                
        return recommendations
        
    def print_report(self):
        """Вывод отчета в консоль"""
        report = self.generate_report()
        
        print("\n" + "="*50)
        print("📊 ОТЧЕТ О КАЧЕСТВЕ ОБРАБОТКИ")
        print("="*50)
        
        print(f"\n📈 Общая статистика:")
        for key, value in report["summary"].items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
            
        print(f"\n🎯 Распределение качества:")
        for quality, count in report["quality_distribution"].items():
            print(f"  {quality.title()}: {count}")
            
        print(f"\n❌ Анализ ошибок:")
        for error_type, count in report["error_analysis"].items():
            print(f"  {error_type.replace('_', ' ').title()}: {count}")
            
        print(f"\n💡 Рекомендации:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
            
        print("\n" + "="*50)
