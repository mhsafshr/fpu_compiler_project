from compiler.ast import Number, Var, BinOp, Assign, Program


class CodeGenerator:
    def __init__(self):
        self.instructions = []

    def generate(self, node):
        self.instructions = []
        self.visit(node)
        return self.instructions

    def visit(self, node):

        # ---------------- Program ----------------
        if isinstance(node, Program):
            for stmt in node.statements:
                self.visit(stmt)

        # ---------------- Number ----------------
        elif isinstance(node, Number):
            self.instructions.append(f"LOADF {node.value}")

        # ---------------- Var ----------------
        elif isinstance(node, Var):
            self.instructions.append(f"LOADF {node.name}")

        # ---------------- Assign ----------------
        elif isinstance(node, Assign):
            self.visit(node.value)
            self.instructions.append(f"STORE {node.name}")

        # ---------------- BinOp ----------------
        elif isinstance(node, BinOp):
            self.visit(node.left)
            self.visit(node.right)

            if node.op == "+":
                self.instructions.append("FADD")

            elif node.op == "-":
                self.instructions.append("FSUB")

            elif node.op == "*":
                self.instructions.append("FMUL")

            elif node.op == "/":
                self.instructions.append("FDIV")

        else:
            raise Exception(f"Unknown node type: {type(node)}")
