from enum import Enum
from textwrap import dedent
from typing import Any, Iterable, List

LPAREN = "("
RPAREN = ")"
PIPE = "|"
FOLD = ">"
USU_SYNTAX = frozenset((LPAREN, RPAREN, PIPE, FOLD))
USU_NEWLINE = ("\r", "\n")
QUOTES = frozenset(('"', "'", "`"))
TRUE = frozenset(("True", "true"))
FALSE = frozenset(("False", "false"))
USU_WS = frozenset((" ", "\t", *USU_NEWLINE))
DIGITS = frozenset((str(d) for d in range(0, 10)))


class TT(Enum):
    """Token Kind"""

    BOOL = "bool"
    STR = "str"
    INT = "int"
    FLOAT = "float"
    SYNTAX = "syntax"
    KEY = "key"


class Token:
    def __init__(self, kind: TT, value: Any):
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


def lex_str_bool(string: str) -> Token:
    if string in TRUE:
        return Token(TT.BOOL, True)
    elif string in FALSE:
        return Token(TT.BOOL, False)
    else:
        return Token(TT.STR, string)


def lex_str() -> Token:
    pass


def lex_number() -> Token:
    pass


def lex_value(src: str, inline: bool, tokens: List[Token]) -> List[Token]:
    pos = 0
    src = dedent(src)
    if fold := tokens[-1].value == FOLD:
        src = src.replace("\n", " ")
        tokens.pop(-1)

    list_mode = "(" in [t.value for t in tokens[-1:]]
    if src[pos] not in {*DIGITS, *QUOTES} and not list_mode:
        if not fold:
            if src.lower() not in {*TRUE, *FALSE} and "\n" in src:
                src = src.strip() + "\n"
            tokens.append(lex_str_bool(src))
        else:
            tokens.append(lex_str_bool(src.lstrip()))
        return tokens

    while pos < len(src):
        if (quote := src[pos]) in QUOTES:
            string = ""
            for c in src[pos + 1 :]:
                pos += 1
                if c == quote:
                    break
                string += c
            string = dedent(string.lstrip("\n"))

            tokens.append(Token(TT.STR, string))

        elif src[pos] in DIGITS:
            num = ""
            for c in src[pos:]:
                num += c

                if c in USU_WS:
                    break

                pos += 1

            if "." in num:
                tokens.append(Token(TT.FLOAT, float(num)))
            else:
                tokens.append(Token(TT.INT, int(num)))

        else:
            end_chars = USU_WS if (inline or fold) else USU_NEWLINE
            print(end_chars)
            string = ""
            for c in src[pos:]:
                if c in end_chars:
                    break
                string += c
                pos += 1

            if not string:
                pos += 1
                continue
            tokens.append(lex_str_bool(string.strip()))

        pos += 1
    return tokens


def lex(src: str):
    inline = False
    tokens = []
    pos = 0
    src = dedent(src)
    pos = skip_chars(src, pos, USU_WS)

    while True:
        try:
            c = src[pos]
        except IndexError:
            break

        if c in USU_NEWLINE:
            inline = False

        elif c in USU_SYNTAX:
            tokens.append(Token(TT.SYNTAX, c))

            if c == RPAREN:
                inline = False

            elif c == LPAREN:
                inline = True

        elif c == ":":
            key = ""
            while (c := src[pos + 1]) not in {*USU_WS, RPAREN}:
                key += c
                pos += 1

            pos += 1
            if c != RPAREN:
                key = key
                tokens.append(Token(TT.KEY, key))
            else:
                tokens.append(Token(TT.KEY, None))
                tokens.append(Token(TT.SYNTAX, RPAREN))

        elif c == "#":
            pos = skip_comment(src, pos)

        else:
            value = ""
            for c in src[pos:]:
                if c in (*RPAREN, ":", "#"):
                    pos -= 1
                    break
                value += c
                pos += 1

            value = value.lstrip("\n").rstrip()
            if value:
                tokens = lex_value(value, inline=inline, tokens=tokens)

        pos += 1

    return tokens
