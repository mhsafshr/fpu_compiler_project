from compiler.ast import Number, Var, BinOp, Assign, Program, If, While, Print


class Optimizer:
    """AST-level optimizer for constant folding and identity elimination."""

    def optimize_block(self, block):
        """Optimize a block (list of statements)."""
        if block is None:
            return []

        if isinstance(block, list):
            result = []
            for stmt in block:
                optimized = self.optimize(stmt)
                if optimized is not None:
                    if isinstance(optimized, Program):
                        result.extend(optimized.statements)
                    else:
                        result.append(optimized)
            return result

        optimized = self.optimize(block)
        if optimized is None:
            return []
        if isinstance(optimized, Program):
            return optimized.statements
        return [optimized]

    def optimize(self, node):
        """Recursively optimize an AST node."""

        # Program: optimize all statements
        if isinstance(node, Program):
            return Program(self.optimize_block(node.statements))

        # Leaves: numbers and variables are already optimized
        if isinstance(node, (Number, Var)):
            return node

        # Assign: optimize the right-hand side
        if isinstance(node, Assign):
            return Assign(node.name, self.optimize(node.value))

        # Print: optimize the expression
        if isinstance(node, Print):
            return Print(self.optimize(node.expr))

        # If: constant condition folding
        if isinstance(node, If):
            condition = self.optimize(node.condition)
            then_body = self.optimize_block(node.then_body)
            else_body = self.optimize_block(node.else_body) if node.else_body else []

            # If condition is constant at compile time
            if isinstance(condition, Number):
                if condition.value != 0:  # true branch
                    if len(then_body) == 0:
                        return None
                    elif len(then_body) == 1:
                        return then_body[0]
                    else:
                        return Program(then_body)
                else:  # false branch
                    if len(else_body) == 0:
                        return None
                    elif len(else_body) == 1:
                        return else_body[0]
                    else:
                        return Program(else_body)

            if not else_body:
                else_body = None
            return If(condition, then_body, else_body)

        # While: remove loops with constant false condition
        if isinstance(node, While):
            condition = self.optimize(node.condition)
            body = self.optimize_block(node.body)

            if isinstance(condition, Number):
                if condition.value == 0:  # never executes
                    return None

            if not body:  # empty loop body
                return None

            return While(condition, body)

        # BinOp: constant folding and identity elimination
        if isinstance(node, BinOp):
            left = self.optimize(node.left)
            right = self.optimize(node.right)
            op = node.op

            # Constant folding: both operands are numbers → compute at compile time
            if isinstance(left, Number) and isinstance(right, Number):
                if op == "+":
                    return Number(left.value + right.value)
                if op == "-":
                    return Number(left.value - right.value)
                if op == "*":
                    return Number(left.value * right.value)
                if op == "/":
                    if right.value == 0:
                        raise ZeroDivisionError("Division by zero in optimizer")
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

            # Identity elimination: x + 0 = x, 0 + x = x
            if op == "+":
                if isinstance(right, Number) and right.value == 0:
                    return left
                if isinstance(left, Number) and left.value == 0:
                    return right

            # Identity elimination: x * 1 = x, x * 0 = 0, 1 * x = x, 0 * x = 0
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
