from compiler.isa import is_valid


class VM:
    def __init__(self):
        self.reg = {f"R{i}": 0.0 for i in range(20)}
        self.vars = {}
        self.labels = {}
        self.output = []

    def _fpu_add(self, a, b):
        return float(a + b)

    def _fpu_sub(self, a, b):
        return float(a - b)

    def _fpu_mul(self, a, b):
        return float(a * b)

    def _fpu_div(self, a, b):
        if b == 0:
            raise ZeroDivisionError("FPU Error: Division by zero")
        return float(a / b)

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

    def get(self, x):
        if x in self.reg:
            return self.reg[x]

        if x in self.vars:
            return self.vars[x]

        try:
            return float(x)
        except:
            pass

        if isinstance(x, str) and x.startswith("t"):
            self.vars[x] = 0.0
            return 0.0

        raise Exception(f"Unknown operand: {x}")

    def set_var(self, name, value):
        self.vars[name] = value

    def run(self, instructions, debug=False):
        instructions = self.preprocess_labels(instructions)

        ip = 0
        max_steps = 20000
        steps = 0

        while ip < len(instructions):
            if steps > max_steps:
                raise Exception("Infinite loop detected (step limit)")

            steps += 1

            ins = instructions[ip]
            parts = ins.split()
            op = parts[0]

            if debug:
                print(
                    f"IP={ip}, OP={op}, PARTS={parts[1:]}, REGS={self.reg}, VARS={self.vars}"
                )

            if not is_valid(op):
                raise Exception(f"Illegal instruction: {op}")

            if op == "MOV":
                dest = parts[1]
                value = self.get(parts[2])
                if dest in self.reg:
                    self.reg[dest] = float(value)
                else:
                    self.set_var(dest, float(value))

            elif op == "ASSIGN":
                var_name = parts[1]
                value = self.get(parts[2])
                self.set_var(var_name, value)

            elif op == "CONST":
                temp_name = parts[1]
                value = float(parts[2])
                self.set_var(temp_name, value)

            elif op == "FADD":
                dest = parts[1]
                value = self._fpu_add(self.get(parts[2]), self.get(parts[3]))
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "FSUB":
                dest = parts[1]
                value = self._fpu_sub(self.get(parts[2]), self.get(parts[3]))
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "FMUL":
                dest = parts[1]
                value = self._fpu_mul(self.get(parts[2]), self.get(parts[3]))
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "FDIV":
                dest = parts[1]
                value = self._fpu_div(self.get(parts[2]), self.get(parts[3]))
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "GT":
                dest = parts[1]
                value = 1.0 if self.get(parts[2]) > self.get(parts[3]) else 0.0
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "LT":
                dest = parts[1]
                value = 1.0 if self.get(parts[2]) < self.get(parts[3]) else 0.0
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "GE":
                dest = parts[1]
                value = 1.0 if self.get(parts[2]) >= self.get(parts[3]) else 0.0
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "LE":
                dest = parts[1]
                value = 1.0 if self.get(parts[2]) <= self.get(parts[3]) else 0.0
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "EQ":
                dest = parts[1]
                value = 1.0 if self.get(parts[2]) == self.get(parts[3]) else 0.0
                if dest in self.reg:
                    self.reg[dest] = value
                else:
                    self.set_var(dest, value)

            elif op == "JUMP":
                if parts[1] not in self.labels:
                    raise Exception(f"Unknown label: {parts[1]}")
                ip = self.labels[parts[1]]
                continue

            elif op == "JUMP_IF_FALSE":
                cond = self.get(parts[1])
                if cond == 0.0 or cond == False:
                    if parts[2] not in self.labels:
                        raise Exception(f"Unknown label: {parts[2]}")
                    ip = self.labels[parts[2]]
                    continue

            elif op == "JUMP_IF_TRUE":
                cond = self.get(parts[1])
                if cond != 0.0 and cond != False:
                    if parts[2] not in self.labels:
                        raise Exception(f"Unknown label: {parts[2]}")
                    ip = self.labels[parts[2]]
                    continue

            elif op == "PRINT":
                value = self.get(parts[1])
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                elif isinstance(value, float):
                    value = round(value, 6)
                self.output.append(str(value))

            elif op == "HALT":
                break

            else:
                raise Exception(f"Unknown instruction: {op}")

            ip += 1

        return "\n".join(self.output)

    def reset(self):
        for k in self.reg:
            self.reg[k] = 0.0
        self.vars.clear()
        self.labels.clear()
        self.output.clear()
