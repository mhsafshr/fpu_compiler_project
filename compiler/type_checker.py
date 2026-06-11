class TypeChecker:
    """Semantic analyzer - checks types and builds symbol table."""

    def __init__(self):
        self.symbol_table = {}  # variable name → type ("int" or "float")

    def check(self, node):
        """Entry point: start type checking from root node."""
        return self.visit(node)

    def visit(self, node):
        """Recursively traverse AST, check types, and annotate nodes."""

        # Program: visit all statements
        if node.__class__.__name__ == "Program":
            for stmt in node.statements:
                self.visit(stmt)
            return

        # Number: literal already has its type (int/float)
        elif node.__class__.__name__ == "Number":
            node.type = node.type  # keep existing type
            return node.type

        # Var: look up variable in symbol table
        elif node.__class__.__name__ == "Var":
            if node.name in self.symbol_table:
                node.type = self.symbol_table[node.name]
                return node.type
            else:
                raise Exception(f"Variable '{node.name}' not defined")

        # Assign: evaluate RHS, then store variable type in symbol table
        elif node.__class__.__name__ == "Assign":
            value_type = self.visit(node.value)
            self.symbol_table[node.name] = value_type
            node.type = value_type
            return value_type

        # BinOp: check both sides have same type
        elif node.__class__.__name__ == "BinOp":
            left_type = self.visit(node.left)
            right_type = self.visit(node.right)

            # Type mismatch: int + float not allowed (would need implicit cast)
            if left_type != right_type:
                raise Exception(f"Type mismatch: {left_type} {node.op} {right_type}")

            # Arithmetic ops: result type same as operands
            if node.op in ["+", "-", "*", "/"]:
                node.type = left_type
                return left_type

            # Comparison ops: result is float (1.0 for true, 0.0 for false)
            if node.op in [">", "<", ">=", "<=", "=="]:
                node.type = "float"
                return "float"

            raise Exception(f"Unknown operator {node.op}")

        # Print: just check the expression
        elif node.__class__.__name__ == "Print":
            expr_type = self.visit(node.expr)
            return expr_type

        # If: condition must be float, then check both branches
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

        # While: condition must be float, then check loop body
        elif node.__class__.__name__ == "While":
            cond_type = self.visit(node.condition)
            if cond_type != "float":
                raise Exception("Condition must be float/boolean")
            for stmt in node.body:
                self.visit(stmt)
            return None

        else:
            raise Exception(f"Unknown node: {type(node)}")
