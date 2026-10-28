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
    QWidget
)

from database import Database


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
        QLabel {
            border: none;
            background: transparent;
        }
    """)
    return card


# ЗАДАНИЕ 5.1: Обновленный класс главного окна с поддержкой роли пользователя
class MainWindow(QMainWindow):
    def __init__(self, role_id=None):
        super().__init__()
        self.role_id = role_id  # Сохраняем ID роли
        
        self.db = Database()
        self.products = self.db.get_products()

        self.setWindowTitle("Мир подкастов — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        container = QWidget()
        list_layout = QVBoxLayout()
        list_layout.setSpacing(10)
        list_layout.setContentsMargins(15, 15, 15, 15)

        for product in self.products:
            list_layout.addWidget(create_card(product))
            
        list_layout.addStretch()
        container.setLayout(list_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        self.setCentralWidget(scroll)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
            QLabel {
                color: #000000;
                font-family: Calibri;
            }
        """)

    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()


# ЗАДАНИЕ 5.1: Измененный блок запуска всего приложения
from login_window import LoginWindow

if __name__ == "__main__":
    app = QApplication([])
    db = Database()
    
    # Сначала открываем и показываем окно авторизации
    login = LoginWindow(db)
    login.show()
    
    app.exec()
