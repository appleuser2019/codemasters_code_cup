import os

DIR = os.path.abspath(__file__)[:-14]


def create_folder(src):
    """
    Проверка/создание папки с путём src

    :param src: путь к папке
    :return:
    """
    if not os.path.exists(src):
        os.mkdir(src)
