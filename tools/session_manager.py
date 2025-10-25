#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер сессий для управления авторизацией
"""

import asyncio
from telethon import TelegramClient
from pathlib import Path
import shutil

# Конфигурация
API_ID = 21601645
API_HASH = '6bc7e9ceae3ed7d5694ac49d6d67cedc'

class SessionManager:
    """Менеджер сессий Telegram"""
    
    def __init__(self):
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
    
    async def create_session(self, session_name: str):
        """Создание новой сессии"""
        session_path = self.sessions_dir / session_name
        
        print(f"🆕 Создание новой сессии: {session_name}")
        
        client = TelegramClient(str(session_path), API_ID, API_HASH)
        
        try:
            await client.start()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"✅ Сессия создана успешно!")
                print(f"👤 Пользователь: {me.first_name} (@{me.username})")
                print(f"🆔 ID: {me.id}")
                print(f"📱 Телефон: {me.phone}")
                
                # Сохраняем информацию о сессии
                session_info = {
                    "session_name": session_name,
                    "user_id": me.id,
                    "username": me.username,
                    "first_name": me.first_name,
                    "phone": me.phone
                }
                
                info_file = self.sessions_dir / f"{session_name}.info.json"
                import json
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(session_info, f, ensure_ascii=False, indent=2)
                
                print(f"💾 Информация сохранена: {info_file}")
                return True
            else:
                print("❌ Пользователь не авторизован!")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка создания сессии: {e}")
            return False
        finally:
            await client.disconnect()
    
    async def check_session(self, session_name: str):
        """Проверка существующей сессии"""
        session_path = self.sessions_dir / session_name
        
        if not session_path.exists():
            print(f"❌ Сессия не найдена: {session_path}")
            return False
        
        print(f"🔍 Проверка сессии: {session_name}")
        
        client = TelegramClient(str(session_path), API_ID, API_HASH)
        
        try:
            await client.start()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"✅ Сессия активна!")
                print(f"👤 Пользователь: {me.first_name} (@{me.username})")
                print(f"🆔 ID: {me.id}")
                return True
            else:
                print("❌ Сессия недействительна!")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка проверки сессии: {e}")
            return False
        finally:
            await client.disconnect()
    
    def list_sessions(self):
        """Список всех сессий"""
        print("📋 Список сессий:")
        print("-" * 50)
        
        session_files = list(self.sessions_dir.glob("*.session"))
        
        if not session_files:
            print("📭 Сессии не найдены")
            return []
        
        for session_file in session_files:
            session_name = session_file.stem
            info_file = self.sessions_dir / f"{session_name}.info.json"
            
            print(f"📁 {session_name}")
            
            if info_file.exists():
                try:
                    import json
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                    print(f"   👤 {info.get('first_name', 'Unknown')} (@{info.get('username', 'no_username')})")
                    print(f"   🆔 ID: {info.get('user_id', 'Unknown')}")
                except:
                    print("   ❓ Информация недоступна")
            else:
                print("   ❓ Информация недоступна")
            print()
        
        return [f.stem for f in session_files]
    
    def delete_session(self, session_name: str):
        """Удаление сессии"""
        session_path = self.sessions_dir / session_name
        info_path = self.sessions_dir / f"{session_name}.info.json"
        
        if not session_path.exists():
            print(f"❌ Сессия не найдена: {session_name}")
            return False
        
        try:
            session_path.unlink()
            if info_path.exists():
                info_path.unlink()
            
            print(f"🗑️ Сессия удалена: {session_name}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка удаления сессии: {e}")
            return False
    
    def copy_session(self, source_name: str, target_name: str):
        """Копирование сессии"""
        source_path = self.sessions_dir / source_name
        target_path = self.sessions_dir / target_name
        
        if not source_path.exists():
            print(f"❌ Исходная сессия не найдена: {source_name}")
            return False
        
        try:
            shutil.copy2(source_path, target_path)
            
            # Копируем информацию
            source_info = self.sessions_dir / f"{source_name}.info.json"
            target_info = self.sessions_dir / f"{target_name}.info.json"
            
            if source_info.exists():
                shutil.copy2(source_info, target_info)
            
            print(f"📋 Сессия скопирована: {source_name} → {target_name}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка копирования сессии: {e}")
            return False

async def main():
    """Интерактивное меню"""
    manager = SessionManager()
    
    while True:
        print("\n" + "="*50)
        print("🛠️ Менеджер сессий Telegram")
        print("="*50)
        print("1. Создать новую сессию")
        print("2. Проверить сессию")
        print("3. Список сессий")
        print("4. Удалить сессию")
        print("5. Копировать сессию")
        print("0. Выход")
        print("-"*50)
        
        choice = input("Выберите действие: ").strip()
        
        if choice == "1":
            session_name = input("Введите имя сессии: ").strip()
            if session_name:
                await manager.create_session(session_name)
        
        elif choice == "2":
            session_name = input("Введите имя сессии: ").strip()
            if session_name:
                await manager.check_session(session_name)
        
        elif choice == "3":
            manager.list_sessions()
        
        elif choice == "4":
            sessions = manager.list_sessions()
            if sessions:
                session_name = input("Введите имя сессии для удаления: ").strip()
                if session_name and session_name in sessions:
                    confirm = input(f"Удалить сессию '{session_name}'? (y/N): ").strip().lower()
                    if confirm == 'y':
                        manager.delete_session(session_name)
        
        elif choice == "5":
            sessions = manager.list_sessions()
            if sessions:
                source = input("Исходная сессия: ").strip()
                target = input("Новая сессия: ").strip()
                if source and target:
                    manager.copy_session(source, target)
        
        elif choice == "0":
            print("👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    print("🚀 Запуск менеджера сессий...")
    asyncio.run(main())
