#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ✅ Модель OpenAI обновлена на gpt-4o-mini (по умолчанию)
"""
Переписывание контента из каналов-источников под стиль целевого канала
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import openai
except ImportError:
    openai = None

 

from loguru import logger

@dataclass
class SourcePost:
    """Исходный пост из канала-источника"""
    id: int
    text: str
    channel_id: int
    channel_title: str
    date: str
    views: int
    forwards: int
    url: Optional[str] = None
    media_type: Optional[str] = None  # 'photo', 'video', 'document', 'animation'
    media_object: Optional[Any] = None  # Объект медиа из Telegram
    media_url: Optional[str] = None  # URL медиа файла
    source_type: str = "telegram"  # telegram
    original_url: Optional[str] = None  # Оригинальная ссылка на пост

@dataclass
class RewrittenPost:
    """Переписанный пост"""
    original_post: SourcePost
    rewritten_text: str
    hashtags: List[str]
    style: str
    provider: str
    model: str
    processing_time: float
    media_type: Optional[str] = None  # Копируем медиа из исходного поста
    media_object: Optional[Any] = None
    media_url: Optional[str] = None

class ContentRewriter:
    """Переписывание контента под стиль целевого канала"""
    
    def __init__(self, config):
        self.config = config
        self.default_model = "gpt-4o-mini"
        logger.info(f"✅ Используется модель по умолчанию: {self.default_model}")
        self.model_name = getattr(self.config, "AI_MODEL", self.default_model)
        self.setup_ai_clients()
        
        # Стиль переписывания (будет настраиваться позже)
        self.rewriting_style = {
            "tone": "engaging",  # formal, casual, engaging, humorous
            "length": "adaptive",  # short, medium, long, adaptive
            "language": "ru",  # ru, en, mixed
            "add_emojis": False,
            "add_hashtags": False,
            "add_questions": False,
            "personal_touch": True
        }
        
        
    
    def setup_ai_clients(self):
        """Настройка AI клиентов (только OpenAI)."""
        if openai is None:
            logger.error("❌ Библиотека openai не установлена. Установите: pip install openai")
            return
        
        if not self.config.AI_API_KEY:
            logger.error("❌ AI_API_KEY не указан в config.py")
            return
        
        try:
            openai.api_key = self.config.AI_API_KEY
            self.model_name = getattr(self.config, "AI_MODEL", self.default_model)
            self.openai_client = openai.AsyncOpenAI(api_key=self.config.AI_API_KEY)
            logger.info(f"✅ OpenAI клиент для переписывания настроен (модель: {self.model_name})")
            logger.debug(f"API ключ: {self.config.AI_API_KEY[:10]}...{self.config.AI_API_KEY[-10:]}")
        except Exception as e:
            logger.error(f"❌ Ошибка создания OpenAI клиента: {e}")
            self.openai_client = None
    
    async def rewrite_post(self, source_post: SourcePost) -> RewrittenPost:
        """Переписывает пост под стиль целевого канала"""
        import time
        start_time = time.time()
        
        try:
            rewritten_text = await self._rewrite_with_openai(source_post)
            
            # Очищаем и форматируем текст
            cleaned_text = self._clean_and_format_text(rewritten_text)
            
            # Убираем хештеги и подпись, если нейросеть их добавила
            cleaned_text = self._remove_hashtags_from_text(cleaned_text)
            
            # Форматируем финальный пост
            final_text = self._format_simple_post(cleaned_text, [])
            
            processing_time = time.time() - start_time
            
            logger.info(f"Пост переписан за {processing_time:.2f}с")
            
            return RewrittenPost(
                original_post=source_post,
                rewritten_text=final_text,
                hashtags=[],
                style=self.rewriting_style["tone"],
                provider=self.config.AI_PROVIDER,
                model=getattr(self.config, "AI_MODEL", self.default_model),
                media_type=source_post.media_type,
                media_object=source_post.media_object,
                media_url=source_post.media_url,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Ошибка переписывания поста: {e}")
            logger.error(f"Тип ошибки: {type(e).__name__}")
            logger.error(f"Детали: {str(e)}")
            logger.warning("Используется fallback режим (шаблонный пост). Проверьте логи выше для диагностики.")
            return self._create_fallback_post(source_post)
    
    async def _rewrite_with_openai(self, source_post: SourcePost) -> str:
        """Переписывание через OpenAI"""
        # Проверяем наличие клиента
        if not hasattr(self, 'openai_client') or self.openai_client is None:
            raise Exception("OpenAI клиент не инициализирован. Проверьте API ключ и настройки.")
        
        prompt = self._build_rewriting_prompt(source_post)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=getattr(self.config, "AI_MODEL", self.default_model),
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise Exception("OpenAI вернул пустой ответ")
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Ошибка вызова OpenAI API: {e}")
            raise  # Пробрасываем дальше, чтобы было видно в логах
    
    
    
    def _build_rewriting_prompt(self, source_post: SourcePost) -> str:
        """Создание промпта для переписывания"""
        prompt = f"""
