#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ✅ Модель OpenAI обновлена на gpt-4o-mini (по умолчанию)
"""
Запуск Telegram монитора
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

async def run_telegram_bot():
    """Запуск Telegram бота"""
    try:
        logger.info("🚀 Запуск Telegram бота...")
        
        config = Config()
        config.load_from_env()
        
        # Проверяем наличие API ключа
        if not config.AI_API_KEY:
            logger.error("❌ Не указан AI_API_KEY в config.py или переменных окружения")
            return
        
        # Инициализируем переписыватель (setup_ai_clients вызывается автоматически в __init__)
        content_rewriter = ContentRewriter(config)
        
        # Проверяем, что клиент создан
        if not hasattr(content_rewriter, 'openai_client') or content_rewriter.openai_client is None:
            logger.error("❌ OpenAI клиент не создан! Проверьте API ключ.")
            return
        
        logger.info("✅ OpenAI клиент успешно инициализирован")
        
        bot = TelegramUserBot(config, content_rewriter)
        await bot.start()
        
    except Exception as e:
        logger.error(f"❌ Ошибка Telegram бота: {e}")

async def main():
    """Главная функция - запуск Telegram монитора"""
    logger.info("🎯 Запуск Telegram монитора")
    
    # Создаем задачу для Telegram монитора
    telegram_task = asyncio.create_task(run_telegram_bot())
    
    # Ждем завершения задачи
    try:
        await telegram_task
    except KeyboardInterrupt:
        logger.info("👋 Получен сигнал остановки")
        # Отменяем задачу
        telegram_task.cancel()
        
        # Ждем завершения отмены
        try:
            await asyncio.gather(telegram_task, return_exceptions=True)
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Монитор остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")