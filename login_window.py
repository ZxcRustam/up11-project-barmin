from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox)

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
        padding: 6px 12px;
    }
    QPushButton:hover {
        background-color: #5B9A97;
    }
"""


class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None
        self.role_id = None
        self.full_name = None  

        self.setWindowTitle("Авторизация")
        self.resize(300, 220)
        
        # Общие стили для окна авторизации (Задание 2.1 и 3.1)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: Calibri;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                border: 1px solid #B0BEC5;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Логин:"))

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)

        self.login_button = QPushButton("Войти")
        self.login_button.setStyleSheet(BUTTON_STYLE)  # Применяем акцентный цвет (Задание 4.1)
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        self.guest_button = QPushButton("Войти как гость")
        self.guest_button.setStyleSheet(BUTTON_STYLE)  # Применяем акцентный цвет (Задание 4.1)
        self.guest_button.clicked.connect(self.login_as_guest)
        layout.addWidget(self.guest_button)

        self.setLayout(layout)

    def check_login(self):
        login = self.login_input.text().strip()

        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return

        result = self.db.get_user_by_login(login)

        if result is None:
            QMessageBox.warning(self, "Ошибка", "Неверный логин")
        else:
            self.user_id = result[0]
            self.role_id = result[1]
            self.full_name = " ".join(p for p in result[2:5] if p)

            from main import MainWindow
            self.main_window = MainWindow(role_id=self.role_id, full_name=self.full_name)
            self.main_window.show()
            self.close()

    def login_as_guest(self):
        from main import MainWindow
        self.main_window = MainWindow(role_id=None, full_name="Гость")
        self.main_window.show()
        self.close()
