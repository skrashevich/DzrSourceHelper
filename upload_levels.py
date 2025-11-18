import os
import time
import json

import requests

from config import session
from config import G_URL
from config import S_URL
from config import GAME_ID
from utils import encode_text
from utils import upload_tech_level
from test_doc import test_doc



def upload_levels(add = True) -> None:
    print("Получаю данные из гугл дока")
    g_response = requests.get(G_URL)
    if g_response.status_code == 200:
        g_doc_datas = json.loads(g_response.text)
        print("Данные из гугл дока получены")
    else: 
        print("Ошибка загрузки данных из гугл дока\nПовтори через 30 секунд")
        time.sleep(30)
        return None

    if test_doc(g_doc_datas, add): 
        input("Есть ошибки в доке. Заливка невозможна\nНажми любую клавишу для продолжения")
        return None
        
    inp = input("Ошибок нет\n[1] Продолжить\n[3] Выйти в главное меню\n")
    os.system('cls' if os.name == 'nt' else 'clear')
    if int(inp) != 3:
        for g_doc_data in g_doc_datas:
            level_data = {}

            level_data["category"] = GAME_ID
            if add: level_data["action"] = "add_zadanie" 
            else: level_data["action"] = "update_zadanie"
            level_data["gZone"] = 0

            for title in g_doc_data:
                if not add: level_data["id"] = g_doc_data.get(title).get("ID Уровня:").get("content")
                level_data["title"] = encode_text(title)
                level_data["question"] = encode_text(g_doc_data.get(title).get("Текст уровня:").get("Текст:").get("content"))
                level_data["locationComment"] = encode_text(g_doc_data.get(title).get("Текст уровня:").get("Примечания:").get("content"))
                level_data["clue1"] = encode_text(g_doc_data.get(title).get("Подсказка 1:").get("Текст:").get("content"))
                level_data["clue2"] = encode_text(g_doc_data.get(title).get("Подсказка 2:").get("Текст:").get("content"))
                if g_doc_data.get(title).get("Сквозной:").get("content").lower() == "да": 
                    level_data["skvoz"] = "on"
                    if g_doc_data.get(title).get("Подсказка 1:").get("Выдавать по запросу:").get("content").lower() == "да":
                        level_data["zapros1"] = "on"
                        level_data["shtraf1"] = g_doc_data.get(title).get("Подсказка 1:").get("Штраф за использование:").get("content")
                    if g_doc_data.get(title).get("Подсказка 2:").get("Выдавать по запросу:").get("content").lower() == "да":
                        level_data["zapros2"] = "on"
                        level_data["shtraf2"] = g_doc_data.get(title).get("Подсказка 2:").get("Штраф за использование:").get("content")                 
                else:
                    level_data["ClueMin"] = g_doc_data.get(title).get("Подсказка 1:").get("Время до подсказки:").get("content")
                    level_data["ClueMin2"] = g_doc_data.get(title).get("Подсказка 2:").get("Время до подсказки:").get("content")
                    level_data["ClueMin3"] = g_doc_data.get(title).get("Время до окончания уровня:").get("content")
                level_data["comment"] = encode_text(g_doc_data.get(title).get("Комментарий и фото кодов:").get("content"))
                
                for i, code in enumerate(g_doc_data.get(title).get("Основные коды уровня:").get("tables")[0][1:]):
                    level_data[f"code[{i}]"] = encode_text(code[1])
                    level_data[f"danger[{i}]"] = code[2]
                    level_data[f"sector[{i}]"] = code[3]
                level_data["codeCount"] = g_doc_data.get(title).get("Количество кодов для взятия:").get("Вышка:").get("content")
                if g_doc_data.get(title).get("Сектора на уровне:"):
                    for i, sec in enumerate(g_doc_data.get(title).get("Сектора на уровне:").get("tables")[0][1:]):
                        level_data[f"secName[{i}]"] = encode_text(sec[1])
                if g_doc_data.get(title).get("Бонусные коды уровня:"):
                    for i, bonus in enumerate(g_doc_data.get(title).get("Бонусные коды уровня:").get("tables")[0][1:]):    
                        level_data[f"codeB[{i}]"] = encode_text(bonus[1])
                        level_data[f"dangerB[{i}]"] = bonus[2]
                        level_data[f"timeB[{i}]"] = bonus[3]
                    level_data["timeAddBonusAll"] = g_doc_data.get(title).get("Бонус за полное взятие:").get("content")
                if g_doc_data.get(title).get("Штрафные коды уровня:"):
                    for i, shtraf in enumerate(g_doc_data.get(title).get("Штрафные коды уровня:").get("tables")[0][1:]):    
                        level_data[f"codeF[{i}]"] = encode_text(shtraf[1])
                        level_data[f"fakeShtraf[{i}]"] = shtraf[2]
                
                if g_doc_data.get(title).get("Спойлеры:"):
                    for i, spoiler in enumerate(g_doc_data.get(title).get("Спойлеры:")):
                        level_data[f"spoiler[{i+1}]"] = encode_text(g_doc_data.get(title).get("Спойлеры:").get(f"Спойлер {i+1}:").get("Текст:").get("content"))
                        level_data[f"spoilerCode[{i+1}]"] = encode_text(g_doc_data.get(title).get("Спойлеры:").get(f"Спойлер {i+1}:").get("Ответы на спойлер:").get("content"))   
                
                level_data["penalty"] = g_doc_data.get(title).get("Штраф за слив:").get("content")
                
                if g_doc_data.get(title).get("Бонусный:").get("content").lower() == "да": 
                    level_data["bonus"] = "on"
                    level_data["bonusTime"] = g_doc_data.get(title).get("Бонусный:").get("Время бонуса:").get("content")

            if int(level_data["id"]) == 0:
                continue
            print(f"Заливаю уровень {level_data["title"].decode('cp1251')}")
            headers = {
                "accept-language": "ru,en;q=0.9,de;q=0.8",
                "content-type": "application/x-www-form-urlencoded; charset=windows-1251",
            }
            s_resp = session.post(S_URL, headers=headers, data=level_data)
        if add:
            upload_tech_level()

        input("Загрузка завершена\nНажми любую клавишу для продолжения")
    else:
        return None