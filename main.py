from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget

# Задание 4.1: Импортируем пул из database.py
from database import Database


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Создаем пул соединений с базой данных MySQL
        self.db = Database()

        self.setWindowTitle("Мир подкастов — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))

        central = QWidget()
        layout = QVBoxLayout()

        logo = QLabel()
        logo.setPixmap(QPixmap("resources/logo.png"))
        logo.setScaledContents(False)  # не искажаем пропорции
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        central.setLayout(layout)
        self.setCentralWidget(central)

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

    # Задание 4.1: Метод вызывается автоматически при нажатии на крестик
    def closeEvent(self, event):
        if self.db:
            self.db.close_all()  # Безопасно закрываем пул
        event.accept()  # Разрешаем окну закрыться


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
