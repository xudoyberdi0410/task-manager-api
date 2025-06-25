#!/usr/bin/env python3
"""
Тесты для проверки работы категорий с многоязычными названиями и Unicode символами.
Проверяет поддержку различных языков: русского, китайского, японского, арабского,
эмодзи, специальных символов и т.д.
"""

import pytest

from src.repositories.user_repository import UserRepository
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.services.category_service import CategoryService


def detect_language(text):
    """Простое определение языка по символам для красивого вывода"""
    if any("\u4e00" <= char <= "\u9fff" for char in text):
        return "🇨🇳 Китайский"
    elif any("\u3040" <= char <= "\u309f" for char in text) or any(
        "\u30a0" <= char <= "\u30ff" for char in text
    ):
        return "🇯🇵 Японский"
    elif any("\u0600" <= char <= "\u06ff" for char in text):
        return "🇸🇦 Арабский"
    elif any("\u0590" <= char <= "\u05ff" for char in text):
        return "🇮🇱 Иврит"
    elif any("\uac00" <= char <= "\ud7af" for char in text):
        return "🇰🇷 Корейский"
    elif any("\u0900" <= char <= "\u097f" for char in text):
        return "🇮🇳 Хинди"
    elif any("\u0e00" <= char <= "\u0e7f" for char in text):
        return "🇹🇭 Тайский"
    elif any("\u0370" <= char <= "\u03ff" for char in text):
        return "🇬🇷 Греческий"
    elif any("\u0400" <= char <= "\u04ff" for char in text):
        return "🇷🇺 Русский"
    elif any(ord(char) > 0x1F600 for char in text):  # Диапазон эмодзи
        return "😊 Эмодзи"
    else:
        return "🇺🇸 Английский"


@pytest.fixture
def category_service(db_session):
    return CategoryService(db_session)


@pytest.fixture
def multilingual_test_user(db_session):
    """Создать тестового пользователя для многоязычных тестов"""
    user_repo = UserRepository(db_session)
    return user_repo.create_user(
        email="multilingual@example.com",
        username="multilingual_user",
        password="password123",
    )


