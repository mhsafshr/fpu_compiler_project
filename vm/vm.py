from fpu.fpu_simulator import FPUSimulator


class VM:
    def __init__(self):
        self.stack = []
        self.variables = {}
        self.fpu = FPUSimulator()
        self.last_result = None  # 🔥 نتیجه نهایی

    def run(self, instructions):
        self.stack = []

        for ins in instructions:
            parts = ins.split()
            op = parts[0]

            if op == "LOADF":
                value = parts[1]

                try:
                    value = float(value)
                except:
                    value = self.variables.get(value, 0)

                self.stack.append(value)

            elif op == "STORE":
                var_name = parts[1]
                value = self.stack.pop()
                self.variables[var_name] = value

                self.last_result = None  # assignment نتیجه ندارد

            elif op == "FADD":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.fpu.add(a, b))

            elif op == "FSUB":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.fpu.sub(a, b))

            elif op == "FMUL":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.fpu.mul(a, b))

            elif op == "FDIV":
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(self.fpu.div(a, b))

        # 🔥 فقط اگر چیزی روی stack باقی مانده باشد نتیجه داریم
        if self.stack:
            self.last_result = self.stack[-1]

        return self.last_result
