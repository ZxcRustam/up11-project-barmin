USERS_IN_DB = ["admin", "manager1", "manager2", "client01", "client02"]  # логины из таблицы users


def check_login(login):
    # Проверка в БД: ищем логин среди пользователей
    if login in USERS_IN_DB:
        return "Вход разрешён"
    else:
        return "Ошибка: неверный логин"


print(check_login("admin"))     # Вход разрешён
print(check_login("hacker"))    # Ошибка: неверный логин
