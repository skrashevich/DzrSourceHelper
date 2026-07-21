from loguru import logger
import questionary

from config import S_URL
from config import GAME_ID
from config import get_session
from src.gdoc import get_gdoc
from src.gdoc_const import *
from src.utils import encode_text
from src.test_doc import test_doc_data, test_encoding, test_codes_repeat
from src.test_doc import test_doc_headers
from src.upload_files import upload_files_to_source
from src.spoiler_helpers import iter_uploadable_spoilers, spoiler_preview_summary



def upload_tech_level() -> bool:
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


    logger.info("Заливаю технический уровень")
    headers = {
    "accept-language": "ru,en;q=0.9,de;q=0.8",
    "content-type": "application/x-www-form-urlencoded; charset=windows-1251",
    }
    session = get_session()
    s_resp = session.post(S_URL, data=tec_level, headers=headers)
    if s_resp.status_code != 200:
        logger.warning(f"Технический уровень не залит")
        logger.warning(f"Код ошибки {s_resp.status_code}")
        return True
    else:
        logger.success(f"Технический уровень залит")
        return False


def _log_levels_preview(g_doc_datas, add: bool) -> None:
    logger.info("────────── Сводка перед заливкой ──────────")
    n = 0
    for g_doc_data in g_doc_datas:
        for title in g_doc_data:
            n += 1
            node = g_doc_data[title]
            if add:
                level_id = "новый"
            else:
                raw_id = (node.get(LEVEL_ID) or {}).get(CONTENT)
                level_id = raw_id if raw_id not in (None, "") else "—"
            sk = (node.get(SKVOZ) or {}).get(CONTENT) or "?"
            bonus = (node.get(BONUS) or {}).get(CONTENT) or "?"
            mc = node.get(MAIN_CODES)
            n_codes = 0
            if mc and mc.get(TABLES) and mc[TABLES]:
                n_codes = max(0, len(mc[TABLES][0]) - 1)
            sp_line = spoiler_preview_summary(node.get(SPOILERS))
            logger.info(
                f" {n}. «{title}» | ID: {level_id} | сквозной: {sk} | бонус: {bonus} | "
                f"кодов (осн.): {n_codes} | спойлеры: {sp_line}"
            )
    if add:
        logger.info("После перечисленных уровней будет добавлен технический уровень.")
    logger.info("──────────────────────────────────────────")


