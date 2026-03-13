# RewiRater - AI Content Rewriter Bot

🤖 **RewiRater** - это автоматизированный Telegram бот, который мониторит каналы и Twitter аккаунты, переписывает контент в заданном стиле и публикует его в целевой канал.

## ✨ Возможности

- 📱 **Мониторинг Telegram каналов** - отслеживание 11+ каналов в реальном времени
- 🐦 **Мониторинг Twitter аккаунтов** - отслеживание 16+ ключевых аккаунтов
- 🤖 **AI переписывание** - использование OpenAI GPT для стилизации контента
- ⏰ **Умная публикация** - автоматическое планирование постов с интервалом 20-30 минут
- 📊 **Статистика** - отслеживание производительности и метрик
- 🎯 **Гибкая настройка** - настройка стиля, длины постов и источников

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/rewirater.git
cd rewirater
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка конфигурации

```bash
# Скопируйте пример конфигурации
cp config_example.py config.py

# Отредактируйте config.py и добавьте свои API ключи
```

### 4. Получение API ключей

#### Telegram API
1. Перейдите на [my.telegram.org](https://my.telegram.org)
2. Войдите в свой аккаунт
3. Создайте новое приложение
4. Получите `API ID` и `API Hash`

#### OpenAI API
1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Создайте аккаунт и получите API ключ
3. Добавьте ключ в `config.py`

#### Twitter API
1. Перейдите на [developer.twitter.com](https://developer.twitter.com)
2. Создайте Developer Account
3. Создайте приложение и получите ключи
4. Подробная инструкция в [docs/twitter_setup.md](docs/twitter_setup.md)

### 5. Запуск бота

#### Основной запуск (только Telegram)
```bash
python main.py
```

#### Отдельный Twitter бот
```bash
python twitter/twitter_bot_standalone.py
```

#### Альтернативные способы
```bash
# Только Telegram
python run_telegram_only.py

# Только Twitter  
python run_twitter_only.py

# Параллельный запуск
python run_both_monitors.py
```

## 📁 Структура проекта

```
rewirater/
├── ai/                     # AI модули
│   ├── content_rewriter.py # Основной модуль переписывания
│   └── content_generator.py
├── bot/                    # Telegram бот
│   ├── telegram_bot.py     # Основной бот
│   └── channel_monitor.py # Мониторинг каналов
├── twitter/                # Twitter модули
│   ├── twitter_bot_standalone.py    # Отдельный Twitter бот
│   ├── twitter_monitor.py          # Twitter мониторинг
│   ├── twitter_adapter.py          # Адаптер Twitter постов
│   └── twitter_setup.md            # Настройка Twitter API
├── docs/                   # Документация
│   ├── twitter_setup.md    # Настройка Twitter API
│   └── deepseek_setup.md
├── examples/               # Примеры использования
├── tools/                  # Вспомогательные инструменты
├── utils/                  # Утилиты
├── config.py              # Конфигурация (НЕ в git!)
├── config_example.py      # Пример конфигурации
├── main.py                # Точка входа (Telegram бот)
├── twitter_bot_standalone.py  # Отдельный Twitter бот
├── run_telegram_only.py   # Запуск только Telegram
├── run_twitter_only.py    # Запуск только Twitter
├── run_both_monitors.py   # Параллельный запуск
└── requirements.txt       # Зависимости
```

## ⚙️ Конфигурация

### Основные настройки

```python
# Telegram API
API_ID = 12345678
API_HASH = "your_api_hash"
TARGET_CHANNEL = "@your_channel"

# AI настройки
AI_PROVIDER = "openai"
AI_API_KEY = "your_openai_key"
AI_MODEL = "gpt-4o-mini"

# Twitter API
TWITTER_API_KEY = "your_twitter_key"
TWITTER_BEARER_TOKEN = "your_bearer_token"
```

### Настройка источников

```python
# Telegram каналы для мониторинга
SOURCE_CHANNELS = [
    "@dubaieth",
    "@tonlive",
    # ... другие каналы
]

# Twitter аккаунты для мониторинга
TWITTER_ACCOUNTS = [
    "justinsuntron",
    "coinbase",
    "ethereum",
    # ... другие аккаунты
]
```

## 🎨 Настройка стиля

Бот переписывает контент в профессиональном стиле с:
- Жирными заголовками
- Краткими абзацами (1-3 предложения)
- Подписью @ton_boom
- Без эмодзи и лишних элементов

## 📊 Мониторинг и статистика

Бот предоставляет статистику по:
- Количеству обработанных постов
- Источникам контента
- Производительности AI
- Очереди публикаций

## 🔒 Безопасность

⚠️ **ВАЖНО**: Никогда не публикуйте файл `config.py` в открытом доступе!

- Все API ключи должны быть в `config.py`
- Файл `config.py` добавлен в `.gitignore`
- Используйте `config_example.py` как шаблон
- Регулярно ротируйте API ключи

## 🛠️ Разработка

### Добавление новых источников

1. Добавьте канал/аккаунт в соответствующий список в `config.py`
2. Перезапустите бота

### Изменение стиля переписывания

Отредактируйте промпты в `ai/content_rewriter.py`:

```python
def _build_rewriting_prompt(self, source_post: SourcePost) -> str:
    prompt = f"""
    ТЫ ДОЛЖЕН ПОЛНОСТЬЮ ПЕРЕПИСАТЬ этот пост в стиле автора @marxstud.
    # ... ваш стиль
    """
    return prompt
```

## 📝 Логирование

Бот ведет подробные логи:
- Успешные операции
- Ошибки и предупреждения
- Статистика работы
- API запросы

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

## 🆘 Поддержка

Если у вас возникли проблемы:

1. Проверьте [Issues](https://github.com/yourusername/rewirater/issues)
2. Создайте новый Issue с описанием проблемы
3. Приложите логи (без API ключей!)

## 🔄 Обновления

Для обновления бота:

```bash
git pull origin main
pip install -r requirements.txt
```

## 📈 Roadmap

- [ ] Поддержка других AI провайдеров
- [ ] Веб-интерфейс для управления
- [ ] Расширенная аналитика
- [ ] Поддержка других социальных сетей
- [ ] A/B тестирование стилей

---

**Создано с ❤️ для автоматизации контент-маркетинга**