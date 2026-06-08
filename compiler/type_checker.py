class TypeChecker:
    def __init__(self):
        self.symbol_table = {}

    def check(self, node):
        return self.visit(node)

    def visit(self, node):
        if node.__class__.__name__ == "Program":
            for stmt in node.statements:
                self.visit(stmt)
            return

        elif node.__class__.__name__ == "Number":
            node.type = node.type
            return node.type

        elif node.__class__.__name__ == "Var":
            if node.name in self.symbol_table:
                node.type = self.symbol_table[node.name]
                return node.type
            else:
                raise Exception(f"Variable '{node.name}' not defined")

        elif node.__class__.__name__ == "Assign":
            value_type = self.visit(node.value)
            self.symbol_table[node.name] = value_type
            node.type = value_type
            return value_type

        elif node.__class__.__name__ == "BinOp":
            left_type = self.visit(node.left)
            right_type = self.visit(node.right)

            if left_type != right_type:
                raise Exception(f"Type mismatch: {left_type} {node.op} {right_type}")

            if node.op in ["+", "-", "*", "/"]:
                node.type = left_type
                return left_type

            if node.op in [">", "<", ">=", "<=", "=="]:
                node.type = "float"
                return "float"

            raise Exception(f"Unknown operator {node.op}")

        elif node.__class__.__name__ == "Print":
            expr_type = self.visit(node.expr)
            return expr_type

        elif node.__class__.__name__ == "If":
            cond_type = self.visit(node.condition)
            if cond_type != "float":
                raise Exception("Condition must be float/boolean")
            for stmt in node.then_body:
                self.visit(stmt)
            if node.else_body:
                for stmt in node.else_body:
                    self.visit(stmt)
            return None

        elif node.__class__.__name__ == "While":
            cond_type = self.visit(node.condition)
            if cond_type != "float":
                raise Exception("Condition must be float/boolean")
            for stmt in node.body:
                self.visit(stmt)
            return None

        else:
            raise Exception(f"Unknown node: {type(node)}")