ТЫ ДОЛЖЕН ПОЛНОСТЬЮ ПЕРЕПИСАТЬ этот пост в стиле автора @marxstud. НЕ КОПИРУЙ исходный текст!

ИСХОДНЫЙ ПОСТ:
{source_post.text}

ЗАДАЧА: Полностью переписать этот пост в стиле @marxstud, сохранив КОНКРЕТНЫЕ детали из оригинала!

КОНТЕКСТ КАНАЛА:
- Тематика канала: веб-дизайн, фронтенд/бэкенд разработка, продуктовые интерфейсы, работа с заказчиками, студийные процессы.
- Аудитория: дизайнеры, разработчики, тимлиды, основатели студий, люди из индустрии.
- Формат: осмысленные, практичные посты без воды, с уважением к времени читателя.

КРИТИЧЕСКИ ВАЖНО:
- Сохраняй ВСЕ конкретные факты из оригинала: названия инструментов (Figma, Framer, React, Next.js и т.п.), технологий, сервисов, проектов, клиентов.
- Сохраняй важные цифры: сроки, бюджеты, конверсии, процент роста/просадки, количество экранов, количество правок и т.д.
- Сохраняй ключевые детали кейсов: что было «до», что сделали, что стало «после».
- НЕ заменяй конкретику общими фразами типа "мы всё улучшили", "сделали красиво", "оптимизировали процесс".
- Анализируй ЧТО КОНКРЕТНО написано в оригинале (ситуация, проблема, решение, результат) и переписывай ЭТО, а не абстрактную тему.

СТИЛЬ АВТОРА @marxstud — строго соблюдай:

🎯 СТРУКТУРА ПОСТА:
- Количество абзацев адаптивное и зависит от длины исходного поста.
- В каждом абзаце 2–3 содержательных предложения.
- Каждый абзац отвечает на понятный вопрос: "что произошло?", "почему это важно?", "что мы сделали?", "что из этого вынести комьюнити?".
- Уникальный жирный заголовок: 1–3 слова по смыслу конкретного поста (НЕ шаблонный!).
- Подпись @marxstud добавляется автоматически.

📌 ЗАГОЛОВОК (ОБЯЗАТЕЛЬНО):
- Анализируй содержание поста и создавай УНИКАЛЬНЫЙ заголовок из 1–3 слов.
- Заголовок должен отражать ГЛАВНУЮ СУТЬ конкретного поста: кейс, инсайт, фейл, вывод, важный приём в дизайне/коде.
- НЕ используй шаблоны типа "Немного мыслей", "Полезные советы", "Важно понимать".
- Вместо этого создавай конкретные заголовки по смыслу: "Редизайн личного кабинета", "Боль верстальщика", "Честный кейс по дедлайнам".

