"""
Twitter Adapter Module
Адаптер для преобразования Twitter постов в SourcePost
"""

import logging
from datetime import datetime
from typing import List
from bot.twitter_monitor import TwitterPost
from ai.content_rewriter import SourcePost

logger = logging.getLogger(__name__)

class TwitterAdapter:
    """Адаптер для преобразования Twitter постов в SourcePost"""
    
    @staticmethod
    def convert_twitter_post_to_source_post(twitter_post: TwitterPost) -> SourcePost:
        """Преобразование Twitter поста в SourcePost"""
        try:
            # Создаем SourcePost из Twitter поста
            source_post = SourcePost(
                id=int(twitter_post.id),
                text=twitter_post.text,
                channel_id=0,  # Twitter не имеет channel_id
                channel_title=f"@{twitter_post.author_username}",
                date=twitter_post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                views=twitter_post.retweet_count + twitter_post.like_count + twitter_post.reply_count,
                forwards=twitter_post.retweet_count,
                url=twitter_post.url,
                media_type=None,  # Twitter медиа обрабатывается отдельно
                media_object=None,
                media_url=twitter_post.media_urls[0] if twitter_post.media_urls else None,
                source_type="twitter",
                original_url=twitter_post.url
            )
            
            logger.debug(f"Twitter пост @{twitter_post.author_username} преобразован в SourcePost")
            return source_post
            
        except Exception as e:
            logger.error(f"Ошибка преобразования Twitter поста: {e}")
            raise
    
    @staticmethod
    def convert_twitter_posts_to_source_posts(twitter_posts: List[TwitterPost]) -> List[SourcePost]:
        """Преобразование списка Twitter постов в список SourcePost"""
        source_posts = []
        
        for twitter_post in twitter_posts:
            try:
                source_post = TwitterAdapter.convert_twitter_post_to_source_post(twitter_post)
                source_posts.append(source_post)
            except Exception as e:
                logger.error(f"Ошибка преобразования Twitter поста {twitter_post.id}: {e}")
                continue
        
        logger.info(f"Преобразовано {len(source_posts)} из {len(twitter_posts)} Twitter постов")
        return source_posts
    
    @staticmethod
    def filter_relevant_twitter_posts(twitter_posts: List[TwitterPost], 
                                    min_engagement: int = 10,
                                    exclude_retweets: bool = True,
                                    exclude_replies: bool = True) -> List[TwitterPost]:
        """Фильтрация релевантных Twitter постов"""
        filtered_posts = []
        
        for post in twitter_posts:
            # Проверяем минимальную вовлеченность
            engagement = post.retweet_count + post.like_count + post.reply_count
            if engagement < min_engagement:
                continue
            
            # Исключаем ретвиты, если нужно
            if exclude_retweets and post.is_retweet:
                continue
            
            # Исключаем ответы, если нужно
            if exclude_replies and post.is_reply:
                continue
            
            # Проверяем длину текста
            if len(post.text.strip()) < 20:
                continue
            
            filtered_posts.append(post)
        
        logger.info(f"Отфильтровано {len(filtered_posts)} из {len(twitter_posts)} Twitter постов")
        return filtered_posts
    
    @staticmethod
    def extract_keywords_from_twitter_post(twitter_post: TwitterPost) -> List[str]:
        """Извлечение ключевых слов из Twitter поста"""
        keywords = []
        
        # Добавляем хештеги
        keywords.extend(twitter_post.hashtags)
        
        # Добавляем упоминания
        keywords.extend([f"@{mention}" for mention in twitter_post.mentions])
        
        # Извлекаем ключевые слова из текста
        text_lower = twitter_post.text.lower()
        crypto_keywords = [
            'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
            'blockchain', 'defi', 'nft', 'web3', 'dao', 'token', 'coin',
            'ton', 'telegram', 'binance', 'coinbase', 'uniswap', 'aave'
        ]
        
        for keyword in crypto_keywords:
            if keyword in text_lower:
                keywords.append(keyword)
        
        return list(set(keywords))  # Убираем дубли
