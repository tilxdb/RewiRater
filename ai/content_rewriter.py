#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

try:
    import anthropic
except ImportError:
    anthropic = None

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
    source_type: str = "telegram"  # telegram, twitter
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
        """Настройка AI клиентов"""
        if self.config.AI_PROVIDER == "openai" and openai:
            openai.api_key = self.config.AI_API_KEY
            self.openai_client = openai.AsyncOpenAI(api_key=self.config.AI_API_KEY)
            logger.info("OpenAI клиент для переписывания настроен")
        
        elif self.config.AI_PROVIDER == "anthropic" and anthropic:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=self.config.AI_API_KEY)
            logger.info("Anthropic клиент для переписывания настроен")
        
        elif self.config.AI_PROVIDER == "deepseek" and openai:
            # DeepSeek использует OpenAI-совместимый API
            self.deepseek_client = openai.AsyncOpenAI(
                api_key=self.config.AI_API_KEY,
                base_url="https://api.deepseek.com"
            )
            logger.info("DeepSeek клиент для переписывания настроен")
        
        elif self.config.AI_PROVIDER == "groq" and openai:
            # Groq - бесплатно 14,400 запросов/день
            self.groq_client = openai.AsyncOpenAI(
                api_key=self.config.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            logger.info("Groq клиент для переписывания настроен (бесплатно)")
        
        elif self.config.AI_PROVIDER == "huggingface" and openai:
            # Hugging Face Inference API - бесплатно 30,000 запросов/месяц
            # Используем ваш API ключ с правильным endpoint
            self.huggingface_client = openai.AsyncOpenAI(
                api_key=self.config.HUGGINGFACE_API_KEY,
                base_url="https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            )
            logger.info("Hugging Face клиент для переписывания настроен (бесплатно)")
        
        elif self.config.AI_PROVIDER == "ollama" and openai:
            # Ollama - локальный сервер
            self.ollama_client = openai.AsyncOpenAI(
                api_key="ollama",  # Не используется, но требуется
                base_url=self.config.OLLAMA_BASE_URL
            )
            logger.info("Ollama клиент для переписывания настроен (локально)")
        
        else:
            logger.warning(f"AI провайдер {self.config.AI_PROVIDER} не поддерживается")
    
    async def rewrite_post(self, source_post: SourcePost) -> RewrittenPost:
        """Переписывает пост под стиль целевого канала"""
        import time
        start_time = time.time()
        
        try:
            if self.config.AI_PROVIDER == "openai":
                rewritten_text = await self._rewrite_with_openai(source_post)
            elif self.config.AI_PROVIDER == "anthropic":
                rewritten_text = await self._rewrite_with_anthropic(source_post)
            elif self.config.AI_PROVIDER == "deepseek":
                rewritten_text = await self._rewrite_with_deepseek(source_post)
            elif self.config.AI_PROVIDER == "groq":
                rewritten_text = await self._rewrite_with_groq(source_post)
            elif self.config.AI_PROVIDER == "huggingface":
                rewritten_text = await self._rewrite_with_huggingface(source_post)
            elif self.config.AI_PROVIDER == "ollama":
                rewritten_text = await self._rewrite_with_ollama(source_post)
            else:
                rewritten_text = self._rewrite_fallback(source_post)
            
            # Очищаем и форматируем текст
            cleaned_text = self._clean_and_format_text(rewritten_text)
            
            # Убираем хештеги и подпись, если нейросеть их добавила
            cleaned_text = self._remove_hashtags_from_text(cleaned_text)
            
            # Форматируем финальный пост в зависимости от источника
            if source_post.source_type == "twitter":
                final_text = self._format_twitter_post(cleaned_text, [], source_post.original_url)
            else:
                final_text = self._format_simple_post(cleaned_text, [])
            
            processing_time = time.time() - start_time
            
            logger.info(f"Пост переписан за {processing_time:.2f}с")
            
            return RewrittenPost(
                original_post=source_post,
                rewritten_text=final_text,
                hashtags=[],
                style=self.rewriting_style["tone"],
                provider=self.config.AI_PROVIDER,
                model=self.config.AI_MODEL,
                media_type=source_post.media_type,
                media_object=source_post.media_object,
                media_url=source_post.media_url,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Ошибка переписывания поста: {e}")
            return self._create_fallback_post(source_post)
    
    async def _rewrite_with_openai(self, source_post: SourcePost) -> str:
        """Переписывание через OpenAI"""
        prompt = self._build_rewriting_prompt(source_post)
        
        response = await self.openai_client.chat.completions.create(
            model=self.config.AI_MODEL,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    async def _rewrite_with_anthropic(self, source_post: SourcePost) -> str:
        """Переписывание через Anthropic"""
        prompt = self._build_rewriting_prompt(source_post)
        
        response = await self.anthropic_client.messages.create(
            model=self.config.AI_MODEL,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    async def _rewrite_with_deepseek(self, source_post: SourcePost) -> str:
        """Переписывание через DeepSeek"""
        prompt = self._build_rewriting_prompt(source_post)
        
        response = await self.deepseek_client.chat.completions.create(
            model=self.config.AI_MODEL,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    async def _rewrite_with_groq(self, source_post: SourcePost) -> str:
        """Переписывание через Groq (бесплатно)"""
        prompt = self._build_rewriting_prompt(source_post)
        
        response = await self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Быстрая модель Groq
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    async def _rewrite_with_huggingface(self, source_post: SourcePost) -> str:
        """Переписывание через Hugging Face (бесплатно)"""
        import aiohttp
        import json
        
        # Используем Hugging Face Inference API напрямую
        url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        headers = {
            "Authorization": f"Bearer {self.config.HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Создаем простой промпт для переписывания
        prompt = f"Перепиши этот пост в стиле крипто-блогера: {source_post.text}"
        
        data = {
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            return result[0].get("generated_text", source_post.text)
                        else:
                            return source_post.text
                    else:
                        logger.warning(f"Hugging Face API error: {response.status}")
                        return self._rewrite_fallback(source_post)
        except Exception as e:
            logger.error(f"Hugging Face request error: {e}")
            return self._rewrite_fallback(source_post)
    
    async def _rewrite_with_ollama(self, source_post: SourcePost) -> str:
        """Переписывание через Ollama (локально)"""
        prompt = self._build_rewriting_prompt(source_post)
        
        response = await self.ollama_client.chat.completions.create(
            model="llama3.1:8b",  # Локальная модель Ollama
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _build_rewriting_prompt(self, source_post: SourcePost) -> str:
        """Создание промпта для переписывания"""
        prompt = f"""
ТЫ ДОЛЖЕН ПОЛНОСТЬЮ ПЕРЕПИСАТЬ этот пост в стиле автора @thedegeton. НЕ КОПИРУЙ исходный текст!

ИСХОДНЫЙ ПОСТ:
{source_post.text}

ЗАДАЧА: Полностью переписать этот пост в стиле @thedegeton, сохранив только основную суть и информацию.

СТИЛЬ АВТОРА @thedegeton - строго соблюдай:

🎯 СТРУКТУРА ПОСТА:
- Максимум 3 абзаца по 3 предложения
- Если исходный пост короткий - 1-2 абзаца
- Только ключевая информация
- Краткий жирный заголовок
- Заканчивай подписью @ton_boom

🗣 ЯЗЫК И ТОН:
- Строгий профессиональный тон
- Минимальный сленг: "ладно", "ну а что"
- Деловой стиль общения
- Сдержанная эмоциональность: "интересно", "стоит отметить", "важно понимать"
- Аналитические комментарии: "думаю что", "судя по данным", "необходимо отметить"

📝 СОДЕРЖАНИЕ:
- Только ключевые факты
- Без лишних комментариев
- Четкая и понятная информация

🎨 ОСОБЕННОСТИ ФОРМАТИРОВАНИЯ:
- Максимум 3 абзаца по 3 предложения
- Если исходный пост короткий - 1-2 абзаца
- Жирный заголовок в начале
- Только суть, без воды

ПРИМЕРЫ ФРАЗ В СТИЛЕ:
- "Ключевые изменения..."
- "Важные обновления..."
- "Основные факты..."
- "Новые данные..."
- "Актуальная информация..."

ВАЖНО: 
- НЕ КОПИРУЙ исходный текст
- ПОЛНОСТЬЮ ПЕРЕПИШИ в стиле @thedegeton
- МАКСИМУМ 3 абзаца по 3 предложения
- Если исходный пост короткий - 1-2 абзаца
- ТОЛЬКО ключевая информация
- БЕЗ лишних комментариев
- НЕ ДОБАВЛЯЙ подпись @ton_boom в конце поста - она будет добавлена автоматически
- НЕ ЗАДАВАЙ вопросы аудитории в конце поста
- НЕ ИСПОЛЬЗУЙ "p.s." или дополнительные приписки
- ДЕЛАЙ посты ЧЕТКИМИ и ИНФОРМАТИВНЫМИ

ПЕРЕПИШИ ПОСТ ПОЛНОСТЬЮ в стиле автора @thedegeton БЕЗ подписи в конце.
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
        """Удаляет хештеги, эмодзи и подпись @ton_boom из текста, если нейросеть их добавила"""
        import re
        
        # Сначала удаляем эмодзи
        text = self._remove_emojis_from_text(text)
        
        # Удаляем строки, которые содержат только хештеги
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Если строка содержит только хештеги (начинается с #) или подпись @ton_boom, пропускаем её
            if line and (all(word.startswith('#') for word in line.split()) or line.startswith('@ton_boom')):
                continue
            cleaned_lines.append(line)
        
        # Объединяем обратно
        result = '\n'.join(cleaned_lines)
        
        # Убираем лишние переносы строк
        result = re.sub(r'\n\s*\n\s*\n', '\n\n', result)
        
        return result.strip()
    
    def _format_simple_post(self, text: str, hashtags: List[str]) -> str:
        """Простое форматирование поста без эмодзи"""
        # Добавляем подпись @ton_boom в конец
        return f"{text}\n\n@ton_boom"
    
    def _format_twitter_post(self, text: str, hashtags: List[str], original_url: Optional[str] = None) -> str:
        """Форматирование Twitter поста с указанием источника"""
        # Убираем эмодзи из текста
        clean_text = self._remove_emojis_from_text(text)
        
        # Добавляем подпись и источник
        signature = "@ton_boom"
        source_info = f"Источник: {original_url}" if original_url else "Источник: Twitter"
        
        return f"{clean_text}\n\n{source_info}\n{signature}"
    
    
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
    
    def _get_system_prompt(self) -> str:
        """Системный промпт для AI"""
        return """Ты эксперт по переписыванию контента в стиле автора @thedegeton. 

ТВОЯ РОЛЬ: Ты пишешь как опытный крипто-блогер с уникальным стилем подачи информации.

СТИЛЬ АВТОРА:
- Строгий профессиональный тон
- Минимальное использование сленга: "ладно", "ну а что"
- Аналитические комментарии и мнения
- Аналитическая подача новостей
- Разговорная речь с сокращениями

ТЕМАТИКА:
- Web3 и криптовалюты
- TON экосистема
- Блокчейн технологии
- Анализ рынка и трендов
- Практические советы для трейдеров

СТРУКТУРА:
- Максимум 3 абзаца по 3 предложения
- Если исходный пост короткий - 1-2 абзаца
- Жирный заголовок в начале
- Только ключевая информация
- Подпись @ton_boom в конце

ЯЗЫКОВЫЕ ОСОБЕННОСТИ:
- "ладно", "ну а что"
- "всё как всегда", "ничего нового"
- "думаю что", "судя по данным"

ОБЯЗАТЕЛЬНО:
- Максимум 3 абзаца по 3 предложения
- Если исходный пост короткий - 1-2 абзаца
- Жирный заголовок в начале поста
- Только ключевая информация
- БЕЗ лишних комментариев
- Сохраняй основную суть исходного контента
- НЕ ЗАДАВАЙ вопросы аудитории в конце поста
- НЕ ИСПОЛЬЗУЙ "p.s." или дополнительные приписки
- ЧЕТКО и ИНФОРМАТИВНО

Всегда сохраняй основную суть исходного контента, но переписывай в узнаваемом стиле автора."""
    
    
    
    
    
    
    
    def _rewrite_fallback(self, source_post: SourcePost) -> str:
        """Резервное переписывание без AI в стиле автора"""
        text = source_post.text
        
        # Удаляем эмодзи из исходного текста
        text = self._remove_emojis_from_text(text)
        
        # Анализируем исходный текст
        text_lower = text.lower()
        
        # Определяем тему
        if any(word in text_lower for word in ["bitcoin", "крипт", "токен", "монет"]):
            topic = "криптовалюты"
        elif any(word in text_lower for word in ["ton", "телеграм", "telegram"]):
            topic = "TON экосистемы"
        elif any(word in text_lower for word in ["игра", "gamefi", "nft"]):
            topic = "игровых проектов"
        elif any(word in text_lower for word in ["бирж", "трейд", "торг"]):
            topic = "трейдинга"
        else:
            topic = "интересных новостей"
        
        # Создаем строгий заголовок в стиле автора
        headers = [
            f"<b>Анализ {topic}</b>",
            f"<b>Обзор {topic}</b>",
            f"<b>Новости {topic}</b>",
            f"<b>Тенденции {topic}</b>",
            f"<b>Развитие {topic}</b>"
        ]
        
        import random
        header = random.choice(headers)
        
        # ПЕРЕПИСЫВАЕМ текст в стиле автора, а не копируем
        rewritten_content = self._rewrite_content_in_style(text, topic)
        
        # Добавляем краткие стилевые элементы
        style_elements = [
            "\n\nСледим за развитием.",
            "\n\nАнализируем тренды.",
            "\n\nИнтересная ситуация.",
            "\n\nВажно понимать."
        ]
        
        style_element = random.choice(style_elements)
        
        return f"{header}\n\n{rewritten_content}{style_element}"
    
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
        
        # Форматируем в зависимости от источника
        if source_post.source_type == "twitter":
            final_text = self._format_twitter_post(rewritten_text, [], source_post.original_url)
        else:
            final_text = self._format_simple_post(rewritten_text, [])
        
        return RewrittenPost(
            original_post=source_post,
            rewritten_text=final_text,
            hashtags=[],
            style="fallback",
            provider="fallback",
            model="template",
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
