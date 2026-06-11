from compiler.isa import is_valid
from compiler.fpu_core import IEEE754_32


class VM:
    """Virtual Machine that executes VM instructions with FPU support."""

    def __init__(self):
        # 20 general-purpose registers (R0 to R19), all start at 0.0
        self.reg = {f"R{i}": 0.0 for i in range(20)}
        # User variables (x, sum, etc.) stored here
        self.vars = {}
        # Labels for jump targets (L0 -> instruction index)
        self.labels = {}
        # Collected print output
        self.output = []
        # FPU core for IEEE754 floating-point operations
        self.fpu = IEEE754_32

    # Wrapper methods for FPU operations
    def _fpu_add(self, a, b):
        return self.fpu.add(a, b)

    def _fpu_sub(self, a, b):
        return self.fpu.sub(a, b)

    def _fpu_mul(self, a, b):
        return self.fpu.mul(a, b)

    def _fpu_div(self, a, b):
        return self.fpu.div(a, b)

    def hex_to_float(self, x):
        """Convert IEEE754 hex string (0x40490FDB) back to float (3.14159)."""
        if isinstance(x, str) and x.startswith("0x"):
            try:
                bits = int(x, 16)
                import struct

                return struct.unpack("!f", struct.pack("!I", bits))[0]
            except:
                pass
        return None

    def preprocess_labels(self, instructions):
        """Scan instructions, record label positions, and remove LABEL instructions."""
        cleaned = []
        self.labels = {}

        for i, ins in enumerate(instructions):
            ins = ins.strip()

            if ins.startswith("LABEL"):
                parts = ins.split()
                if len(parts) != 2:
                    raise Exception(f"Invalid label: {ins}")
                # Store label name -> index in cleaned list
                self.labels[parts[1]] = len(cleaned)
            else:
                cleaned.append(ins)

        return cleaned

    def get(self, x):
        """Get value from: hex literal, register, variable, number literal, or temporary."""
        # 1. Check if it's a hex literal (0x...)
        hex_val = self.hex_to_float(x)
        if hex_val is not None:
            return hex_val

        # 2. Check if it's a register (R0, R1, ...)
        if x in self.reg:
            return self.reg[x]

        # 3. Check if it's a user variable
        if x in self.vars:
            return self.vars[x]

        # 4. Try to convert to float directly (e.g., "3.14")
        try:
            return float(x)
        except:
            pass

        # 5. Uninitialized temporary (t0, t1...) - create with 0.0
        if isinstance(x, str) and x.startswith("t"):
            self.vars[x] = 0.0
            return 0.0

        raise Exception(f"Unknown operand: {x}")

    def set_var(self, name, value):
        """Store a value in a variable."""
        self.vars[name] = value

    def run(self, instructions, debug=False):
        """Execute VM instructions. Returns concatenated output as string."""

        # Step 1: Preprocess labels
        instructions = self.preprocess_labels(instructions)

        ip = 0  # Instruction pointer (program counter)
        max_steps = 20000  # Prevent infinite loops
        steps = 0

        # Step 2: Main execution loop
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

            # Validate instruction
            if not is_valid(op):
                raise Exception(f"Illegal instruction: {op}")

            # ----- Data Movement -----
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
                value = self.get(parts[2])
                self.set_var(temp_name, value)

            # ----- FPU Arithmetic -----
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

            # ----- Comparisons (result is 1.0 for true, 0.0 for false) -----
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

            # ----- Control Flow -----
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

            # ----- I/O -----
            elif op == "PRINT":
                value = self.get(parts[1])
                # Clean up output: int if whole number, round floats
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                elif isinstance(value, float):
                    value = round(value, 6)
                self.output.append(str(value))

            # ----- Termination -----
            elif op == "HALT":
                break

            else:
                raise Exception(f"Unknown instruction: {op}")

            ip += 1

        # Return all printed output joined by newline
        return "\n".join(self.output)

    def reset(self):
        """Reset VM state for a fresh execution."""
        for k in self.reg:
            self.reg[k] = 0.0
        self.vars.clear()
        self.labels.clear()
        self.output.clear()
