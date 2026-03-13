# 📘 Полное руководство по управлению RewiRater на сервере

## 🔐 Данные для подключения

**SSH доступ:**
- **Хост:** `80.90.191.109`
- **Логин:** `root`
- **Пароль:** `aDn_UGx+tUtE7j`

**GitHub репозиторий:**
- **URL:** `https://github.com/tilxdb/RewiRater.git`
- **Ветка:** `main`

**Директория проекта на сервере:**
- **Путь:** `/home/ubuntu/rewirater`
- **Screen сессия:** `rewirater`

---

## 📤 Обновление файлов на GitHub (локально)

### PowerShell (Windows)

```powershell
# 1. Перейти в директорию проекта
cd C:\Users\menal\OneDrive\Desktop\RewiRater

# 2. Проверить статус изменений
git status

# 3. Добавить все изменения
git add -A
# Или конкретный файл:
# git add config.py

# 4. Закоммитить изменения
git commit -m "Описание изменений"

# 5. Отправить на GitHub
git push origin main
```

### CMD (Windows)

```cmd
cd C:\Users\menal\OneDrive\Desktop\RewiRater
git status
git add -A
git commit -m "Описание изменений"
git push origin main
```

### Проверка синхронизации

```powershell
# Проверить последние коммиты
git log --oneline -5

# Проверить, всё ли синхронизировано
git status
```

---

## 📥 Обновление файлов на сервере из GitHub

### Вариант 1: Автоматический скрипт (рекомендуется)

#### Шаг 1: Загрузить скрипт на сервер (PowerShell)

```powershell
cd C:\Users\menal\OneDrive\Desktop\RewiRater
scp update_from_github.sh root@80.90.191.109:/root/
```

#### Шаг 2: Подключиться к серверу и запустить скрипт

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

chmod +x /root/update_from_github.sh
/root/update_from_github.sh
```

### Вариант 2: Ручное обновление (если скрипт недоступен)

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

cd /home/ubuntu/rewirater
git fetch origin
git pull origin main

# Обновить зависимости Python (если нужно)
source rewirater_env/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Запуск бота на сервере

### Основной способ: Интерактивный запуск через screen (рекомендуется)

**Этот способ позволяет видеть вывод бота в реальном времени и работает после отключения.**

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

screen -S rewirater
cd /home/ubuntu/rewirater
source rewirater_env/bin/activate
python3 main.py
```

**После запуска бота:**
- Для **отсоединения** от screen (бот продолжит работать): нажмите `Ctrl+A`, затем `D`
- Для **возврата** к сессии: `screen -r rewirater`
- Для **выхода** из бота: внутри screen нажмите `Ctrl+C`, затем выйдите из screen

#### Проверка запуска

```bash
# Проверить активные screen сессии
screen -ls

# Проверить процесс бота
ps aux | grep "python.*main.py" | grep -v grep
```

### Альтернатива: Запуск в detached режиме (фоном)

Если нужно запустить бота сразу в фоне без подключения к сессии:

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

screen -dmS rewirater bash -c "cd /home/ubuntu/rewirater && source rewirater_env/bin/activate && python3 main.py"
```

---

## ⏹️ Остановка бота

### Через screen

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

# Проверить активные сессии
screen -ls

# Остановить сессию rewirater
screen -S rewirater -X quit

# Или остановить процесс напрямую
pkill -f "python.*main.py"
```

---

## 📊 Просмотр логов

### Вариант 1: Логи файла приложения

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

# Просмотр последних строк лога
tail -f /home/ubuntu/rewirater/logs/rewirater.log

# Последние 50 строк
tail -n 50 /home/ubuntu/rewirater/logs/rewirater.log

# Поиск ошибок
grep -i error /home/ubuntu/rewirater/logs/rewirater.log
```

### Вариант 2: Просмотр через screen

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

# Подключиться к сессии (видеть вывод в реальном времени)
screen -r rewirater

# Для выхода: Ctrl+A, затем D
```

### Вариант 3: Systemd логи (если используется systemd)

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

sudo journalctl -u rewirater -f
sudo journalctl -u rewirater -n 50
```

---

## 🔍 Проверка статуса бота

### Проверить, запущен ли бот

```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j

# Проверить процессы
ps aux | grep "python.*main.py" | grep -v grep

# Проверить screen сессии
screen -ls