🗣 ЯЗЫК И ТОН:
- Спокойный, уверенный, профессиональный тон без пафоса.
- Обращение к читателю как к коллеге из индустрии, а не к новичку.
- Разговорный, но аккуратный язык: можно использовать живые формулировки, но без токсичности и хайпа.
- Допускаются ирония и самоирония, если они усиливают мысль, а не размывают её.
- Важен фокус на пользе для читателя: инсайты, выводы, что можно применить в своей работе.

📝 СОДЕРЖАНИЕ:
- Сохраняй ВСЕ конкретные факты из оригинала: названия проектов, технологий, подходов, конкретные ситуации с заказчиками/командой.
- НЕ заменяй конкретику общими фразами (если в оригинале есть конкретный инструмент или контекст, не подменяй это абстракцией).
- Оставляй только ключевые факты: что произошло, что было сделано, какой вывод.
- Убирай лишнюю "воду", повторения и мусорные фразы.
- Делай выводы явно: что это показывает, чему учит, что перестали делать после этого опыта.

🎨 ОСОБЕННОСТИ ФОРМАТИРОВАНИЯ:
- Количество абзацев выбирай по объёму исходного текста (адаптивно).
- В каждом абзаце 2–3 предложения, без перегруза.
- Уникальный жирный заголовок: 1–3 слова по смыслу поста (НЕ шаблонный!).
- При необходимости используй списки для шагов, выводов, проблем и решений.
- Только суть, без воды.

ПРИМЕРЫ ФРАЗ В СТИЛЕ:
- "Ключевой инсайт..."
- "Что это значит для команды..."
- "Где здесь реальная проблема..."
- "Что мы изменили в процессе..."
- "Что можно забрать в свою работу..."

ВАЖНО:
- НЕ КОПИРУЙ исходный текст, но СОХРАНЯЙ все конкретные факты!
- Если в оригинале описывается конкретный кейс (клиент, продукт, фичи, метрики) — перепиши его, не превращая в абстрактный "опыт в IT".
- Если есть конкретные цифры, даты, названия — ОБЯЗАТЕЛЬНО сохрани их.
- ПОЛНОСТЬЮ ПЕРЕПИШИ в стиле @marxstud, но с сохранением конкретики.
- Количество абзацев — адаптивно по длине исходного поста.
- Каждый абзац содержит 2–3 предложения.
- ЗАГОЛОВОК: создавай УНИКАЛЬНЫЙ по смыслу конкретного поста (1–3 слова), НЕ используй шаблоны типа "Мысли о дизайне".
- ЗАГОЛОВОК должен отражать конкретную тему поста (например "Редизайн дашборда", "Фейл с дедлайном").
- ТОЛЬКО ключевая информация с сохранением конкретных фактов.
- БЕЗ лишних комментариев "ради стиля".
- НЕ ДОБАВЛЯЙ подпись @marxstud в конце поста — она будет добавлена автоматически.
- НЕ используй кликабельные призывы-хуки ради клика, если они не вытекают из сути поста.