def upload_levels(add = True) -> None:
    if questionary.confirm("Загрузить файлы из гугл диска в движок?", default=False).ask():
        upload_files_to_source()

    logger.info("Получаю данные из гугл дока")
    g_doc_datas = get_gdoc()
    if g_doc_datas is None:
        logger.error(
            "Данные из Google Docs не получены (проверьте DOCUMENT_ID в secrets/.env — "
            "это ID из URL документа; сервисный аккаунт должен иметь доступ к файлу)."
        )
        return None
    logger.success("Данные из гугл дока получены")

    if test_doc_headers(g_doc_datas):
        logger.warning("Есть ошибки в заголовках дока. Заливка невозможна")
        return None
    logger.success("Ошибок в заголовках дока нет")

    if test_doc_data(g_doc_datas, add): 
        logger.warning("Есть ошибки в данных дока. Заливка невозможна")
        return None
    logger.success("Ошибок данных дока нет")

    if test_encoding(g_doc_datas):
        logger.warning("Есть ошибки в перекодировании дока. Заливка невозможна")
        return None
    logger.success("Ошибок перекодирования дока нет")

    if test_codes_repeat(g_doc_datas):
        logger.warning("Есть повторяющиеся коды в доке. Заливка невозможна")
        return None
    logger.success("Повторяющихся кодов в доке нет")

    _log_levels_preview(g_doc_datas, add)

    if questionary.confirm("Продолжить?", default=False).ask():
        has_error = False
        for g_doc_data in g_doc_datas:
            level_data = {}

            level_data["category"] = GAME_ID
            if add: level_data["action"] = "add_zadanie" 
            else: level_data["action"] = "update_zadanie"
            level_data["gZone"] = 0

            for title in g_doc_data:
                if not add: level_data["id"] = g_doc_data.get(title).get(LEVEL_ID).get(CONTENT)
                level_data["title"] = encode_text(title)
                level_data["question"] = encode_text(g_doc_data.get(title).get(LEVEL_TEXT).get(TEXT).get(CONTENT))
                level_data["locationComment"] = encode_text(g_doc_data.get(title).get(LEVEL_TEXT).get(NOTES).get(CONTENT))
                level_data["clue1"] = encode_text(g_doc_data.get(title).get(HINT1).get(TEXT).get(CONTENT))
                level_data["clue2"] = encode_text(g_doc_data.get(title).get(HINT2).get(TEXT).get(CONTENT))
                if g_doc_data.get(title).get(SKVOZ).get(CONTENT).lower() == "да": 
                    level_data["skvoz"] = "on"
                    if g_doc_data.get(title).get(HINT1).get(HINT_CONFIRM).get(CONTENT).lower() == "да":
                        level_data["zapros1"] = "on"
                        level_data["shtraf1"] = g_doc_data.get(title).get(HINT1).get(PENALTY_FOR_USE).get(CONTENT)
                    if g_doc_data.get(title).get(HINT2).get(HINT_CONFIRM).get(CONTENT).lower() == "да":
                        level_data["zapros2"] = "on"
                        level_data["shtraf2"] = g_doc_data.get(title).get(HINT2).get(PENALTY_FOR_USE).get(CONTENT)                 
                else:
                    level_data["ClueMin"] = g_doc_data.get(title).get(HINT1).get(HINT_TIME).get(CONTENT)
                    level_data["ClueMin2"] = g_doc_data.get(title).get(HINT2).get(HINT_TIME).get(CONTENT)
                    level_data["ClueMin3"] = g_doc_data.get(title).get(TIME_TO_AP).get(CONTENT)
                level_data["comment"] = encode_text(g_doc_data.get(title).get(COMMENTS_AND_PHOTOS).get(CONTENT))

                for i, code in enumerate(g_doc_data.get(title).get(MAIN_CODES).get(TABLES)[0][1:]):
                    level_data[f"code[{i}]"] = encode_text(code[1])
                    level_data[f"danger[{i}]"] = code[2]
                    level_data[f"sector[{i}]"] = code[3]
                level_data["codeCount"] = g_doc_data.get(title).get(CODES_NEEDED).get(MAJOR).get(CONTENT)
                if g_doc_data.get(title).get(SECTORS):
                    for i, sec in enumerate(g_doc_data.get(title).get(SECTORS).get(TABLES)[0][1:]):
                        level_data[f"secName[{i}]"] = encode_text(sec[1])
                if g_doc_data.get(title).get(BONUS_CODES):
                    for i, bonus in enumerate(g_doc_data.get(title).get(BONUS_CODES).get(TABLES)[0][1:]):    
                        level_data[f"codeB[{i}]"] = encode_text(bonus[1])
                        level_data[f"dangerB[{i}]"] = bonus[2]
                        level_data[f"timeB[{i}]"] = bonus[3]
                    level_data["timeAddBonusAll"] = g_doc_data.get(title).get(FULL_CAPT_BONUS).get(CONTENT)
                if g_doc_data.get(title).get(FAKE_CODES):
                    for i, shtraf in enumerate(g_doc_data.get(title).get(FAKE_CODES).get(TABLES)[0][1:]):    
                        level_data[f"codeF[{i}]"] = encode_text(shtraf[1])
                        level_data[f"fakeShtraf[{i}]"] = shtraf[2]
                
                if g_doc_data.get(title).get(SPOILERS):
                    # DozoR expects spoiler fields to start from 1; spoiler[0] is ignored/empty.
                    for spoiler_ix, (_sk, text_raw, code_raw) in enumerate(
                        iter_uploadable_spoilers(g_doc_data.get(title).get(SPOILERS)),
                        start=1,
                    ):
                        level_data[f"spoiler[{spoiler_ix}]"] = encode_text(text_raw)
                        level_data[f"spoilerCode[{spoiler_ix}]"] = encode_text(code_raw)
                
                level_data["penalty"] = g_doc_data.get(title).get(PENALTY).get(CONTENT)
                
                if g_doc_data.get(title).get(BONUS).get(CONTENT).lower() == "да": 
                    level_data["bonus"] = "on"
                    level_data["bonusTime"] = g_doc_data.get(title).get(BONUS).get(BONUS_TIME).get(CONTENT)

            if not add and int(level_data["id"]) == 0:
                continue
            
            logger.info(f"Заливаю уровень '{level_data["title"].decode('cp1251')}'")
            headers = {
                "accept-language": "ru,en;q=0.9,de;q=0.8",
                "content-type": "application/x-www-form-urlencoded; charset=windows-1251",
            }
            session = get_session()
            s_resp = session.post(S_URL, headers=headers, data=level_data)
            if s_resp.status_code != 200:
                logger.warning(f"Уровень '{level_data["title"].decode('cp1251')}' не залит")
                logger.warning(f"Код ошибки {s_resp.status_code}")
                has_error = True
            else:
                logger.success(f"Уровень '{level_data["title"].decode('cp1251')}' залит")
        
        if add:
            has_error = upload_tech_level()
        
        if has_error:
            logger.warning("Загрузка завершена с ошибками")
        else:
            logger.success("Загрузка завершена без ошибок")

        questionary.text("Нажми любую клавишу для продолжения").ask()
    else:
        return None