# Проверить использование ресурсов
htop
# или
top
```

### Проверить файлы проекта

```bash
cd /home/ubuntu/rewirater
ls -la
git status
git log --oneline -5
```

---

## 🔄 Полный цикл обновления (быстрая инструкция)

### 1. Обновить на GitHub (локально)

**PowerShell:**
```powershell
cd C:\Users\menal\OneDrive\Desktop\RewiRater
git add -A
git commit -m "Обновление функционала"
git push origin main
```

### 2. Обновить на сервере

**SSH подключение:**
```bash
ssh root@80.90.191.109
# Пароль: aDn_UGx+tUtE7j
```

**Запуск скрипта обновления:**
```bash
/root/update_from_github.sh
```

**Или вручную:**
```bash
cd /home/ubuntu/rewirater
git pull origin main
source rewirater_env/bin/activate
pip install -r requirements.txt
```

### 3. Перезапустить бота

```bash
# Остановить старую сессию (если есть)
screen -S rewirater -X quit 2>/dev/null
# Или остановить процесс напрямую
pkill -f "python.*main.py"

# Запустить бота (интерактивно)
screen -S rewirater
cd /home/ubuntu/rewirater
source rewirater_env/bin/activate
python3 main.py
# После запуска: Ctrl+A, затем D для отсоединения
```

### 4. Проверить логи

```bash
tail -f /home/ubuntu/rewirater/logs/rewirater.log
```

---

## 🛠️ Полезные команды

### Работа с Git на сервере

```bash
# Проверить статус
cd /home/ubuntu/rewirater
git status

# Посмотреть изменения
git diff

# Посмотреть историю коммитов
git log --oneline -10

# Откатить последние изменения (если что-то пошло не так)
git reset --hard HEAD
git pull origin main
```

### Работа с screen

```bash
# Список всех сессий
screen -ls

# Подключиться к сессии
screen -r rewirater

# Создать новую сессию с именем
screen -S название_сессии

# Убить все сессии
killall screen

# Выход из screen (находясь внутри): Ctrl+A, затем D
```

### Работа с процессами

```bash
# Найти процесс бота
ps aux | grep python

# Остановить процесс по PID
kill <PID>

# Остановить все процессы бота
pkill -f "python.*main.py"

# Остановить принудительно
pkill -9 -f "python.*main.py"
```

### Проверка системы

```bash
# Место на диске
df -h

# Размер директории проекта
du -sh /home/ubuntu/rewirater

# Использование памяти
free -h

# Активные сетевые подключения
netstat -tulpn | grep python
```

---

## ⚠️ Решение проблем

### Бот не запускается

```bash
# Проверить ошибки в логах
tail -n 100 /home/ubuntu/rewirater/logs/rewirater.log

# Проверить Python версию
python3 --version

# Проверить зависимости
cd /home/ubuntu/rewirater
source rewirater_env/bin/activate
pip list

# Переустановить зависимости
pip install -r requirements.txt --force-reinstall
```

### Сессия screen не работает

```bash
# Очистить все screen сессии
killall screen

# Пересоздать сессию
screen -dmS rewirater bash -c "cd /home/ubuntu/rewirater && source rewirater_env/bin/activate && python3 main.py"
```

### Ошибки при обновлении

```bash
# Откатить изменения на сервере
cd /home/ubuntu/rewirater
git reset --hard HEAD
git pull origin main
```

### Проблемы с SSH подключением

**PowerShell:**
```powershell
# Очистить кеш SSH
ssh-keygen -R 80.90.191.109
```

---

## 📝 Шаблоны команд для быстрого копирования

### Подключение к серверу
```bash
ssh root@80.90.191.109
```

### Проверка статуса бота
```bash
screen -ls && ps aux | grep "python.*main.py" | grep -v grep
```

### Быстрый перезапуск
```bash
# Остановить и запустить заново (интерактивно)
screen -S rewirater -X quit 2>/dev/null
screen -S rewirater
cd /home/ubuntu/rewirater
source rewirater_env/bin/activate
python3 main.py
# После запуска: Ctrl+A, затем D
```

### Просмотр логов
```bash
tail -f /home/ubuntu/rewirater/logs/rewirater.log
```

---

## 🔐 Безопасность

⚠️ **Важно:**
- Не коммитьте файл `config.py` в Git (он содержит API ключи)
- Регулярно меняйте пароли SSH
- Используйте SSH ключи вместо пароля (опционально)
- Регулярно создавайте резервные копии

---

**Последнее обновление:** 2025-01-01

