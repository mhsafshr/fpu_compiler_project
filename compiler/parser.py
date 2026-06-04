from compiler.ast import Number, Var, BinOp, Assign, Program, If, While


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token_type):
        if self.current() and self.current().type == token_type:
            self.pos += 1
        else:
            raise Exception(f"Expected {token_type}, got {self.current()}")

    # ---------------- FACTOR ----------------
    def factor(self):
        token = self.current()

        if token is None:
            raise Exception("Unexpected end of input")

        if token.type == "NUMBER":
            self.eat("NUMBER")
            return Number(token.value)

        elif token.type == "IDENT":
            self.eat("IDENT")
            return Var(token.value)

        elif token.type == "LPAREN":
            self.eat("LPAREN")
            node = self.comparison()
            self.eat("RPAREN")
            return node

        raise Exception(f"Invalid syntax near {token}")

    # ---------------- TERM ----------------
    def term(self):
        node = self.factor()

        while self.current() and self.current().type in ("MUL", "DIV"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.factor())

        return node

    # ---------------- EXPR ----------------
    def expr(self):
        node = self.term()

        while self.current() and self.current().type in ("PLUS", "MINUS"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.term())

        return node

    # ---------------- COMPARISON ----------------
    def comparison(self):
        node = self.expr()

        while self.current() and self.current().type in ("GT", "LT", "GE", "LE", "EQ"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.expr())

        return node

    # ---------------- STATEMENT (FIXED FOR MULTI-STATEMENT BODY) ----------------
    def statement(self):

        # ---------- IF ----------
        if self.current() and self.current().type == "IF":
            self.eat("IF")
            condition = self.comparison()
            then_body = self.parse_block()
            else_body = None
            if self.current() and self.current().type == "ELSE":
                self.eat("ELSE")
                else_body = self.parse_block()
            return If(condition, then_body, else_body)

        # ---------- WHILE (FIXED: reads multiple statements as body) ----------
        if self.current() and self.current().type == "WHILE":
            self.eat("WHILE")
            condition = self.comparison()
            body = self.parse_block()  # خواندن بلاک چند statement
            return While(condition, body)

        # ---------- ASSIGNMENT ----------
        if (
            self.current()
            and self.current().type == "IDENT"
            and self.pos + 1 < len(self.tokens)
            and self.tokens[self.pos + 1].type == "ASSIGN"
        ):
            name = self.current().value
            self.eat("IDENT")
            self.eat("ASSIGN")
            value = self.comparison()
            return Assign(name, value)

        # ---------- EXPRESSION ----------
        return self.comparison()

    # ---------------- NEW: PARSE BLOCK (multiple statements until next keyword) ----------------
    def parse_block(self):
        """خواندن یک بلاک از statements تا رسیدن به while بعدی، if بعدی، یا end of input"""
        statements = []

        while self.current() is not None:
            # اگر به کلیدواژه‌های جدید رسیدیم، توقف کن (مال بلاک بعدی هستند)
            if self.current().type in ["WHILE", "IF", "ELSE"]:
                break

            # خواندن یک statement
            statements.append(self.statement())

        return statements

    # ---------------- PROGRAM ----------------
    def parse_program(self):
        statements = []

        while self.current() is not None:
            statements.append(self.statement())

        return Program(statements)


def parse(tokens):
    parser = Parser(tokens)
    return parser.parse_program()
