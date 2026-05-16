import pytest

from src.spoiler_helpers import (
    get_spoiler_answer_raw,
    get_spoiler_text_raw,
    is_spoiler_block_key,
    iter_uploadable_spoilers,
    spoiler_preview_summary,
)


@pytest.mark.parametrize(
    "key,expected",
    [
        ("Спойлер 1:", True),
        ("спойлер 2:", True),
        ("Спойлер1:", True),
        ("  Спойлер 12:  ", True),
        ("Спойлер 3", True),
        ("content", False),
        ("tables", False),
        ("Не спойлер 1:", False),
    ],
)
def test_is_spoiler_block_key(key, expected):
    assert is_spoiler_block_key(key) is expected


def test_iter_uploadable_spoilers_order_and_filter():
    spoilers = {
        "content": None,
        "Спойлер 1:": {
            "Текст:": {"content": " t "},
            "Ответы на спойлер:": {"content": " a "},
        },
        "Спойлер 2:": {
            "Текст:": {"content": "only text"},
            "Ответы на спойлер:": {"content": ""},
        },
        "Спойлер3:": {
            "Текст:": {"content": "x"},
            "Ответы на спойлер:": {"content": "y"},
        },
    }
    out = list(iter_uploadable_spoilers(spoilers))
    assert len(out) == 2
    assert out[0][0] == "Спойлер 1:"
    assert out[0][1] == "t"
    assert out[0][2] == "a"
    assert out[1][0] == "Спойлер3:"
    assert out[1][1] == "x"
    assert out[1][2] == "y"


def test_answer_fallback_subheading():
    sp = {
        "Текст:": {"content": "txt"},
        "Ответ на спойлер:": {"content": "ans"},
    }
    assert get_spoiler_text_raw(sp) == "txt"
    assert get_spoiler_answer_raw(sp) == "ans"


def test_spoiler_preview_summary():
    assert "уедет в движок 1" in spoiler_preview_summary(
        {
            "Спойлер 1:": {
                "Текст:": {"content": "a"},
                "Ответы на спойлер:": {"content": "b"},
            }
        }
    )
