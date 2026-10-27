import mysql.connector

# =====================================================================
# ЗАДАНИЯ 2, 3, 4: Базовая функция расчета цены товаров
# =====================================================================

def calculate_price(product_id, base_price):
    # ЗАДАНИЕ 3.1: Проверка входных данных в Python
    if not isinstance(product_id, int):
        print("Ошибка: product_id должен быть числом")
        return None

    if not isinstance(base_price, (int, float)):
        print("Ошибка: base_price должен быть числом")
        return None

    if base_price <= 0:
        print("Ошибка: цена должна быть > 0")
        return None

    try:
        # Подключение к вашей базе данных MySQL
        connection = mysql.connector.connect(
            database="podcasts_db",
            user="root",
            password="1234",  # Ваш пароль от MySQL
            host="127.0.0.1",
            port="3306"
        )
        cursor = connection.cursor()

        # Выполнение SQL-запроса
        query = "SELECT COUNT(*) FROM order_items WHERE product_id = %s;"
        cursor.execute(query, (product_id,))

        # ЗАДАНИЕ 4.1: Получение результата и проверка на None
        result = cursor.fetchone()

        if result is None:
            print("Ошибка: нет результата")
            cursor.close()
            connection.close()
            return None

        orders_count = result[0]

        cursor.close()
        connection.close()

        # ЗАДАНИЕ 3.1: Расчет цены на основе заказов
        if orders_count == 0:
            return base_price * 0.75
        else:
            return base_price

    except mysql.connector.Error as e:
        print(f"Ошибка БД: {e}")
        return None
    except Exception as e:
        print(f"Системная ошибка: {e}")
        return None


# =====================================================================
# ЗАДАНИЕ 6: Самостоятельная работа (Мир подкастов)
# =====================================================================

def calculate_price_podcast(item_id, base_price):
    # Проверка входных данных
    if not isinstance(item_id, int):
        print("Ошибка: item_id должен быть числом")
        return None

    if not isinstance(base_price, (int, float)):
        print("Ошибка: base_price должен быть числом")
        return None

    if base_price <= 0:
        print("Ошибка: цена должна быть > 0")
        return None

    conn = None
    cursor = None

    try:
        # Подключение к вашей СУБД MySQL
        conn = mysql.connector.connect(
            database="podcasts_db",
            user="root",
            password="1234",
            host="127.0.0.1",
            port="3306"
        )
        cursor = conn.cursor()

        # Проверяем, что подкаст существует в каталоге таблицы products
        cursor.execute("SELECT name FROM products WHERE product_id = %s;", (item_id,))
        podcast = cursor.fetchone()

        # Проверка fetchone() на None (Если такого подкаста нет в каталоге)
        if podcast is None:
            print(f"Ошибка: подкаст с id={item_id} не найден")
            return None

        # Считаем заказы этого подкаста за последний месяц данных (апрель-май 2026 года)
        query = """
            SELECT COUNT(*) FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s
            AND o.order_date >= '2026-04-01';
        """
        cursor.execute(query, (item_id,))
        result = cursor.fetchone()

        # Проверка fetchone() на None для агрегатного запроса
        if result is None:
            print("Ошибка: нет результата")
            return None

        # Анализ результатов: если заказов за месяц нет (0) -> даем скидку 25%
        orders_count = result[0]
        if orders_count == 0:
            return base_price * 0.75
        else:
            return base_price

    except mysql.connector.Error as e:
        print(f"Ошибка БД: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return None

    # Блок finally для гарантированного освобождения ресурсов
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =====================================================================
# ОБЪЕДИНЕННЫЙ ТЕСТОВЫЙ ЗАПУСК
# =====================================================================
if __name__ == "__main__":
    print("--- СТАРТ ТЕСТИРОВАНИЯ ИЗ ПРЕДЫДУЩИХ ЗАЗАНИЙ (Задания 3 и 4) ---")
    
    print("\nТест 1 (product_id = 'abc'):")
    calculate_price("abc", 1000)

    print("\nТест 2 (base_price = 'abc'):")
    calculate_price(1, "abc")

    print("\nТест 3 (base_price = -100):")
    calculate_price(1, -100)

    print("\nТест 4 (base_price = None):")
    calculate_price(1, None)

    print("\nТест 5 (Товар с ID 99999, которого нет в базе):")
    price_99999 = calculate_price(99999, 1000)
    print(f"Результат функции: {price_99999}")


    print("\n--- СТАРТ САМОСТОЯТЕЛЬНОГО ТЕСТИРОВАНИЯ (ЗАДАНИЕ 6) ---")

    print("\nТест 6 (Правильный подкаст с ID=1, проверка скидки):")
    price_1 = calculate_price_podcast(1, 500)
    if price_1 is not None:
        print(f"Результат расчета цены: {price_1} руб.")

    print("\nТест 7 (Несуществующий ID подкаста = 99999):")
    calculate_price_podcast(99999, 500)

    print("\nТест 8 (Некорректный тип ID - строка 'abc'):")
    calculate_price_podcast("abc", 500)

    print("\nТест 9 (Отрицательная базовая цена):")
    calculate_price_podcast(1, -500)

    print("\nТест 10 (Пустая базовая цена None):")
    calculate_price_podcast(1, None)

    print("\n--- ТЕСТИРОВАНИЕ ПОЛНОСТЬЮ ЗАВЕРШЕНО ---")
