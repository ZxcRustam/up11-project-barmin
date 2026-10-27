from database import Database

db = Database()
products = db.get_products()

print(f"Количество товаров: {len(products)}")

print("\nПервые 3 товара с остатками на складе:")
for row in products[:3]:
    print(row)

db.close_all()
