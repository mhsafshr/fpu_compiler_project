class Number:
    def __init__(self, value):
        if isinstance(value, int):
            self.value = value
            self.type = "int"
        else:
            self.value = float(value)
            self.type = "float"

    def __repr__(self):
        return f"Number({self.value})"


class Var:
    def __init__(self, name):
        self.name = name
        self.type = None

    def __repr__(self):
        return f"Var({self.name})"


class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        self.type = None

    def __repr__(self):
        return f"BinOp({self.left}, {self.op}, {self.right})"


class Assign:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = None

    def __repr__(self):
        return f"Assign({self.name}, {self.value})"


class Program:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


class If:
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body if isinstance(then_body, list) else [then_body]
        self.else_body = (
            else_body
            if isinstance(else_body, list)
            else ([else_body] if else_body else [])
        )

    def __repr__(self):
        return (
            f"If({self.condition}, "
            f"then={self.then_body}, "
            f"else={self.else_body})"
        )


class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body if isinstance(body, list) else [body]

    def __repr__(self):
        return f"While({self.condition}, body={self.body})"


class Print:
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"
