#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отдельный Twitter монитор, работающий независимо от Telegram бота
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

from config import Config
from bot.twitter_monitor import TwitterMonitor
from bot.twitter_adapter import TwitterAdapter
from ai.content_rewriter import ContentRewriter, SourcePost
from utils.logger import setup_logger

logger = setup_logger()

class TwitterMonitorStandalone:
    """Отдельный Twitter монитор"""
    
    def __init__(self):
        self.config = Config()
        self.twitter_monitor = None
        self.content_rewriter = None
        
    async def start(self):
        """Запуск Twitter монитора"""
        try:
            logger.info("🚀 Запуск отдельного Twitter монитора")
            
            # Инициализируем Twitter монитор
            self.twitter_monitor = TwitterMonitor(self.config)
            if not await self.twitter_monitor.initialize():
                logger.error("❌ Не удалось инициализировать Twitter монитор")
                return
            
            # Инициализируем content rewriter
            self.content_rewriter = ContentRewriter(self.config)
            await self.content_rewriter.setup_ai_clients()
            
            logger.info("✅ Twitter монитор готов к работе")
            
            # Запускаем мониторинг
            await self._run_monitoring()
            
        except Exception as e:
            logger.error(f"💥 Критическая ошибка: {e}")
    
    async def _run_monitoring(self):
        """Основной цикл мониторинга"""
        while True:
            try:
                logger.info(f"🔍 Проверяем Twitter аккаунты (интервал: {self.config.TWITTER_CHECK_INTERVAL_MINUTES} мин)")
                
                # Проверяем все аккаунты
                new_tweets = await self.twitter_monitor.check_all_accounts()
                
                if new_tweets:
                    logger.info(f"📱 Получено {len(new_tweets)} новых твитов")
                    await self._process_twitter_posts(new_tweets)
                else:
                    logger.info("📱 Новых твитов не найдено")
                
                # Ждем до следующей проверки
                logger.info(f"⏰ Ждем {self.config.TWITTER_CHECK_INTERVAL_MINUTES} минут до следующей проверки")
                await asyncio.sleep(self.config.TWITTER_CHECK_INTERVAL_MINUTES * 60)
                
            except Exception as e:
                logger.error(f"❌ Ошибка в цикле мониторинга: {e}")
                # При rate limit ждем дольше, при других ошибках - меньше
                if "Rate limit exceeded" in str(e):
                    logger.warning("⚠️ Rate limit Twitter API, ждем 15 минут")
                    await asyncio.sleep(900)  # 15 минут
                else:
                    logger.warning("⚠️ Ошибка Twitter API, ждем 5 минут")
                    await asyncio.sleep(300)  # 5 минут
    
    async def _process_twitter_posts(self, twitter_posts):
        """Обработка новых Twitter постов"""
        try:
            # Фильтруем релевантные посты
            relevant_posts = TwitterAdapter.filter_relevant_twitter_posts(
                twitter_posts,
                min_engagement=10,
                exclude_retweets=True,
                exclude_replies=True
            )
            
            if not relevant_posts:
                logger.info("📱 Нет релевантных твитов для обработки")
                return
            
            # Преобразуем в SourcePost
            source_posts = TwitterAdapter.convert_twitter_posts_to_source_posts(relevant_posts)
            
            # Обрабатываем каждый пост
            for source_post in source_posts:
                await self._process_single_post(source_post)
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки Twitter постов: {e}")
    
    async def _process_single_post(self, source_post: SourcePost):
        """Обработка одного Twitter поста"""
        try:
            logger.info(f"🔄 Обработка Twitter поста: {source_post.id} от @{source_post.channel_title}")
            
            # Переписываем пост
            rewritten_post = await self.content_rewriter.rewrite_post(source_post)
            
            logger.info(f"✅ Twitter пост переписан: {rewritten_post.rewritten_text[:100]}...")
            
            # Здесь можно добавить логику для отправки в Telegram
            # Например, через API или файловую систему
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки Twitter поста: {e}")

async def main():
    """Главная функция"""
    monitor = TwitterMonitorStandalone()
    await monitor.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Twitter монитор остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")
