# ---------------------------------------------------------------
# PHƯƠNG PHÁP PHẦN TỬ SINH (slide 30-32): lập bảng g^k rồi nhân = cộng số mũ
# ---------------------------------------------------------------
def chu_ky(g, m):
    """Số lần nhân g liên tiếp để quay về 1 (g^1, g^2, ... đến khi bằng 1)."""
    v, dem = g, 1                           # v = g^dem, bắt đầu từ g^1
    while v != 1:
        v = gf_mul_cach1(v, g, m)           # v = v * g
        dem += 1
        if dem > (1 << bac(m)):             # chặn lặp vô hạn (chỉ xảy ra nếu m không tối giản)
            return 0
    return dem


def tim_phan_tu_sinh(m):
    """Tìm g sao cho g^1, ..., g^(2^n - 1) chạy hết mọi phần tử khác 0 (chu kỳ = 2^n - 1)."""
    n = bac(m)
    for g in range(2, 1 << n):              # thử g = 2 (x), 3 (x+1), 4, ...
        if chu_ky(g, m) == (1 << n) - 1:    # chu kỳ đủ dài thì g là phần tử sinh
            return g
    return None                             # không tìm thấy (m không tối giản)


def lap_bang(m):
    """Lập bảng exp[k] = g^k và log[v] = k. Trả về (g, exp, log)."""
    n = bac(m)
    g = tim_phan_tu_sinh(m)                 # tìm phần tử sinh cho đúng đa thức m
    N = (1 << n) - 1                        # số phần tử khác 0 của trường
    exp = [0] * N                           # exp[k] = g^k, k = 0..N-1
    log = [0] * (1 << n)                    # log[v] = k sao cho g^k = v (log[0] không dùng)
    v = 1                                   # g^0 = 1
    for k in range(N):
        exp[k] = v                          # ghi g^k
        log[v] = k                          # ghi ngược lại: v có số mũ là k
        v = gf_mul_cach1(v, g, m)           # g^(k+1) = g^k * g
    return g, exp, log


def gf_mul_bang(a, b, exp, log):
    """a * b bằng bảng: g^i * g^j = g^(i+j mod N)."""
    if a == 0 or b == 0:                    # 0 không có log nên xử lý riêng
        return 0
    return exp[(log[a] + log[b]) % len(exp)]


def gf_chia_bang(a, b, exp, log):
    """a / b bằng bảng: g^i / g^j = g^(i-j mod N). Yêu cầu b != 0."""
    if a == 0:
        return 0
    return exp[(log[a] - log[b]) % len(exp)]


def gf_nghich_dao_bang(a, exp, log):
    """1 / a = g^(-i) = g^(N-i). Yêu cầu a != 0."""
    return exp[(-log[a]) % len(exp)]