# improved_scraper.py
import logging
from bs4 import BeautifulSoup
from src.core.enhanced_utils import clean_text
import asyncio
import time
from urllib.parse import urljoin, urlparse
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import config.settings as config

MAX_CONTENT_LENGTH = 6000  # Увеличено для лучшего контекста
MIN_CONTENT_LENGTH = 20   # Повышено минимальное требование

class ContentQualityValidator:
    """Валидация качества извлеченного контента"""
    
    @staticmethod
    def validate_content(text: str, url: str) -> dict:
        """Возвращает метрики качества контента"""
        metrics = {
            'length': len(text),
            'words_count': len(text.split()),
            'sentences_count': text.count('.') + text.count('!') + text.count('?'),
            'has_business_keywords': any(keyword in text.lower() for keyword in [
                'services', 'products', 'solutions', 'company', 'business',
                'about', 'contact', 'pricing', 'features'
            ]),
            'quality_score': 0,
            'extraction_issues': []
        }
        
        # Подсчет качества (более мягкие критерии)
        if metrics['length'] < MIN_CONTENT_LENGTH:
            metrics['extraction_issues'].append('Content too short')
        if metrics['words_count'] < 30:  # Снижен с 50 до 30
            metrics['extraction_issues'].append('Too few meaningful words')
        if not metrics['has_business_keywords']:
            metrics['extraction_issues'].append('No business-related keywords found')
            
        # Качественная оценка (более мягкая)
        score = 0
        if metrics['length'] >= MIN_CONTENT_LENGTH: score += 25  # Снижен с 30
        if metrics['words_count'] >= 50: score += 25   # Снижен с 100 и 30
        if metrics['words_count'] >= 100: score += 20  # Дополнительные баллы
        if metrics['has_business_keywords']: score += 30  # Снижен с 40
        
        metrics['quality_score'] = score
        return metrics


