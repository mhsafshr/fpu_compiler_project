# compiler/lexer.py

import re

# توکن‌ها
NUMBER = "NUMBER"
IDENT = "IDENT"
PLUS = "PLUS"
MINUS = "MINUS"
MUL = "MUL"
DIV = "DIV"
ASSIGN = "ASSIGN"
LPAREN = "LPAREN"
RPAREN = "RPAREN"

# الگوهای توکن
token_specification = [
    (NUMBER, r"\d+(\.\d+)?"),
    (IDENT, r"[a-zA-Z_][a-zA-Z0-9_]*"),
    (PLUS, r"\+"),
    (MINUS, r"-"),
    (MUL, r"\*"),
    (DIV, r"/"),
    (ASSIGN, r"="),
    (LPAREN, r"\("),
    (RPAREN, r"\)"),
    # 🔥 مهم: پشتیبانی از فاصله + خط جدید
    ("SKIP", r"[ \t\r\n]+"),
]


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

        for tok_type, pattern in token_specification:
            regex = re.compile(pattern)
            match = regex.match(text, pos)

            if match:
                value = match.group(0)

                # skip whitespace
                if tok_type != "SKIP":
                    tokens.append(Token(tok_type, value))

                pos = match.end()
                break

        if not match:
            raise Exception(f"Illegal character: {repr(text[pos])}")

    return tokens
