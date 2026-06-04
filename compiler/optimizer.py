from compiler.ast import Number, Var, BinOp, Assign, Program, If, While


class Optimizer:

    def optimize_block(self, block):
        if block is None:
            return None

        if isinstance(block, list):
            return [self.optimize(stmt) for stmt in block]

        return self.optimize(block)

    def optimize(self, node):

        # ---------------- Program ----------------
        if isinstance(node, Program):
            return Program([self.optimize(stmt) for stmt in node.statements])

        # ---------------- Number / Var ----------------
        if isinstance(node, Number) or isinstance(node, Var):
            return node

        # ---------------- Assign ----------------
        if isinstance(node, Assign):
            return Assign(node.name, self.optimize(node.value))

        # ---------------- IF (🔥 IMPROVED) ----------------
        if isinstance(node, If):
            condition = self.optimize(node.condition)
            then_body = self.optimize_block(node.then_body)
            else_body = self.optimize_block(node.else_body)

            # 🔥 constant condition evaluation
            if isinstance(condition, Number):
                if condition.value != 0:
                    return then_body
                else:
                    return else_body if else_body else None

            return If(condition, then_body, else_body)

        # ---------------- WHILE ----------------
        if isinstance(node, While):
            return While(self.optimize(node.condition), self.optimize_block(node.body))

        # ---------------- BinOp ----------------
        if isinstance(node, BinOp):

            left = self.optimize(node.left)
            right = self.optimize(node.right)
            op = node.op

            # constant folding
            if isinstance(left, Number) and isinstance(right, Number):
                if op == "+":
                    return Number(left.value + right.value)
                if op == "-":
                    return Number(left.value - right.value)
                if op == "*":
                    return Number(left.value * right.value)
                if op == "/":
                    return Number(left.value / right.value)

                # comparisons → return boolean as Number
                if op == ">":
                    return Number(1.0 if left.value > right.value else 0.0)
                if op == "<":
                    return Number(1.0 if left.value < right.value else 0.0)
                if op == ">=":
                    return Number(1.0 if left.value >= right.value else 0.0)
                if op == "<=":
                    return Number(1.0 if left.value <= right.value else 0.0)
                if op == "==":
                    return Number(1.0 if left.value == right.value else 0.0)

            # simplification
            if op == "+":
                if isinstance(right, Number) and right.value == 0:
                    return left
                if isinstance(left, Number) and left.value == 0:
                    return right

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
