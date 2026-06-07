from flask import Flask, render_template, request, jsonify
from compiler.lexer import lexer
from compiler.parser import parse
from compiler.optimizer import Optimizer
from compiler.ir import IRGenerator
from compiler.iropt import IROptimizer
from compiler.backend import Backend
from vm.vm import VM
import traceback

app = Flask(__name__)


def run_compiler(code):
    try:
        tokens = lexer(code)
        tokens_str = [str(t) for t in tokens]

        ast = parse(tokens)

        optimizer = Optimizer()
        opt_ast = optimizer.optimize(ast)

        irgen = IRGenerator()
        ir = irgen.generate(opt_ast)
        ir_str = [str(i) for i in ir]

        iropt = IROptimizer()
        ir_opt = iropt.optimize(ir)
        ir_opt_str = [str(i) for i in ir_opt]

        backend = Backend()
        instructions = backend.generate(ir_opt)

        vm = VM()
        vm.reset()
        result = vm.run(instructions)

        return {
            "success": True,
            "tokens": tokens_str,
            "ast": str(ast),
            "optimized_ast": str(opt_ast),
            "ir": ir_str,
            "optimized_ir": ir_opt_str,
            "instructions": instructions,
            "result": str(result),
            "output": "\n".join(vm.output),
        }

    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.get_json()
    code = data.get("code", "")
    result = run_compiler(code)
    return jsonify(result)


if __name__ == "__main__":
    print("🚀 Server starting at http://localhost:5000")
    app.run(debug=True, port=5000)
