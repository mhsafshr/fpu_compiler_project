# compiler/isa.py

ARITHMETIC_OPS = ["ADD", "SUB", "MUL", "DIV"]

FPU_OPS = ["FADD", "FSUB", "FMUL", "FDIV"]

COMPARE_OPS = ["GT", "LT", "GE", "LE", "EQ"]

CONTROL_FLOW_OPS = ["JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"]

MEMORY_OPS = ["MOV", "LOAD", "STORE"]

SYSTEM_OPS = ["PRINT", "HALT"]


def is_valid(op: str) -> bool:
    return (
        op in ARITHMETIC_OPS
        or op in FPU_OPS
        or op in COMPARE_OPS
        or op in CONTROL_FLOW_OPS
        or op in MEMORY_OPS
        or op in SYSTEM_OPS
    )
