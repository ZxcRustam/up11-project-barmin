import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, 
    QScrollArea, QVBoxLayout, QWidget, QPushButton, QMessageBox
)

from database import Database
from src.logic.discount import calculate_price

ROLE_NAMES = {1: "Администратор", 2: "Менеджер", 3: "Покупатель", None: "Гость"}

DISCOUNT_LIMIT = 15
DISCOUNT_COLOR = "#2E8B57"

# Фирменный стиль для кнопок (Задание 4.1)
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
    QPushButton:hover {
        background-color: #5B9A97;
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
    (product_id, name, category_id, studio, old_price_raw, image_path, total_quantity) = product

    card = QWidget()
    card_layout = QHBoxLayout()

    image_label = QLabel()
    cover_pixmap = load_cover(image_path)
    image_label.setPixmap(cover_pixmap.scaled(
        100, 100, 
        Qt.AspectRatioMode.KeepAspectRatio, 
        Qt.TransformationMode.SmoothTransformation
    ))
    image_label.setFixedSize(100, 100)
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
    def __init__(self, role_id=None, full_name=None):
        super().__init__()
        self.role_id = role_id          
        self.full_name = full_name      
        self.db = Database()
        self.products = self.db.get_products()

        self.setWindowTitle("Мир подкастов — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        # ЗАДАНИЯ 2.1 и 3.1: Основной белый фон и фирменный шрифт Calibri для QMainWindow
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
        """)

        self.setup_ui()                 
        self.setup_role_interface()     

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # --- ЗАДАНИЕ 3.1 и 5.1: Создание header_widget с дополнительным фоном ---
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #D2F6E7;")  # Дополнительный светло-зеленый фон
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)

        # Логотип (Задание 5.1)
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/logo.png")
        logo_label.setPixmap(logo_pixmap.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        logo_label.setScaledContents(False)  # Пропорции не искажены
        header_layout.addWidget(logo_label)

        header_layout.addStretch()

        text = f"ФИО: {self.full_name}" if self.full_name else "Гость"
        self.name_label = QLabel(text)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2C3E50; background: transparent;")
        header_layout.addWidget(self.name_label)

        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet(BUTTON_STYLE)  # Бирюзовая кнопка (Задание 4.1)
        header_layout.addWidget(self.logout_button)
        
        main_layout.addWidget(header_widget)  # Добавляем виджет шапки в основной слой
        # -----------------------------------------------------------------------

        # Панель кнопок ролей
        buttons_widget = QWidget()
        buttons_widget.setStyleSheet("background: transparent;")
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(15, 5, 15, 5)
        
        self.order_button = QPushButton("Купить подкаст")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        # Применяем бирюзовый стиль ко всем кнопкам ролей (Задание 4.1)
        self.order_button.setStyleSheet(BUTTON_STYLE)
        self.manager_button.setStyleSheet(BUTTON_STYLE)
        self.admin_button.setStyleSheet(BUTTON_STYLE)
        self.logout_button.clicked.connect(self.logout)
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addStretch()
        main_layout.addWidget(buttons_widget)

        # Контейнер каталога подкастов
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        list_layout = QVBoxLayout()
        list_layout.setSpacing(10)
        list_layout.setContentsMargins(15, 5, 15, 15)
        
        for product in self.products:
            list_layout.addWidget(create_card(product))
            
        list_layout.addStretch()
        container.setLayout(list_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        main_layout.addWidget(scroll)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

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
