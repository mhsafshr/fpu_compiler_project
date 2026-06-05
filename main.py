from compiler.lexer import lexer
from compiler.parser import parse
from compiler.optimizer import Optimizer
from compiler.codegen import CodeGenerator
from vm.vm import VM

vm = VM()
optimizer = Optimizer()
codegen = CodeGenerator()

print("Mini Compiler REPL (type END to run block, EXIT to quit)\n")

lines = []

while True:
    line = input(">>> ")

    if line.strip() == "EXIT":
        break

    if line.strip() == "END":
        code = "\n".join(lines)

        try:
            # ---------------- Pipeline ----------------
            tokens = lexer(code)
            ast = parse(tokens)
            opt_ast = optimizer.optimize(ast)
            instructions = codegen.generate(opt_ast)

            result = vm.run(instructions)

            # ---------------- Debug Output ----------------
            print("\nTOKENS:")
            print(tokens)

            print("\nAST:")
            print(ast)

            print("\nOPTIMIZED AST:")
            print(opt_ast)

            print("\nINSTRUCTIONS:")
            for i, ins in enumerate(instructions):
                print(f"{i}: {ins}")

            print("\nRESULT:")
            print(result)

            print("\n-----------------------------\n")

        except Exception as e:
            print("ERROR:", e)

        lines = []
        continue

    lines.append(line)
