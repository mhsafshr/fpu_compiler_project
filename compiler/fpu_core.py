import struct


class IEEE754_32:
    SIGN_MASK = 0x80000000
    EXP_MASK = 0x7F800000
    MANT_MASK = 0x007FFFFF
    EXP_BIAS = 127
    MANT_BITS = 23
    IMPLICIT_BIT = 0x800000

    @staticmethod
    def float_to_bits(f: float) -> int:
        return struct.unpack("!I", struct.pack("!f", f))[0]

    @staticmethod
    def bits_to_float(bits: int) -> float:
        return struct.unpack("!f", struct.pack("!I", bits))[0]

    @staticmethod
    def extract_fields(bits: int):
        sign = (bits >> 31) & 1
        exp = (bits >> 23) & 0xFF
        mant = bits & 0x7FFFFF
        return sign, exp, mant

    @staticmethod
    def make_bits(sign: int, exp: int, mant: int) -> int:
        return (sign << 31) | ((exp & 0xFF) << 23) | (mant & 0x7FFFFF)

    @staticmethod
    def is_nan(bits: int) -> bool:
        exp = (bits >> 23) & 0xFF
        mant = bits & 0x7FFFFF
        return exp == 0xFF and mant != 0

    @staticmethod
    def is_inf(bits: int) -> bool:
        exp = (bits >> 23) & 0xFF
        mant = bits & 0x7FFFFF
        return exp == 0xFF and mant == 0

    @staticmethod
    def is_zero(bits: int) -> bool:
        exp = (bits >> 23) & 0xFF
        mant = bits & 0x7FFFFF
        return exp == 0 and mant == 0

    @classmethod
    def add(cls, a: float, b: float) -> float:
        bits_a = cls.float_to_bits(a)
        bits_b = cls.float_to_bits(b)

        if cls.is_nan(bits_a):
            return a
        if cls.is_nan(bits_b):
            return b
        if cls.is_inf(bits_a) and cls.is_inf(bits_b):
            sign_a = (bits_a >> 31) & 1
            sign_b = (bits_b >> 31) & 1
            if sign_a != sign_b:
                return cls.bits_to_float(0x7FC00000)
            return a
        if cls.is_inf(bits_a):
            return a
        if cls.is_inf(bits_b):
            return b
        if cls.is_zero(bits_a):
            return b
        if cls.is_zero(bits_b):
            return a

        sign_a, exp_a, mant_a = cls.extract_fields(bits_a)
        sign_b, exp_b, mant_b = cls.extract_fields(bits_b)

        if exp_a != 0:
            mant_a |= cls.IMPLICIT_BIT
        else:
            exp_a = 1

        if exp_b != 0:
            mant_b |= cls.IMPLICIT_BIT
        else:
            exp_b = 1

        if exp_a > exp_b:
            shift = exp_a - exp_b
            mant_b >>= shift
            exp_b = exp_a
        elif exp_b > exp_a:
            shift = exp_b - exp_a
            mant_a >>= shift
            exp_a = exp_b

        exponent = exp_a
        sign_result = sign_a

        if sign_a == sign_b:
            mant_sum = mant_a + mant_b
            sign_result = sign_a
        else:
            if mant_a >= mant_b:
                mant_sum = mant_a - mant_b
                sign_result = sign_a
            else:
                mant_sum = mant_b - mant_a
                sign_result = sign_b

        if mant_sum == 0:
            return 0.0

        while mant_sum < cls.IMPLICIT_BIT and mant_sum != 0:
            mant_sum <<= 1
            exponent -= 1

        if mant_sum >= (cls.IMPLICIT_BIT << 1):
            mant_sum >>= 1
            exponent += 1

        mant_result = mant_sum & cls.MANT_MASK

        if exponent >= 0xFF:
            return cls.bits_to_float(cls.make_bits(sign_result, 0xFF, 0))
        if exponent <= 0:
            return cls.bits_to_float(cls.make_bits(sign_result, 0, 0))

        result_bits = cls.make_bits(sign_result, exponent, mant_result)
        return cls.bits_to_float(result_bits)

    @classmethod
    def sub(cls, a: float, b: float) -> float:
        bits_b = cls.float_to_bits(b)
        bits_b ^= cls.SIGN_MASK
        return cls.add(a, cls.bits_to_float(bits_b))

    @classmethod
    def mul(cls, a: float, b: float) -> float:
        return a * b

    @classmethod
    def div(cls, a: float, b: float) -> float:
        if b == 0.0:
            if a == 0.0:
                return 0.0
            return float("inf") if a > 0 else float("-inf")
        return a / b
