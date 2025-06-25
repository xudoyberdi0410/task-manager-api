#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест для проверки работы категорий с многоязычными названиями и Unicode символами
Проверяет поддержку различных языков: русского, китайского, японского, арабского,
эмодзи, специальных символов и т.д.
"""
import os
import sys
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Добавляем путь к проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.base import BaseModel
from src.models.category import Category
from src.models.user import User
from src.repositories.category_repository import CategoryRepository
from src.repositories.user_repository import UserRepository
from src.services.category_service import CategoryService
from src.schemas.category import CategoryCreate, CategoryUpdate

def detect_language(text):
    """Простое определение языка по символам для красивого вывода"""
    if any('\u4e00' <= char <= '\u9fff' for char in text):
        return "🇨🇳 Китайский"
    elif any('\u3040' <= char <= '\u309f' for char in text) or any('\u30a0' <= char <= '\u30ff' for char in text):
        return "🇯🇵 Японский"  
    elif any('\u0600' <= char <= '\u06ff' for char in text):
        return "🇸🇦 Арабский"
    elif any('\u0590' <= char <= '\u05ff' for char in text):
        return "🇮🇱 Иврит"
    elif any('\uac00' <= char <= '\ud7af' for char in text):
        return "🇰🇷 Корейский"
    elif any('\u0900' <= char <= '\u097f' for char in text):
        return "🇮🇳 Хинди"
    elif any('\u0e00' <= char <= '\u0e7f' for char in text):
        return "🇹🇭 Тайский"
    elif any('\u0370' <= char <= '\u03ff' for char in text):
        return "🇬🇷 Греческий"
    elif any('\u0400' <= char <= '\u04ff' for char in text):
        return "🇷🇺 Русский"
    elif any(ord(char) > 0x1f600 for char in text):  # Диапазон эмодзи
        return "😊 Эмодзи"
    else:
        return "🇺🇸 Английский"

def test_multilingual_category_names():
    """Тест работы с многоязычными названиями категорий и Unicode символами"""
    
    # Создаем тестовую базу данных в памяти с поддержкой UTF-8
    engine = create_engine(
        "sqlite:///:memory:", 
        echo=True,
        connect_args={"check_same_thread": False}
    )
    
    # Создаем таблицы
    BaseModel.metadata.create_all(bind=engine)
    
    # Создаем сессию
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Проверяем кодировку базы данных
        encoding_result = db.execute(text("PRAGMA encoding")).fetchone()
        print(f"Database encoding: {encoding_result}")
        
        # Создаем тестового пользователя
        user_repo = UserRepository(db)
        test_user = user_repo.create_user(
            email="test@example.com",
            username="testuser",
            password="password123"
        )
        
        # Создаем сервис категорий
        category_service = CategoryService(db)
        
        # Тестируем различные языки и символы
        multilingual_categories = [
            # Русский язык
            "Работа",
            "Личные дела", 
            "Покупки и финансы",
            
            # Английский язык
            "Work Tasks",
            "Personal Projects",
            "Shopping List",
            
            # Китайский язык (упрощённый)
            "工作任务",  # Рабочие задачи
            "个人项目",  # Личные проекты  
            "购物清单",  # Список покупок
            "家庭事务",  # Семейные дела
            
            # Японский язык (хирагана, катакана, кандзи)
            "仕事のタスク",     # Рабочие задачи
            "プライベート",     # Личное (катакана)
            "かいもの",        # Покупки (хирагана)
            "家族の用事",      # Семейные дела
            
            # Арабский язык (письмо справа налево)
            "مهام العمل",      # Рабочие задачи
            "المشاريع الشخصية", # Личные проекты
            "قائمة التسوق",    # Список покупок
            
            # Корейский язык (хангыль)
            "업무 작업",        # Рабочие задачи
            "개인 프로젝트",     # Личные проекты
            "쇼핑 목록",        # Список покупок
            
            # Хинди (деванагари)
            "कार्य कार्य",      # Рабочие задачи
            "व्यक्तिगत परियोजनाएं", # Личные проекты
            
            # Тайский язык
            "งานที่ต้องทำ",     # Задачи для выполнения
            "โครงการส่วนตัว",   # Личные проекты
            
            # Греческий язык  
            "Εργασίες",        # Работы
            "Προσωπικά έργα",   # Личные проекты
            
            # Иврит (письмо справа налево)
            "משימות עבודה",     # Рабочие задачи
            "פרויקטים אישיים",   # Личные проекты
        ]
        
        created_categories = []
        
        print("\n=== Создание категорий с многоязычными названиями ===")
        for title in multilingual_categories:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(category_data, test_user.user_id)
            
            if category:
                created_categories.append(category)
                # Определяем язык для красивого вывода
                lang_info = detect_language(title)
                print(f"✅ {lang_info}: '{category.title}' (ID: {category.category_id})")
            else:
                print(f"❌ Не удалось создать категорию: '{title}'")
        
        print(f"\nВсего создано многоязычных категорий: {len(created_categories)}")
        
        # Проверяем получение категорий
        print("\n=== Получение многоязычных категорий из базы данных ===")
        all_categories, total = category_service.get_categories_by_user(test_user.user_id)
        
        for category in all_categories:
            lang_info = detect_language(category.title)
            print(f"📁 {lang_info}: {category.title} (ID: {category.category_id})")
        
        # Тестируем эмодзи и специальные символы
        print("\n=== Тест эмодзи и специальных символов ===")
        emoji_categories = [
            # Эмодзи категории
            "💼 Работа",
            "🏠 Дом",
            "🛒 Покупки", 
            "🎯 Цели",
            "💰 Финансы",
            "🎮 Развлечения",
            "📚 Обучение",
            "🚗 Транспорт",
            "🏥 Здоровье",
            "🎨 Творчество",
            
            # Только эмодзи
            "🔥",
            "⭐",
            "🚀",
            "💡", 
            "🎉",
            "📝",
            "🎵",
            "🌟",
            
            # Смешанные символы
            "❤️ Важное",
            "⚡ Срочно",
            "🔔 Напоминания", 
            "🎪 События",
            "🌈 Настроение",
            
            # Математические и научные символы
            "∑ Математика",
            "π Наука", 
            "∞ Бесконечность",
            "α Альфа проекты",
            "β Бета тесты",
            
            # Разные виды кавычек и символов
            "«Важные задачи»",
            '"Проекты"',
            "'Идеи'",
            "°C Температура",
            "№1 Приоритет",
            "© Авторские права",
            "™ Торговые марки",
        ]
        
        print(f"Тестируем {len(emoji_categories)} категорий с эмодзи и спецсимволами...")
        emoji_created = []
        
        for title in emoji_categories:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(category_data, test_user.user_id)
            
            if category:
                emoji_created.append(category)
                lang_info = detect_language(title)
                print(f"✅ {lang_info}: '{title}'")
            else:
                print(f"❌ Не удалось создать: '{title}'")
        
        print(f"\nСоздано эмодзи категорий: {len(emoji_created)}")
        
        # Тестируем очень длинные многоязычные названия
        print("\n=== Тест длинных многоязычных названий ===")
        long_multilingual = [
            "Very Long English Category Name With Multiple Words",
            "Очень длинное русское название категории с множественными словами",
            "非常に長い日本語のカテゴリ名前です",  # Очень длинное японское название категории
            "这是一个非常长的中文类别名称",  # Это очень длинное китайское название категории
            "📚🎯💼 Смешанная категория с эмодзи и текстом на разных языках",
        ]
        
        for title in long_multilingual:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(category_data, test_user.user_id)
            
            char_count = len(title)
            if category:
                lang_info = detect_language(title)
                print(f"✅ {lang_info} ({char_count} символов): '{title[:50]}{'...' if len(title) > 50 else ''}'")
            else:
                print(f"❌ Не удалось создать ({char_count} символов): '{title[:50]}{'...' if len(title) > 50 else ''}'")
        
        # Тестируем поиск многоязычных категорий
        print("\n=== Поиск многоязычных категорий ===")
        search_terms = [
            # Поиск на разных языках
            ("工作", "китайский поиск"),
            ("仕事", "японский поиск"), 
            ("💼", "поиск по эмодзи"),
            ("Work", "английский поиск"),
            ("Работа", "русский поиск"),
        ]
        
        for term, description in search_terms:
            found_categories, _ = category_service.search_categories(term, test_user.user_id)
            if found_categories:
                print(f"🔍 {description} '{term}': найдено {len(found_categories)} категорий")
                for cat in found_categories[:3]:  # Показываем первые 3
                    print(f"   → {cat.title}")
            else:
                print(f"🔍 {description} '{term}': категории не найдены")
        
        # Тестируем обновление многоязычной категории
        print("\n=== Обновление многоязычной категории ===")
        if created_categories:
            category_to_update = created_categories[0]
            new_title = "🔄 Updated • Обновлено • 更新された"
            
            update_data = CategoryUpdate(title=new_title)
            updated_category = category_service.update_category(
                category_to_update.category_id,
                update_data,
                test_user.user_id
            )
            
            if updated_category:
                old_lang = detect_language(category_to_update.title)
                new_lang = detect_language(updated_category.title)
                print(f"✏️ Обновлена категория:")
                print(f"   Было: {old_lang} '{category_to_update.title}'")
                print(f"   Стало: {new_lang} '{updated_category.title}'")
            else:
                print(f"❌ Не удалось обновить категорию")
        
        # Тестируем экстремальные случаи
        print("\n=== Тест экстремальных случаев ===")
        extreme_cases = [
            # Смешение языков в одном названии
            "Work-работа-仕事-💼",
            "混合Mixed混ぜるمختلط",
            
            # Числа и символы из разных систем
            "123 ١٢٣ 一二三 αβγ",
            
            # Направление письма (LTR + RTL)
            "English العربية עברית",
            
            # Экстремально длинное многоязычное название
            "🌍 Global Project • Глобальный проект • グローバルプロジェクト • 全球项目 • مشروع عالمي",
            
            # Только пробелы и специальные символы (должно быть отвергнуто)
            "   ",
            "",
            
            # Unicode символы высокого порядка
            "𝕌𝕟𝕚𝕔𝕠𝕕𝕖 𝔼𝕩𝕥𝕣𝕒",
            "🚀🌟💫⭐🌙",
        ]
        
        for title in extreme_cases:
            if not title.strip():  # Пропускаем пустые названия
                print(f"⏭️ Пропускаем пустое название: '{title}'")
                continue
                
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(category_data, test_user.user_id)
            
            if category:
                lang_info = detect_language(title)
                print(f"✅ {lang_info}: '{title}'")
            else:
                print(f"❌ Отклонено: '{title}'")
        
        # Финальная статистика
        print("\n=== Итоговая статистика многоязычных категорий ===")
        final_categories, total = category_service.get_categories_by_user(test_user.user_id)
        print(f"Общее количество категорий: {len(final_categories)}")
        
        # Группируем по языкам
        language_stats = {}
        for category in final_categories:
            lang = detect_language(category.title)
            if lang not in language_stats:
                language_stats[lang] = []
            language_stats[lang].append(category.title)
        
        print("\n📊 Статистика по языкам:")
        for lang, titles in language_stats.items():
            print(f"   {lang}: {len(titles)} категорий")
        
        print("\n📝 Все категории:")
        for i, category in enumerate(final_categories, 1):
            lang_info = detect_language(category.title)
            print(f"{i:2d}. {lang_info}: {category.title}")
        
        # Тестируем кодировки и правильность сохранения
        print("\n=== Проверка корректности сохранения Unicode ===")
        test_unicode_chars = [
            ("🌍", "Эмодзи земля"),
            ("中文", "Китайские иероглифы"),
            ("ひらがな", "Японская хирагана"),
            ("العربية", "Арабский текст"),
            ("עברית", "Иврит"),
            ("Русский", "Кириллица"),
            ("∑∞α", "Математические символы"),
        ]
        
        for char, description in test_unicode_chars:
            # Создаем категорию
            test_title = f"Test {char} {description}"
            category_data = CategoryCreate(title=test_title)
            category = category_service.create_category(category_data, test_user.user_id)
            
            if category:
                # Проверяем, что символы сохранились правильно
                if category.title == test_title:
                    print(f"✅ Unicode корректен: {description} - '{char}'")
                else:
                    print(f"❌ Unicode искажён: ожидалось '{test_title}', получено '{category.title}'")
            else:
                print(f"❌ Не удалось создать тест для: {description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    print("🌍 Запуск тестирования многоязычных названий категорий...")
    success = test_multilingual_category_names()
    
    if success:
        print("\n✅ Тестирование завершено успешно!")
    else:
        print("\n❌ Тестирование завершено с ошибками!")
        sys.exit(1)
