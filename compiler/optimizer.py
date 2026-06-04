from compiler.ast import Number, Var, BinOp, Assign, Program


class Optimizer:

    def optimize(self, node):

        # ---------------- Program ----------------
        if isinstance(node, Program):
            optimized_statements = []

            for stmt in node.statements:
                optimized_statements.append(self.optimize(stmt))

            return Program(optimized_statements)

        # ---------------- Number / Var ----------------
        if isinstance(node, Number) or isinstance(node, Var):
            return node

        # ---------------- Assign ----------------
        if isinstance(node, Assign):
            value = self.optimize(node.value)
            return Assign(node.name, value)

        # ---------------- BinOp ----------------
        if isinstance(node, BinOp):

            left = self.optimize(node.left)
            right = self.optimize(node.right)
            op = node.op

            # x + 0
            if op == "+":
                if isinstance(right, Number) and right.value == 0:
                    return left
                if isinstance(left, Number) and left.value == 0:
                    return right

            # x * 1 / 0
            if op == "*":
                if isinstance(right, Number) and right.value == 1:
                    return left
                if isinstance(left, Number) and left.value == 1:
                    return right
                if isinstance(right, Number) and right.value == 0:
                    return Number(0)
                if isinstance(left, Number) and left.value == 0:
                    return Number(0)

            return BinOp(left, op, right)

        raise Exception(f"Unknown node type: {type(node)}")
