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
        if isinstance(node, Program):
            for stmt in node.statements:
                self.visit(stmt)

        elif isinstance(node, Number):
            t = self.new_temp()
            self.instructions.append(("CONST", t, node.value))
            return t

        elif isinstance(node, Var):
            return node.name

        elif isinstance(node, Assign):
            value = self.visit(node.value)
            self.instructions.append(("ASSIGN", node.name, value))
            return node.name

        elif isinstance(node, BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            t = self.new_temp()
            self.instructions.append((t, node.op, left, right))
            return t

        elif isinstance(node, Print):
            value = self.visit(node.expr)
            self.instructions.append(("PRINT", value))
            return None

        elif isinstance(node, If):
            cond = self.visit(node.condition)
            end_l = self.new_label()

            self.instructions.append(("IF_FALSE", cond, end_l))

            for stmt in node.then_body:
                self.visit(stmt)

            self.instructions.append(("LABEL", end_l))
            return None

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
