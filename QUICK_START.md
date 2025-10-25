# 🚀 RewiRater - Быстрый старт

## 📋 Что это?
AI копирайтер для Telegram, который автоматически переписывает посты из канала -1812865083 в стиле @twitterweb3 и публикует в @twitterweb3.

## ⚡ Быстрый запуск (5 минут)

### Вариант 1: Бесплатные AI (рекомендуется для тестов)
```bash
# Тестирование бесплатных провайдеров
python test_free_ai.py

# Настройка в config.py:
AI_PROVIDER = "groq"  # или "huggingface", "ollama"
```

### Вариант 2: DeepSeek (лучшее качество)
- Перейти: https://platform.deepseek.com/
- Войти в аккаунт
- Пополнить баланс (минимум $1)

### 3. Запустить систему
```bash
python main.py
```

### 4. Готово!
Система автоматически:
- Мониторит канал @dubaieth
- Переписывает посты с AI
- Добавляет Premium эмодзи
- Публикует в @twitterweb3 **одним сообщением**

## 🔧 Настройки (уже готовы)

### API ключи:
- **Telegram**: 21601645, 6bc7e9ceae3ed7d5694ac49d6d67cedc
- **DeepSeek**: sk-1753963687804d249cbb9d6ae1c03b46

### Каналы:
- **Источник**: @dubaieth
- **Цель**: @twitterweb3

### Premium эмодзи:
👋🌈😏😔🧐🤩👍😠😂🥴

## 🧪 Тесты
```bash
python test_config_simple.py  # Проверка настроек
python test_free_ai.py        # Тест бесплатных AI
python final_test.py          # Полный тест
```

## 📁 Основные файлы
- `main.py` - запуск системы
- `config.py` - настройки
- `PROJECT_STATUS.md` - полная документация

## ❓ Проблемы?
- **"Insufficient Balance"** → пополнить DeepSeek или использовать бесплатные AI
- **"Authorization required"** → войти в Telegram при первом запуске
- **"Channel not found"** → проверить права доступа
- **"API key invalid"** → проверить ключи в config.py

## 🎯 Результат
После запуска система работает 24/7, переписывая посты в вашем стиле с Premium эмодзи!

---
**Создано**: 14.10.2025  
**Статус**: Готов к запуску (нужен только баланс DeepSeek)
