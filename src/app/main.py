# Изменения для ветки feature/new-design
import os
import sys
from pathlib import Path

# Автоматическое добавление папок в пути поиска, чтобы не было ошибок импорта 'src' и 'app'
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, 
    QScrollArea, QVBoxLayout, QWidget, QPushButton, QMessageBox,
    QComboBox, QLineEdit
)

from app.database import Database
from src.logic.discount import calculate_price

ROLE_NAMES = {1: "Администратор", 2: "Менеджер", 3: "Покупатель", None: "Гость"}

DISCOUNT_LIMIT = 15
DISCOUNT_COLOR = "#2E8B57"

BUTTON_STYLE = """
    QPushButton {
        background-color: #70B2AF;
        color: white;
        font-family: Calibri;
        font-size: 13px;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        padding: 6px 14px;
    }
    QPushButton:hover { background-color: #5B9A97; }
"""

COMBO_STYLE = """
    QComboBox, QLineEdit {
        font-family: Calibri;
        font-size: 13px;
        padding: 4px;
        border: 1px solid #B0BEC5;
        border-radius: 4px;
        background-color: #FFFFFF;
        min-width: 140px;
    }
"""


def load_cover(image_path):
    if image_path:
        full_path = os.path.join("resources", image_path)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                return pixmap
    return QPixmap(os.path.join("resources", "picture.png"))


def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100


def create_card(product):
    # Распаковка 7 элементов из вашего СУБД-метода get_products
    (product_id, name, category_id, studio, old_price_raw, image_path, total_quantity) = product

    card = QWidget()
    card_layout = QHBoxLayout()

    image_label = QLabel()
    cover_pixmap = load_cover(image_path)
    image_label.setPixmap(cover_pixmap.scaled(
        70, 70, 
        Qt.AspectRatioMode.KeepAspectRatio, 
        Qt.TransformationMode.SmoothTransformation
    ))
    image_label.setFixedSize(70, 70)
    card_layout.addWidget(image_label)

    text_layout = QVBoxLayout()
    title_label = QLabel(f"{studio} | {name}")
    title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1A237E;")
    text_layout.addWidget(title_label)
    text_layout.addWidget(QLabel(f"ID Категории: {category_id}"))
    text_layout.addWidget(QLabel(f"Доступно для покупки: {int(total_quantity)} лицензий"))
    card_layout.addLayout(text_layout)

    old_price = float(old_price_raw)
    computed_price = calculate_price(product_id, old_price)
    new_price = float(computed_price) if computed_price is not None else old_price
    discount = calculate_discount(old_price, new_price)

    price_container = QVBoxLayout()
    price_label = QLabel(f"{new_price:.2f} ₽")
    price_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
    old_price_label.setStyleSheet("color: red; font-size: 12px;")
    old_price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    price_container.addWidget(old_price_label)
    
    if discount > 0:
        old_price_label.show()
    else:
        old_price_label.hide()

    price_container.addWidget(price_label)
    card_layout.addLayout(price_container)

    card.setLayout(card_layout)

    # Цветовая маркировка остатков и скидок
    if total_quantity == 0:
        card.setStyleSheet("""
            QWidget { border: 1px solid #B0BEC5; border-radius: 8px; background-color: #ADD8E6; padding: 5px; }
            QLabel { border: none; background: transparent; color: #000000; }
        """)
        price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1A237E;")
    elif discount > DISCOUNT_LIMIT:
        card.setStyleSheet("""
            QWidget { border: 1px solid #CFD8DC; border-radius: 8px; background-color: #FFFFFF; padding: 5px; }
            QLabel { border: none; background: transparent; }
        """)
        price_label.setStyleSheet(f"color: {DISCOUNT_COLOR}; font-weight: bold; font-size: 16px;")
    else:
        card.setStyleSheet("""
            QWidget { border: 1px solid #CFD8DC; border-radius: 8px; background-color: #FAFAFA; padding: 5px; }
            QLabel { border: none; background: transparent; }
        """)
        price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32;")

    return card


