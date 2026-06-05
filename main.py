from compiler.lexer import lexer
from compiler.parser import parse
from compiler.optimizer import Optimizer

from compiler.ir import IRGenerator
from compiler.iropt import IROptimizer
from compiler.backend import Backend

from vm.vm import VM

vm = VM()
optimizer = Optimizer()

irgen = IRGenerator()
iropt = IROptimizer()
backend = Backend()

print("Mini Compiler REPL (type END to run block, EXIT to quit)\n")

lines = []


def print_section(title, content):
    print(f"\n===== {title} =====")
    print(content)


while True:
    line = input(">>> ")

    if line.strip() == "EXIT":
        break

    if line.strip() == "END":
        code = "\n".join(lines)

        try:
            # =====================================================
            # FRONTEND
            # =====================================================
            tokens = lexer(code)
            ast = parse(tokens)
            opt_ast = optimizer.optimize(ast)

            # =====================================================
            # IR GENERATION
            # =====================================================
            ir = irgen.generate(opt_ast)

            # =====================================================
            # IR OPTIMIZATION
            # =====================================================
            ir = iropt.optimize(ir)

            # =====================================================
            # BACKEND (IR → ISA)
            # =====================================================
            instructions = backend.generate(ir)

            # =====================================================
            # EXECUTION
            # =====================================================
            vm.reset()
            result = vm.run(instructions)

            # =====================================================
            # DEBUG OUTPUT (STRUCTURED)
            # =====================================================
            print_section("TOKENS", tokens)
            print_section("AST", ast)
            print_section("OPTIMIZED AST", opt_ast)
            print_section("IR", "\n".join(str(x) for x in ir))
            print_section("INSTRUCTIONS", "\n".join(instructions))
            print_section("RESULT", result)

            print("\n-----------------------------\n")

        except Exception as e:
            print("ERROR:", e)

        lines = []
        continue

    lines.append(line)
