from compiler.ast import Number, Var, BinOp, Assign, Program, If, While


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

    # ---------------- VISIT BLOCK SAFE ----------------
    def visit_block(self, node):
        # support both list and single statement
        if isinstance(node, list):
            for stmt in node:
                self.visit(stmt)
        else:
            self.visit(node)

    def visit(self, node):

        # ---------------- Program ----------------
        if isinstance(node, Program):
            self.visit_block(node.statements)

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

            self.instructions.append(f"{else_label}:")

            if node.else_body:
                self.visit_block(node.else_body)

            self.instructions.append(f"{end_label}:")

        # ---------------- WHILE ----------------
        elif isinstance(node, While):

            start_label = self.new_label()
            end_label = self.new_label()

            self.instructions.append(f"{start_label}:")

            self.visit(node.condition)
            self.instructions.append(f"JUMP_IF_FALSE {end_label}")

            self.visit_block(node.body)

            self.instructions.append(f"JUMP {start_label}")

            self.instructions.append(f"{end_label}:")

        else:
            raise Exception(f"Unknown node type: {type(node)}")
