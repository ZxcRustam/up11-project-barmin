from database import Database

db = Database()
conn = db.get_connection()

# Добавляем проверку, чтобы Pylance не ругался на возможный None
if conn is not None:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    result = cursor.fetchone()
    
    if result is not None:
        print(f"Количество подкастов: {result[0]}")
    
    cursor.close()
    db.release_connection(conn)
else:
    print("Не удалось получить соединение с базой данных.")

db.close_all()
