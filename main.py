from compiler.lexer import lexer
from compiler.parser import parse
from compiler.optimizer import Optimizer
from compiler.codegen import CodeGenerator
from vm.vm import VM

# ----------------------------
# گرفتن ورودی چندخطی
# ----------------------------
lines = []

print("Enter your program (type END to run):")

while True:
    line = input()

    if line.strip() == "END":
        break

    lines.append(line)

code = "\n".join(lines)

# ----------------------------
# Compile Pipeline
# ----------------------------
tokens = lexer(code)
ast = parse(tokens)

optimizer = Optimizer()
opt_ast = optimizer.optimize(ast)

codegen = CodeGenerator()
instructions = codegen.generate(opt_ast)

vm = VM()
result = vm.run(instructions)

# ----------------------------
# Output
# ----------------------------
print("\nTOKENS:", tokens)
print("\nAST:", ast)
print("\nOPTIMIZED AST:", opt_ast)

print("\nINSTRUCTIONS:")
for i in instructions:
    print(i)

print("\nRESULT:", result)
