import re

# Token types - each is a unique string constant
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

# Control flow keywords
IF = "IF"
WHILE = "WHILE"
PRINT = "PRINT"
DO = "DO"
END = "END"

# Comparison operators
GT = "GT"
LT = "LT"
GE = "GE"
LE = "LE"
EQ = "EQ"

# Map reserved words to their token types (identifiers are checked against this)
KEYWORDS = {
    "if": IF,
    "while": WHILE,
    "print": PRINT,
    "do": DO,
    "end": END,
}

# Token patterns in priority order.
# Longer patterns (>=) come before shorter ones (>) to avoid incorrect matching.
token_specification = [
    (GE, r">="),
    (LE, r"<="),
    (EQ, r"=="),
    (GT, r">"),
    (LT, r"<"),
    (FLOAT, r"(\d+\.\d+|\d+\.|\.\d+)"),  # matches 3.14, 3., .5
    (INT, r"\d+"),  # matches 0, 42, 100
    (IDENT, r"[a-zA-Z_][a-zA-Z0-9_]*"),
    (PLUS, r"\+"),
    (MINUS, r"-"),
    (MUL, r"\*"),
    (DIV, r"/"),
    (ASSIGN, r"="),
    (LPAREN, r"\("),
    (RPAREN, r"\)"),
    ("SKIP", r"[ \t\r\n]+"),  # whitespace - ignored, not tokenized
]

# Pre-compile regex patterns for faster matching (compile once, use many times)
compiled_specs = [(t, re.compile(p)) for t, p in token_specification]


class Token:
    """Represents a single token with type and value."""

    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"{self.type}({self.value})"


def lexer(text):
    """
    Convert source code string into a list of tokens.

    Algorithm:
    1. Start at position 0
    2. Try each pattern in priority order at current position
    3. If match found: add token (skip whitespace), advance position, repeat
    4. If no match: illegal character error
    """
    tokens = []
    pos = 0

    while pos < len(text):
        match = None

        for tok_type, regex in compiled_specs:
            match = regex.match(text, pos)
            if match:
                value = match.group(0)

                if tok_type != "SKIP":  # ignore whitespace
                    # Check if identifier is actually a reserved keyword
                    if tok_type == IDENT and value in KEYWORDS:
                        tokens.append(Token(KEYWORDS[value], value))
                    else:
                        tokens.append(Token(tok_type, value))

                pos = match.end()
                break  # exit loop - token found at this position

        if not match:
            raise Exception(f"Illegal character: {repr(text[pos])}")

    return tokens
