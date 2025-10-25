"""
Twitter Monitor Module
Мониторинг Twitter аккаунтов для получения новостей и твитов
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import tweepy
from config import Config

logger = logging.getLogger(__name__)

@dataclass
class TwitterPost:
    """Структура данных для Twitter поста"""
    id: str
    text: str
    author: str
    author_username: str
    created_at: datetime
    url: str
    retweet_count: int
    like_count: int
    reply_count: int
    is_retweet: bool
    is_reply: bool
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]

class TwitterMonitor:
    """Класс для мониторинга Twitter аккаунтов"""
    
    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[tweepy.Client] = None
        self.api: Optional[tweepy.API] = None
        self.last_check_times: Dict[str, datetime] = {}
        self.is_running = False
        
    async def setup_twitter_client(self) -> bool:
        """Настройка Twitter API клиента"""
        try:
            if not self.config.TWITTER_BEARER_TOKEN:
                logger.warning("Twitter Bearer Token не настроен")
                return False
                
            # Создаем клиент с Bearer Token и дополнительными ключами
            client_kwargs = {
                'bearer_token': self.config.TWITTER_BEARER_TOKEN,
                'wait_on_rate_limit': True
            }
            
            # Добавляем дополнительные ключи, если они есть
            if self.config.TWITTER_API_KEY and self.config.TWITTER_API_SECRET:
                client_kwargs['consumer_key'] = self.config.TWITTER_API_KEY
                client_kwargs['consumer_secret'] = self.config.TWITTER_API_SECRET
                
            if self.config.TWITTER_ACCESS_TOKEN and self.config.TWITTER_ACCESS_TOKEN_SECRET:
                client_kwargs['access_token'] = self.config.TWITTER_ACCESS_TOKEN
                client_kwargs['access_token_secret'] = self.config.TWITTER_ACCESS_TOKEN_SECRET
            
            self.client = tweepy.Client(**client_kwargs)
            
            # Проверяем подключение простым запросом
            try:
                logger.info("Проверяем подключение к Twitter API...")
                # Пробуем получить информацию о пользователе для проверки токена
                test_user = self.client.get_user(username="twitter")
                if test_user.data:
                    logger.info(f"Twitter API подключен успешно. Тестовый пользователь: @{test_user.data.username}")
                    return True
                else:
                    logger.warning("Twitter API подключен, но тестовый пользователь не найден")
                    return True
            except Exception as e:
                logger.error(f"Ошибка проверки Twitter API: {e}")
                logger.error(f"Тип ошибки: {type(e).__name__}")
                # Продолжаем работу, возможно токен валиден
                return True
                
        except Exception as e:
            logger.error(f"Ошибка настройки Twitter API: {e}")
            return False
    
    async def get_user_tweets(self, username: str, since_id: Optional[str] = None) -> List[TwitterPost]:
        """Получение твитов пользователя"""
        if not self.client:
            logger.error("Twitter клиент не инициализирован")
            return []
            
        try:
            # Получаем ID пользователя по username
            user = self.client.get_user(username=username)
            if not user.data:
                logger.warning(f"Пользователь @{username} не найден")
                return []
                
            user_id = user.data.id
            
            # Получаем твиты пользователя
            exclude_list = []
            if not self.config.TWITTER_INCLUDE_RETWEETS:
                exclude_list.append('retweets')
            if not self.config.TWITTER_INCLUDE_REPLIES:
                exclude_list.append('replies')
            
            tweets = self.client.get_users_tweets(
                id=user_id,
                since_id=since_id,
                max_results=min(self.config.TWITTER_MAX_TWEETS_PER_CHECK, 100),
                tweet_fields=[
                    'created_at', 'public_metrics', 'context_annotations',
                    'entities', 'referenced_tweets'
                ],
                exclude=exclude_list if exclude_list else None
            )
            
            if not tweets.data:
                return []
                
            twitter_posts = []
            for tweet in tweets.data:
                # Проверяем, не ретвит ли это
                is_retweet = False
                is_reply = False
                
                if tweet.referenced_tweets:
                    for ref in tweet.referenced_tweets:
                        if ref.type == 'retweeted':
                            is_retweet = True
                        elif ref.type == 'replied_to':
                            is_reply = True
                
                # Извлекаем медиа
                media_urls = []
                if tweet.entities and 'urls' in tweet.entities:
                    for url in tweet.entities['urls']:
                        if 'expanded_url' in url and any(ext in url['expanded_url'].lower() 
                                                        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4']):
                            media_urls.append(url['expanded_url'])
                
                # Извлекаем хештеги
                hashtags = []
                if tweet.entities and 'hashtags' in tweet.entities:
                    hashtags = [tag['tag'] for tag in tweet.entities['hashtags']]
                
                # Извлекаем упоминания
                mentions = []
                if tweet.entities and 'mentions' in tweet.entities:
                    mentions = [mention['username'] for mention in tweet.entities['mentions']]
                
                # Получаем метрики
                metrics = tweet.public_metrics if tweet.public_metrics else {}
                
                twitter_post = TwitterPost(
                    id=tweet.id,
                    text=tweet.text,
                    author=user.data.name,
                    author_username=user.data.username,
                    created_at=tweet.created_at,
                    url=f"https://twitter.com/{user.data.username}/status/{tweet.id}",
                    retweet_count=metrics.get('retweet_count', 0),
                    like_count=metrics.get('like_count', 0),
                    reply_count=metrics.get('reply_count', 0),
                    is_retweet=is_retweet,
                    is_reply=is_reply,
                    media_urls=media_urls,
                    hashtags=hashtags,
                    mentions=mentions
                )
                
                twitter_posts.append(twitter_post)
            
            return twitter_posts
            
        except Exception as e:
            logger.error(f"Ошибка получения твитов для @{username}: {e}")
            return []
    
    async def check_all_accounts(self) -> List[TwitterPost]:
        """Проверка всех аккаунтов на новые твиты"""
        if not self.config.TWITTER_MONITORING_ENABLED or not self.client:
            return []
            
        all_new_tweets = []
        
        for username in self.config.TWITTER_ACCOUNTS:
            try:
                # Получаем время последней проверки
                last_check = self.last_check_times.get(username)
                since_id = None
                
                # Если это первая проверка, берем твиты за последний час
                if not last_check:
                    last_check = datetime.utcnow() - timedelta(hours=1)
                
                # Получаем новые твиты
                new_tweets = await self.get_user_tweets(username, since_id)
                
                # Фильтруем по времени
                filtered_tweets = []
                for tweet in new_tweets:
                    if tweet.created_at.replace(tzinfo=None) > last_check:
                        filtered_tweets.append(tweet)
                
                if filtered_tweets:
                    logger.info(f"Найдено {len(filtered_tweets)} новых твитов от @{username}")
                    all_new_tweets.extend(filtered_tweets)
                
                # Обновляем время последней проверки
                self.last_check_times[username] = datetime.utcnow()
                
                # Небольшая задержка между запросами
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка проверки аккаунта @{username}: {e}")
                # При rate limit или других ошибках, пропускаем остальные аккаунты
                if "Rate limit exceeded" in str(e):
                    logger.warning("Превышен лимит Twitter API, пропускаем остальные аккаунты")
                    break
                continue
        
        return all_new_tweets
    
    async def initialize(self):
        """Инициализация Twitter клиента"""
        if not await self.setup_twitter_client():
            logger.error("Не удалось настроить Twitter клиент")
            return False
        return True
    
    def stop_monitoring(self):
        """Остановка мониторинга Twitter"""
        self.is_running = False
        logger.info("Остановка мониторинга Twitter")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики мониторинга"""
        return {
            "is_running": self.is_running,
            "accounts_monitored": len(self.config.TWITTER_ACCOUNTS),
            "last_check_times": {
                username: last_check.isoformat() if last_check else None
                for username, last_check in self.last_check_times.items()
            },
            "check_interval_minutes": self.config.TWITTER_CHECK_INTERVAL_MINUTES
        }
