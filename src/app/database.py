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
        if conn:
            try:
                conn.close()
            except mysql.connector.Error:
                pass

    # --- ЗАДАНИЕ 1.1: Получение списка уникальных категорий из БД ---
    def get_categories(self):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category_id FROM products ORDER BY category_id")
            categories = cursor.fetchall()
            cursor.close()
            return categories
        except mysql.connector.Error as e:
            print(f"Ошибка БД при получении категорий: {e}")
            return []
        finally:
            self.release_connection(conn)

    # --- ЗАДАНИЕ 5.1 и 7.1: Получение подкастов с поиском, фильтром и сортировкой (MySQL) ---
    def get_products(self, search="", category_text="Все категории", order="ASC"):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            pattern = f"%{search}%"
            
            # Поиск подкастов по подстроке без учета регистра с помощью LIKE
            query = f"""
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
                WHERE (p.name LIKE %s OR p.manufacturer LIKE %s)  
                  AND (CAST(p.category_id AS CHAR) = %s OR %s = 'Все категории')
                GROUP BY 
                    p.product_id, 
                    p.name, 
                    p.category_id, 
                    p.manufacturer, 
                    p.price, 
                    p.image_path
                ORDER BY p.price {order}
            """
            cursor.execute(query, (pattern, pattern, category_text, category_text))
            products = cursor.fetchall()
            cursor.close()
            return products
        except mysql.connector.Error as e:
            print(f"Ошибка БД при получении подкастов: {e}")
            return []
        finally:
            self.release_connection(conn)

    def get_user_by_login(self, login):
        conn = self.get_connection()
        if conn is None:
            return None
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, role_id, last_name, first_name, COALESCE(middle_name, '') "
                "FROM users WHERE login = %s",
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

    # === ЗАДАНИЕ 12: Оформление заказа (Откатоустойчивая транзакция через пул) ===
    def create_order(self, user_id, product_id, size_id, quantity, price):
        conn = self.get_connection()
        if conn is None:
            return False, "Нет соединения с базой данных!"
        cursor = None
        try:
            cursor = conn.cursor()
            
            # 1. Проверяем остаток
            cursor.execute(
                "SELECT quantity FROM stock_items WHERE product_id = %s AND size_id = %s",
                (product_id, size_id)
            )
            res = cursor.fetchone()
            if not res or res[0] < quantity:
                return False, "Недостаточно доступных лицензий на складе!"

            # 2. Создаем шапку заказа
            cursor.execute("INSERT INTO orders (order_date, user_id) VALUES (CURRENT_DATE, %s)", (user_id,))
            order_id = cursor.lastrowid
            
            # 3. Создаем позицию заказа
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, size_id, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                (order_id, product_id, size_id, quantity, price)
            )
            
            # 4. Обновляем складские остатки
            cursor.execute(
                "UPDATE stock_items SET quantity = quantity - %s WHERE product_id = %s AND size_id = %s",
                (quantity, product_id, size_id)
            )
            
            conn.commit()
            return True, f"Заказ №{order_id} успешно оформлен! База обновлена."
        except mysql.connector.Error as e:
            conn.rollback()
            return False, f"Ошибка при оформлении транзакции: {e.msg}"
        finally:
            if cursor:
                cursor.close()
            self.release_connection(conn)

    # === ЗАДАНИЕ 13: Управление заказами (Вывод лога продаж для Менеджера) ===
    def get_all_orders_for_manager(self):
        conn = self.get_connection()
        if conn is None:
            return []
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    o.order_id, 
                    DATE_FORMAT(o.order_date, '%d.%m.%Y') AS date, 
                    u.last_name, 
                    u.first_name, 
                    SUM(oi.quantity * oi.price) AS total_sum
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                JOIN order_items oi ON o.order_id = oi.order_id
                GROUP BY o.order_id
                ORDER BY o.order_id DESC
            """)
            orders = cursor.fetchall()
            cursor.close()
            return orders
        except mysql.connector.Error as e:
            print(f"Ошибка при выгрузке списка заказов: {e}")
            return []
        finally:
            self.release_connection(conn)
    # === ЗАДАНИЕ ДЛЯ АДМИН-ПАНЕЛИ: Сбор сводной статистики системы ===
    def get_admin_stats(self):
        conn = self.get_connection()
        if conn is None:
            return None
        cursor = None
        try:
            cursor = conn.cursor()
            
            # Считаем пользователей, товары и общую сумму всех заказов
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]
            
            cursor.execute("SELECT COALESCE(SUM(quantity * price), 0) FROM order_items")
            total_sales = cursor.fetchone()[0]
            
            cursor.close()
            return total_users, total_products, total_sales
        except mysql.connector.Error as e:
            print(f"Ошибка БД при сборе статистики админа: {e}")
            return None
        finally:
            self.release_connection(conn)
