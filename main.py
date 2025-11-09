#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ✅ Модель OpenAI обновлена на gpt-4o-mini (по умолчанию)
"""
AI Копирайтер для Telegram канала через User Bot
RewiRater - автоматическая генерация и публикация контента
"""

import asyncio
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
sys.path.append(str(Path(__file__).parent))

from config import Config
from bot.telegram_bot import TelegramUserBot
from ai.content_rewriter import ContentRewriter
from utils.logger import setup_logger

async def main():
    """Главная функция программы"""
    logger = setup_logger()
    logger.info("Запуск AI копирайтера RewiRater")
    
    try:
        # Загружаем конфигурацию
        config = Config()
        config.load_from_env()
        
        if not config.API_ID or not config.API_HASH:
            logger.error("Не указаны API_ID и API_HASH для Telegram")
            return
        
        if not config.AI_API_KEY:
            logger.error("Не указан AI_API_KEY")
            return
        
        # Инициализируем переписыватель контента (setup_ai_clients вызывается автоматически в __init__)
        logger.info("Инициализация AI переписывателя...")
        content_rewriter = ContentRewriter(config)
        
        # Проверяем, что клиент создан
        if not hasattr(content_rewriter, 'openai_client') or content_rewriter.openai_client is None:
            logger.error("❌ OpenAI клиент не создан! Проверьте API ключ в config.py")
            return
        
        logger.info("✅ OpenAI клиент успешно инициализирован")
        
        # Инициализируем Telegram User Bot
        logger.info("Инициализация Telegram бота...")
        telegram_bot = TelegramUserBot(config, content_rewriter)
        
        # Запускаем бота
        logger.info("Запуск основного бота...")
        await telegram_bot.start()
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Завершение работы")

if __name__ == "__main__":
    asyncio.run(main())
