#!/bin/bash
#cloud-config
# Автоматический скрипт развертывания RewiRater с GitHub на Timeweb Cloud

echo "🚀 Развертывание RewiRater с GitHub на Timeweb Cloud..."

# Проверка подключения к интернету
echo "🌐 Проверка подключения к интернету..."
if ! ping -c 1 google.com &> /dev/null; then
    echo "❌ Нет подключения к интернету!"
    exit 1
fi

# Обновление системы
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
echo "🔧 Установка зависимостей..."
sudo apt install git python3 python3-pip python3-venv htop curl -y

# Создание директории проекта
echo "📁 Создание директории проекта..."
mkdir -p /home/ubuntu/rewirater
cd /home/ubuntu/rewirater

# Клонирование репозитория (замените на ваш репозиторий)
echo "📥 Клонирование репозитория..."
echo "Введите URL вашего GitHub репозитория:"
read -p "GitHub URL: " GITHUB_URL

if [ -z "$GITHUB_URL" ]; then
    echo "❌ URL репозитория не указан!"
    exit 1
fi

git clone $GITHUB_URL .
if [ $? -ne 0 ]; then
    echo "❌ Ошибка клонирования репозитория!"
    exit 1
fi

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

# Создание config.py (пользователь должен заполнить)
echo "⚙️ Создание config.py..."
if [ ! -f config.py ]; then
    echo "Создаю config.py из примера..."
    cp config_example.py config.py
    echo "⚠️  ВАЖНО: Отредактируйте config.py и добавьте ваши API ключи!"
    echo "nano config.py"
else
    echo "✅ config.py уже существует"
fi

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
chmod 600 config.py 2>/dev/null || echo "config.py не найден, создайте его"
chmod 644 main.py
chmod 755 ai/ bot/ utils/ twitter/ 2>/dev/null || echo "Некоторые папки не найдены"

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

# Создание скрипта обновления
echo "🔄 Создание скрипта обновления..."
tee update.sh > /dev/null <<EOF
#!/bin/bash
echo "🔄 Обновление RewiRater..."
cd /home/ubuntu/rewirater
git pull origin main
source rewirater_env/bin/activate
pip install -r requirements.txt
sudo systemctl restart rewirater
echo "✅ Обновление завершено!"
EOF

chmod +x update.sh

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
echo "✅ Бэкап создан: rewirater_\$DATE.tar.gz"
EOF

chmod +x backup.sh

# Настройка файрвола
echo "🛡️ Настройка файрвола..."
sudo ufw allow ssh
sudo ufw --force enable

# Создание cron задач
echo "⏰ Настройка автоматических задач..."
(crontab -l 2>/dev/null; echo "0 3 * * * /home/ubuntu/rewirater/update.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/rewirater/backup.sh") | crontab -

echo "✅ Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте config.py: nano config.py"
echo "2. Добавьте ваши API ключи в config.py"
echo "3. Запустите бота: sudo systemctl start rewirater"
echo "4. Проверьте статус: sudo systemctl status rewirater"
echo "5. Просмотрите логи: sudo journalctl -u rewirater -f"
echo ""
echo "🔄 Для обновления: ./update.sh"
echo "💾 Для бэкапа: ./backup.sh"
echo ""
echo "🎉 RewiRater готов к работе на Timeweb Cloud!"
