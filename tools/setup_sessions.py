#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для настройки папки sessions
"""

import os
from pathlib import Path

def setup_sessions():
    """Настройка папки sessions"""
    print("🛠️ Настройка папки sessions...")
    
    try:
        # Создаем папку sessions
        sessions_dir = Path("sessions")
        sessions_dir.mkdir(exist_ok=True)
        
        print(f"✅ Папка sessions создана: {sessions_dir.absolute()}")
        
        # Проверяем права на запись
        test_file = sessions_dir / "test.tmp"
        test_file.write_text("test")
        test_file.unlink()
        
        print("✅ Права на запись в папку sessions есть")
        
        # Создаем .gitignore если не существует
        gitignore_file = Path(".gitignore")
        gitignore_content = """# Сессии Telegram
sessions/
*.session
*.session-journal

# Временные файлы
*.tmp
*.log

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
"""
        
        if not gitignore_file.exists():
            gitignore_file.write_text(gitignore_content, encoding='utf-8')
            print("✅ Создан .gitignore файл")
        else:
            print("ℹ️ .gitignore уже существует")
        
        print("\n🎉 Настройка завершена!")
        print("📁 Теперь можно запускать боты:")
        print("   python tools/emoji_bot_fixed.py")
        print("   python tools/debug_emoji_bot.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка настройки: {e}")
        return False

if __name__ == "__main__":
    setup_sessions()
