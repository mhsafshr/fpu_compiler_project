from fpu.fpu_simulator import FPUSimulator


class VM:
    def __init__(self):
        self.stack = []
        self.variables = {}
        self.fpu = FPUSimulator()
        self.last_result = None
        self.labels = {}

    # -----------------------------
    # preprocess labels
    # -----------------------------
    def preprocess_labels(self, instructions):
        cleaned = []
        self.labels = {}

        for i, ins in enumerate(instructions):
            ins = ins.strip()

            if ins.endswith(":"):
                label = ins[:-1].strip()
                self.labels[label] = len(cleaned)
            else:
                cleaned.append(ins)

        return cleaned

    # -----------------------------
    # safe pop
    # -----------------------------
    def pop(self):
        if not self.stack:
            raise Exception("Stack underflow")
        return self.stack.pop()

    # -----------------------------
    # safe peek (برای دیباگ)
    # -----------------------------
    def peek(self):
        if not self.stack:
            return None
        return self.stack[-1]

    # -----------------------------
    # run VM با پشتیبانی کامل از while
    # -----------------------------
    def run(self, instructions):
        self.stack = []
        instructions = self.preprocess_labels(instructions)

        ip = 0
        max_iterations = 10000  # جلوگیری از حلقه بی‌نهایت
        iteration_count = 0

        while ip < len(instructions) and iteration_count < max_iterations:
            iteration_count += 1
            ins = instructions[ip]
            parts = ins.split()
            op = parts[0]

            # ---------------- LOADF ----------------
            if op == "LOADF":
                value = parts[1]

                try:
                    value = float(value)
                except ValueError:
                    if value in self.variables:
                        value = self.variables[value]
                    else:
                        raise Exception(f"Undefined variable: {value}")

                self.stack.append(value)

            # ---------------- STORE ----------------
            elif op == "STORE":
                var_name = parts[1]
                self.variables[var_name] = self.pop()

            # ---------------- ARITHMETIC ----------------
            elif op == "FADD":
                b = self.pop()
                a = self.pop()
                self.stack.append(self.fpu.add(a, b))

            elif op == "FSUB":
                b = self.pop()
                a = self.pop()
                self.stack.append(self.fpu.sub(a, b))

            elif op == "FMUL":
                b = self.pop()
                a = self.pop()
                self.stack.append(self.fpu.mul(a, b))

            elif op == "FDIV":
                b = self.pop()
                a = self.pop()
                self.stack.append(self.fpu.div(a, b))

            # ---------------- COMPARISON ----------------
            elif op == "GT":
                b = self.pop()
                a = self.pop()
                result = 1.0 if a > b else 0.0
                self.stack.append(result)

            elif op == "LT":
                b = self.pop()
                a = self.pop()
                result = 1.0 if a < b else 0.0
                self.stack.append(result)

            elif op == "GE":
                b = self.pop()
                a = self.pop()
                result = 1.0 if a >= b else 0.0
                self.stack.append(result)

            elif op == "LE":
                b = self.pop()
                a = self.pop()
                result = 1.0 if a <= b else 0.0
                self.stack.append(result)

            elif op == "EQ":
                b = self.pop()
                a = self.pop()
                result = 1.0 if a == b else 0.0
                self.stack.append(result)

            # ---------------- JUMP (پرش بدون شرط) ----------------
            elif op == "JUMP":
                label = parts[1]
                if label not in self.labels:
                    raise Exception(f"Undefined label: {label}")
                ip = self.labels[label]
                continue

            # ---------------- JUMP_IF_FALSE (پرش اگر شرط false باشد) ----------------
            elif op == "JUMP_IF_FALSE":
                label = parts[1]
                if label not in self.labels:
                    raise Exception(f"Undefined label: {label}")

                cond = self.pop()

                # شرط false: هر مقداری که 0 یا 0.0 باشد
                if cond == 0.0 or cond == 0:
                    ip = self.labels[label]
                    continue

            # ---------------- JUMP_IF_TRUE (پرش اگر شرط true باشد) - برای راحتی ----------------
            elif op == "JUMP_IF_TRUE":
                label = parts[1]
                if label not in self.labels:
                    raise Exception(f"Undefined label: {label}")

                cond = self.pop()

                # شرط true: هر مقداری که 0 نباشد
                if cond != 0.0 and cond != 0:
                    ip = self.labels[label]
                    continue

            # ---------------- PRINT (برای دیباگ) ----------------
            elif op == "PRINT":
                val = self.pop()
                print(f"[DEBUG] PRINT: {val}")

            # ---------------- HALT ----------------
            elif op == "HALT":
                break

            else:
                raise Exception(f"Unknown instruction: {ins}")

            ip += 1

        if iteration_count >= max_iterations:
            raise Exception("Maximum iterations exceeded - possible infinite loop")

        # برگرداندن آخرین مقدار روی استک (اگر وجود داشته باشد)
        if self.stack:
            self.last_result = self.stack[-1]
            return self.last_result

        return None

    # -----------------------------
    # reset VM state
    # -----------------------------
    def reset(self):
        self.stack = []
        self.variables = {}
        self.last_result = None
        self.labels = {}
