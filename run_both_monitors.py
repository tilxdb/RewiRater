#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск Telegram и Twitter мониторов одновременно
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
        content_rewriter = ContentRewriter(config)
        await content_rewriter.setup_ai_clients()
        
        bot = TelegramUserBot(config, content_rewriter)
        await bot.start()
        
    except Exception as e:
        logger.error(f"❌ Ошибка Telegram бота: {e}")

async def run_twitter_monitor():
    """Запуск Twitter монитора"""
    try:
        logger.info("🚀 Запуск Twitter монитора...")
        
        from twitter.twitter_monitor_standalone import TwitterMonitorStandalone
        monitor = TwitterMonitorStandalone()
        await monitor.start()
        
    except Exception as e:
        logger.error(f"❌ Ошибка Twitter монитора: {e}")

async def main():
    """Главная функция - запуск обоих мониторов"""
    logger.info("🎯 Запуск Telegram и Twitter мониторов одновременно")
    
    # Создаем задачи для обоих мониторов
    telegram_task = asyncio.create_task(run_telegram_bot())
    twitter_task = asyncio.create_task(run_twitter_monitor())
    
    # Ждем завершения обеих задач
    try:
        await asyncio.gather(telegram_task, twitter_task)
    except KeyboardInterrupt:
        logger.info("👋 Получен сигнал остановки")
        # Отменяем задачи
        telegram_task.cancel()
        twitter_task.cancel()
        
        # Ждем завершения отмены
        try:
            await asyncio.gather(telegram_task, twitter_task, return_exceptions=True)
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Мониторы остановлены пользователем")
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")
