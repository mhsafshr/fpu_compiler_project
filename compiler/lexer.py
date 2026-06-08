import re

INT = "INT"
FLOAT = "FLOAT"
IDENT = "IDENT"
PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
DIV = "DIV"
ASSIGN = "ASSIGN"
LPAREN = "LPAREN"
RPAREN = "RPAREN"

IF = "IF"
WHILE = "WHILE"
PRINT = "PRINT"
DO = "DO"
END = "END"

GT = "GT"
LT = "LT"
GE = "GE"
LE = "LE"
EQ = "EQ"

KEYWORDS = {
    "if": IF,
    "while": WHILE,
    "print": PRINT,
    "do": DO,
    "end": END,
}

token_specification = [
    (GE, r">="),
    (LE, r"<="),
    (EQ, r"=="),
    (GT, r">"),
    (LT, r"<"),
    (FLOAT, r"(\d+\.\d+|\d+\.|\.\d+)"),
    (INT, r"\d+"),
    (IDENT, r"[a-zA-Z_][a-zA-Z0-9_]*"),
    (PLUS, r"\+"),
    (MINUS, r"-"),
    (MUL, r"\*"),
    (DIV, r"/"),
    (ASSIGN, r"="),
    (LPAREN, r"\("),
    (RPAREN, r"\)"),
    ("SKIP", r"[ \t\r\n]+"),
]

compiled_specs = [(t, re.compile(p)) for t, p in token_specification]


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"


def lexer(text):
    tokens = []
    pos = 0

    while pos < len(text):
        match = None

        for tok_type, regex in compiled_specs:
            match = regex.match(text, pos)

            if match:
                value = match.group(0)

                if tok_type != "SKIP":
                    if tok_type == IDENT and value in KEYWORDS:
                        tokens.append(Token(KEYWORDS[value], value))
                    else:
                        tokens.append(Token(tok_type, value))

                pos = match.end()
                break

        if not match:
            raise Exception(f"Illegal character: {repr(text[pos])}")

    return tokens
