class IROptimizer:
    def optimize(self, ir):
        optimized = []
        temp_values = {}
        constants = {}

        for ins in ir:
            if ins[0] == "LABEL":
                optimized.append(ins)
                continue

            if ins[0] == "CONST":
                target = ins[1]
                value = ins[2]

                if target.startswith("t") and len(target) > 1 and target[1].isdigit():
                    try:
                        temp_values[target] = float(value)
                    except:
                        temp_values[target] = value
                else:
                    constants[target] = value

                optimized.append(ins)
                continue

            if ins[0] == "ASSIGN":
                target = ins[1]
                value = ins[2]

                if (
                    value in temp_values
                    and target.startswith("t")
                    and len(target) > 1
                    and target[1].isdigit()
                ):
                    optimized.append(("CONST", target, temp_values[value]))
                    temp_values[target] = temp_values[value]
                    continue

                optimized.append(ins)
                if target.startswith("t") and len(target) > 1 and target[1].isdigit():
                    temp_values.pop(target, None)
                else:
                    constants.pop(target, None)
                continue

            if ins[0] == "PRINT":
                optimized.append(ins)
                continue

            if ins[0] == "GOTO":
                optimized.append(ins)
                continue

            if ins[0] == "IF_FALSE":
                cond = ins[1]
                label = ins[2]

                if cond in temp_values:
                    cond_val = temp_values[cond]
                    if cond_val == 0.0:
                        optimized.append(("GOTO", label))
                        continue
                    else:
                        continue

                optimized.append(ins)
                continue

            if len(ins) == 4:
                target, op, left, right = ins

                compare_ops = {"<", ">", "<=", ">=", "=="}
                is_compare = op in compare_ops

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

                        optimized.append(("CONST", target, val))
                        temp_values[target] = val
                        continue

                    except (ValueError, TypeError, ZeroDivisionError):
                        pass

                optimized.append(ins)
                if target.startswith("t") and len(target) > 1 and target[1].isdigit():
                    temp_values.pop(target, None)
                continue

            optimized.append(ins)

        return optimized
