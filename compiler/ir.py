from compiler.ast import Number, Var, BinOp, Assign, Program, If, While, Print


class IRGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_id = 0
        self.label_id = 0

    def new_temp(self):
        t = f"t{self.temp_id}"
        self.temp_id += 1
        return t

    def new_label(self):
        l = f"L{self.label_id}"
        self.label_id += 1
        return l

    def generate(self, node):
        self.instructions = []
        self.visit(node)
        return self.instructions

    def visit(self, node):

        # ---------------- PROGRAM ----------------
        if isinstance(node, Program):
            for stmt in node.statements:
                self.visit(stmt)

        # ---------------- NUMBER - FIXED ----------------
        elif isinstance(node, Number):
            t = self.new_temp()
            self.instructions.append(
                ("=", t, node.value)
            )  # تغییر: ("=", target, value)
            return t

        # ---------------- VARIABLE ----------------
        elif isinstance(node, Var):
            return node.name

        # ---------------- ASSIGN ----------------
        elif isinstance(node, Assign):
            value = self.visit(node.value)
            self.instructions.append(("=", node.name, value))
            return node.name

        # ---------------- BINOP ----------------
        elif isinstance(node, BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)

            t = self.new_temp()
            self.instructions.append((t, node.op, left, right))
            return t

        # ---------------- PRINT ----------------
        elif isinstance(node, Print):
            value = self.visit(node.expr)
            self.instructions.append(("PRINT", value))
            return None

        # ---------------- IF ----------------
        elif isinstance(node, If):
            cond = self.visit(node.condition)

            else_l = self.new_label()
            end_l = self.new_label()

            self.instructions.append(("IF_FALSE_GOTO", cond, else_l))

            for stmt in node.then_body:
                self.visit(stmt)

            self.instructions.append(("GOTO", end_l))
            self.instructions.append(("LABEL", else_l))

            for stmt in node.else_body:
                self.visit(stmt)

            self.instructions.append(("LABEL", end_l))

        # ---------------- WHILE ----------------
        elif isinstance(node, While):
            start = self.new_label()
            end = self.new_label()

            self.instructions.append(("LABEL", start))

            cond = self.visit(node.condition)
            self.instructions.append(("IF_FALSE_GOTO", cond, end))

            for stmt in node.body:
                self.visit(stmt)

            self.instructions.append(("GOTO", start))
            self.instructions.append(("LABEL", end))

        else:
            raise Exception(f"Unknown node: {type(node)}")
