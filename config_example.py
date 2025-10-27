"""
Пример конфигурации для RewiRater
Скопируйте этот файл в config.py и заполните своими данными
"""

from typing import List, Optional

class Config:
    """Конфигурация бота"""
    
    # Telegram API (получите на https://my.telegram.org)
    API_ID: int = 12345678  # Ваш API ID
    API_HASH: str = "your_api_hash_here"  # Ваш API Hash
    SESSION_NAME: str = "rewirater_bot_v3"
    
    # Каналы для мониторинга
    SOURCE_CHANNELS: List[str] = [
        "@dubaieth",
        "@tonlive",
        "@tonraffles_ru",
        "@MyTonWalletRu",
        "@tonkeeper_ru",
        "@durov",
        "@ston_fi_ru",
        "@dedust_ru",
        "@x1000News",
        "@tginfo",
        "@tonmonitoring"
    ]
    
    
    # ID канала для публикации переработанных постов
    TARGET_CHANNEL: str = "@your_target_channel"
    
    # Настройки AI
    AI_PROVIDER: str = "openai"  # openai, anthropic, deepseek, local, groq, huggingface, ollama, fallback
    AI_API_KEY: Optional[str] = "your_openai_api_key_here"  # Ваш OpenAI API ключ
    AI_MODEL: str = "gpt-4o-mini"  # gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
    
    
    # Настройки публикации
    PROCESSING_DELAY_MINUTES: int = 5  # Задержка перед обработкой нового поста
    PUBLISH_INTERVAL_MIN: int = 20  # Минимальный интервал между публикациями (минуты)
    PUBLISH_INTERVAL_MAX: int = 30  # Максимальный интервал между публикациями (минуты)
    MAX_POSTS_PER_DAY: int = 24
    MIN_POST_LENGTH: int = 50  # Минимальная длина поста для обработки
    
    
    # Настройки контента
    POST_LENGTH: str = "medium"  # short, medium, long
    CONTENT_TYPE: str = "mixed"  # news, tips, entertainment, mixed
    
    # Настройки стиля переписывания
    rewriting_style: dict = {
        "tone": "professional",
        "length": "concise",
        "add_emojis": False,
        "add_hashtags": False,
        "add_questions": False,
        "signature": "@ton_boom"
    }
