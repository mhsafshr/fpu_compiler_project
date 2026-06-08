from flask import Flask, render_template, request, jsonify
from compiler.lexer import lexer
from compiler.parser import parse
from compiler.optimizer import Optimizer
from compiler.ir import IRGenerator
from compiler.iropt import IROptimizer
from compiler.backend import Backend
from vm.vm import VM
import traceback
import time

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


def run_benchmark(code):
    try:
        tokens = lexer(code)
        ast = parse(tokens)

        optimizer = Optimizer()
        irgen = IRGenerator()
        iropt = IROptimizer()
        backend = Backend()
        vm = VM()

        ir_before = irgen.generate(ast)
        inst_before = backend.generate(ir_before)

        vm.reset()
        start = time.time()
        vm.run(inst_before)
        time_before = (time.time() - start) * 1000

        opt_ast = optimizer.optimize(ast)
        ir_after = irgen.generate(opt_ast)
        ir_after = iropt.optimize(ir_after)
        inst_after = backend.generate(ir_after)

        vm.reset()
        start = time.time()
        vm.run(inst_after)
        time_after = (time.time() - start) * 1000

        ir_reduction = (
            (1 - len(ir_after) / len(ir_before)) * 100 if len(ir_before) > 0 else 0
        )
        inst_reduction = (
            (1 - len(inst_after) / len(inst_before)) * 100
            if len(inst_before) > 0
            else 0
        )
        speedup = time_before / time_after if time_after > 0 else 1.0

        return {
            "success": True,
            "ir_before": len(ir_before),
            "ir_after": len(ir_after),
            "ir_reduction": round(ir_reduction, 1),
            "inst_before": len(inst_before),
            "inst_after": len(inst_after),
            "inst_reduction": round(inst_reduction, 1),
            "time_before_ms": round(time_before, 2),
            "time_after_ms": round(time_after, 2),
            "speedup": round(speedup, 2),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/compile", methods=["POST"])
def compile_code():
    data = request.get_json()
    code = data.get("code", "")
    result = run_compiler(code)
    return jsonify(result)


@app.route("/benchmark", methods=["POST"])
def benchmark_code():
    data = request.get_json()
    code = data.get("code", "")
    result = run_benchmark(code)
    return jsonify(result)


if __name__ == "__main__":
    print("🚀 Server starting at http://localhost:5000")
    app.run(debug=True, port=5000)
