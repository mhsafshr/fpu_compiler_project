from compiler.ast import Number, Var, BinOp, Assign, Program


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
            raise Exception(f"Expected {token_type}")

    # ---------- expressions ----------

    def factor(self):
        token = self.current()

        if token.type == "NUMBER":
            self.eat("NUMBER")
            return Number(token.value)

        elif token.type == "IDENT":
            self.eat("IDENT")
            return Var(token.value)

        elif token.type == "LPAREN":
            self.eat("LPAREN")
            node = self.expr()
            self.eat("RPAREN")
            return node

        raise Exception("Invalid syntax")

    def term(self):
        node = self.factor()

        while self.current() and self.current().type in ("MUL", "DIV"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.current() and self.current().type in ("PLUS", "MINUS"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.term())

        return node

    # ---------- statement ----------

    def statement(self):
        if (
            self.current()
            and self.current().type == "IDENT"
            and self.pos + 1 < len(self.tokens)
            and self.tokens[self.pos + 1].type == "ASSIGN"
        ):
            name = self.current().value
            self.eat("IDENT")
            self.eat("ASSIGN")
            value = self.expr()
            return Assign(name, value)

        return self.expr()

    # ---------- PROGRAM (NEW) ----------

    def parse_program(self):
        statements = []

        while self.current() is not None:
            statements.append(self.statement())

        return Program(statements)


def parse(tokens):
    parser = Parser(tokens)
    return parser.parse_program()
