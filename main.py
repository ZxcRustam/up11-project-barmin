import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, 
    QScrollArea, QVBoxLayout, QWidget, QPushButton, QMessageBox
)

from database import Database
# Импортируем функцию расчета новой цены из вашей бизнес-логики (Пара 29)
from src.logic.discount import calculate_price

ROLE_NAMES = {1: "Администратор", 2: "Менеджер", 3: "Покупатель", None: "Гость"}

DISCOUNT_LIMIT = 15
DISCOUNT_COLOR = "#2E8B57"


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
    (product_id, name, category_id, studio, old_price_raw, image_path, total_quantity) = product

    card = QWidget()
    card_layout = QHBoxLayout()

    # Блок обложки подкаста
    image_label = QLabel()
    cover_pixmap = load_cover(image_path)
    image_label.setPixmap(cover_pixmap.scaled(
        100, 100, 
        Qt.AspectRatioMode.KeepAspectRatio, 
        Qt.TransformationMode.SmoothTransformation
    ))
    image_label.setFixedSize(100, 100)
    card_layout.addWidget(image_label)

    # Текстовые метаданные подкаста
    text_layout = QVBoxLayout()
    title_label = QLabel(f"{studio} | {name}")
    title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1A237E;")
    text_layout.addWidget(title_label)
    text_layout.addWidget(QLabel(f"ID Категории: {category_id}"))
    text_layout.addWidget(QLabel(f"Доступно для покупки: {int(total_quantity)} лицензий"))
    card_layout.addLayout(text_layout)

    # Логика расчёта цены и применения цвета скидки
    old_price = float(old_price_raw)
    computed_price = calculate_price(product_id, old_price)
    new_price = float(computed_price) if computed_price is not None else old_price
    
    discount = calculate_discount(old_price, new_price)

    price_container = QVBoxLayout()
    price_label = QLabel(f"{new_price:.2f} ₽")
    
    if discount > DISCOUNT_LIMIT:
        price_label.setStyleSheet(f"color: {DISCOUNT_COLOR}; font-weight: bold; font-size: 16px;")
        old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
        old_price_label.setStyleSheet("color: red; font-size: 12px;")
        old_price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        price_container.addWidget(old_price_label)
    else:
        price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32;")

    price_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    price_container.addWidget(price_label)
    card_layout.addLayout(price_container)

    card.setLayout(card_layout)
    card.setStyleSheet("""
        QWidget { border: 1px solid #CFD8DC; border-radius: 8px; background-color: #FAFAFA; padding: 5px; }
        QLabel { border: none; background: transparent; }
    """)
    return card


class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None):
        super().__init__()
        self.role_id = role_id          
        self.full_name = full_name      
        self.db = Database()
        self.products = self.db.get_products()

        self.setWindowTitle("Мир подкастов — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        # Вызов строго в таком порядке
        self.setup_ui()                 
        self.setup_role_interface()     

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        # Панель заголовка (Header Layout)
        header_layout = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap("resources/logo.png").scaled(
            60, 60, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        header_layout.addWidget(logo)
        header_layout.addStretch()

        text = f"ФИО: {self.full_name}" if self.full_name else "Гость"
        self.name_label = QLabel(text)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333333;")
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
        main_layout.addLayout(header_layout)

        # Панель кнопок ролей
        buttons_layout = QHBoxLayout()
        self.order_button = QPushButton("Купить подкаст")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

        # Список подкастов вынесен в изолированный контейнер каталога
        container = QWidget()
        list_layout = QVBoxLayout()
        list_layout.setSpacing(10)
        list_layout.setContentsMargins(5, 5, 5, 5)
        
        for product in self.products:
            list_layout.addWidget(create_card(product))
            
        list_layout.addStretch()
        container.setLayout(list_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.setStyleSheet("""
            QMainWindow, QWidget { font-family: Calibri; }
            QLabel { color: #000000; }
            QPushButton { 
                padding: 6px 12px; font-size: 13px; background-color: #F5F5F5; 
                border: 1px solid #B0BEC5; border-radius: 4px; 
            }
            QPushButton:hover { background-color: #E0E0E0; }
        """)

    def logout(self):
        reply = QMessageBox.question(
            self, "Выход", "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(Database())
            self.login_window.show()
            self.close()

    def setup_role_interface(self):
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()

        if self.role_id == 1:        
            self.admin_button.show()
            self.manager_button.show()
        elif self.role_id == 2:      
            self.manager_button.show()
        elif self.role_id == 3:      
            self.order_button.show()

        role_name = ROLE_NAMES.get(self.role_id, "Гость")
        self.setWindowTitle(f"Мир подкастов — Каталог ({role_name})")

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()


from login_window import LoginWindow

if __name__ == "__main__":
    app = QApplication([])
    db = Database()
    login = LoginWindow(db)
    login.show()
    app.exec()
