# Развертывание RewiRater на Timeweb Cloud

## 🚀 Подготовка к развертыванию

### 1. Подготовка файлов

**Обязательные файлы для загрузки:**
- `main.py` - основной файл бота
- `config.py` - конфигурация (с вашими API ключами)
- `requirements.txt` - зависимости Python
- `ai/` - папка с AI модулями
- `bot/` - папка с Telegram ботом
- `utils/` - папка с утилитами
- `twitter/` - папка с Twitter ботом (опционально)

**НЕ загружайте:**
- `*.session` - файлы сессий (создадутся на сервере)
- `logs/` - папка с логами
- `data/` - папка с данными
- `__pycache__/` - кэш Python

### 2. Настройка сервера

**Минимальные требования:**
- Python 3.8+
- 1GB RAM
- 10GB диска
- Ubuntu 20.04+ или CentOS 8+

**Рекомендуемые характеристики:**
- 2GB RAM
- 20GB SSD
- Ubuntu 22.04 LTS

### 3. Установка зависимостей

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Создание виртуального окружения
python3 -m venv rewirater_env
source rewirater_env/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 4. Настройка конфигурации

**Создайте config.py на сервере:**
```python
# Скопируйте ваш config.py на сервер
# Убедитесь что все API ключи указаны правильно
```

### 5. Запуск бота

**Первый запуск (создание сессии):**
```bash
# Активируйте виртуальное окружение
source rewirater_env/bin/activate

# Запустите бота
python3 main.py
```

**Последующие запуски:**
```bash
# Обычный запуск
python3 main.py
```

### 6. Настройка автозапуска

**Создайте systemd сервис:**

```bash
sudo nano /etc/systemd/system/rewirater.service
```

**Содержимое файла:**
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

### 7. Мониторинг и логи

**Просмотр логов:**
```bash
# Логи сервиса
sudo journalctl -u rewirater -f

# Логи приложения
tail -f rewirater.log
```

**Перезапуск бота:**
```bash
sudo systemctl restart rewirater
```

**Остановка бота:**
```bash
sudo systemctl stop rewirater
```

### 8. Безопасность

**Настройка файрвола:**
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

**Права доступа:**
```bash
chmod 600 config.py
chmod 644 main.py
chmod 755 ai/ bot/ utils/
```

### 9. Резервное копирование

**Автоматический бэкап:**
```bash
# Создайте скрипт бэкапа
nano backup.sh
```

**Содержимое backup.sh:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /home/ubuntu/backups/rewirater_$DATE.tar.gz \
    --exclude='*.session' \
    --exclude='logs/' \
    --exclude='data/' \
    /home/ubuntu/rewirater/
```

### 10. Мониторинг ресурсов

**Установка htop:**
```bash
sudo apt install htop -y
htop
```

**Проверка места на диске:**
```bash
df -h
du -sh /home/ubuntu/rewirater/
```

## 🔧 Troubleshooting

### Проблема: Бот не запускается
```bash
# Проверьте логи
sudo journalctl -u rewirater -n 50

# Проверьте права доступа
ls -la /home/ubuntu/rewirater/

# Проверьте Python
python3 --version
```

### Проблема: Ошибки API
```bash
# Проверьте config.py
cat config.py | grep API

# Проверьте интернет
ping google.com
```

### Проблема: Сессия заблокирована
```bash
# Удалите старые сессии
rm -f *.session *.session-journal

# Перезапустите бота
sudo systemctl restart rewirater
```

## 📊 Мониторинг производительности

**Проверка статуса:**
```bash
sudo systemctl status rewirater
ps aux | grep python
```

**Проверка логов:**
```bash
tail -f rewirater.log | grep ERROR
tail -f rewirater.log | grep "Опубликован пост"
```

## 🚀 Готово!

После выполнения всех шагов ваш бот будет:
- ✅ Автоматически запускаться при перезагрузке сервера
- ✅ Перезапускаться при сбоях
- ✅ Логировать все действия
- ✅ Работать 24/7

**Удачного развертывания! 🎉**
