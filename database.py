import mysql.connector
from mysql.connector import pooling


class Database:

    def __init__(self):
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="podcasts_pool",
                pool_size=5,
                database="podcasts_db",
                user="root",
                password="1234",
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

    def get_products(self):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                p.product_id, p.name, p.category_id, p.manufacturer AS studio, 
                p.price, p.image_path, COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            LEFT JOIN stock_items si ON p.product_id = si.product_id
            GROUP BY p.product_id, p.name, p.category_id, p.manufacturer, p.price, p.image_path;
            """)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            print(f"Ошибка БД при получении подкастов: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    
    def get_user_by_login(self, login):
        conn = self.get_connection()
        if conn is None:
            return None
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, role_id FROM users WHERE login = %s;",
                (login,)
            )
            return cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Ошибка БД при поиске пользователя: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    def close_all(self):
        pass
