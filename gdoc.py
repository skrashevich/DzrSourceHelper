from pprint import pprint
import json
import enum

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import GAME_ID
from utils import rgb_to_hex
from utils import struct_gdoc_data


SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DOCUMENT_ID = '1fZI8-dhf4HFQxLeP84WKP-_YtiZTd8Ofv_lur7rpP1U'
SERVICE_ACCOUNT_FILE = 'credentials.json'

FILES_FOLDER_LNK = f'https://classic.dzzzr.ru/uploaded/moscow/Night/games/{GAME_ID}/'

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('docs', 'v1', credentials=credentials)


document = service.documents().get(documentId=DOCUMENT_ID, includeTabsContent=True).execute()
tabs = []
for tab in document.get('tabs')[3:]:
    tabs.append({f'{tab.get('tabProperties').get('title')}': struct_gdoc_data(tab.get('documentTab').get('body').get('content')[1:])})
with open("test.json", "w", encoding="utf-8") as f:
    json.dump(tabs, f, indent=4, ensure_ascii=False)


# print(text_content)
# if element.get('textRun'):
#     if element.get('textRun').get('content') == '\n':
#         txt_out += element.get('textRun').get('content')
#     if element.get('textRun').get('textStyle').get('foregroundColor'):
#         hex_color = rgb_to_hex(
#             GDoc.get_red(element),
#             GDoc.get_greed(element),
#             GDoc.get_blue(element)
#         )
#         txt_out += f'<span color:"{hex_color}">{element.get('textRun').get('content').strip()}</span>'
#     else:
#         txt_out += element.get('textRun').get('content').strip()
# if element.get('richLink'):
#     if 'image' in element.get('richLink').get('richLinkProperties').get('mimeType'):
#         txt_out += f'{FILES_FOLDER_LNK}{element.get('richLink').get('richLinkProperties').get('title')}'
#     else:
#         txt_out += f'<a href="{element.get('richLink').get('richLinkProperties').get('uri')}">{element.get('richLink').get('richLinkProperties').get('title')}</a>'

# input(...)