# Number: integer or float literal with automatic type detection
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


# Var: variable reference, type resolved later by type checker
class Var:
    def __init__(self, name):
        self.name = name
        self.type = None

    def __repr__(self):
        return f"Var({self.name})"


# BinOp: binary operation (+, -, *, /, <, >, <=, >=, ==)
class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        self.type = None

    def __repr__(self):
        return f"BinOp({self.left}, {self.op}, {self.right})"


# Assign: variable assignment (x = expression)
class Assign:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.type = None

    def __repr__(self):
        return f"Assign({self.name}, {self.value})"


# Program: root node containing a list of statements
class Program:
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


# If: conditional statement with optional else
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


# While: loop statement
class While:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body if isinstance(body, list) else [body]

    def __repr__(self):
        return f"While({self.condition}, body={self.body})"


# Print: output statement
class Print:
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"
