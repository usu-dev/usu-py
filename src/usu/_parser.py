from __future__ import annotations

from typing import Any, Dict, List

from ._lexer import LCLOSE, LOPEN, MCLOSE, MOPEN, TK, Token


class UsuDecodeError(ValueError):
    """An error raise if a document is not valid usu."""


def parse_map(tokens: List[Token]):
    usu_map = dict()

    t, next_usu = tokens[0], tokens[1]

    if t.value == MCLOSE:
        return usu_map, tokens[1:]

    while True:
        usu_key = tokens.pop(0)

        if usu_key.kind != TK.KEY:
            raise UsuDecodeError(f"Expected to find key but got: {usu_key.value}")

        if next_usu.kind == TK.KEY:
            raise UsuDecodeError(f"Missing value for key: {usu_key.value}")

        value, tokens = parse(tokens)

        if usu_key.value in usu_map:
            raise UsuDecodeError(
                "Keys must be unique, " f"found duplicate entries for {usu_key.value}"
            )

        usu_map[usu_key.value] = value

        t = tokens[0]
        if t.value == MCLOSE:
            return usu_map, tokens[1:]


def parse_list(tokens):
    usu_list = []

    t = tokens[0]
    if t.value == LCLOSE:
        return usu_list, tokens[1:]

    while True:
        usu, tokens = parse(tokens)
        usu_list.append(usu)

        t = tokens[0]
        if t.value == LCLOSE:
            return usu_list, tokens[1:]
        elif t.kind == TK.KEY:
            raise UsuDecodeError(f"Unexpected key in list {t.value}")

    raise UsuDecodeError("Expected list to end with right paranthesis")


def parse(tokens: List[Token], root: bool = False) -> List | Dict[str, Any]:
    if tokens and tokens[0].value == MCLOSE:
        # FIXME: no parens
        raise UsuDecodeError("Unexpected closing paranthesis encountered")

    t = tokens.pop(0)
    next = tokens[0]

    if root and t.value not in {MOPEN, LOPEN}:
        # FIXME: no parens
        raise UsuDecodeError("Expected document to begin with left parenthesis")

    if t.kind not in {TK.KEY, TK.SYNTAX}:
        return t.value, tokens

    if next.kind == TK.KEY or next.value == MCLOSE:
        value, tokens = parse_map(tokens)
    else:
        value, tokens = parse_list(tokens)

    return value, tokens
