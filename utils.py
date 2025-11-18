from datetime import datetime
from pprint import pprint

import requests

from config import GAME_ID
from config import S_URL
from config import session



def encode_text(text: str) -> str:
    return text.replace("\n", "<br>") \
               .replace("\ufeff", "") \
               .replace("”", "\"") \
               .encode("windows-1251")


def send_log_message(log: str) -> None:
    TOKEN = "5522451121:AAFsK7BuiYxN07sWo8eTzwlnj-KQ6BQYPok"
    ADMIN_ID = 411775595
    
    resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={ADMIN_ID}&text={str(datetime.now())}\n```{log}```&parse_mode=markdown")


def rgb_to_hex(r, g, b) -> str:
    if r == None: r = 0
    if g == None: g = 0
    if b == None: b = 0

    r = round(r * 255)
    g = round(g * 255)
    b = round(b * 255)

    return f'#{r:02x}{g:02x}{b:02x}'


def upload_tech_level() -> None:
    tec_level = {}
    tec_level["category"] = GAME_ID
    tec_level["action"] =  "add_zadanie"
    tec_level["gZone"] = 0
    tec_level["title"] = "Технический уровень".encode("windows-1251")
    tec_level["question"] = """<p>Это техническая заглушка</p>
<script src="../../uploaded/msk/Night/jquery-1.11.2.min.txt"></script>
<script src="../../uploaded/msk/Night/jquery.cookie.txt"></script>
<script type="text/javascript">// <![CDATA[
$(document).ready(function() {
  $.ajax({ url: "https://alt.where.games/initn.js?v=1", dataType: "script", cache: true, });
});
// ]]></script>""".encode("windows-1251")
    tec_level["clue1"] = "-"
    tec_level["clue2"] = "-"
    tec_level["comment"] = "-"
    tec_level["code[0]"] = 456457643867837433636
    tec_level["danger[0]"] = "null"
    tec_level["bonus"] = "on"
    tec_level["skvoz"] = "on"


    headers = {
    "accept-language": "ru,en;q=0.9,de;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=windows-1251",
    }
    session.post(S_URL, data=tec_level, headers=headers)


def struct_gdoc_data(gdoc_data):
    
    root = {}
    stack = [root]
    heading_levels = {
        "HEADING_1": 1,
        "HEADING_2": 2,
        "HEADING_3": 3,
        "HEADING_4": 4,
        "HEADING_5": 5,
        "HEADING_6": 6,
        "NORMAL_TEXT": 0,
        1: "HEADING_1",
        2: "HEADING_2",
        3: "HEADING_3",
        4: "HEADING_4",
        5: "HEADING_5",
        6: "HEADING_6"
    }
    current_level = 1
    current_heading_name = ""
    new_content_block = {}
    for element in gdoc_data:
        if element.get("paragraph"):
            current_heading_type = element.get("paragraph").get("paragraphStyle").get("namedStyleType")
            if heading_levels.get(element.get("paragraph").get("paragraphStyle").get("namedStyleType")) > current_level:
                current_level = heading_levels.get(element.get("paragraph").get("paragraphStyle").get("namedStyleType"))
                current_heading_type = element.get("paragraph").get("paragraphStyle").get("namedStyleType")
                current_heading_name = element.get("paragraph").get("elements")[0].get("textRun").get("content").strip()
                new_content_block = {
                    current_heading_name: ""
                }
            else:
                if current_heading_type != "NORMAL_TEXT":
                    new_content_block[current_heading_name] = ""
                else:
                    for text_element in element.get("paragraph").get("elements"):
                        new_content_block[current_heading_name] += text_element.get("textRun").get("content")
        #             print(element)
        #             print(0)
        # print("---------------------------------------------")
        print(new_content_block)
        input(...)


    return gdoc_data