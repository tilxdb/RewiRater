#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Запуск только Twitter монитора (без Telegram)
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

from twitter_monitor_standalone import TwitterMonitorStandalone
from utils.logger import setup_logger

logger = setup_logger()

async def main():
    """Главная функция"""
    try:
        logger.info("🚀 Запуск только Twitter монитора (Telegram отключен)")
        
        monitor = TwitterMonitorStandalone()
        await monitor.start()
        
    except KeyboardInterrupt:
        logger.info("👋 Twitter монитор остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
