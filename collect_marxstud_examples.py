#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сбор примеров постов из канала @marxstud
и сохранение их в файл для использования основным ботом.
"""

import asyncio
import os
from pathlib import Path
from typing import List

from telethon import TelegramClient
from telethon.tl.types import Message

from config import Config


# Настройки сбора примеров
SOURCE_CHANNEL = "@marxstud"  # канал, из которого забираем посты
OUTPUT_FILE = Path("examples/marxstud_examples.txt")  # куда сохраняем примеры

# Telegram API данные (для безопасности НЕ храним в файле)
# Задай переменные окружения:
# - TELEGRAM_API_ID
# - TELEGRAM_API_HASH
API_ID = int(os.getenv("TELEGRAM_API_ID", "0") or "0") or None
API_HASH = os.getenv("TELEGRAM_API_HASH")

# Минимальная длина текста поста (можно подстроить при необходимости)
MIN_POST_LENGTH = getattr(Config, "MIN_POST_LENGTH", 10)


def _should_keep_message(message: Message) -> bool:
    """
    Фильтрация сообщений, чтобы в примерах были только осмысленные посты.
    Логика упрощённо повторяет _should_process_message из ChannelMonitor.
    """
    if not message.text or not message.text.strip():
        return False

    text = message.text.strip()
    if len(text) < MIN_POST_LENGTH:
        return False

    # Служебные сообщения / пересылки нам не нужны
    if message.action:
        return False
    if message.fwd_from:
        return False

    return True


async def collect_examples() -> None:
    """
    Собирает все (насколько позволяет Telegram) подходящие посты из канала
    SOURCE_CHANNEL и сохраняет их в OUTPUT_FILE.
    """
    if not API_ID or not API_HASH:
        raise RuntimeError(
            "Не заданы TELEGRAM_API_ID / TELEGRAM_API_HASH. "
            "Задай их в переменных окружения и запусти скрипт снова."
        )

    client = TelegramClient(Config.SESSION_NAME, API_ID, API_HASH)

    await client.start()

    texts: List[str] = []

    # Проходим по всей истории канала
    async for message in client.iter_messages(SOURCE_CHANNEL, limit=None):
        if not _should_keep_message(message):
            continue

        text = message.text.strip()
        texts.append(text)

    # Разворачиваем, чтобы в файле шли от старых к новым
    texts.reverse()

    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        for idx, text in enumerate(texts, start=1):
            f.write(f"### POST {idx}\n")
            f.write(text)
            f.write("\n" + "-" * 80 + "\n")

    await client.disconnect()

    print(f"Готово: собрано {len(texts)} постов → {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(collect_examples())

