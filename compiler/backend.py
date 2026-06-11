import struct


class Backend:
    """Code generator - converts IR to VM instructions with register allocation."""

    def __init__(self):
        self.instructions = []  # output VM instructions
        self.reg_count = 0  # next available register (R0, R1, ...)
        self.var_map = {}  # variable/temp -> register mapping
        self.label_count = 0  # counter for label generation
        self.max_regs = 20  # maximum registers (R0-R19)

    def new_reg(self):
        """Allocate a new register. Raise error if no registers left."""
        if self.reg_count >= self.max_regs:
            raise Exception("Out of registers! Need spilling.")
        r = f"R{self.reg_count}"
        self.reg_count += 1
        return r

    def new_label(self):
        """Generate a fresh label name for jumps."""
        l = f"L{self.label_count}"
        self.label_count += 1
        return l

    def generate(self, ir_instructions):
        """Entry point: convert IR list to VM instruction list."""
        self.instructions = []
        self.var_map = {}
        self.reg_count = 0
        self.label_count = 0

        for ins in ir_instructions:
            self.visit(ins)

        # Ensure program ends with HALT
        if not self.instructions or self.instructions[-1] != "HALT":
            self.instructions.append("HALT")

        return self.instructions

    def float_to_hex(self, value):
        """Convert float to IEEE754 hex representation (e.g., 0x40490FDB for 3.14159)."""
        try:
            f = float(value)
            bits = struct.unpack("!I", struct.pack("!f", f))[0]
            return f"0x{bits:08X}"
        except:
            return None

    def is_float_literal(self, x):
        """Check if string represents a float literal."""
        try:
            float(x)
            return True
        except:
            return False

    def load(self, x):
        """
        Load a value into a register.
        Returns register name containing the value.
        Handles: float literals, existing registers, variables, temporaries.
        """
        # Float literal: MOV immediate hex value into new register
        if self.is_float_literal(x):
            r = self.new_reg()
            hex_val = self.float_to_hex(x)
            self.instructions.append(f"MOV {r} {hex_val}")
            return r

        # Already a register: return as-is
        if isinstance(x, str) and x.startswith("R"):
            return x

        # Already mapped variable: return its register
        if x in self.var_map:
            return self.var_map[x]

        # Temporary variable (t0, t1, ...): allocate new register
        if isinstance(x, str) and x.startswith("t"):
            r = self.new_reg()
            self.var_map[x] = r
            return r

        # Regular variable: allocate new register
        r = self.new_reg()
        self.var_map[x] = r
        return r

    def visit(self, ins):
        """Convert a single IR instruction to VM instruction(s)."""
        op = ins[0]

        # CONST: load constant into register
        if op == "CONST":
            target = ins[1]
            value = ins[2]
            r = self.new_reg()
            if self.is_float_literal(value):
                hex_val = self.float_to_hex(value)
                self.instructions.append(f"MOV {r} {hex_val}")
            else:
                self.instructions.append(f"MOV {r} {value}")
            self.var_map[target] = r
            return

        # ASSIGN: copy value from source to destination
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

        # PRINT: output value
        if op == "PRINT":
            src = self.load(ins[1])
            self.instructions.append(f"PRINT {src}")
            return

        # LABEL: define jump target
        if op == "LABEL":
            self.instructions.append(f"LABEL {ins[1]}")
            return

        # GOTO: unconditional jump
        if op == "GOTO":
            self.instructions.append(f"JUMP {ins[1]}")
            return

        # IF_FALSE: conditional jump
        if op == "IF_FALSE":
            cond = self.load(ins[1])
            self.instructions.append(f"JUMP_IF_FALSE {cond} {ins[2]}")
            return

        # Binary operations (+, -, *, /, comparisons)
        if len(ins) == 4:
            target, binop, left, right = ins

            ops = {"+", "-", "*", "/", ">", "<", ">=", "<=", "=="}
            if binop not in ops:
                raise Exception(f"Unknown op {binop}")

            r1 = self.load(left)
            r2 = self.load(right)
            result = self.new_reg()

            # Map IR operators to VM FPU instructions
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
        """Reset backend state for fresh compilation."""
        self.instructions = []
        self.var_map = {}
        self.reg_count = 0
        self.label_count = 0
