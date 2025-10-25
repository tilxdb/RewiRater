# 🆓 Настройка бесплатных AI провайдеров

## 🚀 Быстрый старт с бесплатными AI

### 1. **Groq** (Рекомендуется) ⭐
**Бесплатно**: 14,400 запросов/день
**Скорость**: Очень быстрая (до 800 токенов/сек)

#### Настройка:
1. Регистрация: https://console.groq.com/
2. Получить API ключ: `gsk_...`
3. В `config.py`:
```python
AI_PROVIDER = "groq"
GROQ_API_KEY = "gsk_your_key_here"
AI_MODEL = "llama-3.1-8b-instant"
```

### 2. **Hugging Face** 
**Бесплатно**: 30,000 запросов/месяц
**Модели**: Llama, Mistral, CodeLlama

#### Настройка:
1. Регистрация: https://huggingface.co/
2. Получить токен: `hf_...`
3. В `config.py`:
```python
AI_PROVIDER = "huggingface"
HUGGINGFACE_API_KEY = "hf_your_token_here"
AI_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
```

### 3. **Ollama** (Локально)
**Бесплатно**: Полностью бесплатно
**Требования**: 8GB+ RAM

#### Настройка:
1. Установка: https://ollama.ai/
2. Скачать модель:
```bash
ollama pull llama3.1:8b
```
3. В `config.py`:
```python
AI_PROVIDER = "ollama"
OLLAMA_BASE_URL = "http://localhost:11434"
AI_MODEL = "llama3.1:8b"
```

## 🔧 Тестирование

### Запуск тестов:
```bash
# Тест Groq
python -c "
from config import Config
config = Config()
config.AI_PROVIDER = 'groq'
config.GROQ_API_KEY = 'your_key'
from ai.content_rewriter import ContentRewriter
rewriter = ContentRewriter(config)
print('Groq настроен!')
"

# Тест Hugging Face
python -c "
from config import Config
config = Config()
config.AI_PROVIDER = 'huggingface'
config.HUGGINGFACE_API_KEY = 'your_token'
from ai.content_rewriter import ContentRewriter
rewriter = ContentRewriter(config)
print('Hugging Face настроен!')
"

# Тест Ollama
python -c "
from config import Config
config = Config()
config.AI_PROVIDER = 'ollama'
from ai.content_rewriter import ContentRewriter
rewriter = ContentRewriter(config)
print('Ollama настроен!')
"
```

## 📊 Сравнение провайдеров

| Провайдер | Бесплатно | Скорость | Качество | Настройка |
|-----------|-----------|----------|----------|-----------|
| **Groq** | 14,400/день | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Hugging Face** | 30,000/месяц | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Ollama** | Полностью | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **DeepSeek** | $1+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🎯 Рекомендации

### Для тестирования:
1. **Groq** - самый быстрый и простой
2. **Hugging Face** - больше запросов в месяц
3. **Ollama** - полная приватность

### Для продакшена:
1. **DeepSeek** - лучшее качество и цена
2. **Groq** - если нужна скорость
3. **OpenAI** - если нужна стабильность

## 🔄 Переключение между провайдерами

В `config.py` просто меняйте:
```python
# Для тестирования
AI_PROVIDER = "groq"

# Для продакшена  
AI_PROVIDER = "deepseek"
```

Система автоматически переключится на новый провайдер!

## 🚨 Важные моменты

1. **Groq**: Ограничение 14,400 запросов/день
2. **Hugging Face**: Может быть медленным при холодном старте
3. **Ollama**: Требует 8GB+ RAM для Llama 3.1
4. **Все провайдеры**: Поддерживают русский язык

## 📝 Примеры использования

### Тест переписывания с Groq:
```python
from config import Config
from ai.content_rewriter import ContentRewriter, SourcePost

config = Config()
config.AI_PROVIDER = "groq"
config.GROQ_API_KEY = "your_key"

rewriter = ContentRewriter(config)

# Тестовый пост
test_post = SourcePost(
    id=1,
    text="Bitcoin достиг нового максимума",
    channel_id=-1001234567890,
    channel_title="Test Channel",
    date="2024-01-01",
    views=1000,
    forwards=50
)

# Переписывание
import asyncio
result = asyncio.run(rewriter.rewrite_post(test_post))
print(result.rewritten_text)
```

---

**Создано**: 14.10.2025  
**Статус**: Готово к использованию  
**Следующий шаг**: Выберите провайдера и настройте API ключ
