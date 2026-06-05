class Backend:
    def __init__(self):
        self.instructions = []
        self.reg_count = 0
        self.var_map = {}

    def new_reg(self):
        r = f"R{self.reg_count}"
        self.reg_count += 1
        return r

    def generate(self, ir_instructions):
        self.instructions = []
        self.var_map = {}
        self.reg_count = 0

        for ins in ir_instructions:
            self.visit(ins)

        # optional: add HALT at the end
        self.instructions.append("HALT")

        return self.instructions

    def load(self, x):
        # if x is a number
        try:
            float(x)
            r = self.new_reg()
            self.instructions.append(f"MOV {r} {x}")
            return r
        except:
            pass

        # if x is a variable already mapped to a register
        if x in self.var_map:
            return self.var_map[x]

        # if x is a raw register name (like "R0")
        if isinstance(x, str) and x.startswith("R"):
            return x

        # fallback: treat as variable not yet mapped
        r = self.new_reg()
        self.var_map[x] = r
        return r

    def visit(self, ins):

        # =========================================================
        # ASSIGN - FIXED: now handles ("=", "a", "t0") format
        # =========================================================
        if len(ins) == 3 and ins[0] == "=":
            target = ins[1]  # variable name like "a"
            value = ins[2]  # value or temp like "t0"
            src = self.load(value)
            self.var_map[target] = src
            return

        # =========================================================
        # PRINT
        # =========================================================
        if ins[0] == "PRINT":
            src = self.load(ins[1])
            self.instructions.append(f"PRINT {src}")
            return

        # =========================================================
        # LABEL
        # =========================================================
        if ins[0] == "LABEL":
            self.instructions.append(f"LABEL {ins[1]}")
            return

        # =========================================================
        # GOTO
        # =========================================================
        if ins[0] == "GOTO":
            self.instructions.append(f"JUMP {ins[1]}")
            return

        # =========================================================
        # IF FALSE GOTO
        # =========================================================
        if ins[0] == "IF_FALSE_GOTO":
            cond = self.load(ins[1])
            self.instructions.append(f"JUMP_IF_FALSE {cond} {ins[2]}")
            return

        # =========================================================
        # BINARY OPS (+, -, *, /, >, <, >=, <=, ==)
        # =========================================================
        if len(ins) == 4:
            target, op, left, right = ins

            ops = {"+", "-", "*", "/", ">", "<", ">=", "<=", "=="}
            if op not in ops:
                raise Exception(f"Unknown op {op}")

            r1 = self.load(left)
            r2 = self.load(right)

            result = self.new_reg()

            op_map = {
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

            self.instructions.append(f"{op_map[op]} {result} {r1} {r2}")

            self.var_map[target] = result
            return

        raise Exception(f"Bad IR: {ins}")
