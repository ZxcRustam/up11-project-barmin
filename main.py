import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QPushButton
)

# Импортируем пул соединений с базой данных
from database import Database

# ЗАДАНИЕ 6.1: Словарь соответствия ID ролей и их названий для вашей темы подкастов
ROLE_NAMES = {1: "Администратор", 2: "Менеджер", 3: "Покупатель", None: "Гость"}


def load_cover(image_path):
    if image_path:
        full_path = os.path.join("resources", image_path)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                return pixmap
    return QPixmap(os.path.join("resources", "picture.png"))


def create_card(product):
    (product_id, name, category_id, studio, price, image_path, total_quantity) = product

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

    price_label = QLabel(f"{price} ₽")
    price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32;")
    price_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    card_layout.addWidget(price_label)

    card.setLayout(card_layout)
    card.setStyleSheet("""
        QWidget {
            border: 1px solid #CFD8DC;
            border-radius: 8px;
            background-color: #FAFAFA;
            padding: 5px;
        }
        QLabel { border: none; background: transparent; }
    """)
    return card


# --- ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ С АДАПТИРОВАННЫМИ РОЛЯМИ ---
class MainWindow(QMainWindow):
    def __init__(self, role_id=None):
        super().__init__()
        self.role_id = role_id          
        self.db = Database()
        self.products = self.db.get_products()

        # Базовый заголовок, который изменится в setup_role_interface
        self.setWindowTitle("Мир подкастов — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        self.setup_ui()                 
        self.setup_role_interface()     

    # ЗАДАНИЕ 6.1: Подписи кнопок изменены под автоматизацию продаж подкастов
    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()
        self.order_button = QPushButton("Купить подкаст")  # Изменили подпись
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)

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
                padding: 6px 12px; 
                font-size: 13px; 
                background-color: #F5F5F5; 
                border: 1px solid #B0BEC5; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #E0E0E0; }
        """)

    # ЗАДАНИЕ 6.1: Адаптированный метод с динамическим изменением заголовка роли подкастов
    def setup_role_interface(self):
        # По умолчанию скрываем все элементы управления
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()

        # Накатываем права видимости кнопок на основе ID роли
        if self.role_id == 1:        # Администратор
            self.admin_button.show()
            self.manager_button.show()
        elif self.role_id == 2:      # Менеджер
            self.manager_button.show()
        elif self.role_id == 3:      # Покупатель
            self.order_button.show()

        # Динамически меняем заголовок окна в зависимости от роли из словаря ROLE_NAMES
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
