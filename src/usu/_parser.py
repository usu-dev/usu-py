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
        value, tokens = parse(tokens)

        # TODO: only accept unique keys
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
    t = tokens.pop(0)
    next = tokens[0]

    if root and t.value != LPAREN:
        raise UsuDecodeError("Expected document to begin with left parenthesis")

    if t.value == LPAREN:
        if next.kind == TT.KEY:
            return parse_map(tokens)
        else:
            return parse_list(tokens)
    else:
        return t.value, tokens
