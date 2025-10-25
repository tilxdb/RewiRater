# Развертывание RewiRater с GitHub на Timeweb Cloud

## 🚀 Автоматическое развертывание через GitHub

### 1. Подготовка GitHub репозитория

**Создайте репозиторий на GitHub:**
```bash
# Инициализация Git (если еще не сделано)
git init
git add .
git commit -m "Initial commit"

# Создание репозитория на GitHub
# Перейдите на github.com -> New Repository
# Название: rewirater
# Описание: AI Telegram Bot for Content Rewriting
# Публичный или приватный (рекомендуется приватный)

# Подключение к GitHub
git remote add origin https://github.com/ваш-username/rewirater.git
git branch -M main
git push -u origin main
```

### 2. Настройка сервера Timeweb

**Подключение к серверу:**
```bash
ssh root@ваш-ip-адрес
```

**Установка Git и зависимостей:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install git python3 python3-pip python3-venv htop -y
```

### 3. Клонирование репозитория

**Клонирование проекта:**
```bash
# Переход в домашнюю директорию
cd /home/ubuntu

# Клонирование репозитория
git clone https://github.com/ваш-username/rewirater.git
cd rewirater

# Проверка файлов
ls -la
```

### 4. Настройка конфигурации

**Создание config.py на сервере:**
```bash
# Создание конфигурации
nano config.py
```

**Содержимое config.py (с вашими API ключами):**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from typing import Optional, List

class Config:
    # Telegram API данные
    API_ID: Optional[int] = ВАШ_API_ID
    API_HASH: Optional[str] = 'ВАШ_API_HASH'
    SESSION_NAME: str = "rewirater_bot_v3"
    
    # Каналы для мониторинга
    SOURCE_CHANNELS: List[str] = [
        "@dubaieth",
        "@tonlive",
        "@tonraffles_ru", 
        "@MyTonWalletRu",
        "@tonkeeper_ru",
        "@durov",
        "@ston_fi_ru",
        "@dedust_ru",
        "@x1000News",
        "@tginfo",
        "@tonmonitoring",
        "@kokoronoki_group",
        "@upscale_news_ru",
        "@xrocketnewsru",
        "@CryptoBotRU"
    ]
    
    # Канал для публикации
    TARGET_CHANNEL: str = "@ваш-канал"
    
    # AI настройки
    AI_PROVIDER: str = "openai"
    AI_API_KEY: Optional[str] = "ВАШ_OPENAI_API_KEY"
    AI_MODEL: str = "gpt-4o-mini"
    
    # Настройки публикации
    PROCESSING_DELAY_MINUTES: int = 5
    PUBLISH_INTERVAL_MIN: int = 20
    PUBLISH_INTERVAL_MAX: int = 30
    MAX_POSTS_PER_DAY: int = 24
    MIN_POST_LENGTH: int = 10
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "rewirater.log"
```

### 5. Установка зависимостей

**Создание виртуального окружения:**
```bash
# Создание виртуального окружения
python3 -m venv rewirater_env
source rewirater_env/bin/activate

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Первый запуск

**Запуск бота для создания сессии:**
```bash
# Активация виртуального окружения
source rewirater_env/bin/activate

# Запуск бота
python3 main.py
```

**При первом запуске:**
- Введите номер телефона
- Введите код подтверждения из Telegram
- Сессия сохранится автоматически

### 7. Настройка автозапуска

**Создание systemd сервиса:**
```bash
sudo nano /etc/systemd/system/rewirater.service
```

**Содержимое сервиса:**
```ini
[Unit]
Description=RewiRater Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/rewirater
Environment=PATH=/home/ubuntu/rewirater/rewirater_env/bin
ExecStart=/home/ubuntu/rewirater/rewirater_env/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Активация сервиса:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable rewirater
sudo systemctl start rewirater
sudo systemctl status rewirater
```

### 8. Автоматическое обновление

**Создание скрипта обновления:**
```bash
nano update.sh
```

**Содержимое update.sh:**
```bash
#!/bin/bash
cd /home/ubuntu/rewirater
git pull origin main
source rewirater_env/bin/activate
pip install -r requirements.txt
sudo systemctl restart rewirater
echo "Обновление завершено!"
```

**Сделать скрипт исполняемым:**
```bash
chmod +x update.sh
```

### 9. Настройка автоматических обновлений

**Создание cron задачи:**
```bash
# Редактирование crontab
crontab -e

# Добавление строки для ежедневного обновления в 3:00
0 3 * * * /home/ubuntu/rewirater/update.sh
```

### 10. Мониторинг и управление

**Проверка статуса:**
```bash
sudo systemctl status rewirater
```

**Просмотр логов:**
```bash
sudo journalctl -u rewirater -f
```

**Управление ботом:**
```bash
# Запуск
sudo systemctl start rewirater

# Остановка
sudo systemctl stop rewirater

# Перезапуск
sudo systemctl restart rewirater
```

### 11. Обновление кода

**Когда нужно обновить бота:**
```bash
# На сервере
cd /home/ubuntu/rewirater
./update.sh
```

**Или вручную:**
```bash
cd /home/ubuntu/rewirater
git pull origin main
source rewirater_env/bin/activate
pip install -r requirements.txt
sudo systemctl restart rewirater
```

## 🔄 Workflow разработки

### 1. Локальная разработка
```bash
# Внесите изменения в код
# Протестируйте локально
python main.py
```

### 2. Коммит изменений
```bash
git add .
git commit -m "Описание изменений"
git push origin main
```

### 3. Автоматическое обновление на сервере
```bash
# На сервере (автоматически через cron)
./update.sh
```

## 🛡️ Безопасность

### Защита API ключей
```bash
# Убедитесь что config.py не в Git
echo "config.py" >> .gitignore

# Проверьте что config.py не загружен
git status
```

### Права доступа
```bash
chmod 600 config.py
chmod 644 main.py
chmod 755 ai/ bot/ utils/
```

## 📊 Преимущества GitHub развертывания

✅ **Автоматические обновления** - код обновляется автоматически
✅ **Версионность** - можно откатиться к предыдущей версии
✅ **Безопасность** - API ключи не попадают в репозиторий
✅ **Простота** - один раз настроил, работает всегда
✅ **Мониторинг** - видно все изменения в коде
✅ **Резервное копирование** - код всегда сохранен в GitHub

## 🚀 Готово!

Теперь ваш бот:
- Автоматически обновляется с GitHub
- Работает 24/7 на сервере
- Перезапускается при сбоях
- Логирует все действия
- Безопасно хранит API ключи

**Удачного развертывания! 🎉**
