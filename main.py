from compiler.lexer import lexer
from compiler.parser import parse
from compiler.optimizer import Optimizer
from compiler.ir import IRGenerator
from compiler.iropt import IROptimizer
from compiler.backend import Backend
from compiler.type_checker import TypeChecker
from vm.vm import VM
from benchmark import FPUBenchmark

vm = VM()
optimizer = Optimizer()
irgen = IRGenerator()
iropt = IROptimizer()
backend = Backend()
type_checker = TypeChecker()
benchmark = FPUBenchmark()

print(
    "Mini Compiler REPL (type END to run block, BENCHMARK to benchmark, EXIT to quit)\n"
)

lines = []


def print_section(title, content):
    print(f"\n===== {title} =====")
    print(content)


while True:
    line = input(">>> ")

    if line.strip() == "EXIT":
        break

    if line.strip() == "BENCHMARK":
        if not lines:
            print(
                "ERROR: No code to benchmark. Write some code first then type BENCHMARK"
            )
            continue

        code = "\n".join(lines)
        benchmark.run_benchmark(code, "User Code")
        lines = []
        continue

    if line.strip() == "END":
        code = "\n".join(lines)

        try:
            tokens = lexer(code)
            ast = parse(tokens)

            type_checker.check(ast)

            opt_ast = optimizer.optimize(ast)

            ir = irgen.generate(opt_ast)
            ir = iropt.optimize(ir)

            instructions = backend.generate(ir)

            vm.reset()
            result = vm.run(instructions)

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
