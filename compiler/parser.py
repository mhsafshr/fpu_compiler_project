from compiler.ast import Number, Var, BinOp, Assign, Program, If, While, Print


class Parser:
    """Recursive descent parser that converts tokens to AST."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        """Return current token without consuming it (lookahead)."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, token_type):
        """Consume current token if it matches expected type, else error."""
        if self.current() and self.current().type == token_type:
            self.pos += 1
        else:
            raise Exception(f"Expected {token_type}, got {self.current()}")

    # factor = NUMBER | IDENT | "(" comparison ")"
    def factor(self):
        token = self.current()
        if token is None:
            raise Exception("Unexpected end of input")

        if token.type == "INT":
            self.eat("INT")
            return Number(int(token.value))
        elif token.type == "FLOAT":
            self.eat("FLOAT")
            return Number(float(token.value))
        elif token.type == "IDENT":
            self.eat("IDENT")
            return Var(token.value)
        elif token.type == "LPAREN":
            self.eat("LPAREN")
            node = self.comparison()  # recursive call inside parentheses
            self.eat("RPAREN")
            return node
        raise Exception(f"Invalid syntax near {token}")

    # term = factor { ("*" | "/") factor }
    def term(self):
        node = self.factor()
        while self.current() and self.current().type in ("MUL", "DIV"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.factor())  # left-associative
        return node

    # expr = term { ("+" | "-") term }
    def expr(self):
        node = self.term()
        while self.current() and self.current().type in ("PLUS", "MINUS"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.term())  # left-associative
        return node

    # comparison = expr { ("<" | ">" | "<=" | ">=" | "==") comparison }?
    def comparison(self):
        node = self.expr()
        while self.current() and self.current().type in ("GT", "LT", "GE", "LE", "EQ"):
            op = self.current().value
            self.eat(self.current().type)
            node = BinOp(node, op, self.comparison())  # right-associative
        return node

    # block = { statement } "end"
    def block(self):
        statements = []
        while self.current() is not None and self.current().type != "END":
            statements.append(self.statement())
        if self.current() is None:
            raise Exception("Expected END but got EOF")
        self.eat("END")
        return statements

    # statement = print_stmt | if_stmt | while_stmt | assign_stmt | expr
    def statement(self):
        # Print statement: print comparison
        if self.current() and self.current().type == "PRINT":
            self.eat("PRINT")
            expr = self.comparison()
            return Print(expr)

        # If statement: if [LPAREN] comparison [RPAREN] do (block | statement)
        if self.current() and self.current().type == "IF":
            self.eat("IF")
            # optional parentheses around condition
            if self.current() and self.current().type == "LPAREN":
                self.eat("LPAREN")
                condition = self.comparison()
                self.eat("RPAREN")
            else:
                condition = self.comparison()
            # optional DO with block
            if self.current() and self.current().type == "DO":
                self.eat("DO")
                then_body = self.block()
            else:
                then_body = [self.statement()]
            return If(condition, then_body, None)

        # While statement: while [LPAREN] comparison [RPAREN] do (block | statement)
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

        # Assignment: IDENT "=" comparison
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

        # Otherwise, it's just an expression (e.g., x + y by itself)
        expr = self.comparison()
        return expr

    # program = { statement }
    def parse_program(self):
        statements = []
        while self.current() is not None:
            statements.append(self.statement())
        return Program(statements)


def parse(tokens):
    """Helper function to parse a list of tokens into an AST."""
    return Parser(tokens).parse_program()
