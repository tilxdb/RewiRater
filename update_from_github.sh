#!/bin/bash
# Скрипт для обновления RewiRater на сервере из GitHub

echo "🔄 Начинаем обновление RewiRater из GitHub..."

# Определяем директорию проекта (попробуем найти автоматически)
if [ -d "/home/ubuntu/rewirater" ]; then
    PROJECT_DIR="/home/ubuntu/rewirater"
elif [ -d "/root/RewiRater" ]; then
    PROJECT_DIR="/root/RewiRater"
elif [ -d "$HOME/RewiRater" ]; then
    PROJECT_DIR="$HOME/RewiRater"
else
    echo "❌ Не найдена директория проекта. Укажите путь вручную."
    exit 1
fi

echo "📁 Директория проекта: $PROJECT_DIR"
cd "$PROJECT_DIR" || exit 1

# Проверяем наличие git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Устанавливаем..."
    sudo apt update && sudo apt install -y git
fi

# Проверяем, является ли это git репозиторием
if [ ! -d ".git" ]; then
    echo "⚠️  Это не git репозиторий. Клонируем из GitHub..."
    cd ..
    git clone https://github.com/tilxdb/RewiRater.git
    if [ -d "RewiRater" ]; then
        PROJECT_DIR="$(pwd)/RewiRater"
        cd "$PROJECT_DIR"
    else
        echo "❌ Не удалось клонировать репозиторий"
        exit 1
    fi
fi

echo "📥 Получаем последние изменения из GitHub..."
git fetch origin

# Проверяем текущую ветку
CURRENT_BRANCH=$(git branch --show-current)
echo "🌿 Текущая ветка: $CURRENT_BRANCH"

# Показываем какие изменения будут
echo "📊 Изменения для применения:"
git log HEAD..origin/main --oneline || git log HEAD..origin/master --oneline

# Создаём резервную копию перед обновлением
echo "💾 Создаём резервную копию..."
BACKUP_DIR="$PROJECT_DIR/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" \
    --exclude='*.session' \
    --exclude='*.session-journal' \
    --exclude='logs/*' \
    --exclude='data/*.json' \
    --exclude='__pycache__' \
    --exclude='.git' \
    -C "$(dirname $PROJECT_DIR)" "$(basename $PROJECT_DIR)" 2>/dev/null
echo "✅ Резервная копия создана: $BACKUP_FILE"

# Обновляем код
echo "⬇️  Обновляем файлы..."
git pull origin main || git pull origin master

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при обновлении из GitHub"
    exit 1
fi

# Обновляем зависимости Python, если есть venv
if [ -d "rewirater_env" ]; then
    echo "🐍 Обновляем зависимости Python..."
    source rewirater_env/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
elif [ -f "requirements.txt" ]; then
    echo "⚠️  Виртуальное окружение не найдено. Обновляем зависимости глобально..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
fi

# Проверяем наличие systemd сервиса
if systemctl list-units --type=service | grep -q rewirater; then
    echo "🔄 Перезапускаем сервис rewirater..."
    sudo systemctl restart rewirater
    sleep 2
    echo "📊 Статус сервиса:"
    sudo systemctl status rewirater --no-pager -l
else
    echo "ℹ️  Systemd сервис не найден. Бот нужно перезапустить вручную."
fi

echo ""
echo "✅ Обновление завершено!"
echo "📋 Проверьте логи: sudo journalctl -u rewirater -f"
echo "   или: tail -f $PROJECT_DIR/logs/rewirater.log"

