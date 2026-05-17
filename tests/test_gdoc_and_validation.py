import importlib
import types

import src.gdoc as gdoc
import src.test_doc as test_doc
import src.download_files as download_files


def test_parse_content_handles_styles_and_tables():
    content = [
        {
            "paragraph": {
                "paragraphStyle": {"namedStyleType": "HEADING_1"},
                "elements": [
                    {"textRun": {"content": "Level Title"}},
                ],
            }
        },
        {
            "paragraph": {
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "elements": [
                    {"textRun": {"content": "Bold text", "textStyle": {"bold": True}}},
                    {"textRun": {"content": " and plain", "textStyle": {}}},
                ],
            }
        },
        {
            "table": {
                "tableRows": [
                    {
                        "tableCells": [
                            {
                                "content": [
                                    {
                                        "paragraph": {
                                            "elements": [{"textRun": {"content": "H1"}}]
                                        }
                                    }
                                ]
                            },
                            {
                                "content": [
                                    {
                                        "paragraph": {
                                            "elements": [{"textRun": {"content": "H2"}}]
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        "tableCells": [
                            {
                                "content": [
                                    {
                                        "paragraph": {
                                            "elements": [{"textRun": {"content": "R1"}}]
                                        }
                                    }
                                ]
                            },
                            {
                                "content": [
                                    {
                                        "paragraph": {
                                            "elements": [{"textRun": {"content": "R2"}}]
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                ]
            }
        },
    ]

    parsed = gdoc.parse_content(content)

    assert "Level Title" in parsed
    level_node = parsed["Level Title"]
    assert level_node["content"] == "<b>Bold text</b> and plain"
    assert level_node["tables"][0] == [["H1", "H2"], ["R1", "R2"]]


def test_parse_content_treats_missing_paragraph_style_as_body_text():
    """Google Docs often omits namedStyleType for default paragraphs — they must still parse."""
    content = [
        {
            "paragraph": {
                "paragraphStyle": {"namedStyleType": "HEADING_1"},
                "elements": [{"textRun": {"content": "Текст уровня:"}}],
            }
        },
        {
            "paragraph": {
                "paragraphStyle": {"namedStyleType": "HEADING_2"},
                "elements": [{"textRun": {"content": "Текст:"}}],
            }
        },
        {
            "paragraph": {
                "elements": [{"textRun": {"content": "Строка без namedStyleType в API."}}],
            }
        },
    ]

    parsed = gdoc.parse_content(content)
    assert parsed["Текст уровня:"]["Текст:"]["content"] == "Строка без namedStyleType в API."


def test_parse_content_inlines_google_doc_images():
    content = [
        {
            "paragraph": {
                "paragraphStyle": {"namedStyleType": "HEADING_1"},
                "elements": [{"textRun": {"content": "Текст уровня:"}}],
            }
        },
        {
            "paragraph": {
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "elements": [
                    {"textRun": {"content": "До картинки ", "textStyle": {}}},
                    {
                        "inlineObjectElement": {
                            "inlineObjectId": "img1",
                            "textStyle": {},
                        }
                    },
                    {"textRun": {"content": " после.", "textStyle": {}}},
                ],
            }
        },
    ]
    inline_objects = {
        "img1": {
            "inlineObjectProperties": {
                "embeddedObject": {
                    "imageProperties": {"contentUri": "https://googleusercontent.test/image"},
                    "size": {"width": {"magnitude": 640}},
                }
            }
        }
    }

    parsed = gdoc.parse_content(
        content,
        inline_objects=inline_objects,
        image_url_resolver=lambda _uri: "https://classic.dzzzr.ru/uploaded/moscow/Night/games/1559/image.jpg",
    )

    text = parsed["Текст уровня:"]["content"]
    assert "До картинки " in text
    assert " после." in text
    assert '<img style="width:640px;" src="https://classic.dzzzr.ru/uploaded/moscow/Night/games/1559/image.jpg">' in text


def test_test_doc_flags_missing_fields():
    invalid_data = [
        {
            "Broken": {
                "Сквозной:": {"content": "да"},
                "Текст уровня:": {
                    "Текст:": {"content": None},
                    "Примечания:": {"content": None},
                },
                "Подсказка 1:": {
                    "Текст:": {"content": None},
                    "Выдавать по запросу:": {"content": None},
                    "Штраф за использование:": {"content": None},
                },
                "Подсказка 2:": {
                    "Текст:": {"content": None},
                    "Выдавать по запросу:": {"content": None},
                    "Штраф за использование:": {"content": None},
                },
                "Комментарий и фото кодов:": {"content": None},
                "Основные коды уровня:": {
                    "tables": [
                        [
                            ["№", "Код", "КС", "Сектор"],
                            ["1", "", "", ""],
                        ]
                    ]
                },
                "Количество кодов для взятия:": {"Вышка:": {"content": None}},
                "Штраф за слив:": {"content": None},
                "Бонусный:": {"content": None},
                "Время до окончания уровня:": {"content": None},
            }
        }
    ]

    assert test_doc.test_doc(invalid_data, add=True) is True


class _FakeStatus:
    def __init__(self, progress):
        self._progress = progress

    def progress(self):
        return self._progress


class _FakeMediaDownloader:
    def __init__(self, stream, request):
        self.stream = stream
        self.done = False

    def next_chunk(self):
        if not self.done:
            self.stream.write(b"data")
            self.done = True
            return _FakeStatus(1.0), True
        return _FakeStatus(1.0), True


class _FakeService:
    class _Files:
        def list(self, q=None, fields=None):
            return self

        def execute(self):
            return {
                "files": [
                    {"id": "1", "name": "image.png", "mimeType": "image/png"},
                    {"id": "2", "name": "note.txt", "mimeType": "text/plain"},
                ]
            }

        def get_media(self, fileId=None):
            return {"fileId": fileId}

    def __init__(self):
        self._files = self._Files()

    def files(self):
        return self._files


def test_get_files_from_drive_downloads_images(monkeypatch):
    monkeypatch.setattr(download_files, "MediaIoBaseDownload", _FakeMediaDownloader)
    files = download_files.get_files_from_drive(_FakeService(), "folder")

    assert files == {"image.png": b"data"}
