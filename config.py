import os

import requests

from dotenv import load_dotenv
load_dotenv()



LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

GAME_ID = os.getenv("GAME_ID")
S_URL = os.getenv("S_URL")
DOCUMENT_ID = os.getenv("DOCUMENT_ID")

def get_session():
    session = requests.Session()
    session.auth = (LOGIN, PASSWORD)

    return session
