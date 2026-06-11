# Entry point - REPL for the compiler
# Type code line by line, then type END to compile and run
# Type BENCHMARK to see performance stats
# Type EXIT to quit

from compiler.lexer import lexer
from compiler.parser import parse
from compiler.optimizer import Optimizer
from compiler.ir import IRGenerator
from compiler.iropt import IROptimizer
from compiler.backend import Backend
from compiler.type_checker import TypeChecker
from vm.vm import VM
from benchmark import FPUBenchmark

# Create all compiler components
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

lines = []  # buffer for multi-line input


def print_section(title, content):
    """Pretty print a section with a title."""
    print(f"\n===== {title} =====")
    print(content)


# Main REPL loop
while True:
    line = input(">>> ")

    # Exit command
    if line.strip() == "EXIT":
        break

    # Benchmark command - runs performance tests on current code
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

    # END command - compile and run the accumulated code
    if line.strip() == "END":
        code = "\n".join(lines)

        try:
            # Step 1: Lexical analysis (tokens)
            tokens = lexer(code)

            # Step 2: Syntax analysis (AST)
            ast = parse(tokens)

            # Step 3: Semantic analysis (type checking)
            type_checker.check(ast)

            # Step 4: AST-level optimization
            opt_ast = optimizer.optimize(ast)

            # Step 5: IR generation
            ir = irgen.generate(opt_ast)

            # Step 6: IR-level optimization
            ir = iropt.optimize(ir)

            # Step 7: Code generation (VM instructions)
            instructions = backend.generate(ir)

            # Step 8: Execution on VM
            vm.reset()
            result = vm.run(instructions)

            # Show all intermediate results
            print_section("TOKENS", tokens)
            print_section("AST", ast)
            print_section("OPTIMIZED AST", opt_ast)
            print_section("IR", "\n".join(str(x) for x in ir))
            print_section("INSTRUCTIONS", "\n".join(instructions))
            print_section("RESULT", result)

            print("\n-----------------------------\n")

        except Exception as e:
            print("ERROR:", e)

        lines = []  # clear buffer after execution
        continue

    # Regular input line - add to buffer
    lines.append(line)
