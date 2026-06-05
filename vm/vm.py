from fpu.fpu_simulator import FPUSimulator
from compiler.isa import is_valid


class VM:
    def __init__(self):

        # ---------------- REGISTERS ----------------
        self.reg = {f"R{i}": 0.0 for i in range(6)}

        # ---------------- FPU ----------------
        self.fpu = FPUSimulator()

        # ---------------- LABEL TABLE ----------------
        self.labels = {}

    # =========================================================
    # LABEL PREPROCESS
    # =========================================================
    def preprocess_labels(self, instructions):
        cleaned = []
        self.labels = {}

        for i, ins in enumerate(instructions):
            ins = ins.strip()

            if ins.startswith("LABEL"):
                parts = ins.split()

                if len(parts) != 2:
                    raise Exception(f"Invalid label: {ins}")

                self.labels[parts[1]] = len(cleaned)
            else:
                cleaned.append(ins)

        return cleaned

    # =========================================================
    # OPERAND RESOLVER
    # =========================================================
    def get(self, x):
        if x in self.reg:
            return self.reg[x]

        try:
            return float(x)
        except:
            raise Exception(f"Unknown operand: {x}")

    # =========================================================
    # EXECUTION LOOP
    # =========================================================
    def run(self, instructions):

        instructions = self.preprocess_labels(instructions)

        ip = 0
        max_steps = 10000
        steps = 0

        while ip < len(instructions):

            if steps > max_steps:
                raise Exception("Infinite loop detected")

            steps += 1

            ins = instructions[ip]
            parts = ins.split()
            op = parts[0]

            # ---------------- VALIDATION ----------------
            if not is_valid(op):
                raise Exception(f"Illegal instruction: {op}")

            # =====================================================
            # MOV
            # =====================================================
            if op == "MOV":
                self.reg[parts[1]] = self.get(parts[2])

            # =====================================================
            # ARITHMETIC
            # =====================================================
            elif op == "ADD":
                self.reg[parts[1]] = self.get(parts[2]) + self.get(parts[3])

            elif op == "SUB":
                self.reg[parts[1]] = self.get(parts[2]) - self.get(parts[3])

            elif op == "MUL":
                self.reg[parts[1]] = self.get(parts[2]) * self.get(parts[3])

            elif op == "DIV":
                b = self.get(parts[3])
                if b == 0:
                    raise ZeroDivisionError("Division by zero")
                self.reg[parts[1]] = self.get(parts[2]) / b

            # =====================================================
            # FPU
            # =====================================================
            elif op == "FADD":
                self.reg[parts[1]] = self.fpu.add(
                    self.get(parts[2]), self.get(parts[3])
                )

            elif op == "FSUB":
                self.reg[parts[1]] = self.fpu.sub(
                    self.get(parts[2]), self.get(parts[3])
                )

            elif op == "FMUL":
                self.reg[parts[1]] = self.fpu.mul(
                    self.get(parts[2]), self.get(parts[3])
                )

            elif op == "FDIV":
                self.reg[parts[1]] = self.fpu.div(
                    self.get(parts[2]), self.get(parts[3])
                )

            # =====================================================
            # COMPARISON → stored in destination register
            # =====================================================
            elif op == "GT":
                self.reg[parts[1]] = (
                    1.0 if self.get(parts[2]) > self.get(parts[3]) else 0.0
                )

            elif op == "LT":
                self.reg[parts[1]] = (
                    1.0 if self.get(parts[2]) < self.get(parts[3]) else 0.0
                )

            elif op == "GE":
                self.reg[parts[1]] = (
                    1.0 if self.get(parts[2]) >= self.get(parts[3]) else 0.0
                )

            elif op == "LE":
                self.reg[parts[1]] = (
                    1.0 if self.get(parts[2]) <= self.get(parts[3]) else 0.0
                )

            elif op == "EQ":
                self.reg[parts[1]] = (
                    1.0 if self.get(parts[2]) == self.get(parts[3]) else 0.0
                )

            # =====================================================
            # CONTROL FLOW
            # =====================================================
            elif op == "JUMP":
                ip = self.labels[parts[1]]
                continue

            elif op == "JUMP_IF_FALSE":
                if self.reg[parts[1]] == 0.0:
                    ip = self.labels[parts[2]]
                    continue

            elif op == "JUMP_IF_TRUE":
                if self.reg[parts[1]] != 0.0:
                    ip = self.labels[parts[2]]
                    continue

            # =====================================================
            # OUTPUT
            # =====================================================
            elif op == "PRINT":
                print(self.reg[parts[1]])

            elif op == "HALT":
                break

            ip += 1

        return self.reg["R0"]

    # =========================================================
    # RESET
    # =========================================================
    def reset(self):
        for k in self.reg:
            self.reg[k] = 0.0
        self.labels.clear()
