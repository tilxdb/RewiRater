#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Мониторинг каналов-источников для отслеживания новых постов
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import json
from pathlib import Path

from telethon import TelegramClient, events
from telethon.tl.types import Message, PeerChannel
from telethon.errors import FloodWaitError, ChannelPrivateError

from loguru import logger

class ChannelMonitor:
    """Монитор каналов для отслеживания новых постов"""
    
    def __init__(self, config, telegram_client: TelegramClient):
        self.config = config
        self.client = telegram_client
        self.processed_posts_file = Path("data/processed_posts.json")
        self.processed_posts_file.parent.mkdir(exist_ok=True)
        
        # Загружаем список обработанных постов
        self.processed_posts: Set[int] = self._load_processed_posts()
        
        # Callback для обработки новых постов
        self.on_new_post_callback = None
        
        # Статистика
        self.stats = {
            "total_monitored_channels": len(self.config.SOURCE_CHANNELS),
            "total_processed_posts": len(self.processed_posts),
            "last_check_time": None
        }
    
    def set_post_processor(self, callback):
        """Устанавливает callback для обработки новых постов"""
        self.on_new_post_callback = callback
        logger.info("Callback для обработки постов установлен")
    
    async def start_monitoring(self):
        """Запуск мониторинга каналов"""
        logger.info(f"Запуск мониторинга {len(self.config.SOURCE_CHANNELS)} каналов")
        
        try:
            # Проверяем доступность каналов
            await self._verify_channels_access()
            
            # Регистрируем обработчик новых сообщений для всех каналов
            @self.client.on(events.NewMessage(chats=self.config.SOURCE_CHANNELS))
            async def new_message_handler(event):
                await self._handle_new_message(event)
            
            logger.info("Мониторинг каналов запущен успешно")
            
            # Запускаем бесконечный цикл для поддержания соединения
            while True:
                await asyncio.sleep(60)  # Проверяем каждую минуту
                
                # Обновляем статистику
                self.stats["last_check_time"] = datetime.now().isoformat()
                
        except Exception as e:
            logger.error(f"Ошибка запуска мониторинга: {e}")
            raise
    
    async def _verify_channels_access(self):
        """Проверка доступа к каналам"""
        accessible_channels = []
        
        for channel_id in self.config.SOURCE_CHANNELS:
            try:
                # Для каналов используем get_entity с правильным типом
                if isinstance(channel_id, int) and channel_id < 0:
                    # Это канал или супергруппа (числовой ID)
                    entity = await self.client.get_entity(channel_id)
                elif isinstance(channel_id, int):
                    # Это обычный чат (числовой ID)
                    entity = await self.client.get_entity(channel_id)
                else:
                    # Это строковый ID (например, @username)
                    entity = await self.client.get_entity(channel_id)
                
                accessible_channels.append(channel_id)
                logger.info(f"Доступ к каналу {channel_id} подтвержден: {entity.title}")
                
            except ChannelPrivateError:
                logger.warning(f"Нет доступа к приватному каналу {channel_id}")
            except Exception as e:
                logger.error(f"Ошибка проверки канала {channel_id}: {e}")
                # Попробуем альтернативный способ для каналов
                try:
                    if isinstance(channel_id, int) and channel_id < 0:
                        # Преобразуем ID канала в правильный формат
                        # Для каналов ID должен быть положительным с префиксом -100
                        channel_id_corrected = -1000000000000 - channel_id
                        logger.info(f"Пробуем исправленный ID канала: {channel_id_corrected}")
                        
                        entity = await self.client.get_entity(channel_id_corrected)
                        accessible_channels.append(channel_id)
                        logger.info(f"Доступ к каналу {channel_id} подтвержден (исправленный ID): {entity.title}")
                    else:
                        # Для строковых ID пробуем через строку
                        logger.info(f"Пробуем получить канал через строку: {channel_id}")
                        entity = await self.client.get_entity(str(channel_id))
                        accessible_channels.append(channel_id)
                        logger.info(f"Доступ к каналу {channel_id} подтвержден (через строку): {entity.title}")
                except Exception as e2:
                    logger.error(f"Альтернативная проверка канала {channel_id} также не удалась: {e2}")
        
        if not accessible_channels:
            raise Exception("Нет доступных каналов для мониторинга")
        
        logger.info(f"Доступно каналов для мониторинга: {len(accessible_channels)}")
    
    async def _handle_new_message(self, event):
        """Обработка нового сообщения из канала"""
        try:
            message = event.message
            
            logger.info(f"Получено сообщение из канала {event.chat_id}: ID={message.id}, текст='{message.text[:50] if message.text else 'None'}...'")
            
            # Проверяем, не обрабатывали ли мы уже этот пост
            if message.id in self.processed_posts:
                logger.info(f"Пост {message.id} уже обработан, пропускаем")
                return
            
            # Фильтруем сообщения
            if not self._should_process_message(message):
                logger.info(f"Пост {message.id} не прошел фильтрацию, пропускаем")
                return
            
            logger.info(f"✅ Новый пост в канале {event.chat_id}: {message.id}")
            
            # Создаем объект поста
            post_data = await self._extract_post_data(message, event.chat_id)
            
            # Вызываем callback для обработки
            if self.on_new_post_callback:
                logger.info(f"Вызываем callback для обработки поста {message.id}")
                await self.on_new_post_callback(post_data)
            else:
                logger.warning("Callback для обработки постов не установлен!")
            
            # Помечаем пост как обработанный
            self._mark_post_as_processed(message.id)
            
        except Exception as e:
            logger.error(f"Ошибка обработки нового сообщения: {e}")
    
    def _should_process_message(self, message: Message) -> bool:
        """Проверяет, стоит ли обрабатывать сообщение"""
        # Пропускаем сообщения без текста
        if not message.text or not message.text.strip():
            logger.debug(f"Пост {message.id}: нет текста")
            return False
        
        # Пропускаем слишком короткие сообщения
        if len(message.text.strip()) < self.config.MIN_POST_LENGTH:
            logger.debug(f"Пост {message.id}: слишком короткий ({len(message.text.strip())} < {self.config.MIN_POST_LENGTH})")
            return False
        
        # Пропускаем служебные сообщения
        if message.action:
            logger.debug(f"Пост {message.id}: служебное сообщение")
            return False
        
        # Пропускаем пересланные сообщения (если нужно)
        if message.fwd_from:
            logger.debug(f"Пост {message.id}: пересланное сообщение")
            return False
        
        logger.debug(f"Пост {message.id}: прошел все фильтры")
        return True
    
    async def _extract_post_data(self, message: Message, channel_id: int) -> Dict:
        """Извлекает данные из поста"""
        # Извлекаем информацию о медиа
        media_type = None
        media_file_id = None
        media_url = None
        
        if message.media:
            media_type, media_file_id, media_url = await self._extract_media_info(message)
        
        return {
            "id": message.id,
            "text": message.text,
            "date": message.date,
            "channel_id": channel_id,
            "channel_title": await self._get_channel_title(channel_id),
            "has_media": bool(message.media),
            "media_type": media_type,
            "media_object": media_file_id,  # Здесь сохраняем медиа объект
            "media_url": media_url,
            "views": message.views or 0,
            "forwards": message.forwards or 0,
            "url": f"https://t.me/{await self._get_channel_username(channel_id)}/{message.id}" if await self._get_channel_username(channel_id) else None
        }
    
    async def _extract_media_info(self, message: Message) -> tuple:
        """Извлекает информацию о медиа из сообщения"""
        try:
            if not message.media:
                return None, None, None
            
            # Определяем тип медиа
            media_type = None
            
            if hasattr(message.media, 'photo'):
                media_type = 'photo'
            elif hasattr(message.media, 'document'):
                media_type = 'document'
                
                # Определяем подтип документа
                if message.media.document.mime_type:
                    if message.media.document.mime_type.startswith('video/'):
                        media_type = 'video'
                    elif message.media.document.mime_type == 'image/gif':
                        media_type = 'animation'
            elif hasattr(message.media, 'video'):
                media_type = 'video'
            elif hasattr(message.media, 'gif'):
                media_type = 'animation'
            
            # Получаем URL медиа (если доступен)
            media_url = None
            try:
                # Пытаемся получить прямую ссылку на файл
                media_url = f"https://t.me/{message.chat.username}/{message.id}" if message.chat.username else None
            except:
                media_url = None
            
            logger.info(f"Извлечено медиа: тип={media_type}")
            return media_type, message.media, media_url
            
        except Exception as e:
            logger.error(f"Ошибка извлечения медиа информации: {e}")
            return None, None, None
    
    async def _get_channel_title(self, channel_id: int) -> str:
        """Получает название канала"""
        try:
            entity = await self.client.get_entity(channel_id)
            return entity.title or f"Channel {channel_id}"
        except:
            return f"Channel {channel_id}"
    
    async def _get_channel_username(self, channel_id: int) -> Optional[str]:
        """Получает username канала"""
        try:
            entity = await self.client.get_entity(channel_id)
            return entity.username
        except:
            return None
    
    def _mark_post_as_processed(self, post_id: int):
        """Помечает пост как обработанный"""
        self.processed_posts.add(post_id)
        self._save_processed_posts()
        self.stats["total_processed_posts"] = len(self.processed_posts)
    
    def _load_processed_posts(self) -> Set[int]:
        """Загружает список обработанных постов"""
        try:
            if self.processed_posts_file.exists():
                with open(self.processed_posts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get("processed_posts", []))
        except Exception as e:
            logger.error(f"Ошибка загрузки обработанных постов: {e}")
        
        return set()
    
    def _save_processed_posts(self):
        """Сохраняет список обработанных постов"""
        try:
            data = {
                "processed_posts": list(self.processed_posts),
                "last_update": datetime.now().isoformat(),
                "total_count": len(self.processed_posts)
            }
            
            with open(self.processed_posts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Ошибка сохранения обработанных постов: {e}")
    
    async def get_recent_posts(self, channel_id: int, limit: int = 10) -> List[Dict]:
        """Получает последние посты из канала"""
        try:
            posts = []
            async for message in self.client.iter_messages(channel_id, limit=limit):
                if self._should_process_message(message):
                    post_data = await self._extract_post_data(message, channel_id)
                    posts.append(post_data)
            
            return posts
            
        except Exception as e:
            logger.error(f"Ошибка получения постов из канала {channel_id}: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Возвращает статистику мониторинга"""
        return {
            **self.stats,
            "processed_posts_count": len(self.processed_posts),
            "monitored_channels": self.config.SOURCE_CHANNELS,
            "last_check_time": self.stats.get("last_check_time")
        }
