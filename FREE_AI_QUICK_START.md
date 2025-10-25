# 🆓 Быстрый старт с бесплатными AI

## 🚀 За 3 минуты до работающего бота

### 1. **Groq** (Самый быстрый) ⭐
```bash
# 1. Регистрация: https://console.groq.com/
# 2. Получить API ключ: gsk_...

# 3. В config.py изменить:
AI_PROVIDER = "groq"
GROQ_API_KEY = "gsk_your_key_here"

# 4. Запустить:
python main.py
```

### 2. **Hugging Face** (Больше запросов)
```bash
# 1. Регистрация: https://huggingface.co/
# 2. Получить токен: hf_...

# 3. В config.py изменить:
AI_PROVIDER = "huggingface"
HUGGINGFACE_API_KEY = "hf_your_token_here"

# 4. Запустить:
python main.py
```

### 3. **Ollama** (Локально)
```bash
# 1. Установка: https://ollama.ai/
# 2. Скачать модель:
ollama pull llama3.1:8b

# 3. В config.py изменить:
AI_PROVIDER = "ollama"

# 4. Запустить:
python main.py
```

## 🧪 Тестирование всех провайдеров
```bash
python test_free_ai.py
```

## 📊 Сравнение

| Провайдер | Бесплатно | Скорость | Настройка |
|-----------|-----------|----------|-----------|
| **Groq** | 14,400/день | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Hugging Face** | 30,000/месяц | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Ollama** | Полностью | ⭐⭐ | ⭐⭐⭐ |

## 🎯 Рекомендация
**Начните с Groq** - самый быстрый и простой в настройке!

---
**Время настройки**: 3 минуты  
**Стоимость**: 0₽  
**Результат**: Работающий AI копирайтер
