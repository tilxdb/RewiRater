#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram User Bot для мониторинга каналов и публикации переработанного контента
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from pathlib import Path

from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, ChatWriteForbiddenError
from telethon.tl.types import PeerChannel

from loguru import logger
from bot.channel_monitor import ChannelMonitor
from ai.content_rewriter import ContentRewriter, SourcePost

class TelegramUserBot:
    """Telegram User Bot для мониторинга и публикации переработанного контента"""
    
    def __init__(self, config, content_rewriter: ContentRewriter):
        self.config = config
        self.content_rewriter = content_rewriter
        self.client = None
        self.channel_monitor = None
        self.stats_file = Path("data/stats.json")
        self.stats_file.parent.mkdir(exist_ok=True)
        
        # Статистика
        self.stats = self._load_stats()
        
        # Настройки публикации
        self.last_post_time = None
        self.posts_today = 0
        
        # Система очереди постов с таймингом
        self.post_queue = []
        self.publish_task = None
        
    async def start(self):
        """Запуск бота"""
        try:
            # Создаем клиент
            self.client = TelegramClient(
                self.config.SESSION_NAME,
                self.config.API_ID,
                self.config.API_HASH
            )
            
            # Пытаемся запустить с существующей сессией
            try:
                await self.client.start()
                logger.info("Telegram User Bot запущен")
            except Exception as e:
                logger.warning(f"Не удалось запустить с существующей сессией: {e}")
                logger.info("Создаем новую сессию...")
                
                # Создаем новую сессию
                await self.client.connect()
                if not await self.client.is_user_authorized():
                    logger.info("Требуется авторизация. Запустите систему в интерактивном режиме.")
                    raise Exception("Требуется авторизация в Telegram")
                
                logger.info("Telegram User Bot запущен с новой сессией")
            
            # Проверяем подключение
            me = await self.client.get_me()
            logger.info(f"Подключен как: {me.first_name} (@{me.username})")
            
            # Инициализируем монитор каналов
            self.channel_monitor = ChannelMonitor(self.config, self.client)
            self.channel_monitor.set_post_processor(self._process_new_post)
            logger.info("Монитор каналов инициализирован")
            
            
            # Запускаем мониторинг каналов (включает основной цикл)
            logger.info("Запускаем мониторинг каналов...")
            await self.channel_monitor.start_monitoring()
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
            raise
    
    
    async def _process_new_post(self, post_data: Dict):
        """Обработка нового поста из канала-источника"""
        try:
            logger.info(f"Обработка нового поста: {post_data['id']} из {post_data['channel_title']}")
            logger.info(f"Текст поста: {post_data['text'][:100]}...")
            
            # Проверяем лимиты публикации
            if not self._should_publish():
                logger.info("Достигнут дневной лимит публикаций")
                return
            
            # Создаем объект исходного поста
            source_post = SourcePost(
                id=post_data['id'],
                text=post_data['text'],
                channel_id=post_data['channel_id'],
                channel_title=post_data['channel_title'],
                date=post_data['date'].isoformat(),
                views=post_data['views'],
                forwards=post_data['forwards'],
                url=post_data.get('url'),
                media_type=post_data.get('media_type'),
                media_object=post_data.get('media_object'),
                media_url=post_data.get('media_url')
            )
            
            # Отправляем в ЛС ссылку на оригинальный пост и ссылки из него
            try:
                recipient = getattr(self.config, 'DM_RECIPIENT', None) or 'me'
                
                # Формируем ссылку на оригинальный пост
                post_url = source_post.url
                if not post_url:
                    # Если URL нет, формируем ссылку через channel_title (убираем @ если есть)
                    channel_name = source_post.channel_title.replace('@', '').replace(' ', '')
                    post_url = f"https://t.me/{channel_name}/{source_post.id}"
                
                # Извлекаем ссылки из поста
                links = self.content_rewriter.extract_links(source_post.text)
                
                # Формируем сообщение
                msg = f"📝 Оригинальный пост: {post_url}"
                if links:
                    msg += f"\n\n🔗 Ссылки из поста ({len(links)}):\n" + "\n".join(links)
                
                await self.client.send_message(entity=recipient, message=msg)
                logger.info(f"Отправлена ссылка на пост и {len(links) if links else 0} ссылок в ЛС")
            except Exception as e:
                logger.warning(f"Не удалось отправить ссылку на пост и ссылки в ЛС: {e}")

            # Переписываем пост под стиль целевого канала
            logger.info("Начинаем переписывание поста...")
            rewritten_post = await self.content_rewriter.rewrite_post(source_post)
            logger.info(f"Пост переписан: {rewritten_post.rewritten_text[:100]}...")
            
            # Добавляем пост в очередь для публикации с таймингом
            logger.info("Добавляем пост в очередь...")
            await self._add_post_to_queue(rewritten_post)
            
        except Exception as e:
            logger.error(f"Ошибка обработки поста: {e}")
    
    async def _publish_rewritten_post(self, rewritten_post):
        """Публикация переписанного поста"""
        try:
            logger.info(f"Публикуем пост в {self.config.TARGET_CHANNEL}")
            
            # Если есть медиа, отправляем с медиа
            if rewritten_post.media_type and rewritten_post.media_object:
                logger.info(f"Отправляем пост с медиа: {rewritten_post.media_type}")
                await self._send_media_post(rewritten_post)
            else:
                # Отправляем простой текст
                logger.info("Отправляем текстовый пост")
                await self.client.send_message(
                    entity=self.config.TARGET_CHANNEL,
                    message=rewritten_post.rewritten_text,
                    parse_mode='html'
                )
            
            logger.info(f"Переписанный пост опубликован в {self.config.TARGET_CHANNEL}")
            self.last_post_time = datetime.now()
            self.posts_today += 1
            
        except FloodWaitError as e:
            logger.warning(f"Превышен лимит запросов, ждем {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
        except ChatWriteForbiddenError:
            logger.error("Нет прав на запись в целевой канал")
        except Exception as e:
            logger.error(f"Ошибка публикации переписанного поста: {e}")
            raise
    
    async def _send_media_post(self, rewritten_post):
        """Отправка поста с медиа"""
        try:
            media_type = rewritten_post.media_type
            media_object = rewritten_post.media_object
            
            # Отправляем медиа с подписью
            await self.client.send_file(
                entity=self.config.TARGET_CHANNEL,
                file=media_object,
                caption=rewritten_post.rewritten_text,
                parse_mode='html'
            )
                
            logger.info(f"Пост с медиа ({media_type}) опубликован в {self.config.TARGET_CHANNEL}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки медиа поста: {e}")
            # Если не удалось отправить с медиа, отправляем только текст
            await self.client.send_message(
                entity=self.config.TARGET_CHANNEL,
                message=rewritten_post.rewritten_text,
                parse_mode='html'
            )
            logger.info("Отправлен только текст из-за ошибки с медиа")
    
    async def _add_post_to_queue(self, rewritten_post):
        """Добавляет пост в очередь для публикации с таймингом"""
        import random
        from datetime import datetime, timedelta
        
        # Вычисляем время публикации
        if self.last_post_time is None:
            # Первый пост публикуем сразу
            publish_time = datetime.now() + timedelta(minutes=1)
        else:
            # Следующие посты с интервалом 20-30 минут
            interval_minutes = random.randint(
                self.config.PUBLISH_INTERVAL_MIN, 
                self.config.PUBLISH_INTERVAL_MAX
            )
            publish_time = self.last_post_time + timedelta(minutes=interval_minutes)
        
        # Добавляем пост в очередь
        self.post_queue.append({
            'post': rewritten_post,
            'publish_time': publish_time
        })
        
        logger.info(f"Пост добавлен в очередь на {publish_time.strftime('%H:%M:%S')}")
        logger.info(f"Всего постов в очереди: {len(self.post_queue)}")
        
        # Запускаем обработчик очереди, если он еще не запущен
        if self.publish_task is None or self.publish_task.done():
            logger.info("Запускаем обработчик очереди...")
            self.publish_task = asyncio.create_task(self._process_post_queue())
    
    async def _process_post_queue(self):
        """Обрабатывает очередь постов и публикует их по расписанию"""
        logger.info("Обработчик очереди запущен")
        
        while self.post_queue:
            now = datetime.now()
            logger.info(f"Проверяем очередь: {len(self.post_queue)} постов")
            
            # Находим посты, готовые к публикации
            ready_posts = []
            remaining_posts = []
            
            for item in self.post_queue:
                if item['publish_time'] <= now:
                    ready_posts.append(item)
                    logger.info(f"Пост готов к публикации: {item['publish_time'].strftime('%H:%M:%S')}")
                else:
                    remaining_posts.append(item)
            
            # Публикуем готовые посты
            for item in ready_posts:
                try:
                    await self._publish_rewritten_post(item['post'])
                    self._update_stats(item['post'])
                    self.last_post_time = datetime.now()
                    self.posts_today += 1
                    logger.info(f"Пост опубликован из очереди")
                except Exception as e:
                    logger.error(f"Ошибка публикации поста из очереди: {e}")
            
            # Обновляем очередь
            self.post_queue = remaining_posts
            
            if self.post_queue:
                # Ждем до следующего поста
                next_post_time = min(item['publish_time'] for item in self.post_queue)
                wait_seconds = (next_post_time - now).total_seconds()
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
            else:
                break
        
        logger.info("Обработка очереди постов завершена")
    
    def _should_publish(self) -> bool:
        """Проверяет, можно ли добавлять посты в очередь"""
        now = datetime.now()
        
        # Проверяем лимит постов в день (включая очередь)
        total_posts = self.posts_today + len(self.post_queue)
        if total_posts >= self.config.MAX_POSTS_PER_DAY:
            # Сбрасываем счетчик в полночь
            if now.hour == 0 and now.minute < 5:
                self.posts_today = 0
                self.post_queue = []  # Очищаем очередь
                logger.info("Сброс счетчика постов на новый день")
            return False
        
        return True
    
    def _update_daily_stats(self):
        """Обновление дневной статистики"""
        now = datetime.now()
        if now.hour == 0 and now.minute < 5:
            self.posts_today = 0
            logger.info("Статистика обновлена на новый день")
    
    
    def _update_stats(self, rewritten_post):
        """Обновление статистики"""
        self.stats["total_posts"] = self.stats.get("total_posts", 0) + 1
        self.stats["posts_today"] = self.posts_today
        self.stats["last_post_time"] = datetime.now().isoformat()
        self.stats["provider_stats"] = self.stats.get("provider_stats", {})
        
        provider = rewritten_post.provider
        self.stats["provider_stats"][provider] = self.stats["provider_stats"].get(provider, 0) + 1
        
        # Статистика по источникам
        self.stats["source_stats"] = self.stats.get("source_stats", {})
        source_channel = rewritten_post.original_post.channel_title
        self.stats["source_stats"][source_channel] = self.stats["source_stats"].get(source_channel, 0) + 1
        
        # Сохраняем статистику
        self._save_stats()
    
    def _load_stats(self) -> Dict[str, Any]:
        """Загрузка статистики из файла"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки статистики: {e}")
        
        return {}
    
    def _save_stats(self):
        """Сохранение статистики в файл"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение текущей статистики"""
        stats = {
            "total_posts": self.stats.get("total_posts", 0),
            "posts_today": self.posts_today,
            "posts_in_queue": len(self.post_queue),
            "max_posts_per_day": self.config.MAX_POSTS_PER_DAY,
            "last_post_time": self.last_post_time.isoformat() if self.last_post_time else None,
            "publish_interval": f"{self.config.PUBLISH_INTERVAL_MIN}-{self.config.PUBLISH_INTERVAL_MAX} мин",
            "provider_stats": self.stats.get("provider_stats", {}),
            "source_stats": self.stats.get("source_stats", {}),
            "monitoring_stats": self.channel_monitor.get_stats() if self.channel_monitor else {}
        }
        
        
        return stats
    
    async def stop(self):
        """Остановка бота"""
        
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram User Bot остановлен")
