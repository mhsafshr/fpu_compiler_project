# This file defines all valid VM instructions and provides
# a validation function used by the VM during execution.

# Arithmetic operations for integers (NOT currently used in this VM)
# Kept for potential future extension
ARITHMETIC_OPS = ["ADD", "SUB", "MUL", "DIV"]

# FPU operations for floating-point arithmetic
# These are the core instructions for float calculations
FPU_OPS = ["FADD", "FSUB", "FMUL", "FDIV"]

# Comparison operations
# All return 1.0 (true) or 0.0 (false) as float
COMPARE_OPS = ["GT", "LT", "GE", "LE", "EQ"]

# Control flow operations
CONTROL_FLOW_OPS = ["JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"]

# Memory operations
# MOV: move between registers/variables
# LOAD/STORE: not heavily used in current implementation
MEMORY_OPS = ["MOV", "LOAD", "STORE"]

# System operations
# PRINT: output value to console
# HALT: stop program execution
SYSTEM_OPS = ["PRINT", "HALT"]


def is_valid(op: str) -> bool:
    """
    Check if an instruction opcode is valid in this VM.

    Used by the VM's run() method to detect illegal instructions
    and prevent execution of invalid code.

    Args:
        op: Instruction name as string (e.g., "FADD", "PRINT")

    Returns:
        True if instruction is valid, False otherwise
    """
    return (
        op in ARITHMETIC_OPS
        or op in FPU_OPS
        or op in COMPARE_OPS
        or op in CONTROL_FLOW_OPS
        or op in MEMORY_OPS
        or op in SYSTEM_OPS
    )
