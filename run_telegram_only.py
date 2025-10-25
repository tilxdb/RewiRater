#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск только Telegram бота (без Twitter)
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

from config import Config
from bot.telegram_bot import TelegramUserBot
from ai.content_rewriter import ContentRewriter
from utils.logger import setup_logger

logger = setup_logger()

async def main():
    """Главная функция"""
    try:
        logger.info("🚀 Запуск только Telegram бота (Twitter отключен)")
        
        config = Config()
        # Временно отключаем Twitter
        config.TWITTER_MONITORING_ENABLED = False
        
        content_rewriter = ContentRewriter(config)
        await content_rewriter.setup_ai_clients()
        
        bot = TelegramUserBot(config, content_rewriter)
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("👋 Telegram бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
