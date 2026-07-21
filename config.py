import os
from pathlib import Path

import requests
from loguru import logger

from dotenv import load_dotenv
load_dotenv("secrets/.env")



def check_config_files():
    has_error = False

    env_path = Path("secrets/.env")
    secrets_path = Path("secrets")
    if not secrets_path.exists():
        logger.warning("Папка secrets не найдена")
        logger.info("Создаю папку secrets")
        secrets_path.mkdir()
    if not env_path.exists():
        logger.warning("Файл .env не найден")
        logger.info("Создаю файл .env с настройками по умолчанию")
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("LOGIN=\nPASSWORD=\nGAME_ID=\nCITY=\n\nDOCUMENT_ID=\nFOLDER_ID=")
        has_error = True
    else:
        logger.info("Файл .env найден")
        if os.getenv("LOGIN") == "" or os.getenv("PASSWORD") == "" or os.getenv("GAME_ID") == "" or os.getenv("CITY") == "" or os.getenv("DOCUMENT_ID") == "" or os.getenv("FOLDER_ID") == "":
            logger.warning("В файле secrets/.env не все переменные окружения заполнены")
            has_error = True
        
    env_path = Path("secrets/credentials.json")
    if not env_path.exists():
        logger.error("Файл secrets/credentials.json не найден")
        has_error = True
    else:
        logger.info("Файл secrets/credentials.json найден")
    
    return has_error


LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

GAME_ID = os.getenv("GAME_ID")
CITY = os.getenv("CITY")
S_URL = f"https://classic.dzzzr.ru/{CITY}/admin/admin.php"
FILES_UPLOAD_URL = f"https://classic.dzzzr.ru/{CITY}/admin/tinymce/jscripts/tiny_mce/plugins/filemanager/stream/index.php"
DOCUMENT_ID = os.getenv("DOCUMENT_ID")
FOLDER_ID = os.getenv("FOLDER_ID")


def get_session():
    session = requests.Session()
    session.auth = (LOGIN, PASSWORD)

    return session
