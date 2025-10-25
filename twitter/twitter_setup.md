# Настройка Twitter API для RewiRater

## Получение Twitter API ключей

### 1. Создание Twitter Developer Account

1. Перейдите на [developer.twitter.com](https://developer.twitter.com)
2. Войдите в свой Twitter аккаунт
3. Подайте заявку на Developer Account
4. Заполните форму с описанием вашего проекта
5. Дождитесь одобрения (обычно 1-3 дня)

### 2. Создание приложения

1. После одобрения перейдите в [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Нажмите "Create App"
3. Заполните информацию о приложении:
   - **App Name**: RewiRater Bot
   - **Description**: Telegram bot for monitoring and rewriting crypto news
   - **Website**: (можно оставить пустым)
   - **Callback URL**: (можно оставить пустым)

### 3. Получение API ключей

1. Перейдите в созданное приложение
2. Во вкладке "Keys and Tokens" найдите:
   - **API Key** (Consumer Key)
   - **API Secret Key** (Consumer Secret)
   - **Bearer Token**

### 4. Настройка прав доступа

1. Во вкладке "App permissions" установите:
   - **Read** - для чтения твитов
   - **Read and Write** - если планируете публиковать твиты

### 5. Настройка в config.py

Добавьте полученные ключи в `config.py`:

```python
# Настройки Twitter API
TWITTER_API_KEY: str = "ваш_api_key"
TWITTER_API_SECRET: str = "ваш_api_secret"
TWITTER_ACCESS_TOKEN: str = "ваш_access_token"
TWITTER_ACCESS_TOKEN_SECRET: str = "ваш_access_token_secret"
TWITTER_BEARER_TOKEN: str = "ваш_bearer_token"

# Настройки Twitter мониторинга
TWITTER_MONITORING_ENABLED: bool = True
TWITTER_CHECK_INTERVAL_MINUTES: int = 15
TWITTER_MAX_TWEETS_PER_CHECK: int = 5
TWITTER_INCLUDE_RETWEETS: bool = False
TWITTER_INCLUDE_REPLIES: bool = False
```

## Настройка мониторинга аккаунтов

### Список аккаунтов по умолчанию

В `config.py` уже настроен список ключевых аккаунтов:

```python
TWITTER_ACCOUNTS: List[str] = [
    # Ключевые личности
    "VitalikButerin",      # Vitalik Buterin
    "elonmusk",            # Elon Musk
    "naval",               # Naval Ravikant
    "balajis",             # Balaji Srinivasan
    "aantonop",            # Andreas Antonopoulos
    "APompliano",          # Anthony Pompliano
    "cz_binance",          # CZ Binance
    "justinsuntron",       # Justin Sun
    "brian_armstrong",     # Brian Armstrong (Coinbase)
    "michael_saylor",      # Michael Saylor
    
    # Крупные проекты и биржи
    "coinbase",            # Coinbase
    "binance",             # Binance
    "ethereum",            # Ethereum
    "solana",              # Solana
    "avalancheavax",       # Avalanche
    "polygon",             # Polygon
    "chainlink",           # Chainlink
    "uniswap",             # Uniswap
    "aave",                # Aave
    "makerdao",            # MakerDAO
    
    # TON экосистема
    "ton_blockchain",      # TON Blockchain
    "tonkeeper",           # TON Keeper
    "tonfoundation",       # TON Foundation
    "toncoin",             # TON Coin
    "ton_whales",          # TON Whales
    "ton_community",       # TON Community
    "ton_developers",      # TON Developers
    "ton_news",            # TON News
    "ton_updates",         # TON Updates
    "ton_announcements",   # TON Announcements
]
```

### Добавление новых аккаунтов

Чтобы добавить новые аккаунты для мониторинга:

1. Откройте `config.py`
2. Найдите список `TWITTER_ACCOUNTS`
3. Добавьте username аккаунта (без @)
4. Перезапустите бота

## Ограничения Twitter API

### Rate Limits

- **User Timeline**: 1500 запросов в 15 минут
- **User Lookup**: 300 запросов в 15 минут
- **Tweet Lookup**: 300 запросов в 15 минут

### Рекомендации

1. **Интервал проверки**: Не менее 15 минут между проверками
2. **Количество твитов**: Максимум 5 твитов за проверку
3. **Фильтрация**: Исключайте ретвиты и ответы для экономии лимитов

## Мониторинг и статистика

### Статистика Twitter мониторинга

Бот предоставляет статистику по Twitter мониторингу:

```python
{
    "twitter_stats": {
        "is_running": true,
        "accounts_monitored": 30,
        "last_check_times": {
            "VitalikButerin": "2025-01-21T10:30:00",
            "elonmusk": "2025-01-21T10:30:00",
            ...
        },
        "check_interval_minutes": 15
    }
}
```

### Логирование

Все действия Twitter мониторинга логируются:

- Подключение к API
- Получение твитов
- Ошибки API
- Статистика обработки

## Устранение неполадок

### Ошибка "Unauthorized"

1. Проверьте правильность API ключей
2. Убедитесь, что приложение имеет права на чтение
3. Проверьте, что Bearer Token активен

### Ошибка "Rate limit exceeded"

1. Увеличьте интервал проверки
2. Уменьшите количество твитов за проверку
3. Исключите ретвиты и ответы

### Ошибка "User not found"

1. Проверьте правильность username (без @)
2. Убедитесь, что аккаунт не заблокирован
3. Проверьте, что аккаунт публичный

## Безопасность

### Защита API ключей

1. Никогда не публикуйте API ключи в открытом доступе
2. Используйте переменные окружения для продакшена
3. Регулярно ротируйте ключи
4. Ограничьте права доступа приложения

### Мониторинг использования

1. Регулярно проверяйте статистику использования API
2. Настройте уведомления о превышении лимитов
3. Мониторьте логи на предмет подозрительной активности
