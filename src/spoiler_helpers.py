"""Разбор блоков спойлеров из структуры Google Docs (устойчиво к вариациям заголовков)."""
from __future__ import annotations

import re
from typing import Any, Iterator, Optional

from src.gdoc_const import SPOILER_ANSWERS, TEXT

# «Спойлер 1:», «Спойлер1:», без обязательного пробела после слова «Спойлер»
_SPOILER_HEADING_RE = re.compile(r"^\s*спойлер\s*\d+\s*:?\s*$")


def is_spoiler_block_key(key: Any) -> bool:
    if not isinstance(key, str) or key == "content":
        return False
    return _SPOILER_HEADING_RE.match(key.strip().casefold()) is not None


def _nonempty_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _dict_content(node: Any) -> Any:
    if isinstance(node, dict):
        return node.get("content")
    return None


def get_spoiler_text_raw(sp_node: Any) -> Optional[str]:
    if not isinstance(sp_node, dict):
        return None
    r = _nonempty_str(_dict_content(sp_node.get(TEXT)))
    if r is not None:
        return r
    for subk, subv in sp_node.items():
        if subk == "content" or not isinstance(subv, dict):
            continue
        if subk.strip().casefold().startswith("текст"):
            r = _nonempty_str(_dict_content(subv))
            if r is not None:
                return r
    return None


def get_spoiler_answer_raw(sp_node: Any) -> Optional[str]:
    if not isinstance(sp_node, dict):
        return None
    r = _nonempty_str(_dict_content(sp_node.get(SPOILER_ANSWERS)))
    if r is not None:
        return r
    for subk, subv in sp_node.items():
        if subk in ("content", TEXT) or not isinstance(subv, dict):
            continue
        lk = subk.casefold()
        if "ответ" in lk and "спойлер" in lk:
            r = _nonempty_str(_dict_content(subv))
            if r is not None:
                return r
    return None


def iter_uploadable_spoilers(spoilers: Optional[dict]) -> Iterator[tuple[str, str, str]]:
    """Пары текст+ответ (непустые) для отправки в админку, в порядке ключей в документе."""
    if not spoilers:
        return
    for key in spoilers:
        if not is_spoiler_block_key(key):
            continue
        sp = spoilers.get(key)
        if not isinstance(sp, dict):
            continue
        text = get_spoiler_text_raw(sp)
        answer = get_spoiler_answer_raw(sp)
        if text is None or answer is None:
            continue
        yield key, text, answer


def spoiler_preview_summary(spoilers: Optional[dict]) -> str:
    """Краткая строка для превью: сколько уйдёт в движок и что в документе."""
    if not spoilers or not isinstance(spoilers, dict):
        return "нет секции «Спойлеры:»"

    blocks = complete = partial = empty = 0
    for key in spoilers:
        if not is_spoiler_block_key(key):
            continue
        sp = spoilers.get(key)
        if not isinstance(sp, dict):
            continue
        blocks += 1
        te = get_spoiler_text_raw(sp)
        ae = get_spoiler_answer_raw(sp)
        t_ok = te is not None
        a_ok = ae is not None
        if t_ok and a_ok:
            complete += 1
        elif t_ok or a_ok:
            partial += 1
        else:
            empty += 1

    if blocks == 0:
        return "нет блоков «Спойлер N:»"
    parts = [f"уедет в движок {complete}"]
    if partial:
        parts.append(f"неполных {partial}")
    if empty:
        parts.append(f"пустых {empty}")
    return f"{', '.join(parts)} из {blocks} в документе"
