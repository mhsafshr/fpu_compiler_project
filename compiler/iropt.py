class IROptimizer:
    """IR-level optimizer for constant propagation and dead code elimination."""

    def optimize(self, ir):
        """
        Optimize IR instruction list.

        Optimizations:
        1. Constant propagation: replace ASSIGN with CONST when source is known
        2. Constant folding: compute operations at compile time
        3. Conditional branch elimination: remove IF_FALSE when condition is known
        """
        optimized = []
        temp_values = {}  # known values of temporaries (t0 -> 3.14)
        constants = {}  # known values of regular variables

        for ins in ir:
            # Labels: keep as-is
            if ins[0] == "LABEL":
                optimized.append(ins)
                continue

            # CONST: record the value for future propagation
            if ins[0] == "CONST":
                target = ins[1]
                value = ins[2]

                # Only track temporaries (t0, t1, ...)
                if target.startswith("t") and len(target) > 1 and target[1].isdigit():
                    try:
                        temp_values[target] = float(value)
                    except:
                        temp_values[target] = value
                else:
                    constants[target] = value

                optimized.append(ins)
                continue

            # ASSIGN: propagate constant if possible
            if ins[0] == "ASSIGN":
                target = ins[1]
                value = ins[2]

                # If source is a known constant temporary and target is also temporary
                if (
                    value in temp_values
                    and target.startswith("t")
                    and len(target) > 1
                    and target[1].isdigit()
                ):
                    # Replace ASSIGN with CONST
                    optimized.append(("CONST", target, temp_values[value]))
                    temp_values[target] = temp_values[value]
                    continue

                optimized.append(ins)
                # Invalidate any known value for the target
                if target.startswith("t") and len(target) > 1 and target[1].isdigit():
                    temp_values.pop(target, None)
                else:
                    constants.pop(target, None)
                continue

            # PRINT: keep as-is
            if ins[0] == "PRINT":
                optimized.append(ins)
                continue

            # GOTO: keep as-is
            if ins[0] == "GOTO":
                optimized.append(ins)
                continue

            # IF_FALSE: eliminate or simplify if condition is known
            if ins[0] == "IF_FALSE":
                cond = ins[1]
                label = ins[2]

                if cond in temp_values:
                    cond_val = temp_values[cond]
                    if cond_val == 0.0:
                        # Always false: replace with unconditional jump
                        optimized.append(("GOTO", label))
                        continue
                    else:
                        # Always true: remove the branch entirely
                        continue

                optimized.append(ins)
                continue

            # Binary operations: constant folding
            if len(ins) == 4:
                target, op, left, right = ins

                compare_ops = {"<", ">", "<=", ">=", "=="}
                is_compare = op in compare_ops

                # Only fold non-comparison ops (comparisons need special handling)
                if left in temp_values and right in temp_values and not is_compare:
                    try:
                        l = float(temp_values[left])
                        r = float(temp_values[right])

                        if op == "+":
                            val = l + r
                        elif op == "-":
                            val = l - r
                        elif op == "*":
                            val = l * r
                        elif op == "/":
                            if r == 0:
                                raise ZeroDivisionError()
                            val = l / r
                        else:
                            optimized.append(ins)
                            continue

                        # Replace operation with constant
                        optimized.append(("CONST", target, val))
                        temp_values[target] = val
                        continue

                    except (ValueError, TypeError, ZeroDivisionError):
                        pass  # Don't optimize on error

                optimized.append(ins)
                if target.startswith("t") and len(target) > 1 and target[1].isdigit():
                    temp_values.pop(target, None)
                continue

            # Any other instruction: keep as-is
            optimized.append(ins)

        return optimized
