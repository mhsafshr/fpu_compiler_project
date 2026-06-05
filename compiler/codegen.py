from compiler.ast import Number, Var, BinOp, Assign, Program, If, While, Print


class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.label_count = 0

    def generate(self, node):
        self.instructions = []
        self.visit(node)
        return self.instructions

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def visit_block(self, node):
        if isinstance(node, list):
            for stmt in node:
                self.visit(stmt)
        else:
            self.visit(node)

    def visit(self, node):

        # ---------------- PROGRAM ----------------
        if isinstance(node, Program):
            self.visit_block(node.statements)

        # ---------------- NUMBER ----------------
        elif isinstance(node, Number):
            self.instructions.append(f"CONSTF {node.value}")

        # ---------------- VARIABLE ----------------
        elif isinstance(node, Var):
            self.instructions.append(f"LOAD {node.name}")

        # ---------------- ASSIGN ----------------
        elif isinstance(node, Assign):
            self.visit(node.value)
            self.instructions.append(f"STORE {node.name}")

        # ---------------- PRINT ----------------
        elif isinstance(node, Print):
            self.visit(node.expr)
            self.instructions.append("PRINT")

        # ---------------- BINARY OP ----------------
        elif isinstance(node, BinOp):
            self.visit(node.left)
            self.visit(node.right)

            ops = {
                "+": "FADD",
                "-": "FSUB",
                "*": "FMUL",
                "/": "FDIV",
                ">": "GT",
                "<": "LT",
                ">=": "GE",
                "<=": "LE",
                "==": "EQ",
            }

            if node.op in ops:
                self.instructions.append(ops[node.op])
            else:
                raise Exception(f"Unknown operator: {node.op}")

        # ---------------- IF ----------------
        elif isinstance(node, If):
            else_label = self.new_label()
            end_label = self.new_label()

            self.visit(node.condition)
            self.instructions.append(f"JUMP_IF_FALSE {else_label}")

            self.visit_block(node.then_body)
            self.instructions.append(f"JUMP {end_label}")

            self.instructions.append(f"LABEL {else_label}")

            if node.else_body:
                self.visit_block(node.else_body)

            self.instructions.append(f"LABEL {end_label}")

        # ---------------- WHILE ----------------
        elif isinstance(node, While):
            start_label = self.new_label()
            end_label = self.new_label()

            self.instructions.append(f"LABEL {start_label}")

            self.visit(node.condition)
            self.instructions.append(f"JUMP_IF_FALSE {end_label}")

            self.visit_block(node.body)

            self.instructions.append(f"JUMP {start_label}")
            self.instructions.append(f"LABEL {end_label}")

        else:
            raise Exception(f"Unknown node type: {type(node)}")
