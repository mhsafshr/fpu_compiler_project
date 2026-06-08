import time
from compiler.lexer import lexer
from compiler.parser import parse
from compiler.optimizer import Optimizer
from compiler.ir import IRGenerator
from compiler.iropt import IROptimizer
from compiler.backend import Backend
from vm.vm import VM


class FPUBenchmark:
    def __init__(self):
        self.optimizer = Optimizer()
        self.irgen = IRGenerator()
        self.iropt = IROptimizer()
        self.backend = Backend()
        self.vm = VM()

    def run_benchmark(self, code, name="Unnamed"):
        print(f"\n{'='*60}")
        print(f"Benchmark: {name}")
        print(f"{'='*60}")

        tokens = lexer(code)
        ast = parse(tokens)

        ir = self.irgen.generate(ast)
        inst = self.backend.generate(ir)

        self.vm.reset()
        start = time.time()
        result_no_opt = self.vm.run(inst)
        time_no_opt = time.time() - start

        opt_ast = self.optimizer.optimize(ast)
        ir_opt = self.irgen.generate(opt_ast)
        ir_opt_opt = self.iropt.optimize(ir_opt)
        inst_opt = self.backend.generate(ir_opt_opt)

        self.vm.reset()
        start = time.time()
        result_opt = self.vm.run(inst_opt)
        time_opt = time.time() - start

        ir_before_count = len(ir)
        ir_after_count = len(ir_opt_opt)
        inst_before_count = len(inst)
        inst_after_count = len(inst_opt)

        ir_reduction = (
            (1 - ir_after_count / ir_before_count) * 100 if ir_before_count > 0 else 0
        )
        inst_reduction = (
            (1 - inst_after_count / inst_before_count) * 100
            if inst_before_count > 0
            else 0
        )
        speedup = time_no_opt / time_opt if time_opt > 0 else 1.0

        print(f"\n📊 STATISTICS:")
        print(f"  IR instructions (before opt):  {ir_before_count}")
        print(f"  IR instructions (after opt):   {ir_after_count}")
        print(f"  Reduction:                     {ir_reduction:.1f}%")

        print(f"\n  Backend instructions (before): {inst_before_count}")
        print(f"  Backend instructions (after):  {inst_after_count}")
        print(f"  Reduction:                     {inst_reduction:.1f}%")

        print(f"\n  Execution time (no opt):  {time_no_opt*1000:.2f} ms")
        print(f"  Execution time (with opt): {time_opt*1000:.2f} ms")
        print(f"  Speedup:                   {speedup:.2f}x")

        if result_no_opt == result_opt:
            print(f"\n✅ Output match")
        else:
            print(f"\n❌ Output MISMATCH!")

        return {
            "name": name,
            "ir_before": ir_before_count,
            "ir_after": ir_after_count,
            "ir_reduction": ir_reduction,
            "inst_before": inst_before_count,
            "inst_after": inst_after_count,
            "inst_reduction": inst_reduction,
            "time_no_opt_ms": time_no_opt * 1000,
            "time_opt_ms": time_opt * 1000,
            "speedup": speedup,
            "correct": result_no_opt == result_opt,
        }
