class Backend:
    def __init__(self):
        self.instructions = []
        self.reg_count = 0
        self.var_map = {}
        self.label_count = 0
        self.max_regs = 20

    def new_reg(self):
        if self.reg_count >= self.max_regs:
            raise Exception("Out of registers! Need spilling.")
        r = f"R{self.reg_count}"
        self.reg_count += 1
        return r

    def new_label(self):
        l = f"L{self.label_count}"
        self.label_count += 1
        return l

    def generate(self, ir_instructions):
        self.instructions = []
        self.var_map = {}
        self.reg_count = 0
        self.label_count = 0

        for ins in ir_instructions:
            self.visit(ins)

        if not self.instructions or self.instructions[-1] != "HALT":
            self.instructions.append("HALT")

        return self.instructions

    def load(self, x):
        try:
            float(x)
            r = self.new_reg()
            self.instructions.append(f"MOV {r} {x}")
            return r
        except:
            pass

        if isinstance(x, str) and x.startswith("R"):
            return x

        if x in self.var_map:
            return self.var_map[x]

        if isinstance(x, str) and x.startswith("t"):
            r = self.new_reg()
            self.var_map[x] = r
            return r

        r = self.new_reg()
        self.var_map[x] = r
        return r

    def visit(self, ins):
        op = ins[0]

        if op == "CONST":
            target = ins[1]
            value = ins[2]
            r = self.new_reg()
            self.instructions.append(f"MOV {r} {value}")
            self.var_map[target] = r
            return

        if op == "ASSIGN":
            target = ins[1]
            value = ins[2]
            src = self.load(value)
            if target in self.var_map:
                dest_reg = self.var_map[target]
                self.instructions.append(f"MOV {dest_reg} {src}")
            else:
                dest_reg = self.new_reg()
                self.var_map[target] = dest_reg
                self.instructions.append(f"MOV {dest_reg} {src}")
            return

        if op == "PRINT":
            src = self.load(ins[1])
            self.instructions.append(f"PRINT {src}")
            return

        if op == "LABEL":
            self.instructions.append(f"LABEL {ins[1]}")
            return

        if op == "GOTO":
            self.instructions.append(f"JUMP {ins[1]}")
            return

        if op == "IF_FALSE":
            cond = self.load(ins[1])
            self.instructions.append(f"JUMP_IF_FALSE {cond} {ins[2]}")
            return

        if len(ins) == 4:
            target, binop, left, right = ins

            ops = {"+", "-", "*", "/", ">", "<", ">=", "<=", "=="}
            if binop not in ops:
                raise Exception(f"Unknown op {binop}")

            r1 = self.load(left)
            r2 = self.load(right)
            result = self.new_reg()

            op_map = {
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

            self.instructions.append(f"{op_map[binop]} {result} {r1} {r2}")
            self.var_map[target] = result
            return

        raise Exception(f"Bad IR: {ins}")

    def reset(self):
        self.instructions = []
        self.var_map = {}
        self.reg_count = 0
        self.label_count = 0
