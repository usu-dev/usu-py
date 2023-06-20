from typing import Any, Dict, List

from ._lexer import LPAREN, RPAREN, TT, Token


class UsuDecodeError(ValueError):
    """An error raise if a document is not valid usu."""


def parse_map(tokens: List[Token]):
    usu_map = dict()

    t, next = tokens[0], tokens[1]
    if t.value is None and next.value == RPAREN:
        return usu_map, tokens[2:]

    while True:
        key = tokens.pop(0).value

        if next.kind == TT.KEY:
            UsuDecodeError(f"Missing value for key: {key}")

        value, tokens = parse(tokens)

        if key in usu_map:
            UsuDecodeError(f"Keys must be unique, found duplicate entries for {key}")

        usu_map[key] = value

        t = tokens[0]
        if t.value == RPAREN:
            return usu_map, tokens[1:]


def parse_list(tokens):
    usu_list = []

    t = tokens[0]
    if t.value == RPAREN:
        return usu_list, tokens[1:]

    while True:
        usu, tokens = parse(tokens)
        usu_list.append(usu)

        t = tokens[0]
        if t.value == RPAREN:
            return usu_list, tokens[1:]

    raise UsuDecodeError("Expected list to end with right paranthesis")


def parse(tokens: List[Token], root: bool = False) -> List | Dict[str, Any]:
    if tokens and tokens[0].value == RPAREN:
        raise UsuDecodeError("Unexpected closing paranthesis encountered")

    t = tokens.pop(0)
    next = tokens[0]

    if root and t.value != LPAREN:
        raise UsuDecodeError("Expected document to begin with left parenthesis")

    if t.kind not in {TT.KEY, TT.SYNTAX}:
        return t.value, tokens

    if next.kind == TT.KEY:
        value, tokens = parse_map(tokens)
    else:
        value, tokens = parse_list(tokens)

    return value, tokens
