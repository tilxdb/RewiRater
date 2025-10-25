# 🐦 Twitter модули RewiRater

Эта папка содержит все компоненты для работы с Twitter.

## 📁 Структура

```
twitter/
├── README.md                    # Этот файл
├── twitter_bot_standalone.py    # Отдельный Twitter бот
├── twitter_monitor_standalone.py # Альтернативный Twitter монитор
├── run_twitter_only.py         # Скрипт запуска только Twitter
├── twitter_monitor.py          # Основной Twitter монитор
├── twitter_adapter.py          # Адаптер для конвертации твитов
└── twitter_setup.md            # Инструкция по настройке Twitter API
```

## 🚀 Запуск

### Основной Twitter бот
```bash
python twitter_bot_standalone.py
```

### Альтернативный монитор
```bash
python twitter_monitor_standalone.py
```

### Только Twitter (из корня проекта)
```bash
python run_twitter_only.py
```

## ⚙️ Настройка

1. Получите Twitter API ключи (см. `twitter_setup.md`)
2. Добавьте ключи в `config.py`
3. Настройте список аккаунтов в `TWITTER_ACCOUNTS`
4. Запустите бота

## 🔧 Компоненты

- **twitter_bot_standalone.py** - полноценный Twitter бот с публикацией в Telegram
- **twitter_monitor.py** - мониторинг Twitter аккаунтов
- **twitter_adapter.py** - конвертация твитов в формат SourcePost
- **twitter_setup.md** - подробная инструкция по настройке API

## 📊 Особенности

- Мониторинг 16+ Twitter аккаунтов
- AI переписывание твитов
- Публикация в Telegram канал
- Обработка rate limits
- Фильтрация релевантного контента

## 🔗 Связь с основным ботом

Twitter бот работает независимо от основного Telegram бота и публикует переписанные твиты в тот же целевой канал.
