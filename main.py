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

# Импортируем пул соединений с базой данных
from database import Database


# --- ЗАДАНИЕ 6.1: Самостоятельная функция загрузки обложки подкаста ---
def load_cover(image_path):
    """Возвращает обложку подкаста из ресурсов или стандартную заглушку, если файла нет"""
    if image_path:
        full_path = os.path.join("resources", image_path)
        if os.path.exists(full_path):
            pixmap = QPixmap(full_path)
            if not pixmap.isNull():
                return pixmap
                
    # Если путь пустой, файла нет на диске или он поврежден — возвращаем заглушку
    return QPixmap(os.path.join("resources", "picture.png"))


# --- ЗАДАНИЕ 4 и 6.1: Функция создания карточки подкаста ---
def create_card(product):
    # Распаковываем кортеж по структуре нашего MySQL-запроса
    (product_id, name, category_id, studio, price, image_path, total_quantity) = product

    card = QWidget()
    card_layout = QHBoxLayout()

    # Блок изображения: вызываем нашу самостоятельную функцию load_cover
    image_label = QLabel()
    cover_pixmap = load_cover(image_path)
    
    # Масштабируем обложку (100х100) с сохранением пропорций и сглаживанием
    image_label.setPixmap(cover_pixmap.scaled(
        100, 100, 
        Qt.AspectRatioMode.KeepAspectRatio, 
        Qt.TransformationMode.SmoothTransformation
    ))
    image_label.setFixedSize(100, 100)
    card_layout.addWidget(image_label)

    # Текстовые подписи, адаптированные под тему «Мир подкастов» (по центру)
    text_layout = QVBoxLayout()
    
    title_label = QLabel(f"{studio} | {name}")
    title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1A237E;")
    text_layout.addWidget(title_label)
    
    text_layout.addWidget(QLabel(f"ID Категории: {category_id}"))
    text_layout.addWidget(QLabel(f"Доступно для покупки: {int(total_quantity)} лицензий"))
    
    card_layout.addLayout(text_layout)

    # Цена подкаста (справа)
    price_label = QLabel(f"{price} ₽")
    price_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E7D32;")
    price_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    card_layout.addWidget(price_label)

    card.setLayout(card_layout)
    
    # Оформление границ карточки подкаста
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


# --- ГЛАВНОЕ ОКНО ПРИЛОЖЕНИЯ ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Подключаем БД и вытаскиваем записи
        self.db = Database()
        self.products = self.db.get_products()

        self.setWindowTitle("Мир подкастов — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        # Создаем контейнер для размещения списка карточек
        container = QWidget()
        list_layout = QVBoxLayout()
        list_layout.setSpacing(10)
        list_layout.setContentsMargins(15, 15, 15, 15)

        # Проходим циклом по всем подкастам из MySQL
        for product in self.products:
            list_layout.addWidget(create_card(product))
            
        list_layout.addStretch()  # Прижимаем карточки к верху
        container.setLayout(list_layout)

        # Настраиваем область прокрутки (Scroll Area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        
        self.setCentralWidget(scroll)

        # Глобальные стили шрифтов и бэкграунда
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

    # Автоматическое закрытие ресурсов пула при выходе из приложения
    def closeEvent(self, event):
        if self.db:
            self.db.close_all()
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
