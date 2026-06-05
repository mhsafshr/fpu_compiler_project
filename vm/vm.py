from fpu.fpu_simulator import FPUSimulator


class VM:
    def __init__(self):
        self.stack = []
        self.variables = {}
        self.fpu = FPUSimulator()
        self.labels = {}

    # ---------------- LABEL PREPROCESS ----------------
    def preprocess_labels(self, instructions):
        cleaned = []
        self.labels = {}

        for i, ins in enumerate(instructions):
            ins = ins.strip()

            if ins.startswith("LABEL"):
                label = ins.split()[1]
                self.labels[label] = len(cleaned)
            else:
                cleaned.append(ins)

        return cleaned

    # ---------------- STACK OPS ----------------
    def pop(self):
        if not self.stack:
            raise Exception("Stack underflow")
        return self.stack.pop()

    def push(self, value):
        self.stack.append(value)

    # ---------------- EXECUTION ----------------
    def run(self, instructions):
        self.stack = []
        instructions = self.preprocess_labels(instructions)

        ip = 0
        max_iterations = 10000
        iteration_count = 0

        while ip < len(instructions) and iteration_count < max_iterations:
            iteration_count += 1
            ins = instructions[ip]
            parts = ins.split()
            op = parts[0]

            # ---------------- CONST ----------------
            if op == "CONSTF":
                self.push(float(parts[1]))

            # ---------------- LOAD VARIABLE ----------------
            elif op == "LOAD":
                var = parts[1]
                if var not in self.variables:
                    raise Exception(f"Undefined variable: {var}")
                self.push(self.variables[var])

            # ---------------- STORE ----------------
            elif op == "STORE":
                var = parts[1]
                self.variables[var] = self.pop()

            # ---------------- FPU OPS ----------------
            elif op == "FADD":
                b = self.pop()
                a = self.pop()
                self.push(self.fpu.add(a, b))

            elif op == "FSUB":
                b = self.pop()
                a = self.pop()
                self.push(self.fpu.sub(a, b))

            elif op == "FMUL":
                b = self.pop()
                a = self.pop()
                self.push(self.fpu.mul(a, b))

            elif op == "FDIV":
                b = self.pop()
                a = self.pop()
                self.push(self.fpu.div(a, b))

            # ---------------- COMPARISON ----------------
            elif op == "GT":
                b = self.pop()
                a = self.pop()
                self.push(1.0 if a > b else 0.0)

            elif op == "LT":
                b = self.pop()
                a = self.pop()
                self.push(1.0 if a < b else 0.0)

            elif op == "GE":
                b = self.pop()
                a = self.pop()
                self.push(1.0 if a >= b else 0.0)

            elif op == "LE":
                b = self.pop()
                a = self.pop()
                self.push(1.0 if a <= b else 0.0)

            elif op == "EQ":
                b = self.pop()
                a = self.pop()
                self.push(1.0 if a == b else 0.0)

            # ---------------- JUMP ----------------
            elif op == "JUMP":
                label = parts[1]
                if label not in self.labels:
                    raise Exception(f"Undefined label: {label}")
                ip = self.labels[label]
                continue

            elif op == "JUMP_IF_FALSE":
                label = parts[1]
                cond = self.pop()

                if cond == 0.0:
                    ip = self.labels[label]
                    continue

            elif op == "JUMP_IF_TRUE":
                label = parts[1]
                cond = self.pop()

                if cond != 0.0:
                    ip = self.labels[label]
                    continue

            # ---------------- PRINT ----------------
            elif op == "PRINT":
                val = self.pop()
                print(f">>> {val}")

            # ---------------- HALT ----------------
            elif op == "HALT":
                break

            else:
                raise Exception(f"Unknown instruction: {ins}")

            ip += 1

        if iteration_count >= max_iterations:
            raise Exception("Infinite loop detected")

        return self.stack[-1] if self.stack else None

    # ---------------- RESET ----------------
    def reset(self):
        self.stack = []
        self.variables = {}
        self.labels = {}
