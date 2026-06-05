from compiler.ast import Number, Var, BinOp, Assign, Program, If, While, Print


class Optimizer:

    # ---------------- BLOCK ----------------
    def optimize_block(self, block):
        if block is None:
            return []

        if isinstance(block, list):
            result = []
            for stmt in block:
                optimized = self.optimize(stmt)
                if optimized is not None:
                    result.append(optimized)
            return result

        optimized = self.optimize(block)
        return [optimized] if optimized is not None else []

    # ---------------- MAIN OPTIMIZE ----------------
    def optimize(self, node):

        # ---------------- PROGRAM ----------------
        if isinstance(node, Program):
            return Program(self.optimize_block(node.statements))

        # ---------------- LEAF NODES ----------------
        if isinstance(node, (Number, Var)):
            return node

        # ---------------- ASSIGN ----------------
        if isinstance(node, Assign):
            return Assign(node.name, self.optimize(node.value))

        # ---------------- PRINT ----------------
        if isinstance(node, Print):
            return Print(self.optimize(node.expr))

        # ---------------- IF ----------------
        if isinstance(node, If):
            condition = self.optimize(node.condition)
            then_body = self.optimize_block(node.then_body)
            else_body = self.optimize_block(node.else_body)

            # constant folding for IF
            if isinstance(condition, Number):
                if condition.value != 0:
                    return Program(then_body)
                else:
                    return Program(else_body) if else_body else Program([])

            return If(condition, then_body, else_body)

        # ---------------- WHILE ----------------
        if isinstance(node, While):
            condition = self.optimize(node.condition)
            body = self.optimize_block(node.body)

            # dead loop elimination
            if isinstance(condition, Number) and condition.value == 0:
                return Program([])

            return While(condition, body)

        # ---------------- BINOP ----------------
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

            # algebraic simplification
            if op == "+":
                if isinstance(right, Number) and right.value == 0:
                    return left
                if isinstance(left, Number) and left.value == 0:
                    return right

            if op == "*":
                if isinstance(right, Number):
                    if right.value == 1:
                        return left
                    if right.value == 0:
                        return Number(0.0)

                if isinstance(left, Number):
                    if left.value == 1:
                        return right
                    if left.value == 0:
                        return Number(0.0)

            return BinOp(left, op, right)

        raise Exception(f"Unknown node type: {type(node)}")
