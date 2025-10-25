# 🔐 Руководство по управлению сессиями

## 📁 Структура файлов сессий

```
sessions/
├── emoji_bot_minimal.session      # Основная сессия бота
├── emoji_bot_minimal.info.json    # Информация о сессии
├── debug_emoji_bot.session        # Отладочная сессия
└── debug_emoji_bot.info.json      # Информация об отладке
```

## 🚀 Быстрый старт

### **1. Первый запуск (авторизация)**
```bash
python tools/emoji_bot_minimal.py
```
- При первом запуске потребуется авторизация
- Введите номер телефона
- Введите код подтверждения
- Сессия автоматически сохранится

### **2. Последующие запуски**
```bash
python tools/emoji_bot_minimal.py
```
- Авторизация больше не требуется
- Бот сразу подключается к аккаунту

## 🛠️ Менеджер сессий

### **Запуск менеджера:**
```bash
python tools/session_manager.py
```

### **Возможности менеджера:**
- ✅ Создание новых сессий
- 🔍 Проверка существующих сессий
- 📋 Список всех сессий
- 🗑️ Удаление сессий
- 📋 Копирование сессий

## 📋 Команды менеджера

```
1. Создать новую сессию    - Создать новую авторизованную сессию
2. Проверить сессию        - Проверить работоспособность сессии
3. Список сессий          - Показать все доступные сессии
4. Удалить сессию         - Удалить ненужную сессию
5. Копировать сессию      - Создать копию существующей сессии
0. Выход                  - Закрыть менеджер
```

## 🔧 Ручное управление сессиями

### **Создание папки sessions:**
```bash
mkdir sessions
```

### **Проверка сессии:**
```python
from telethon import TelegramClient

client = TelegramClient('sessions/my_session', api_id, api_hash)
await client.start()

if await client.is_user_authorized():
    me = await client.get_me()
    print(f"Авторизован как: {me.first_name}")
else:
    print("Не авторизован")

await client.disconnect()
```

## ⚠️ Важные моменты

### **Безопасность:**
- ❌ **НЕ делитесь** файлами .session
- ❌ **НЕ добавляйте** .session файлы в git
- ✅ **Делайте бэкапы** важных сессий

### **Файлы для игнорирования (.gitignore):**
```
sessions/
*.session
*.session-journal
```

### **Бэкап сессий:**
```bash
# Создать архив сессий
tar -czf sessions_backup.tar.gz sessions/

# Восстановить сессии
tar -xzf sessions_backup.tar.gz
```

## 🐛 Решение проблем

### **Проблема: "Пользователь не авторизован"**
**Решение:**
1. Удалите файл сессии: `rm sessions/emoji_bot_minimal.session`
2. Запустите бота заново
3. Пройдите авторизацию

### **Проблема: "Сессия не найдена"**
**Решение:**
1. Проверьте существование папки `sessions/`
2. Создайте папку: `mkdir sessions`
3. Запустите бота

### **Проблема: "Ошибка подключения"**
**Решение:**
1. Проверьте интернет соединение
2. Проверьте правильность API_ID и API_HASH
3. Попробуйте создать новую сессию

## 📱 Множественные сессии

### **Для разных аккаунтов:**
```python
# Аккаунт 1
client1 = TelegramClient('sessions/account1', api_id, api_hash)

# Аккаунт 2  
client2 = TelegramClient('sessions/account2', api_id, api_hash)
```

### **Для разных ботов:**
```python
# Бот для эмодзи
emoji_bot = TelegramClient('sessions/emoji_bot', api_id, api_hash)

# Основной бот
main_bot = TelegramClient('sessions/main_bot', api_id, api_hash)
```

## 🔄 Миграция сессий

### **Копирование сессии:**
```bash
cp sessions/old_session.session sessions/new_session.session
```

### **Переименование сессии:**
```bash
mv sessions/old_name.session sessions/new_name.session
```

## 📊 Мониторинг сессий

### **Проверка активности:**
```python
import asyncio
from telethon import TelegramClient

async def check_session_health():
    client = TelegramClient('sessions/emoji_bot_minimal', api_id, api_hash)
    
    try:
        await client.start()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Сессия активна: {me.first_name}")
            
            # Проверяем последнюю активность
            dialogs = await client.get_dialogs(limit=1)
            print(f"📱 Последний диалог: {dialogs[0].name if dialogs else 'Нет'}")
            
        else:
            print("❌ Сессия недействительна")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await client.disconnect()

# Запуск проверки
asyncio.run(check_session_health())
```

## 🎯 Рекомендации

1. **Регулярно делайте бэкапы** сессий
2. **Используйте менеджер сессий** для управления
3. **Не храните сессии** в публичных репозиториях
4. **Проверяйте работоспособность** сессий перед использованием
5. **Используйте разные сессии** для разных целей
