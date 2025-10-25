# 🚀 Инструкция по добавлению проекта на GitHub

## 📋 Подготовка к публикации

### 1. Проверка файлов

Убедитесь, что у вас есть все необходимые файлы:

```
✅ README.md - описание проекта
✅ LICENSE - лицензия MIT
✅ .gitignore - исключения для Git
✅ config_example.py - пример конфигурации
✅ requirements.txt - зависимости
✅ SECURITY.md - политика безопасности
✅ CONTRIBUTING.md - руководство по вкладу
✅ .github/workflows/ci.yml - CI/CD
✅ .github/ISSUE_TEMPLATE/ - шаблоны issues
✅ .github/pull_request_template.md - шаблон PR
```

### 2. Проверка безопасности

**КРИТИЧЕСКИ ВАЖНО!** Убедитесь, что в репозитории НЕТ:

- ❌ `config.py` (содержит API ключи)
- ❌ `*.session` файлов (Telegram сессии)
- ❌ `*.session-journal` файлов
- ❌ `logs/` папки с логами
- ❌ `data/` папки с данными
- ❌ Любых файлов с API ключами

### 3. Проверка .gitignore

Убедитесь, что `.gitignore` содержит:

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python/
env/
venv/
.venv/

# Telegram Session Files (КРИТИЧЕСКИ ВАЖНО!)
*.session
*.session-journal
sessions/

# API Keys and Secrets (КРИТИЧЕСКИ ВАЖНО!)
.env
config.py
config_local.py
secrets.py
api_keys.txt

# Logs
*.log
logs/
data/

# Temporary files
temp/
tmp/
*.tmp

# Database files
*.db
*.sqlite
*.sqlite3

# IDE-specific files
.vscode/
.idea/

# OS generated files
.DS_Store
Thumbs.db
```

## 🔧 Создание репозитория на GitHub

### 1. Создание нового репозитория

1. Перейдите на [github.com](https://github.com)
2. Нажмите "New repository"
3. Заполните данные:
   - **Repository name**: `rewirater`
   - **Description**: `AI-powered Telegram bot for content rewriting and publishing`
   - **Visibility**: Public (или Private, если хотите)
   - **Initialize**: НЕ ставьте галочки (у нас уже есть файлы)

### 2. Инициализация Git

```bash
# В папке проекта
git init
git add .
git commit -m "Initial commit: RewiRater AI Content Rewriter Bot"
```

### 3. Подключение к GitHub

```bash
# Замените YOUR_USERNAME на ваш GitHub username
git remote add origin https://github.com/YOUR_USERNAME/rewirater.git
git branch -M main
git push -u origin main
```

## 📝 Настройка репозитория

### 1. Описание репозитория

Добавьте в описание репозитория:
```
🤖 AI-powered Telegram bot for automated content rewriting and publishing. Monitors channels, rewrites posts with GPT, and publishes with smart scheduling.
```

### 2. Топики (Topics)

Добавьте топики:
- `telegram-bot`
- `ai`
- `openai`
- `content-rewriting`
- `automation`
- `python`
- `twitter-api`
- `content-marketing`

### 3. Настройка Issues и PR

- ✅ Issues включены
- ✅ Pull Requests включены
- ✅ Wiki отключена (если не нужна)
- ✅ Projects включены (опционально)

## 🔒 Безопасность

### 1. Проверка секретов

**ПЕРЕД ПУБЛИКАЦИЕЙ** выполните:

```bash
# Поиск потенциальных секретов
grep -r "sk-" . --exclude-dir=.git
grep -r "API_KEY" . --exclude-dir=.git
grep -r "SECRET" . --exclude-dir=.git
grep -r "TOKEN" . --exclude-dir=.git
```

### 2. Настройка GitHub Secrets

Если планируете CI/CD, добавьте секреты в Settings → Secrets:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `OPENAI_API_KEY`
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_TOKEN_SECRET`
- `TWITTER_BEARER_TOKEN`

## 📊 Настройка GitHub Pages (опционально)

Если хотите создать документацию:

1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: `gh-pages`
4. Создайте папку `docs/` с документацией

## 🏷️ Создание релизов

### 1. Создание тега

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 2. Создание релиза на GitHub

1. Go to Releases → Create a new release
2. Choose tag: `v1.0.0`
3. Release title: `RewiRater v1.0.0`
4. Description: описание изменений
5. Attach files: `requirements.txt`, `config_example.py`

## 📈 Мониторинг

### 1. Insights

Отслеживайте:
- Traffic (просмотры, клоны)
- Contributors
- Community standards

### 2. Actions

Настройте автоматические проверки:
- Linting
- Testing
- Security scanning

## 🎯 Финальная проверка

Перед публикацией убедитесь:

- [ ] Все API ключи удалены
- [ ] `.gitignore` настроен правильно
- [ ] README.md актуален
- [ ] LICENSE добавлен
- [ ] Все файлы закоммичены
- [ ] Репозиторий публичен
- [ ] Описание и топики добавлены

## 🚀 После публикации

1. **Создайте Issue** с описанием проекта
2. **Добавьте badges** в README (если есть CI/CD)
3. **Настройте автоматические обновления** зависимостей
4. **Создайте CONTRIBUTING.md** с правилами вклада
5. **Настройте CODEOWNERS** для защиты важных файлов

---

**Удачи с публикацией! 🎉**
