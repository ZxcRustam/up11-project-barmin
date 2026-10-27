import mysql.connector
# Импортируем рабочую функцию расчета цены из предыдущего задания
from logic.discount import calculate_price


def test_all_products():
    try:
        # Подключение к вашей базе данных MySQL
        connection = mysql.connector.connect(
            database="podcasts_db",
            user="root",
            password="1234",  # Ваш рабочий пароль
            host="127.0.0.1",
            port="3306",
        )

        cursor = connection.cursor()

        # 1. Выполняем SQL-запрос для получения всех товаров
        query = "SELECT product_id, name, price FROM products;"
        cursor.execute(query)

        # 2. Получаем все строки из базы данных
        products = cursor.fetchall()

        # Закрываем ресурсы базы данных перед началом цикла расчетов
        cursor.close()
        connection.close()

        print(f"--- НАЧАЛО ПРОВЕРКИ (Всего товаров: {len(products)}) ---\n")

        # 3. В цикле for проходимся по каждой строке
        for row in products:
            product_id = row[0]
            name = row[1]
            price = row[2]

            # 4. Для каждого товара вызываем функцию из discount.py
            final_price = calculate_price(product_id, price)

            # 5. Выводим красивый результат через print
            print(
                f"ID: {product_id} | {name} | Стартовая цена: {price} руб. -> Итоговая: {final_price} руб."
            )

        print("\n--- ПРОВЕРКА ЗАВЕРШЕНА ---")

    except mysql.connector.Error as e:
        print(f"Ошибка БД при получении списка товаров: {e}")
    except Exception as e:
        print(f"Системная ошибка в скрипте тестирования: {e}")


if __name__ == "__main__":
    test_all_products()
