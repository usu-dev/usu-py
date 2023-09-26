from __future__ import annotations

from typing import Any, Dict, List

from ._lexer import lex
from ._parser import parse


def loads(src: str) -> Dict[str, Any] | List[Any]:
    tokens = lex(src)
    return parse(tokens, root=True)[0]
