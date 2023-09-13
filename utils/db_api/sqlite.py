import sqlite3
from src.config import DIR

DATABASE = f"{DIR}/DB.sqlite"


def ignore_case_collation(value1_, value2_):
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1


def connect_db():
    """
    Создание подключения к БД
    :return:
    """

    return sqlite3.connect(DATABASE)


def open_db():
    """
    Проверка и создание таблиц в БД при первом запуске
    :return:
    """
    with connect_db() as db:
        db.create_collation("NOCASE", ignore_case_collation)
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS UserList ("
                    "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    "surname TEXT COLLATE NOCASE,"
                    "name TEXT COLLATE NOCASE,"
                    "patronymic TEXT COLLATE NOCASE,"
                    "post TEXT COLLATE NOCASE,"
                    "project TEXT COLLATE NOCASE COLLATE NOCASE,"
                    "picture TEXT,"
                    "date TEXT)")

        cur.execute("CREATE TABLE IF NOT EXISTS Params ("
                    "key TEXT,"
                    "value TEXT)")

        if len(cur.execute("SELECT * FROM Params").fetchall()) == 0:
            param_list = [
                ("hello_message", "Добро пожаловать, @{username}"),
                ("comeback_message", "С возвращением, @{username}"),

            ]
            cur.executemany("INSERT INTO Params (key, value) VALUES (?, ?)", param_list)


open_db()


def get_param(key):
    """
    Получение параметра по ключу

    :param key: ключ
    :return: значение ключа
    """
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM Params WHERE key = ?", [key]).fetchone()[1]


def add_name(user_id, name):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE UserList SET name = ? WHERE id = ?", [name, user_id])


def add_surname(user_id, surname):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE UserList SET surname = ? WHERE id = ?", [surname, user_id])


def add_patronymic(user_id, patronymic):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE UserList SET patronymic = ? WHERE id = ?", [patronymic, user_id])


def add_post(user_id, post):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE UserList SET post = ? WHERE id = ?", [post, user_id])


def add_project(user_id, project):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE UserList SET project = ? WHERE id = ?", [project, user_id])


def add_picture(user_id, picture):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("UPDATE UserList SET picture = ? WHERE id = ?", [picture, user_id])


def add_worker(data):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("INSERT INTO UserList (name, surname, patronymic, post, project, picture, date)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [data['name'], data['surname'], data['patronymic'],
                     data['post'], data['project'], data['photo'], data['date']])


def get_all_workers():
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM UserList", []).fetchall()


def get_worker_on_id(user_id):
    with connect_db() as db:
        cur = db.cursor()
        return cur.execute("SELECT * FROM UserList WHERE id = ?", [user_id]).fetchone()


def delete_worker_on_id(user_id):
    with connect_db() as db:
        cur = db.cursor()
        cur.execute("DELETE FROM UserList WHERE id = ?", [int(user_id)])


def get_workers_on_key(key, column):
    if column == "name":
        with connect_db() as db:
            db.create_collation("NOCASE", ignore_case_collation)
            cur = db.cursor()
            return cur.execute("SELECT * FROM UserList WHERE name = ? COLLATE NOCASE", [key]).fetchall()
    elif column == "surname":
        with connect_db() as db:
            db.create_collation("NOCASE", ignore_case_collation)
            cur = db.cursor()
            return cur.execute("SELECT * FROM UserList WHERE surname = ? COLLATE NOCASE", [key]).fetchall()
    elif column == "name_surname":
        key.split(" ")
        with connect_db() as db:
            db.create_collation("NOCASE", ignore_case_collation)
            cur = db.cursor()
            return cur.execute("SELECT * FROM UserList WHERE surname = ? "
                               "AND name = ? COLLATE NOCASE", [key[0], key[1]]).fetchall()
    elif column == "post":
        with connect_db() as db:
            db.create_collation("NOCASE", ignore_case_collation)
            cur = db.cursor()
            return cur.execute("SELECT * FROM UserList WHERE post = ? COLLATE NOCASE", [key]).fetchall()
    elif column == "project":
        with connect_db() as db:
            db.create_collation("NOCASE", ignore_case_collation)
            cur = db.cursor()
            return cur.execute("SELECT * FROM UserList WHERE project = ? COLLATE NOCASE", [key]).fetchall()
