"""Nhân hai đa thức trong trường hữu hạn GF(2^n), n = 4 và n = 8.

Biểu diễn: phần tử là đa thức nhị phân, lưu bằng số nguyên (bit i = hệ số của x^i).
Phép cộng đa thức = XOR.
Phép nhân = nhân đa thức (hệ số trong Z2) rồi rút gọn modulo đa thức tối giản m(x).
"""

# Đa thức tối giản m(x) (gồm cả bit bậc n)
IRRED = {
    4: 0b10011,        # x^4 + x + 1
    8: 0b100011011,    # x^8 + x^4 + x^3 + x + 1
}


def poly_str(a: int) -> str:
    """In số nguyên dưới dạng đa thức, ví dụ 0xA -> x^3 + x."""
    if a == 0:
        return "0"
    t = []
    for i in range(a.bit_length() - 1, -1, -1):
        if (a >> i) & 1:
            t.append("1" if i == 0 else "x" if i == 1 else f"x^{i}")
    return " + ".join(t)


def mul_x(a: int, n: int) -> int:
    """Tính x (x) a mod m(x): dịch trái 1 bit, nếu xuất hiện x^n thì XOR với m(x)."""
    a <<= 1
    if (a >> n) & 1:           # tràn bậc -> cần rút gọn
        a ^= IRRED[n]
    return a


def gf_mul(p1: int, p2: int, n: int) -> int:
    """Cách 1: x^k (x) P2 với k = 0..n-1, rồi XOR các kết quả ứng với hệ số 1 của P1."""
    if n not in IRRED:
        raise ValueError("Chỉ hỗ trợ n = 4 hoặc n = 8")
    if not (0 <= p1 < (1 << n) and 0 <= p2 < (1 << n)):
        raise ValueError(f"Hệ số phải nằm trong [0, {(1 << n) - 1}]")
    result, cur = 0, p2                       # cur = x^k (x) P2
    for k in range(n):
        if (p1 >> k) & 1:
            result ^= cur
        cur = mul_x(cur, n)
    return result


def gf_mul_reduce(p1: int, p2: int, n: int) -> int:
    """Cách 2: nhân đa thức thường (bậc tới 2n-2) rồi chia lấy dư cho m(x)."""
    m, prod = IRRED[n], 0
    for i in range(n):
        if (p2 >> i) & 1:
            prod ^= p1 << i
    for i in range(2 * n - 2, n - 1, -1):
        if (prod >> i) & 1:
            prod ^= m << (i - n)
    return prod


if __name__ == "__main__":
    # (n, P1, P2, kết quả mong đợi) - tự tính tay
    tests = [
        (4, 0x2, 0x8, 0x3),     # x * x^3 = x^4 = x + 1
        (4, 0x7, 0x9, 0xA),     # (x^2+x+1)(x^3+1) = x^3 + x
        (4, 0x0, 0x5, 0x0),     # nhân với 0
        (4, 0x1, 0xF, 0xF),     # nhân với 1
        (8, 0x02, 0x80, 0x1B),  # x * x^7 = x^8 = x^4 + x^3 + x + 1
        (8, 0x00, 0xAB, 0x00),  # nhân với 0
        (8, 0x01, 0xAB, 0xAB),  # nhân với 1
    ]
    for n, a, b, exp in tests:
        r1, r2 = gf_mul(a, b, n), gf_mul_reduce(a, b, n)
        ok = (r1 == r2 == exp)
        print(f"GF(2^{n}): ({poly_str(a)}) * ({poly_str(b)}) = {poly_str(r1)}"
              f"  -> {'OK' if ok else 'FAIL'}")
        assert ok

    # Hai cách phải cho cùng kết quả với mọi cặp, và phép nhân phải giao hoán
    for n in (4, 8):
        s = 1 << n
        assert all(gf_mul(a, b, n) == gf_mul_reduce(a, b, n) == gf_mul(b, a, n)
                   for a in range(s) for b in range(s))
        print(f"GF(2^{n}): hai cách khớp và giao hoán trên toàn bộ {s * s} cặp")