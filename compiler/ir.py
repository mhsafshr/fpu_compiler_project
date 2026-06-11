from compiler.ast import Number, Var, BinOp, Assign, Program, If, While, Print


class IRGenerator:
    """Three-address code intermediate representation generator."""

    def __init__(self):
        self.instructions = []  # list of IR tuples
        self.temp_id = 0  # counter for temporaries (t0, t1, t2...)
        self.label_id = 0  # counter for labels (L0, L1, L2...)

    def new_temp(self):
        """Generate a fresh temporary variable name."""
        t = f"t{self.temp_id}"
        self.temp_id += 1
        return t

    def new_label(self):
        """Generate a fresh label name for jumps."""
        l = f"L{self.label_id}"
        self.label_id += 1
        return l

    def generate(self, node):
        """Entry point: generate IR from AST root node."""
        self.instructions = []
        self.visit(node)
        return self.instructions

    def visit(self, node):
        """Recursively traverse AST and emit IR instructions."""

        # Program: visit all statements in order
        if isinstance(node, Program):
            for stmt in node.statements:
                self.visit(stmt)

        # Number: allocate temp and load constant
        elif isinstance(node, Number):
            t = self.new_temp()
            self.instructions.append(("CONST", t, node.value))
            return t

        # Var: just return variable name (no temp needed)
        elif isinstance(node, Var):
            return node.name

        # Assign: evaluate RHS, then store to variable
        elif isinstance(node, Assign):
            value = self.visit(node.value)
            self.instructions.append(("ASSIGN", node.name, value))
            return node.name

        # BinOp: evaluate operands, then perform operation
        elif isinstance(node, BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            t = self.new_temp()
            self.instructions.append((t, node.op, left, right))
            return t

        # Print: evaluate expression, then print it
        elif isinstance(node, Print):
            value = self.visit(node.expr)
            self.instructions.append(("PRINT", value))
            return None

        # If: conditional execution
        # Structure: IF_FALSE cond end_label, then_body, LABEL end_label
        elif isinstance(node, If):
            cond = self.visit(node.condition)
            end_l = self.new_label()

            self.instructions.append(("IF_FALSE", cond, end_l))

            for stmt in node.then_body:
                self.visit(stmt)

            self.instructions.append(("LABEL", end_l))
            return None

        # While: loop with conditional jump
        # Structure: LABEL start, IF_FALSE cond end, body, GOTO start, LABEL end
        elif isinstance(node, While):
            start_l = self.new_label()
            end_l = self.new_label()

            self.instructions.append(("LABEL", start_l))

            cond = self.visit(node.condition)
            self.instructions.append(("IF_FALSE", cond, end_l))

            for stmt in node.body:
                self.visit(stmt)

            self.instructions.append(("GOTO", start_l))
            self.instructions.append(("LABEL", end_l))
            return None

        else:
            raise Exception(f"Unknown node: {type(node)}")