ПЕРЕПИШИ ПОСТ ПОЛНОСТЬЮ в стиле автора @marxstud БЕЗ подписи в конце.
        """

        return prompt.strip()
    
    
    def _clean_and_format_text(self, text: str) -> str:
        """Очистка и форматирование текста"""
        import re
        
        # Сначала удаляем все эмодзи
        text = self._remove_emojis_from_text(text)
        
        # Убираем ** из текста и заменяем на жирный формат
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        
        # Убираем лишние пробелы и переносы
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = text.strip()
        
        # Обрабатываем ссылки - извлекаем их и вставляем в похожие слова
        # Это упрощенная версия, в реальности нужно более сложная логика
        text = self._process_links(text)
        
        return text
    
    def _remove_emojis_from_text(self, text: str) -> str:
        """Удаляет все эмодзи из текста"""
        import re
        
        # Паттерн для удаления эмодзи (Unicode диапазоны)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # эмоции
            "\U0001F300-\U0001F5FF"  # символы и пиктограммы
            "\U0001F680-\U0001F6FF"  # транспорт
            "\U0001F1E0-\U0001F1FF"  # флаги
            "\U00002702-\U000027B0"  # символы
            "\U000024C2-\U0001F251"  # дополнительные символы
            "\U0001F900-\U0001F9FF"  # дополнительные символы и пиктограммы
            "\U0001FA70-\U0001FAFF"  # символы и пиктограммы расширенные
            "\U00002600-\U000026FF"  # различные символы
            "\U00002700-\U000027BF"  # Dingbats
            "]+", 
            flags=re.UNICODE
        )
        
        return emoji_pattern.sub('', text)
    
    def _remove_hashtags_from_text(self, text: str) -> str:
        """Удаляет хештеги, эмодзи из текста, если нейросеть их добавила"""
        import re
        
        # Сначала удаляем эмодзи
        text = self._remove_emojis_from_text(text)
        
        # Удаляем строки, которые содержат только хештеги
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Если строка содержит только хештеги (начинается с #) или подпись @marxstud, пропускаем её
            if line and (all(word.startswith('#') for word in line.split()) or line.startswith('@marxstud')):
                continue
            cleaned_lines.append(line)
        
        # Объединяем обратно
        result = '\n'.join(cleaned_lines)
        
        # Убираем лишние переносы строк
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
        
        return result.strip()
    
    def _format_simple_post(self, text: str, hashtags: List[str]) -> str:
        """Простое форматирование поста без эмодзи"""
        # Добавляем подпись @marxstud в конец
        return f"{text}\n\n@marxstud"
    
    
    
    def _process_links(self, text: str) -> str:
        """Обработка ссылок в тексте"""
        import re
        
        # Находим ссылки в скобках
        link_pattern = r'\(([^)]*https?://[^)]*)\)'
        links = re.findall(link_pattern, text)
        
        # Убираем ссылки в скобках из текста
        text = re.sub(link_pattern, '', text)
        
        # Пока просто убираем ссылки, позже можно добавить более сложную логику
        # для вставки их в похожие по смыслу слова
        
        return text

    def extract_links(self, text: str) -> List[str]:
        """Извлекает все ссылки из текста, включая встроенные в слова (markdown) и обычные URL."""
        import re
        urls: List[str] = []
        
        # Markdown-ссылки вида [текст](https://example.com/path)
        markdown_links = re.findall(r'\[[^\]]+\]\((https?://[^)\s]+)\)', text)
        urls.extend(markdown_links)
        
        # Обычные http/https URL
        bare_urls = re.findall(r'(https?://[^\s)]+)', text)
        urls.extend(bare_urls)
        
        # Ссылки, попавшие внутрь скобок, извлекаем изнутри, если они не найдены ранее
        in_parens = re.findall(r'\(([^)]*https?://[^)]*)\)', text)
        for chunk in in_parens:
            for m in re.findall(r'(https?://[^\s)]+)', chunk):
                urls.append(m)
        
        # Удаляем дубли, сохраняя порядок
        seen = set()
        unique_urls: List[str] = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                unique_urls.append(u)
        return unique_urls
    
    def _get_system_prompt(self) -> str:
        """Системный промпт для AI"""
        return """Ты эксперт по переписыванию контента в стиле автора @marxstud.

ТВОЯ РОЛЬ:
- Писать как опытный практик из мира веб-дизайна и разработки.
- Объяснять сложные вещи простым, но профессиональным языком.
- Помогать комьюнити видеть логику решений, а не просто "красивые слова".

КРИТИЧЕСКИ ВАЖНО:
- Сохраняй ВСЕ конкретные факты из оригинала: названия инструментов, технологий, фреймворков, сервисов, продуктов.
- Сохраняй важные цифры: сроки, бюджеты, конверсии, CTR, количество экранов, количество правок, рост/падение метрик.
- Сохраняй структуру кейса: контекст → проблема → решение → результат → вывод.
- НЕ заменяй конкретику общими фразами типа "мы всё улучшили", "результат превзошёл ожидания".
- Анализируй ЧТО КОНКРЕТНО написано в оригинале и переписывай ЭТО, а не абстрактную тему.