class TestMultilingualCategories:
    """Тесты многоязычной поддержки категорий"""

    def test_basic_multilingual_categories(
        self, category_service, multilingual_test_user
    ):
        """Тест создания категорий на разных языках"""
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
            "仕事のタスク",  # Рабочие задачи
            "プライベート",  # Личное (катакана)
            "かいもの",  # Покупки (хирагана)
            "家族の用事",  # Семейные дела
            # Арабский язык (письмо справа налево)
            "مهام العمل",  # Рабочие задачи
            "المشاريع الشخصية",  # Личные проекты
            "قائمة التسوق",  # Список покупок
            # Корейский язык (хангыль)
            "업무 작업",  # Рабочие задачи
            "개인 프로젝트",  # Личные проекты
            "쇼핑 목록",  # Список покупок
        ]

        created_categories = []

        for title in multilingual_categories:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(
                category_data, multilingual_test_user.user_id
            )

            assert category is not None, f"Не удалось создать категорию: '{title}'"
            assert (
                category.title == title
            ), f"Название категории изменилось: ожидалось '{title}', получено '{category.title}'"
            created_categories.append(category)

        assert len(created_categories) == len(multilingual_categories)

        # Проверяем получение категорий
        all_categories, total = category_service.get_categories_by_user(
            multilingual_test_user.user_id
        )
        assert len(all_categories) == len(multilingual_categories)
        assert total == len(multilingual_categories)

    def test_emoji_categories(self, category_service, multilingual_test_user):
        """Тест категорий с эмодзи"""
        emoji_categories = [
            # Эмодзи категории
            "💼 Работа",
            "🏠 Дом",
            "🛒 Покупки",
            "🎯 Цели",
            "💰 Финансы",
            # Только эмодзи
            "🔥",
            "⭐",
            "🚀",
            "💡",
            "🎉",
            # Смешанные символы
            "❤️ Важное",
            "⚡ Срочно",
            "🔔 Напоминания",
        ]

        created_categories = []

        for title in emoji_categories:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(
                category_data, multilingual_test_user.user_id
            )

            assert (
                category is not None
            ), f"Не удалось создать категорию с эмодзи: '{title}'"
            assert (
                category.title == title
            ), f"Эмодзи изменились: ожидалось '{title}', получено '{category.title}'"
            created_categories.append(category)

        assert len(created_categories) == len(emoji_categories)

    def test_special_symbols_categories(self, category_service, multilingual_test_user):
        """Тест категорий со специальными символами"""
        special_categories = [
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

        for title in special_categories:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(
                category_data, multilingual_test_user.user_id
            )

            assert (
                category is not None
            ), f"Не удалось создать категорию со спецсимволами: '{title}'"
            assert (
                category.title == title
            ), f"Спецсимволы изменились: ожидалось '{title}', получено '{category.title}'"

    def test_mixed_language_categories(self, category_service, multilingual_test_user):
        """Тест категорий со смешанными языками"""
        mixed_categories = [
            # Смешение языков в одном названии
            "Work-работа-仕事-💼",
            "混合Mixed混ぜるمختلط",
            # Числа и символы из разных систем
            "123 ١٢٣ 一二三 αβγ",
            # Направление письма (LTR + RTL)
            "English العربية עברית",
            # Экстремально длинное многоязычное название
            "🌍 Global Project • Глобальный проект • グローバルプロジェクト • 全球项目 • مشروع عالمي",
        ]

        for title in mixed_categories:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(
                category_data, multilingual_test_user.user_id
            )

            assert (
                category is not None
            ), f"Не удалось создать смешанную категорию: '{title}'"
            assert (
                category.title == title
            ), f"Смешанное название изменилось: ожидалось '{title}', получено '{category.title}'"

    def test_unicode_high_order_characters(
        self, category_service, multilingual_test_user
    ):
        """Тест Unicode символов высокого порядка"""
        unicode_categories = [
            # Unicode символы высокого порядка
            "𝕌𝕟𝕚𝕔𝕠𝕕𝕖 𝔼𝕩𝕥𝕣𝕒",
            "🚀🌟💫⭐🌙",
        ]

        for title in unicode_categories:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(
                category_data, multilingual_test_user.user_id
            )

            assert (
                category is not None
            ), f"Не удалось создать Unicode категорию: '{title}'"
            assert (
                category.title == title
            ), f"Unicode символы изменились: ожидалось '{title}', получено '{category.title}'"

    def test_multilingual_search(self, category_service, multilingual_test_user):
        """Тест поиска многоязычных категорий"""
        # Создаем тестовые категории
        test_categories = [
            "工作任务",  # Китайский
            "仕事のタスク",  # Японский
            "💼 Работа",  # Эмодзи + русский
            "Work Tasks",  # Английский
            "Работа",  # Русский
        ]

        for title in test_categories:
            category_data = CategoryCreate(title=title)
            category_service.create_category(
                category_data, multilingual_test_user.user_id
            )

        # Тестируем поиск
        search_tests = [
            ("工作", 1),  # Поиск китайских иероглифов
            ("仕事", 1),  # Поиск японских символов
            ("💼", 1),  # Поиск по эмодзи
            ("Work", 1),  # Поиск английского
            ("Работа", 2),  # Поиск русского (должен найти 2: "💼 Работа" и "Работа")
        ]

        for search_term, expected_count in search_tests:
            found_categories, _ = category_service.search_categories(
                search_term, multilingual_test_user.user_id
            )
            assert (
                len(found_categories) == expected_count
            ), f"Поиск '{search_term}': ожидалось {expected_count} результатов, найдено {len(found_categories)}"

    def test_unicode_preservation(self, category_service, multilingual_test_user):
        """Тест корректности сохранения Unicode символов"""
        unicode_test_cases = [
            ("🌍", "Эмодзи земля"),
            ("中文", "Китайские иероглифы"),
            ("ひらがな", "Японская хирагана"),
            ("العربية", "Арабский текст"),
            ("עברית", "Иврит"),
            ("Русский", "Кириллица"),
            ("∑∞α", "Математические символы"),
        ]

        for unicode_char, description in unicode_test_cases:
            test_title = f"Test {unicode_char} {description}"
            category_data = CategoryCreate(title=test_title)
            category = category_service.create_category(
                category_data, multilingual_test_user.user_id
            )

            assert category is not None, f"Не удалось создать тест для: {description}"
            assert (
                category.title == test_title
            ), f"Unicode искажён для {description}: ожидалось '{test_title}', получено '{category.title}'"

    def test_long_multilingual_names(self, category_service, multilingual_test_user):
        """Тест длинных многоязычных названий"""
        long_names = [
            "Very Long English Category Name With Multiple Words",  # 51 символ
            "Очень длинное русское название категории с множественными словами",  # 65 символов
            "非常に長い日本語のカテゴリ名前です",  # 17 символов
            "这是一个非常长的中文类别名称",  # 14 символов
            "📚🎯💼 Смешанная категория с эмодзи и текстом на разных языках",  # 59 символов
        ]

        for title in long_names:
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(
                category_data, multilingual_test_user.user_id
            )

            assert (
                category is not None
            ), f"Не удалось создать длинное название ({len(title)} символов): '{title}'"
            assert (
                category.title == title
            ), f"Длинное название изменилось: ожидалось '{title}', получено '{category.title}'"

    def test_multilingual_update(self, category_service, multilingual_test_user):
        """Тест обновления многоязычных категорий"""
        # Создаем категорию на русском
        original_title = "Оригинальное название"
        category_data = CategoryCreate(title=original_title)
        category = category_service.create_category(
            category_data, multilingual_test_user.user_id
        )

        assert category is not None

        # Обновляем на смешанный многоязычный
        new_title = "🔄 Updated • Обновлено • 更新された"
        update_data = CategoryUpdate(title=new_title)
        updated_category = category_service.update_category(
            category.category_id, update_data, multilingual_test_user.user_id
        )

        assert updated_category is not None, "Не удалось обновить категорию"
        assert (
            updated_category.title == new_title
        ), f"Обновление не сработало: ожидалось '{new_title}', получено '{updated_category.title}'"

    def test_empty_and_whitespace_handling(
        self, category_service, multilingual_test_user
    ):
        """Тест обработки пустых и пробельных названий"""
        from pydantic import ValidationError

        # Только пустая строка должна вызывать ValidationError из-за min_length=1
        with pytest.raises(ValidationError):
            CategoryCreate(title="")

        # Строки с пробелами проходят валидацию Pydantic (min_length=1),
        # но должны быть отклонены на уровне бизнес-логики
        whitespace_titles = [
            "   ",  # Только пробелы
            "\t\n",  # Табы и переносы
        ]

        for title in whitespace_titles:
            # Эти строки проходят валидацию схемы, но должны быть отклонены сервисом
            category_data = CategoryCreate(title=title)
            category = category_service.create_category(
                category_data, multilingual_test_user.user_id
            )
            # Сервис должен вернуть None для пустых названий после очистки
            assert (
                category is None
            ), f"Сервис не должен создавать категории с пустым названием: '{title}'"


if __name__ == "__main__":
    # Запуск тестов через pytest при прямом вызове файла
    pytest.main([__file__, "-v"])