def enhanced_parse_html(html, url):
    """Улучшенный парсер HTML с множественными стратегиями"""
    try:
        soup = BeautifulSoup(html, "lxml")
        
        # Удаляем ненужные элементы
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'iframe']):
            tag.decompose()
            
        # Стратегия 1: Основной контент
        main_content = ""
        content_selectors = [
            'main', 'article', '.content', '#content', '#main',
            '.main-content', '.page-content', '.entry-content',
            '.post-content', '.article-content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                main_content = element.get_text(separator=' ', strip=True)
                break
                
        # Стратегия 2: Если основной контент не найден, берем body
        if not main_content or len(main_content) < MIN_CONTENT_LENGTH:
            main_content = soup.body.get_text(separator=' ', strip=True) if soup.body else ''
            
        # Стратегия 3: Извлечение ключевых секций
        if not main_content or len(main_content) < MIN_CONTENT_LENGTH:
            key_sections = []
            for section in soup.find_all(['section', 'div'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['about', 'service', 'product', 'solution', 'feature', 'company', 'business']
            )):
                section_text = section.get_text(separator=' ', strip=True)
                if len(section_text) > 30:  # Снижен с 50 до 30
                    key_sections.append(section_text)
            main_content = ' '.join(key_sections)
            
        # Стратегия 4: Если все еще мало контента, берем все параграфы
        if not main_content or len(main_content) < MIN_CONTENT_LENGTH:
            paragraphs = []
            for p in soup.find_all('p'):
                p_text = p.get_text(strip=True)
                if len(p_text) > 20:  # Минимальная длина параграфа
                    paragraphs.append(p_text)
            main_content = ' '.join(paragraphs)
            
        text = clean_text(main_content)
        
        # Валидация качества
        quality_metrics = ContentQualityValidator.validate_content(text, url)
        
        # Снижаем порог качества и добавляем fallback логику
        if quality_metrics['quality_score'] < 20:  # Снижен с 40 до 20
            logging.warning(f"Low quality content for {url}: score={quality_metrics['quality_score']}, issues={quality_metrics['extraction_issues']}")
            # Вместо возврата None, пробуем альтернативные стратегии
            return text[:MAX_CONTENT_LENGTH] if text else None
            
        return text[:MAX_CONTENT_LENGTH]
        
    except Exception as e:
        logging.error(f"Ошибка парсинга HTML для {url}: {e}")
        return None


async def smart_fetch_content(context, url):
    """Умная загрузка контента с множественными стратегиями + защита от зависания"""
    page = None
    try:
        # Глобальный timeout для всей операции (30s max)
        return await asyncio.wait_for(_smart_fetch_content_internal(context, url), timeout=30.0)
    except asyncio.TimeoutError:
        logging.warning(f"Операция превысила 30s для {url}, пропускаем")
        return None
    except Exception as e:
        logging.error(f"Критическая ошибка при обработке {url}: {e}")
        return None

async def _smart_fetch_content_internal(context, url):
    """Внутренняя функция загрузки контента"""
    page = None
    try:
        page = await context.new_page()
        
        # Блокируем ресурсы для ускорения
        await page.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,css,ico}", lambda route: route.abort())
        
        # Стратегия 1: Быстрая загрузка (агрессивные таймауты)
        try:
            await page.goto(url, timeout=8000, wait_until="domcontentloaded")  # 8s вместо 15s
            await asyncio.sleep(0.3)  # Уменьшено с 0.5s до 0.3s
            
            html = await page.content()
            content = enhanced_parse_html(html, url)
            
            if content:
                await page.close()
                return content
                
        except Exception as e:
            logging.info(f"Быстрая загрузка не удалась для {url}: {e}")
            
        # Стратегия 2: Ожидание ключевых элементов
        try:
            selectors_to_wait = [
                "main", "article", ".content", "#content", 
                ".main-content", "h1", "p"
            ]
            
            for selector in selectors_to_wait:
                try:
                    await page.wait_for_selector(selector, timeout=3000)  # 3s вместо 5s
                    break
                except:
                    continue
                    
            await asyncio.sleep(0.5)  # Уменьшено с 1s до 0.5s
            html = await page.content()
            content = enhanced_parse_html(html, url)
            
            if content:
                await page.close()
                return content
                
        except Exception as e:
            logging.info(f"Ожидание элементов не помогло для {url}: {e}")
            
        # Стратегия 3: Прокрутка и ожидание
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            await asyncio.sleep(1)
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(0.5)  # Уменьшено с 1s до 0.5s
            
            html = await page.content()
            content = enhanced_parse_html(html, url)
            
            if content:
                await page.close()
                return content
                
        except Exception as e:
            logging.warning(f"Прокрутка не помогла для {url}: {e}")
            
        # Fallback: отключен для ускорения (экономим время)
        try:
            if False:  # Отключаем дополнительные страницы для скорости
                combined = content or ""
                suffixes = ["/pricing", "/features", "/product", "/products", "/solutions", "/platform", "/services", "/about", "/company", "/who-we-are", "/our-story"]
                for suf in suffixes:
                    try:
                        target = urljoin(url if url.endswith('/') else url+'/', suf.lstrip('/'))
                        await page.goto(target, timeout=5000, wait_until="domcontentloaded")  # 5s для доп страниц
                        await asyncio.sleep(config.SCRAPING_SETTINGS.get('content_wait_delay', 1))
                        html2 = await page.content()
                        parsed2 = enhanced_parse_html(html2, target)
                        if parsed2:
                            combined = (combined + "\n" + parsed2).strip()
                        if len(combined) >= config.MIN_CONTENT_LENGTH:
                            break
                    except Exception:
                        continue
                await page.close()
                return combined if combined else None
        except Exception:
            pass

        await page.close()
        return None
        
    except Exception as e:
        logging.error(f"Критическая ошибка при обработке {url}: {e}")
        if page and not page.is_closed():
            await page.close()
        return None


# Обновленная основная функция
async def fetch_content(context, url):
    """Основная функция для извлечения контента"""
    return await smart_fetch_content(context, url)
