import mysql.connector


def calculate_price_podcasts(item_id, base_price):
    try:
        # 1. Подключаемся к базе данных подкастов
        connection = mysql.connector.connect(
            database="podcasts_db",
            user="root",
            password="1234",  # Ваш проверенный пароль
            host="127.0.0.1",
            port="3306",
        )

        cursor = connection.cursor()

        # 2. SQL-запрос: считаем заказы для конкретного подкаста (item_id) за последний месяц данных
        # (Используем явную фильтрацию по апрелю-маю 2026 года, так как ваши данные из будущего)
        query = """
            SELECT COUNT(*) 
            FROM orders 
            WHERE user_id = %s AND order_date >= '2026-04-01';
        """
        cursor.execute(query, (item_id,))

        # 3. Получаем orders_count
        result = cursor.fetchone()
        orders_count = result[0]

        cursor.close()
        connection.close()

        # 4. Условие if/else для скидки:
        # Если подкаст за месяц никто не заказывал (0 заказов), даем скидку 20% для стимуляции продаж
        if orders_count == 0:
            discounted_price = base_price * 0.80
            print(
                f"[ID {item_id}] Заказов за месяц: 0. Применена скидка 20%."
            )
            return discounted_price
        else:
            print(
                f"[ID {item_id}] Заказов за месяц: {orders_count}. Цена без изменений."
            )
            return base_price

    except mysql.connector.Error as e:
        print(f"Ошибка БД: {e}")
        return base_price
    except Exception as e:
        print(f"Системная ошибка: {e}")
        return base_price


# 5. Тестовый запуск
if __name__ == "__main__":
    print("--- ТЕСТИРОВАНИЕ СИСТЕМЫ СКИДОК ПОДКАСТОВ ---")

    # Тестируем подкаст "Наука вслух" (ID: 1, базовая цена 190.00)
    podcasts_price_1 = calculate_price_podcasts(1, 190.00)
    print(f"Итоговая стоимость подкаста №1: {podcasts_price_1} руб.\n")

    # Тестируем подкаст, которого точно нет в заказах (например, ID: 99, базовая цена 500.00)
    podcasts_price_99 = calculate_price_podcasts(99, 500.00)
    print(f"Итоговая стоимость подкаста №99: {podcasts_price_99} руб.")
