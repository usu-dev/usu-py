from __future__ import annotations

from enum import Enum
from textwrap import dedent
from typing import Any, Iterable, List, Set

from ._errors import UsuDecodeError

MOPEN = "{"
MCLOSE = "}"
LOPEN = "["
LCLOSE = "]"
FOLD = ">"
USU_SYNTAX = frozenset((MOPEN, MCLOSE, LOPEN, LCLOSE))
USU_NEWLINE = ("\r", "\n")
QUOTES = frozenset(('"', "'", "`"))
TRUE = frozenset(("True", "true"))
FALSE = frozenset(("False", "false"))
USU_WS = frozenset((" ", "\t", *USU_NEWLINE))
DIGITS = frozenset((str(d) for d in range(0, 10)))


class TK(Enum):
    """Token Kind"""

    BOOL = "bool"
    STR = "str"
    INT = "int"
    FLOAT = "float"
    NULL = "null"
    SYNTAX = "syntax"
    KEY = "key"


class Flags(Enum):
    INLINE = 1
    FOLD = 2


class Token:
    def __init__(self, kind: TK, value: Any):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return f"(kind:{self.kind}, value:`{self.value}`)"


def skip_chars(src: str, pos: int, chars: Iterable[str]) -> int:
    try:
        while src[pos] in chars:
            pos += 1
    except IndexError:
        pass
    return pos


def skip_comment(src: str, pos: int) -> int:
    try:
        if src[pos + 1] == "(":
            while src[pos : pos + 2] != ")#":
                pos += 1
        while src[pos] not in ("\n", "\r"):
            pos += 1
    except IndexError:
        pass
    return pos


def lex_str_bool_null(string: str) -> Token:
    if string in TRUE:
        return Token(TK.BOOL, True)
    elif string in FALSE:
        return Token(TK.BOOL, False)
    elif string == "null":
        return Token(TK.NULL, None)
    else:
        return Token(TK.STR, string)


def lex_quoted_str(pos, src, end_char):
    string = ""
    pos += 1
    while True:
        try:
            c = src[pos]
        except IndexError:
            raise UsuDecodeError("Quoted string literal missing final quote")

        if c == end_char:
            string = dedent(string.lstrip("\n"))
            return pos, Token(TK.STR, string)

        if c == "\\":
            pos += 1
            c = src[pos]
        string += c
        pos += 1


def lex_unquoted_str(pos, src, flags, inside_list):
    string = ""
    end_chars = {*USU_SYNTAX, ":", "#"}
    if inside_list:
        end_chars |= {*USU_NEWLINE}
    if {Flags.FOLD, Flags.INLINE} & flags and inside_list:
        end_chars |= USU_WS
    preceed = src[pos - 1]
    for c in src[pos:]:
        if c in end_chars:
            if c in {":", *USU_SYNTAX, "#"}:
                pos -= 1
            break

        string += c
        pos += 1

    string = dedent(string.rstrip(" " if preceed == "\n" else " \n\t")).lstrip()
    if Flags.FOLD in flags:
        string = string.replace("\n", " ").strip()
    return pos, string


def lex_number(pos, src) -> Token:
    num = ""
    for c in src[pos:]:
        if c in {*USU_WS, LCLOSE, MCLOSE}:
            pos -= 1
            break
        else:
            num += c
        pos += 1

    if "." in num:
        token = Token(TK.FLOAT, float(num))
    else:
        token = Token(TK.INT, int(num))

    return pos, token


def lex_value(pos, src: str, flags: Set[Flags], tokens: List[Token]) -> List[Token]:
    inside_list = LOPEN in (t.value for t in tokens[-2:])
    while True:
        if inside_list:
            pos = skip_chars(src, pos, USU_WS)
        try:
            c = src[pos]
        except IndexError:
            break

        if c in {*USU_SYNTAX, ":", "#"}:
            break
        elif c in QUOTES:
            pos, token = lex_quoted_str(pos, src, c)
            tokens.append(token)
        elif c in {*DIGITS, "-"}:
            pos, token = lex_number(pos, src)
            tokens.append(token)
        else:
            pos, string = lex_unquoted_str(pos, src, flags, inside_list)
            if string:
                tokens.append(lex_str_bool_null(string))
        pos += 1
    pos -= 1
    return pos, tokens


def lex(src: str):
    tokens = []
    flags: Set[Flags] = set()
    pos = 0
    src = dedent(src)
    pos = skip_chars(src, pos, USU_WS)

    while True:
        try:
            c = src[pos]
        except IndexError:
            break

        if c in {*USU_NEWLINE}:
            flags -= {Flags.INLINE}

        if c == FOLD:
            flags |= {Flags.FOLD}

        if c in {*USU_SYNTAX, ":"}:
            flags -= {Flags.FOLD}

        if c in {*USU_NEWLINE, FOLD}:
            pos += 1
            continue

        if c in {MOPEN, LOPEN}:
            flags |= {Flags.INLINE}
            tokens.append(Token(TK.SYNTAX, c))
            pos = skip_chars(src, pos + 1, {" ", "\t"})
            continue

        elif c in USU_SYNTAX:
            tokens.append(Token(TK.SYNTAX, c))

        elif c == ":":
            key = ""
            while (c := src[pos + 1]) not in {*USU_WS, MCLOSE}:
                key += c
                pos += 1

            pos += 1
            # NOTE: I think this code is outdated
            if c != MCLOSE:
                tokens.append(Token(TK.KEY, key))
            else:
                tokens.append(Token(TK.KEY, None))
                tokens.append(Token(TK.SYNTAX, MCLOSE))

        elif c == "#":
            pos = skip_comment(src, pos)

        else:
            pos, tokens = lex_value(pos, src, flags=flags, tokens=tokens)

        pos += 1

    if tokens[-1].kind not in {TK.KEY, TK.SYNTAX}:
        pos = skip_chars(src, pos, USU_WS)

    if tokens[0].kind == TK.KEY:
        tokens = [Token(TK.SYNTAX, "{"), *tokens, Token(TK.SYNTAX, "}")]
    return tokens
