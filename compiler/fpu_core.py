import struct


class IEEE754_32:
    """Software implementation of IEEE754 32-bit floating-point unit (FPU)."""

    # IEEE754 single-precision bit masks
    SIGN_MASK = 0x80000000  # 1 bit: sign (bit 31)
    EXP_MASK = 0x7F800000  # 8 bits: exponent (bits 30-23)
    MANT_MASK = 0x007FFFFF  # 23 bits: mantissa (bits 22-0)
    EXP_BIAS = 127  # bias for exponent (2^(8-1)-1)
    MANT_BITS = 23  # number of mantissa bits
    IMPLICIT_BIT = 0x800000  # implicit 1 at bit 24 (for normalized numbers)

    @staticmethod
    def float_to_bits(f: float) -> int:
        """Convert a Python float to its 32-bit IEEE754 representation."""
        return struct.unpack("!I", struct.pack("!f", f))[0]

    @staticmethod
    def bits_to_float(bits: int) -> float:
        """Convert 32-bit IEEE754 representation back to Python float."""
        return struct.unpack("!f", struct.pack("!I", bits))[0]

    @staticmethod
    def extract_fields(bits: int):
        """Extract sign, exponent, and mantissa from 32-bit IEEE754."""
        sign = (bits >> 31) & 1  # bit 31
        exp = (bits >> 23) & 0xFF  # bits 30-23
        mant = bits & 0x7FFFFF  # bits 22-0
        return sign, exp, mant

    @staticmethod
    def make_bits(sign: int, exp: int, mant: int) -> int:
        """Combine sign, exponent, mantissa into 32-bit IEEE754."""
        return (sign << 31) | ((exp & 0xFF) << 23) | (mant & 0x7FFFFF)

    @staticmethod
    def is_nan(bits: int) -> bool:
        """Check if bits represent NaN (Not a Number)."""
        exp = (bits >> 23) & 0xFF
        mant = bits & 0x7FFFFF
        return exp == 0xFF and mant != 0  # all exponent bits 1, mantissa != 0

    @staticmethod
    def is_inf(bits: int) -> bool:
        """Check if bits represent Infinity (positive or negative)."""
        exp = (bits >> 23) & 0xFF
        mant = bits & 0x7FFFFF
        return exp == 0xFF and mant == 0  # all exponent bits 1, mantissa = 0

    @staticmethod
    def is_zero(bits: int) -> bool:
        """Check if bits represent zero (positive or negative zero)."""
        exp = (bits >> 23) & 0xFF
        mant = bits & 0x7FFFFF
        return exp == 0 and mant == 0  # all exponent and mantissa bits 0

    @classmethod
    def add(cls, a: float, b: float) -> float:
        """
        Add two floating-point numbers following IEEE754 standard.

        Algorithm:
        1. Handle special cases (NaN, Inf, Zero)
        2. Extract sign, exponent, mantissa
        3. Add implicit bit (1) for normalized numbers
        4. Align exponents (shift smaller mantissa right)
        5. Add or subtract mantissas based on signs
        6. Normalize the result
        7. Handle overflow/underflow
        8. Round and return
        """
        # Convert to bit representation for low-level manipulation
        bits_a = cls.float_to_bits(a)
        bits_b = cls.float_to_bits(b)

        # Handle NaN: any operation with NaN returns NaN
        if cls.is_nan(bits_a):
            return a
        if cls.is_nan(bits_b):
            return b

        # Handle Infinity: (+inf) + (-inf) = NaN, otherwise return the infinity
        if cls.is_inf(bits_a) and cls.is_inf(bits_b):
            sign_a = (bits_a >> 31) & 1
            sign_b = (bits_b >> 31) & 1
            if sign_a != sign_b:  # +inf + -inf = NaN
                return cls.bits_to_float(0x7FC00000)  # canonical NaN
            return a  # same sign infinity
        if cls.is_inf(bits_a):
            return a
        if cls.is_inf(bits_b):
            return b

        # Handle zero: x + 0 = x
        if cls.is_zero(bits_a):
            return b
        if cls.is_zero(bits_b):
            return a

        # Extract fields from both numbers
        sign_a, exp_a, mant_a = cls.extract_fields(bits_a)
        sign_b, exp_b, mant_b = cls.extract_fields(bits_b)

        # Add implicit bit (1) for normalized numbers
        # Denormal numbers (exp=0) have implicit bit 0
        if exp_a != 0:
            mant_a |= cls.IMPLICIT_BIT
        else:
            exp_a = 1  # denormal: treat exponent as 1

        if exp_b != 0:
            mant_b |= cls.IMPLICIT_BIT
        else:
            exp_b = 1

        # Align exponents: shift smaller mantissa right
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

        # Add or subtract mantissas based on signs
        if sign_a == sign_b:
            # Same sign: add mantissas
            mant_sum = mant_a + mant_b
            sign_result = sign_a
        else:
            # Different signs: subtract smaller from larger
            if mant_a >= mant_b:
                mant_sum = mant_a - mant_b
                sign_result = sign_a
            else:
                mant_sum = mant_b - mant_a
                sign_result = sign_b

        # If result is zero
        if mant_sum == 0:
            return 0.0

        # Normalize: shift left until implicit bit is 1
        while mant_sum < cls.IMPLICIT_BIT and mant_sum != 0:
            mant_sum <<= 1
            exponent -= 1

        # If mantissa overflowed (carry out), shift right
        if mant_sum >= (cls.IMPLICIT_BIT << 1):
            mant_sum >>= 1
            exponent += 1

        # Mask out the implicit bit (keep only 23 bits)
        mant_result = mant_sum & cls.MANT_MASK

        # Check for overflow (exponent too large)
        if exponent >= 0xFF:
            return cls.bits_to_float(cls.make_bits(sign_result, 0xFF, 0))  # Infinity

        # Check for underflow (exponent too small)
        if exponent <= 0:
            return cls.bits_to_float(cls.make_bits(sign_result, 0, 0))  # Zero

        # Build and return the result
        result_bits = cls.make_bits(sign_result, exponent, mant_result)
        return cls.bits_to_float(result_bits)

    @classmethod
    def sub(cls, a: float, b: float) -> float:
        """
        Subtract two floats: a - b = a + (-b)
        Just flip the sign bit of b and call add.
        """
        bits_b = cls.float_to_bits(b)
        bits_b ^= cls.SIGN_MASK  # flip the sign bit
        return cls.add(a, cls.bits_to_float(bits_b))

    @classmethod
    def mul(cls, a: float, b: float) -> float:
        """Multiply two floats. (Simple implementation using Python's operator.)"""
        # TODO: Full IEEE754 multiplication would need:
        # - Multiply mantissas
        # - Add exponents
        # - Normalize and round
        return a * b

    @classmethod
    def div(cls, a: float, b: float) -> float:
        """Divide two floats with divide-by-zero handling."""
        if b == 0.0:
            if a == 0.0:
                return 0.0  # TODO: Should be NaN (0/0)
            return float("inf") if a > 0 else float("-inf")
        return a / b