ТЕМАТИКА:
- Веб-дизайн (UX/UI, продуктовые интерфейсы, дизайн-системы).
- Веб-разработка (фронтенд, бэкенд, архитектурные решения).
- Командные и студийные процессы (брифы, дедлайны, ревью, работа с заказчиком).
- Кейсы, разборы, факапы и честные выводы.
- Практические советы, которые можно применить в реальных проектах.

СТИЛЬ АВТОРА:
- Строгий, спокойный, уверенный тон без лишнего пафоса.
- Разговор с аудиторией как с коллегами, а не с "новичками".
- Точность формулировок, уважение к фактам и времени читателя.
- Доля иронии допустима, если усиливает мысль, а не превращает текст в шутку.

СТРУКТУРА:
- Количество абзацев адаптивное и зависит от длины исходного поста.
- В каждом абзаце 2–3 предложения, которые последовательно развивают мысль.
- Уникальный жирный заголовок: 1–3 слова по смыслу конкретного поста (НЕ шаблонный!).
- Только ключевая информация, без лишней воды и саморекламы.
- Подпись @marxstud добавляется автоматически.

ЗАГОЛОВОК:
- Анализируй содержание каждого поста и создавай УНИКАЛЬНЫЙ заголовок из 1–3 слов.
- Заголовок должен отражать главную суть: "Редизайн личного кабинета", "Боль фронтенда", "Как мы убили дедлайн".
- НЕ используй шаблоны типа "Полезные советы", "Немного мыслей".
- Каждый пост = свой заголовок, основанный на его содержании.

ОБЯЗАТЕЛЬНО:
- Количество абзацев — адаптивно по длине исходного поста.
- В каждом абзаце 2–3 предложения.
- ЗАГОЛОВОК: создавай УНИКАЛЬНЫЙ по смыслу конкретного поста (1–3 слова), НЕ используй шаблоны.
- Сохраняй ВСЕ конкретные факты: инструменты, метрики, реальные детали из оригинала.
- НЕ заменяй конкретику общими фразами.
- Только ключевая информация с сохранением конкретных фактов.
- БЕЗ лишних комментариев, не поддерживающих мысль.
- Сохраняй основную суть исходного контента с КОНКРЕТНЫМИ деталями.
- НЕ ЗАДАВАЙ вопросы аудитории в конце поста.
- НЕ ИСПОЛЬЗУЙ "p.s." или случайные приписки.
- Пиши ЧЁТКО и ИНФОРМАТИВНО, чтобы текст был полезен людям из индустрии.

