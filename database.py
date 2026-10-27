import mysql.connector
from mysql.connector import pooling


class Database:

    def __init__(self):
        try:
            # Создаем пул соединений для MySQL (максимум 5 подключений)
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="podcasts_pool",
                pool_size=5,
                database="podcasts_db",  # Ваша база данных подкастов
                user="root",             # Стандартный пользователь
                password="1234",         # Ваш пароль от MySQL
                host="127.0.0.1",        # Локальный сервер
                port=3306                # Стандартный порт MySQL
            )
        except mysql.connector.Error as e:
            print(f"Ошибка БД при инициализации пула: {e}")
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
        # В MySQL соединение возвращается в пул обычным закрытием объекта conn
        if conn:
            try:
                conn.close()
            except mysql.connector.Error:
                pass

    # --- ЗАДАНИЕ 6.1: Адаптированный метод для вашей темы подкастов ---
    def get_products(self):
        conn = self.get_connection()
        if conn is None:
            return []

        cursor = None
        try:
            cursor = conn.cursor()
            # MySQL-запрос: связывает товары с остатками и группирует их без ошибок
            cursor.execute("""
            SELECT 
                p.product_id, 
                p.name, 
                p.category_id, 
                p.manufacturer AS studio, 
                p.price, 
                p.image_path,
                COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            LEFT JOIN stock_items si ON p.product_id = si.product_id
            GROUP BY 
                p.product_id, 
                p.name, 
                p.category_id, 
                p.manufacturer, 
                p.price, 
                p.image_path;
            """)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД при получении подкастов: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def close_all(self):
        # Заглушка для совместимости вызовов из интерфейса окна
        pass


# Тестирование структуры при прямом запуске файла database.py
if __name__ == "__main__":
    print("--- ТЕСТ DATABASE.PY ---")
    db = Database()
    res = db.get_products()
    print(f"Успешно получено подкастов: {len(res)}")
    for row in res[:2]:
        print(row)
