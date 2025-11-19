import os
import json

import requests

from download_files import authenticate
from download_files import get_files_from_drive

from dotenv import load_dotenv
load_dotenv()




def upload_files_to_source():
    FOLDER_ID = os.getenv("FOLDER_ID")
    service = authenticate()
    print('Аутентификация успешна. Начинается скачивание...')
    files = get_files_from_drive(service, FOLDER_ID)
    print('Процесс скачивания завершен.')

    for file in files:
        pass


upload_files_to_source()