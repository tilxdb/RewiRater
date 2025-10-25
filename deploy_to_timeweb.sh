#!/bin/bash
# Скрипт для автоматического развертывания RewiRater на Timeweb Cloud

echo "🚀 Начинаем развертывание RewiRater на Timeweb Cloud..."

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
echo "🔧 Установка зависимостей..."
sudo apt install python3 python3-pip python3-venv git htop -y

# Создание директории проекта
echo "📁 Создание директории проекта..."
mkdir -p /home/ubuntu/rewirater
cd /home/ubuntu/rewirater

# Создание виртуального окружения
echo "🐍 Создание виртуального окружения..."
python3 -m venv rewirater_env
source rewirater_env/bin/activate

# Установка Python зависимостей
echo "📚 Установка Python пакетов..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание директорий для логов и данных
echo "📂 Создание директорий..."
mkdir -p logs data backups

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
chmod 600 config.py
chmod 644 main.py
chmod 755 ai/ bot/ utils/ twitter/

# Создание systemd сервиса
echo "⚙️ Создание systemd сервиса..."
sudo tee /etc/systemd/system/rewirater.service > /dev/null <<EOF
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
EOF

# Перезагрузка systemd и активация сервиса
echo "🔄 Активация сервиса..."
sudo systemctl daemon-reload
sudo systemctl enable rewirater

# Настройка файрвола
echo "🛡️ Настройка файрвола..."
sudo ufw allow ssh
sudo ufw --force enable

# Создание скрипта бэкапа
echo "💾 Создание скрипта бэкапа..."
tee backup.sh > /dev/null <<EOF
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
tar -czf /home/ubuntu/backups/rewirater_\$DATE.tar.gz \\
    --exclude='*.session' \\
    --exclude='logs/' \\
    --exclude='data/' \\
    /home/ubuntu/rewirater/
EOF

chmod +x backup.sh

# Создание cron задачи для бэкапа
echo "⏰ Настройка автоматического бэкапа..."
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/rewirater/backup.sh") | crontab -

echo "✅ Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Запустите бота: sudo systemctl start rewirater"
echo "2. Проверьте статус: sudo systemctl status rewirater"
echo "3. Просмотрите логи: sudo journalctl -u rewirater -f"
echo ""
echo "🎉 RewiRater готов к работе на Timeweb Cloud!"
