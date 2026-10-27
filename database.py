import mysql.connector
from mysql.connector import pooling


class Database:

    def __init__(self):
        try:
            # Создаем пул соединений для MySQL (Задание 5)
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="podcasts_pool",
                pool_size=5,
                database="podcasts_db",
                user="root",
                password="1234",  # Ваш проверенный пароль
                host="127.0.0.1",
                port=3306,
            )
        except mysql.connector.Error as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None

    def get_connection(self):
        if self.connection_pool is None:
            return None
        try:
            return self.connection_pool.get_connection()
        except mysql.connector.Error as e:
            print(f"Ошибка получения соединения из пула: {e}")
            return None

    def release_connection(self, conn):
        if conn:
            try:
                conn.close()
            except mysql.connector.Error:
                pass

    # --- ЗАДАНИЕ 6.1: Метод для получения подкастов ---
    def get_products(self):
        conn = self.get_connection()
        if conn is None:
            return []

        cursor = None
        try:
            cursor = conn.cursor()
            # Выполняем SQL-запрос для вашей таблицы подкастов
            cursor.execute("SELECT * FROM products;")
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД при получении подкастов: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            # Возвращаем соединение обратно в пул MySQL
            self.release_connection(conn)

    def close_all(self):
        # Заглушка для совместимости вызовов интерфейса окна
        pass


# --- БЛОК ТЕСТИРОВАНИЯ И ПРОВЕРКИ МЕТОДА ---
if __name__ == "__main__":
    print("--- СТАРТ ТЕСТИРОВАНИЯ МЕТОДА GET_PRODUCTS ---")

    db = Database()
    products = db.get_products()

    print(f"Получено подкастов: {len(products)}")

    # Выводим первые 3 строки таблицы для проверки
    for row in products[:3]:
        print(row)

    db.close_all()
    print("--- ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ---")
