#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отдельный Twitter бот для мониторинга и переписывания твитов
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

from config import Config
from bot.twitter_monitor import TwitterMonitor
from bot.twitter_adapter import TwitterAdapter
from ai.content_rewriter import ContentRewriter, SourcePost
from utils.logger import setup_logger
from telethon import TelegramClient
from telethon.errors import FloodWaitError

logger = setup_logger()

class TwitterBot:
    """Отдельный бот для мониторинга Twitter"""
    
    def __init__(self):
        self.config = Config()
        self.config.load_from_env()
        
        self.twitter_monitor = None
        self.content_rewriter = None
        self.telegram_client = None
        
        # Статистика
        self.posts_today = 0
        self.last_post_time = None
        
    async def initialize(self):
        """Инициализация всех компонентов"""
        try:
            logger.info("Инициализация Twitter бота...")
            
            # Инициализируем AI переписыватель
            logger.info("Настройка AI переписывателя...")
            self.content_rewriter = ContentRewriter(self.config)
            self.content_rewriter.setup_ai_clients()
            
            # Инициализируем Twitter монитор
            logger.info("Настройка Twitter монитора...")
            self.twitter_monitor = TwitterMonitor(self.config)
            if not await self.twitter_monitor.initialize():
                logger.error("Не удалось инициализировать Twitter монитор")
                return False
            
            # Инициализируем Telegram клиент для публикации
            logger.info("Настройка Telegram клиента...")
            self.telegram_client = TelegramClient(
                "twitter_bot_session",
                self.config.API_ID,
                self.config.API_HASH
            )
            await self.telegram_client.start()
            
            logger.info("Twitter бот инициализирован успешно!")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка инициализации Twitter бота: {e}")
            return False
    
    async def start_monitoring(self):
        """Запуск мониторинга Twitter"""
        logger.info("Запуск мониторинга Twitter...")
        
        try:
            while True:
                try:
                    logger.info(f"Проверяем Twitter аккаунты (интервал: {self.config.TWITTER_CHECK_INTERVAL_MINUTES} мин)")
                    
                    # Проверяем все аккаунты
                    new_tweets = await self.twitter_monitor.check_all_accounts()
                    
                    if new_tweets:
                        logger.info(f"Получено {len(new_tweets)} новых твитов")
                        await self._process_twitter_posts(new_tweets)
                    else:
                        logger.info("Новых твитов не найдено")
                    
                    # Ждем до следующей проверки
                    logger.info(f"Ждем {self.config.TWITTER_CHECK_INTERVAL_MINUTES} минут до следующей проверки")
                    await asyncio.sleep(self.config.TWITTER_CHECK_INTERVAL_MINUTES * 60)
                    
                except Exception as e:
                    logger.error(f"Ошибка в цикле Twitter мониторинга: {e}")
                    # При rate limit ждем дольше, при других ошибках - меньше
                    if "Rate limit exceeded" in str(e):
                        logger.warning("Rate limit Twitter API, ждем 15 минут")
                        await asyncio.sleep(900)  # 15 минут
                    else:
                        logger.warning("Ошибка Twitter API, ждем 5 минут")
                        await asyncio.sleep(300)  # 5 минут
                    
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
        except Exception as e:
            logger.error(f"Критическая ошибка в Twitter мониторинге: {e}")
        finally:
            await self.stop()
    
    async def _process_twitter_posts(self, twitter_posts: List[Any]):
        """Обработка новых Twitter постов"""
        try:
            # Фильтруем релевантные посты
            relevant_posts = []
            for tweet in twitter_posts:
                if self._is_relevant_tweet(tweet):
                    relevant_posts.append(tweet)
            
            if not relevant_posts:
                logger.info("Нет релевантных твитов для обработки")
                return
            
            logger.info(f"Обрабатываем {len(relevant_posts)} релевантных твитов")
            
            # Конвертируем и переписываем посты
            for tweet in relevant_posts:
                try:
                    # Конвертируем твит в SourcePost
                    source_post = TwitterAdapter.tweet_to_source_post(tweet)
                    
                    # Переписываем пост
                    rewritten_post = await self.content_rewriter.rewrite_post(source_post)
                    
                    # Публикуем в Telegram
                    await self._publish_to_telegram(rewritten_post)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки твита {tweet.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка обработки Twitter постов: {e}")
    
    def _is_relevant_tweet(self, tweet) -> bool:
        """Проверяет, релевантен ли твит для обработки"""
        # Проверяем длину текста
        if len(tweet.text) < self.config.MIN_POST_LENGTH:
            return False
        
        # Проверяем, что это не ретвит (если они отключены)
        if not self.config.TWITTER_INCLUDE_RETWEETS and hasattr(tweet, 'referenced_tweets'):
            return False
        
        # Проверяем, что это не ответ (если они отключены)
        if not self.config.TWITTER_INCLUDE_REPLIES and hasattr(tweet, 'in_reply_to_user_id'):
            return False
        
        return True
    
    async def _publish_to_telegram(self, rewritten_post):
        """Публикация переписанного поста в Telegram"""
        try:
            logger.info(f"Публикуем пост в {self.config.TARGET_CHANNEL}")
            
            await self.telegram_client.send_message(
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
        except Exception as e:
            logger.error(f"Ошибка публикации в Telegram: {e}")
    
    async def stop(self):
        """Остановка бота"""
        logger.info("Остановка Twitter бота...")
        
        if self.telegram_client:
            await self.telegram_client.disconnect()
        
        logger.info("Twitter бот остановлен")

async def main():
    """Основная функция"""
    logger.info("Запуск отдельного Twitter бота")
    
    bot = TwitterBot()
    
    try:
        if await bot.initialize():
            await bot.start_monitoring()
        else:
            logger.error("Не удалось инициализировать Twitter бота")
    
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await bot.stop()
        logger.info("Завершение работы Twitter бота")

if __name__ == "__main__":
    asyncio.run(main())
