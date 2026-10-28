from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox)


class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None
        self.role_id = None
        self.full_name = None  

        self.setWindowTitle("Авторизация")
        self.resize(300, 220)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Логин:"))

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        self.guest_button = QPushButton("Войти как гость")
        self.guest_button.clicked.connect(self.login_as_guest)
        layout.addWidget(self.guest_button)

        self.setLayout(layout)

    def check_login(self):
        login = self.login_input.text().strip()

        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return

        # ЗАДАНИЕ 7.1: Вызов обновленного метода из базы данных
        result = self.db.get_user_by_login(login)

        if result is None:
            QMessageBox.warning(self, "Ошибка", "Неверный логин")
        else:
            self.user_id = result[0]
            self.role_id = result[1]
            
            # ЗАДАНИЕ 7.1: Безопасная сборка ФИО из полученного среза таблицы users
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
