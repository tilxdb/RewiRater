# 🚀 Руководство по развертыванию RewiRater

## 📋 Предварительные требования

### Системные требования
- Python 3.8+
- 2GB RAM минимум
- 1GB свободного места
- Стабильное интернет-соединение

### API ключи
- Telegram API (API_ID, API_HASH)
- OpenAI API ключ
- Twitter API ключи (опционально)

## 🖥️ Локальное развертывание

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/rewirater.git
cd rewirater
```

### 2. Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка конфигурации

```bash
# Копирование примера конфигурации
cp config_example.py config.py

# Редактирование конфигурации
# Добавьте ваши API ключи в config.py
```

### 4. Первый запуск

```bash
# Запуск основного бота
python main.py

# При первом запуске потребуется авторизация в Telegram
# Введите номер телефона и код из SMS
```

## ☁️ Развертывание на VPS

### Рекомендуемые провайдеры
- **Hetzner** - от €3.29/месяц
- **DigitalOcean** - от $4/месяц  
- **Vultr** - от $2.50/месяц
- **Timeweb** - от 200₽/месяц
- **Yandex Cloud** - от 500₽/месяц

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv git -y

# Создание пользователя для бота
sudo adduser rewirater
sudo usermod -aG sudo rewirater
su - rewirater
```

### 2. Установка приложения

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/rewirater.git
cd rewirater

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 3. Настройка systemd сервиса

Создайте файл `/etc/systemd/system/rewirater.service`:

```ini
[Unit]
Description=RewiRater Telegram Bot
After=network.target

[Service]
Type=simple
User=rewirater
WorkingDirectory=/home/rewirater/rewirater
Environment=PATH=/home/rewirater/rewirater/venv/bin
ExecStart=/home/rewirater/rewirater/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Запуск сервиса

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable rewirater

# Запуск сервиса
sudo systemctl start rewirater

# Проверка статуса
sudo systemctl status rewirater

# Просмотр логов
sudo journalctl -u rewirater -f
```

## 🐳 Развертывание с Docker

### 1. Создание Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Создание пользователя
RUN useradd -m -u 1000 rewirater && chown -R rewirater:rewirater /app
USER rewirater

# Запуск приложения
CMD ["python", "main.py"]
```

### 2. Создание docker-compose.yml

```yaml
version: '3.8'

services:
  rewirater:
    build: .
    container_name: rewirater-bot
    restart: unless-stopped
    environment:
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
      - AI_API_KEY=${AI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - rewirater-network

networks:
  rewirater-network:
    driver: bridge
```

### 3. Запуск с Docker

```bash
# Создание .env файла с переменными окружения
echo "TELEGRAM_API_ID=your_api_id" > .env
echo "TELEGRAM_API_HASH=your_api_hash" >> .env
echo "AI_API_KEY=your_openai_key" >> .env

# Запуск контейнера
docker-compose up -d

# Просмотр логов
docker-compose logs -f
```

## 🔄 Автоматическое обновление

### 1. Скрипт обновления

Создайте файл `update.sh`:

```bash
#!/bin/bash
cd /home/rewirater/rewirater
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rewirater
echo "RewiRater обновлен!"
```

### 2. Настройка cron

```bash
# Добавление в crontab для ежедневного обновления
crontab -e

# Добавить строку:
0 2 * * * /home/rewirater/rewirater/update.sh
```

## 📊 Мониторинг

### 1. Логирование

```bash
# Просмотр логов systemd
sudo journalctl -u rewirater -f

# Просмотр файловых логов
tail -f logs/rewirater.log
```

### 2. Мониторинг ресурсов

```bash
# Использование CPU и памяти
htop

# Использование диска
df -h

# Сетевые соединения
netstat -tulpn
```

### 3. Настройка алертов

Создайте скрипт `health_check.sh`:

```bash
#!/bin/bash
if ! systemctl is-active --quiet rewirater; then
    echo "RewiRater не работает!" | mail -s "Alert" admin@example.com
    sudo systemctl restart rewirater
fi
```

## 🔒 Безопасность

### 1. Firewall

```bash
# Настройка UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow out 443  # HTTPS
sudo ufw allow out 80   # HTTP
```

### 2. Обновления безопасности

```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. Резервное копирование

```bash
# Создание бэкапа конфигурации
tar -czf backup-$(date +%Y%m%d).tar.gz config.py data/ logs/
```

## 🚨 Устранение неполадок

### Частые проблемы

1. **"database is locked"**
   ```bash
   # Остановка всех процессов Python
   pkill -f python
   # Удаление файлов сессий
   rm *.session*
   ```

2. **"EOF when reading a line"**
   ```bash
   # Запуск в интерактивном режиме
   python main.py
   # Введите номер телефона и код
   ```

3. **"Rate limit exceeded"**
   ```bash
   # Ожидание снятия лимита
   # Или настройка более длинных интервалов
   ```

### Полезные команды

```bash
# Проверка статуса сервиса
sudo systemctl status rewirater

# Перезапуск сервиса
sudo systemctl restart rewirater

# Просмотр логов
sudo journalctl -u rewirater --since "1 hour ago"

# Проверка использования ресурсов
ps aux | grep python
```

## 📈 Масштабирование

### Горизонтальное масштабирование

1. **Несколько экземпляров Telegram бота**
   - Разные каналы для каждого экземпляра
   - Разные API ключи

2. **Отдельные серверы для Twitter**
   - Выделенный сервер для Twitter мониторинга
   - Общая база данных для координации

### Вертикальное масштабирование

1. **Увеличение ресурсов сервера**
   - Больше RAM для обработки
   - SSD для быстрого доступа к данным

2. **Оптимизация кода**
   - Асинхронная обработка
   - Кэширование результатов

---

**Успешного развертывания! 🚀**
