# 🚀 Руководство по запуску RewiRater

## 📋 Варианты запуска

### 1. 🎯 **Только Telegram бот** (рекомендуется для начала)
```bash
python run_telegram_only.py
```
- ✅ Мониторит Telegram каналы
- ✅ Переписывает посты через GPT
- ✅ Публикует в целевой канал
- ❌ Twitter отключен

### 2. 📱 **Только Twitter монитор**
```bash
python run_twitter_only.py
```
- ✅ Мониторит Twitter аккаунты
- ✅ Переписывает твиты через GPT
- ❌ Telegram отключен
- ⚠️ Требует настройки Twitter API

### 3. 🔥 **Оба монитора одновременно**
```bash
python run_both_monitors.py
```
- ✅ Telegram + Twitter работают параллельно
- ✅ Независимые процессы
- ⚠️ Требует настройки Twitter API

### 4. 🎯 **Основной запуск (рекомендуется)**
```bash
python main.py
```
- ✅ Только Telegram бот
- ✅ Стабильная работа без конфликтов
- ✅ Мониторинг 11 каналов

## 🛠️ Настройка

### Telegram API
1. Получите `API_ID` и `API_HASH` на [my.telegram.org](https://my.telegram.org)
2. Добавьте в `config.py`:
```python
API_ID = "ваш_api_id"
API_HASH = "ваш_api_hash"
```

### OpenAI API
1. Получите API ключ на [platform.openai.com](https://platform.openai.com)
2. Добавьте в `config.py`:
```python
AI_API_KEY = "sk-proj-..."
```

### Twitter API (опционально)
1. Создайте приложение на [developer.twitter.com](https://developer.twitter.com)
2. Добавьте ключи в `config.py`:
```python
TWITTER_API_KEY = "ваш_api_key"
TWITTER_API_SECRET = "ваш_api_secret"
TWITTER_ACCESS_TOKEN = "ваш_access_token"
TWITTER_ACCESS_TOKEN_SECRET = "ваш_access_token_secret"
TWITTER_BEARER_TOKEN = "ваш_bearer_token"
```

## 📊 Мониторинг

### Логи
- Все действия записываются в логи
- Используйте `tail -f logs/rewirater.log` для мониторинга

### Статистика
- Посты по дням
- Источники контента
- Статистика AI провайдеров

## 🔧 Устранение проблем

### Telegram не работает
1. Проверьте API ключи
2. Убедитесь, что бот авторизован
3. Проверьте доступ к каналам

### Twitter не работает
1. Проверьте Twitter API ключи
2. Убедитесь, что приложение имеет права
3. Проверьте rate limits

### Конфликты между мониторами
1. Используйте `run_telegram_only.py` или `run_twitter_only.py`
2. Или `run_both_monitors.py` для параллельной работы

## 🎯 Рекомендации

1. **Основной запуск**: `python main.py` (рекомендуется)
2. **Только Telegram**: `python run_telegram_only.py` (если нужен только Telegram)
3. **Только Twitter**: `python run_twitter_only.py` (если нужен только Twitter)
4. **Параллельный запуск**: `python run_both_monitors.py` (альтернатива)

## 📞 Поддержка

При проблемах проверьте:
1. Логи в `logs/rewirater.log`
2. Настройки в `config.py`
3. Доступность API ключей
