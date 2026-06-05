from compiler.ast import Number, Var, BinOp, Assign, Program, If, While, Print


class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.label_count = 0
        self.temp_reg_count = 0

    # ---------------- TEMP REGISTER ----------------
    def new_reg(self):
        reg = f"R{self.temp_reg_count}"
        self.temp_reg_count += 1
        if self.temp_reg_count > 4:
            self.temp_reg_count = 0  # simple reuse (no real allocator yet)
        return reg

    # ---------------- LABEL ----------------
    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    # ---------------- MAIN GENERATE ----------------
    def generate(self, node):
        self.instructions = []
        self.temp_reg_count = 0
        self.visit(node)
        return self.instructions

    # ---------------- VISIT BLOCK ----------------
    def visit_block(self, node):
        if isinstance(node, list):
            for stmt in node:
                self.visit(stmt)
        else:
            self.visit(node)

    # ---------------- VISIT ----------------
    def visit(self, node):

        # ---------------- PROGRAM ----------------
        if isinstance(node, Program):
            self.visit_block(node.statements)

        # ---------------- NUMBER ----------------
        elif isinstance(node, Number):
            reg = self.new_reg()
            self.instructions.append(f"MOV {reg} {node.value}")
            return reg

        # ---------------- VARIABLE ----------------
        elif isinstance(node, Var):
            reg = self.new_reg()
            self.instructions.append(f"MOV {reg} {node.name}")
            return reg

        # ---------------- ASSIGN ----------------
        elif isinstance(node, Assign):
            value_reg = self.visit(node.value)
            self.instructions.append(f"MOV {node.name} {value_reg}")

        # ---------------- PRINT ----------------
        elif isinstance(node, Print):
            reg = self.visit(node.expr)
            self.instructions.append(f"PRINT {reg}")

        # ---------------- BINARY OP ----------------
        elif isinstance(node, BinOp):

            left_reg = self.visit(node.left)
            right_reg = self.visit(node.right)
            result_reg = self.new_reg()

            ops = {
                "+": "ADD",
                "-": "SUB",
                "*": "MUL",
                "/": "DIV",
                ">": "GT",
                "<": "LT",
                ">=": "GE",
                "<=": "LE",
                "==": "EQ",
            }

            if node.op in ops:
                self.instructions.append(
                    f"{ops[node.op]} {result_reg} {left_reg} {right_reg}"
                )
                return result_reg

            else:
                raise Exception(f"Unknown operator: {node.op}")

        # ---------------- IF ----------------
        elif isinstance(node, If):

            else_label = self.new_label()
            end_label = self.new_label()

            cond_reg = self.visit(node.condition)

            self.instructions.append(f"JUMP_IF_FALSE {cond_reg} {else_label}")

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

            cond_reg = self.visit(node.condition)
            self.instructions.append(f"JUMP_IF_FALSE {cond_reg} {end_label}")

            self.visit_block(node.body)

            self.instructions.append(f"JUMP {start_label}")
            self.instructions.append(f"LABEL {end_label}")

        else:
            raise Exception(f"Unknown node type: {type(node)}")