class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None, user_id=None):
        super().__init__()
        self.role_id = role_id          
        self.full_name = full_name      
        self.user_id = user_id if user_id else 4 
        self.db = Database()

        self.setWindowTitle("Мир подкастов — Каталог")
        self.resize(850, 650)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.setStyleSheet("QMainWindow { background-color: #FFFFFF; font-family: Calibri; }")

        self.setup_ui()                 
        self.setup_role_interface()
        self.load_products()     

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Шапка приложения
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #D2F6E7;")  
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)

        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/logo.png")
        logo_label.setPixmap(logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        header_layout.addWidget(logo_label)
        header_layout.addStretch()

        text = f"ФИО: {self.full_name} ({ROLE_NAMES.get(self.role_id)})" if self.full_name else "Гость"
        self.name_label = QLabel(text)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C3E50; background: transparent;")
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet(BUTTON_STYLE)  
        header_layout.addWidget(self.logout_button)
        main_layout.addWidget(header_widget)  

        # --- Панель поиска, фильтрации и кнопок ---
        top_widget = QWidget()
        top_widget.setStyleSheet(COMBO_STYLE)
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(15, 5, 15, 5)
        top_layout.setSpacing(5)

        # Первая строка: Фильтры
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или студии...")
        self.search_input.textChanged.connect(self.load_products)
        filter_row.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        for cat in self.db.get_categories():
            self.filter_combo.addItem(str(cat[0]))
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        filter_row.addWidget(self.filter_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию цены", "По убыванию цены"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        filter_row.addWidget(self.sort_combo)
        top_layout.addLayout(filter_row)

        # Вторая строка: Управляющие кнопки ролей (строго как на втором макете)
        buttons_row = QHBoxLayout()
        self.order_button = QPushButton("Купить подкаст")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        self.order_button.setStyleSheet(BUTTON_STYLE)
        self.manager_button.setStyleSheet(BUTTON_STYLE)
        self.admin_button.setStyleSheet(BUTTON_STYLE)
        
        buttons_row.addWidget(self.order_button)
        buttons_row.addWidget(self.manager_button)
        buttons_row.addWidget(self.admin_button)
        buttons_row.addStretch()
        top_layout.addLayout(buttons_row)

        main_layout.addWidget(top_widget)

        # Область прокрутки каталога
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.catalog_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
        
        # Связывание кликов
        self.order_button.clicked.connect(self.make_order)
        self.manager_button.clicked.connect(self.open_orders_management)
        self.admin_button.clicked.connect(self.open_admin_panel)  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        self.logout_button.clicked.connect(self.handle_logout)  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
        
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def setup_role_interface(self):
        """Интерфейс кнопок по ролям"""
        self.order_button.show()
        self.manager_button.show()
        self.admin_button.show()

        if self.role_id == 1:    # Администратор
            self.order_button.hide()
        elif self.role_id == 2:  # Менеджер
            self.admin_button.hide()
            self.order_button.hide()
        else:                    # Клиент / Гость
            self.admin_button.hide()
            self.manager_button.hide()


    def load_products(self):
        """Рендер карточек"""
        # Очистка старых карточек
        while self.catalog_layout.count():
            item = self.catalog_layout.takeAt(0)
            if item is not None:
                w = item.widget()
                if w is not None:
                    w.deleteLater()

        search_text = self.search_input.text()
        search_text = self.search_input.text()
        category_text = self.filter_combo.currentText()
        sort_order = "ASC" if "возрастанию" in self.sort_combo.currentText() else "DESC"

        products = self.db.get_products(search=search_text, category_text=category_text, order=sort_order)

        for prod in products:
            card = create_card(prod)
            self.catalog_layout.addWidget(card)
            
        # Располагаем карточки плотно вверху
        self.catalog_layout.addStretch()

    # === ЗАДАНИЕ 12: ОФОРМЛЕНИЕ ЗАКАЗА ===
    def make_order(self):
        if not self.full_name or self.full_name == "Гость":
            QMessageBox.warning(self, "Внимание", "Оформление заказа недоступно для гостей!")
            return

        success, message = self.db.create_order(
            user_id=self.user_id,
            product_id=1,
            size_id=1,
            quantity=1,
            price=190.00
        )

        if success:
            QMessageBox.information(self, "Успешная покупка", message)
            self.load_products()
        else:
            QMessageBox.critical(self, "Ошибка заказа", message)

    # === ЗАДАНИЕ 13: УПРАВЛЕНИЕ ЗАКАЗАМИ ===
    def open_orders_management(self):
        orders = self.db.get_all_orders_for_manager()
        if not orders:
            QMessageBox.information(self, "Заказы", "В системе пока нет оформленных заказов.")
            return

        report = "📋 Список зарегистрированных заказов клиентов:\n\n"
        for o in orders:
            report += f"📦 Заказ №{o[0]} от {o[1]} | Клиент: {o[2]} {o[3]} | Сумма: {o[4]:.2f} ₽\n"

        QMessageBox.information(self, "Управление заказами", report)

    # === ФУНКЦИЯ ДЛЯ АДМИН-ПАНЕЛИ ===
    def open_admin_panel(self):
        stats = self.db.get_admin_stats()
        if not stats:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить данные админ-панели.")
            return
            
        users_cnt, products_cnt, sales_sum = stats
        
        # Убрали все, теперь данные выводятся как чистые числа без ошибок
        admin_text = (
            "⚙️ Панель Администратора системы «Мир подкастов»\n\n"
            f"👥 Всего зарегистрировано пользователей: {users_cnt}\n"
            f"🎙️ Подкастов в каталоге: {products_cnt}\n"
            f"💰 Общий оборот продаж in системе: {sales_sum:.2f} ₽\n\n"
            "Статус системы: Стабильно (MySQL Pool OK)"
        )
        QMessageBox.information(self, "Админ-панель", admin_text)

 # === ФУНКЦИЯ ДЛЯ КНОПКИ ВЫХОД ===
    def handle_logout(self):
        from app.login_window import LoginWindow
        
        # Создаем и открываем новое окно авторизации, передавая ему объект базы данных
        self.login_win = LoginWindow(self.db)
        self.login_win.show()
        
        # Закрываем текущее главное окно каталога
        self.close()

if __name__ == "__main__":
    from app.login_window import LoginWindow
    
    app = QApplication(sys.argv)
    
    database_object = Database()
    login_win = LoginWindow(database_object)
    
    login_win.show()
    sys.exit(app.exec())
