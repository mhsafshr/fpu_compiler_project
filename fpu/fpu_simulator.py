class FPUSimulator:
    def __init__(self):
        pass

    def add(self, a, b):
        return float(a + b)

    def sub(self, a, b):
        return float(a - b)

    def mul(self, a, b):
        return float(a * b)

    def div(self, a, b):
        if b == 0:
            raise ZeroDivisionError("FPU Error: Division by zero")
        return float(a / b)
