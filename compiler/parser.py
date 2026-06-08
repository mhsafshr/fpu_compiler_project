from compiler.ast import Number, Var, BinOp, Assign, Program, If, While, Print


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

    def comparison(self):
        node = self.expr()

        while self.current() and self.current().type in ("GT", "LT", "GE", "LE", "EQ"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.comparison())

        return node

    def block(self):
        statements = []
        while self.current() is not None and self.current().type != "END":
            statements.append(self.statement())
        if self.current() is None:
            raise Exception("Expected END but got EOF")
        self.eat("END")
        return statements

    def statement(self):
        if self.current() and self.current().type == "PRINT":
            self.eat("PRINT")
            expr = self.comparison()
            return Print(expr)

        if self.current() and self.current().type == "IF":
            self.eat("IF")

            if self.current() and self.current().type == "LPAREN":
                self.eat("LPAREN")
                condition = self.comparison()
                self.eat("RPAREN")
            else:
                condition = self.comparison()

            if self.current() and self.current().type == "DO":
                self.eat("DO")
                then_body = self.block()
            else:
                then_body = [self.statement()]

            return If(condition, then_body, None)

        if self.current() and self.current().type == "WHILE":
            self.eat("WHILE")

            if self.current() and self.current().type == "LPAREN":
                self.eat("LPAREN")
                condition = self.comparison()
                self.eat("RPAREN")
            else:
                condition = self.comparison()

            if self.current() and self.current().type == "DO":
                self.eat("DO")
                body = self.block()
            else:
                body = [self.statement()]

            return While(condition, body)

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

        expr = self.comparison()
        return expr

    def parse_program(self):
        statements = []

        while self.current() is not None:
            statements.append(self.statement())

        return Program(statements)


def parse(tokens):
    return Parser(tokens).parse_program()
