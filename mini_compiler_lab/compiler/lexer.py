import re
from dataclasses import dataclass
from typing import List


# ── Keywords ────────────────────────────────────────────────────────────────
KEYWORDS = {
    "int":    "INT",
    "float":  "FLOAT",
    "bool":   "BOOL",
    "string": "STRING_TYPE",
    "if":     "IF",
    "else":   "ELSE",
    "while":  "WHILE",
    "do":     "DO",
    "for":    "FOR",
    "cout":   "COUT",
    "true":   "TRUE",
    "false":  "FALSE",
}

# ── Token patterns (order matters — longer patterns come first) ──────────────
TOKEN_SPEC = [
    ("COMMENT",       r"//[^\n]*"),
    ("STRING",        r'"(?:\\.|[^"\\])*"'),
    ("NUMBER",        r"(?:\d+\.\d+|\d+)"),
    ("ID",            r"[A-Za-z_][A-Za-z0-9_]*"),

    # Multi-character operators (must precede single-char versions)
    ("LSHIFT",        r"<<"),
    ("INC",           r"\+\+"),
    ("DEC",           r"\-\-"),
    ("PLUS_ASSIGN",   r"\+="),
    ("MINUS_ASSIGN",  r"\-="),
    ("MUL_ASSIGN",    r"\*="),
    ("DIV_ASSIGN",    r"/="),
    ("EQ",            r"=="),
    ("NE",            r"!="),
    ("LE",            r"<="),
    ("GE",            r">="),
    ("AND",           r"&&"),
    ("OR",            r"\|\|"),

    # Arithmetic
    ("PLUS",          r"\+"),
    ("MINUS",         r"-"),
    ("MUL",           r"\*"),
    ("DIV",           r"/"),

    # Comparison
    ("LT",            r"<"),
    ("GT",            r">"),

    # Assignment / logic
    ("ASSIGN",        r"="),
    ("NOT",           r"!"),

    # Delimiters
    ("LPAREN",        r"\("),
    ("RPAREN",        r"\)"),
    ("LBRACE",        r"\{"),
    ("RBRACE",        r"\}"),
    ("SEMI",          r";"),
    ("COMMA",         r","),

    # Whitespace
    ("NEWLINE",       r"\n"),
    ("SKIP",          r"[ \t\r]+"),
]


@dataclass
class Token:
    kind:   str
    value:  str
    line:   int
    column: int


class LexicalError(Exception):
    def __init__(self, message, line, column, lexeme=""):
        super().__init__(message)
        self.message = message
        self.line    = line
        self.column  = column
        self.lexeme  = lexeme


class Lexer:
    def __init__(self, source: str):
        self.source = source

    def tokenize(self) -> List[Token]:
        tokens = []
        i, line, col = 0, 1, 1

        while i < len(self.source):
            chunk   = self.source[i:]
            matched = False

            for kind, pattern in TOKEN_SPEC:
                m = re.match(pattern, chunk)
                if not m:
                    continue

                matched = True
                text    = m.group(0)

                if kind == "NEWLINE":
                    line += 1
                    col   = 0
                elif kind in ("SKIP", "COMMENT"):
                    pass
                elif kind == "ID":
                    tokens.append(Token(KEYWORDS.get(text, "ID"), text, line, col))
                else:
                    tokens.append(Token(kind, text, line, col))

                i   += len(text)
                col += len(text)
                break

            if not matched:
                bad = self.source[i]
                raise LexicalError(f"Unexpected character '{bad}'", line, col, bad)

        tokens.append(Token("EOF", "", line, col))
        return tokens
