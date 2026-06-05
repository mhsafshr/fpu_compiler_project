class IROptimizer:
    def optimize(self, ir):
        optimized = []

        for ins in ir:

            # PRINT
            if ins[0] == "PRINT":
                optimized.append(ins)

            # ASSIGN
            elif len(ins) == 3 and ins[1] == "=":
                optimized.append(ins)

            # BINARY OPS
            elif len(ins) == 4:
                target, op, left, right = ins

                try:
                    l = float(left)
                    r = float(right)

                    if op == "+":
                        val = l + r
                    elif op == "-":
                        val = l - r
                    elif op == "*":
                        val = l * r
                    elif op == "/":
                        val = l / r
                    elif op == ">":
                        val = 1.0 if l > r else 0.0
                    elif op == "<":
                        val = 1.0 if l < r else 0.0
                    elif op == ">=":
                        val = 1.0 if l >= r else 0.0
                    elif op == "==":
                        val = 1.0 if l == r else 0.0
                    else:
                        optimized.append(ins)
                        continue

                    optimized.append((target, "=", val))

                except:
                    optimized.append(ins)

            else:
                optimized.append(ins)

        return optimized
