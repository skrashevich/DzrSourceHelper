import os
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import GAME_ID
from utils import rgb_to_hex

from dotenv import load_dotenv
load_dotenv()


# Функция для рекурсивного удаления пустых content
def remove_empty_content(node):
    if isinstance(node, dict):
        # Если это узел с content
        if 'content' in node:
            node['content'] = node['content'].rstrip()
            # Проверяем, пустой ли content (только пробелы или переносы строк)
            if not node['content'].strip():
                del node['content']
        
        if 'tables' in node:
            # Удаляем полностью пустые таблицы
            node['tables'] = [table for table in node['tables'] 
                                if any(any(cell.strip() for cell in row) for row in table)]
            # Если после фильтрации список таблиц пуст, удаляем его
            if not node['tables']:
                del node['tables']

        # Рекурсивно обрабатываем все дочерние элементы
        for key in list(node.keys()):
            if key != 'content':
                remove_empty_content(node[key])
                
                # Если после обработки дочерний элемент стал пустым, удаляем его
                if isinstance(node[key], dict) and not node[key]:
                    del node[key]
        

def extract_table_data(table_element):
    """Извлекает данные таблицы в виде многомерного массива"""
    table_data = []
    
    for row in table_element.get('tableRows', []):
        row_data = []
        for cell in row.get('tableCells', []):
            cell_text = ""
            # Обрабатываем все элементы содержимого ячейки
            for content_elem in cell.get('content', []):
                if 'paragraph' in content_elem:
                    paragraph = content_elem['paragraph']
                    for elem in paragraph.get('elements', []):
                        if 'textRun' in elem:
                            cell_text += elem['textRun'].get('content', '')
            row_data.append(cell_text.strip())
        table_data.append(row_data)
    
    return table_data


def set_text_style(element):
    text_out = ""
    if element.get("textRun").get("textStyle") != {}:
        if element.get("textRun").get("textStyle").get("bold"):
            text_buffer = f"<b>{element['textRun'].get('content')}</b>"
            if text_out == "":
                text_out = text_buffer
            else:
                text_out = f"<b>{text_out}</b>"
        if element.get("textRun").get("textStyle").get("italic"):
            text_buffer = f"<i>{element['textRun'].get('content')}</i>"
            if text_out == "":
                text_out = text_buffer
            else:
                text_out = f"<i>{text_out}</i>"
        if element.get("textRun").get("textStyle").get("underline"):
            text_buffer = f"<u>{element['textRun'].get('content')}</u>"
            if text_out == "":
                text_out = text_buffer
            else:
                text_out = f"<u>{text_out}</u>"
        if element.get("textRun").get("textStyle").get("strikethrough"):
            text_buffer = f"<s>{element['textRun'].get('content')}</s>"
            if text_out == "":
                text_out = text_buffer
            else:
                text_out = f"<s>{text_out}</s>"
        if element.get("textRun").get("textStyle").get("link"):
            text_buffer = f"<a href=\"{element.get("textRun").get("textStyle").get("link").get("url")}\">{element['textRun'].get('content')}</a>"
            if text_out == "":
                text_out = text_buffer
            else:
                text_out = f"<a href=\"{element.get("textRun").get("textStyle").get("link").get("url")}\">{text_out}</a>"
        if element.get("textRun").get("textStyle").get("foregroundColor"):
            red = element.get("textRun").get("textStyle").get("foregroundColor").get("color").get("rgbColor").get("red")
            green = element.get("textRun").get("textStyle").get("foregroundColor").get("color").get("rgbColor").get("green")
            blue = element.get("textRun").get("textStyle").get("foregroundColor").get("color").get("rgbColor").get("blue")
            text_buffer = f"<span color:\"{rgb_to_hex(red, green, blue)}\">{element['textRun'].get('content')}</span>"
            if text_out == "":
                text_out = text_buffer
            else:
                text_out = f"<span color:\"{rgb_to_hex(red, green, blue)}\">{text_out}</span>"
        return text_out
    
    return element['textRun'].get('content', '')


def set_rich_link(element):
    SOURCE_FILES_URL = f"https://classic.dzzzr.ru/uploaded/moscow/Night/games/{GAME_ID}"
    if "image" in element.get("richLink").get("richLinkProperties").get("mimeType"):
        IMG_URL = f"{SOURCE_FILES_URL}/{element.get("richLink").get("richLinkProperties").get("title")}"
        return f"<a href=\"{IMG_URL}\"><img src=\"{IMG_URL}\"></a>"
    else:
        return f"<a href=\"{element.get("richLink").get("richLinkProperties").get("uri")}\">{element.get("richLink").get("richLinkProperties").get("title")}</a>"
    

def parse_content(content):
    result = {}
    stack = [{'node': result, 'level': 0}]  # Стек для отслеживания текущего уровня
    
    for item in content:
        if 'paragraph' in item:
            paragraph = item['paragraph']
            style_type = paragraph.get('paragraphStyle', {}).get('namedStyleType', '')
            if style_type.startswith('HEADING'):
                # Определяем уровень заголовка
                level = int(style_type.split('_')[1])
                
                # Извлекаем текст заголовка
                heading_text = ''
                for element in paragraph.get('elements', []):
                    if 'textRun' in element:
                        heading_text += element['textRun'].get('content', '')
                
                # Убираем лишние пробелы и переносы строк только для ключей
                heading_text = heading_text.strip()
                
                # Находим правильного родителя в стеке (уровень меньше текущего)
                while stack and stack[-1]['level'] >= level:
                    stack.pop()
                
                # Создаем новый узел для заголовка
                current_parent = stack[-1]['node']
                new_node = {'content': ''}  # Теперь content - строка, а не массив
                current_parent[heading_text] = new_node
                
                # Добавляем в стек
                stack.append({'node': new_node, 'level': level})
                
            elif style_type == "NORMAL_TEXT":
                # Обычный текст - добавляем к текущему узлу
                if stack:
                    text_content = ''
                    for element in paragraph.get('elements', []):
                        if 'textRun' in element:
                            text_content += set_text_style(element)#element['textRun'].get('content', '')
                        if 'richLink' in element:
                            text_content += set_rich_link(element)

                    current_node = stack[-1]['node']
                    # Добавляем текст к существующей строке, сохраняя переносы
                    if current_node['content']:
                        current_node['content'] += text_content
                    else:
                        current_node['content'] = text_content
        elif 'table' in item:
            # Обрабатываем таблицу
            table_data = extract_table_data(item['table'])
            if stack and table_data:
                current_node = stack[-1]['node']
                # Добавляем таблицу в текущий узел
                if 'tables' not in current_node:
                    current_node['tables'] = []
                current_node['tables'].append(table_data)
    
    # Удаляем пустые content из результата
    remove_empty_content(result)
    
    return result


def get_gdoc():
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    DOCUMENT_ID = os.getenv("DOCUMENT_ID")
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('docs', 'v1', credentials=credentials)

    document = service.documents().get(documentId=DOCUMENT_ID, includeTabsContent=True).execute()
    
    tabs = []
    for tab in document.get('tabs')[3:]:
        tabs.append({f'{tab.get('tabProperties').get('title')}': parse_content(tab.get('documentTab').get('body').get('content')[1:])})
    
    return tabs


if __name__ == "__main__":
    print(get_gdoc())