Всегда сохраняй конкретные факты и детали исходного контента, переписывая их в узнаваемом, профессиональном стиле автора @marxstud."""
    
    
    
    
    
    
    
    def _rewrite_fallback(self, source_post: SourcePost) -> str:
        """Резервное переписывание без AI в стиле автора"""
        import re
        text = source_post.text
        
        # Удаляем эмодзи из исходного текста
        text = self._remove_emojis_from_text(text)
        
        # Извлекаем ключевые слова и конкретику из оригинала
        # Ищем названия проектов (слова с заглавной буквы)
        projects = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        # Ищем цифры
        numbers = re.findall(r'\d+[.,]\d+|\d+', text)
        # Ищем даты
        dates = re.findall(r'\d+\s*(?:ноября|декабря|января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября)|(?:ноября|декабря|января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября)\s*\d+', text, re.IGNORECASE)
        
        # Создаем заголовок на основе конкретных слов из текста
        text_words = text.split()
        # Берем первые значимые слова (пропускаем служебные)
        significant_words = [w for w in text_words[:10] if len(w) > 3 and not w.lower() in ['это', 'что', 'для', 'как', 'или', 'был', 'был', 'есть']]
        
        if projects:
            # Используем название проекта для заголовка
            header = f"<b>{projects[0]}</b>"
        elif significant_words:
            # Используем ключевые слова из текста
            header_keyword = significant_words[0].capitalize()
            header = f"<b>{header_keyword}</b>"
        else:
            header = "<b>Важная информация</b>"
        
        # Сохраняем оригинальный текст с минимальной обработкой (только форматирование)
        # Это лучше, чем генерировать шаблоны
        cleaned_text = re.sub(r'\n+', '\n\n', text.strip())
        
        # Если текст слишком длинный, обрезаем
        if len(cleaned_text) > 500:
            cleaned_text = cleaned_text[:500] + "..."
        
        return f"{header}\n\n{cleaned_text}"
    
    def _rewrite_content_in_style(self, original_text: str, topic: str) -> str:
        """Переписывает контент в профессиональном стиле"""
        # Удаляем эмодзи
        text = self._remove_emojis_from_text(original_text)
        
        # Убираем ** и форматирование
        text = text.replace("**", "")
        
        # Убираем ссылки в скобках
        import re
        text = re.sub(r'\([^)]*https?://[^)]*\)', '', text)
        
        # Переписываем в стиле автора (2-3 предложения)
        if "bitcoin" in text.lower() or "крипт" in text.lower():
            return f"Криптовалютный рынок показывает волатильность. Цены колеблются, требуя внимательного анализа. Стоит следить за трендами."
        elif "ton" in text.lower() or "телеграм" in text.lower():
            return f"TON экосистема развивается динамично. Новые проекты привлекают внимание инвесторов. Важно отслеживать обновления."
        elif "игра" in text.lower() or "gamefi" in text.lower():
            return f"Игровая индустрия в Web3 набирает обороты. Новые проекты предлагают инновации. Стоит изучить перспективы."
        else:
            return f"Технологический сектор развивается. Появляются новые решения. Важно понимать изменения."
    
    def _create_fallback_post(self, source_post: SourcePost) -> RewrittenPost:
        """Создание резервного поста при ошибке"""
        rewritten_text = self._rewrite_fallback(source_post)
        
        # Форматируем пост
        final_text = self._format_simple_post(rewritten_text, [])
        
        return RewrittenPost(
            original_post=source_post,
            rewritten_text=final_text,
            hashtags=[],
            style="fallback",
            provider="fallback",
            model=getattr(self.config, "AI_MODEL", self.default_model),
            media_type=source_post.media_type,
            media_object=source_post.media_object,
            media_url=source_post.media_url,
            processing_time=0.0
        )
    
    def update_style(self, style_config: Dict):
        """Обновление стиля переписывания"""
        self.rewriting_style.update(style_config)
        logger.info("Стиль переписывания обновлен")
    
    def get_style_config(self) -> Dict:
        """Получение текущего стиля"""
        return self.rewriting_style.copy()
    
    def add_custom_emojis(self, emojis: List[str]):
        """Добавление кастомных эмодзи в набор автора"""
        self.author_emojis.extend(emojis)
        self.author_emojis = list(set(self.author_emojis))  # Убираем дубли
        logger.info(f"Добавлено {len(emojis)} кастомных эмодзи")
    
    def set_emoji_mapping(self, mapping: Dict[str, List[str]]):
        """Установка кастомного маппинга контекстных эмодзи"""
        self.context_emojis.update(mapping)
        logger.info("Обновлено маппинг контекстных эмодзи")
    
    def get_available_emojis(self) -> List[str]:
        """Получение списка доступных эмодзи"""
        return self.author_emojis.copy()
    
    def set_premium_emojis(self, premium_emojis: Dict[str, str]):
        """Установка Premium эмодзи (file_id стикеров)"""
        self.premium_emojis.update(premium_emojis)
        logger.info(f"Обновлено {len(premium_emojis)} Premium эмодзи")
    
    def get_premium_emojis(self) -> Dict[str, str]:
        """Получение списка Premium эмодзи"""
        return self.premium_emojis.copy()
