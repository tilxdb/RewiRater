#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Настройка логирования для проекта
"""

import sys
from loguru import logger
from pathlib import Path

def setup_logger():
    """Настройка логгера с выводом в файл и консоль"""
    
    # Удаляем стандартный обработчик loguru
    logger.remove()
    
    # Добавляем вывод в консоль
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # Добавляем вывод в файл
    log_file = Path("logs/rewirater.log")
    log_file.parent.mkdir(exist_ok=True)
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    return logger
