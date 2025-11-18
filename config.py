import configparser

import requests



config = configparser.ConfigParser()  
is_exist = config.read("config.ini", encoding="utf-8")


if is_exist == []:
    print("Не найден файл config.ini")
    input("Нажмите любую клавишу для выхода из программы")
    exit()

LOGIN = config["Source"]["Login"]
print(f"Логин: {LOGIN}")
PASSWORD = config["Source"]["Password"]
print(f"Пароль: {PASSWORD}")
S_URL = config["Source"]["S_Url"]
print(f"Ссылка на админку: {S_URL}")
GAME_ID = config["Source"]["Game_Id"]
print(f"ID Игры: {GAME_ID}")

G_URL = config["Docs"]["G_Url"]
print(f"Ссылка на гуглдок: {G_URL}")

session = requests.Session()
session.auth = (LOGIN, PASSWORD)
