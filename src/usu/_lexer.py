from enum import Enum
from textwrap import dedent
from typing import Any, Iterable, List

LPAREN = "("
RPAREN = ")"
USU_NEWLINE = ("\r", "\n")
USU_WS = frozenset((" ", "\t", *USU_NEWLINE))
DIGITS = frozenset((str(d) for d in range(0, 10)))


class TT(Enum):
    """Token Kind"""

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


def lex_value(src: str, inline: bool, last: Token) -> List[Token]:
    pos = 0
    tokens = []
    while pos < len(src):
        if src[pos] in ('"', "'", "`"):
            string = ""
            quote_char = src[pos]
            for c in src[pos + 1 :]:
                if c == quote_char:
                    pos += 1
                    break
                string += c
                pos += 1
            if quote_char == "`":
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

        elif last.value != LPAREN:
            tokens.append(Token(TT.STR, src.replace("\n", " ")))
            break

        else:
            end_chars = USU_WS if inline else USU_NEWLINE
            string = ""
            for c in src[pos:]:
                if c in end_chars:
                    break
                string += c
                pos += 1
            if string:
                tokens.append(Token(TT.STR, string))

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

        if c == LPAREN:
            tokens.append(Token(TT.SYNTAX, c))
            inline = True

        elif c == RPAREN:
            tokens.append(Token(TT.SYNTAX, c))
            inline = False

        elif c in USU_NEWLINE:
            inline = False

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

            value = value.rstrip("\n").rstrip()
            if value:
                if not inline:
                    value = dedent(value)
                tokens.extend(lex_value(value, inline=inline, last=tokens[-1]))

        pos += 1

    return tokens
