"""gf.py - Nhân hai đa thức trong trường hữu hạn GF(2^n) với đa thức tối giản m(x) tuỳ chọn.

Quy ước: đa thức viết thành số nguyên, bit i là hệ số của x^i.
  Ví dụ x^3 + x + 1 -> 0b1011 (= 11).
Đa thức tối giản m(x) viết như vậy và có CẢ bit bậc n.
  Ví dụ GF(2^4): m = x^4 + x + 1 -> 0b10011.
"""


# ============ Các hàm tiện ích ============

def bac(a):
    """Bậc của đa thức a (vị trí bit 1 cao nhất)."""
    return a.bit_length() - 1           # 0b1011 có 4 bit -> bậc 3


def dang_da_thuc(a):
    """Đổi số nguyên sang chuỗi đa thức để in, ví dụ 0b1011 -> 'x^3 + x + 1'."""
    if a == 0:
        return "0"
    ds = []                             # danh sách các số hạng
    for i in range(bac(a), -1, -1):     # duyệt từ bậc cao xuống bậc 0
        if (a >> i) & 1:                # nếu hệ số của x^i bằng 1
            ds.append("1" if i == 0 else "x" if i == 1 else "x^%d" % i)
    return " + ".join(ds)


def tu_so_mu(ds_so_mu):
    """Đổi danh sách số mũ sang số nguyên, ví dụ [4, 1, 0] (x^4 + x + 1) -> 0b10011."""
    m = 0
    for e in ds_so_mu:                  # mỗi số mũ e là một số hạng x^e
        m = m | (1 << e)                # bật bit thứ e
    return m


# ============ THUẬT TOÁN CHÍNH: quy x thành g, nhân, tra bảng, bỏ bậc chẵn lần ============

def nhan_x(a, m):
    """Tính x * a mod m(x): dịch trái 1 bit, nếu tràn bậc n thì XOR với m(x)."""
    n = bac(m)
    a = a << 1                          # nhân với x = dịch trái 1 bit
    if (a >> n) & 1:                    # bit x^n xuất hiện (bị tràn)
        a = a ^ m                       # xoá x^n và thay bằng phần còn lại của m(x)
    return a


def bang_luy_thua(m, so_luong):
    """Bảng g^k = x^k mod m(x), k = 0, 1, ..., so_luong - 1 (quy x thành g)."""
    bang = [1]                          # g^0 = 1
    for _ in range(so_luong - 1):
        bang.append(nhan_x(bang[-1], m))    # g^k = x * g^(k-1) mod m(x)
    return bang


def tao_phep_nhan(m):
    """Lập bảng g^k một lần, rồi trả về hàm nhan(p1, p2) nhân hai đa thức trong GF(2^n)."""
    n = bac(m)
    bang = bang_luy_thua(m, 2 * n - 1)  # tích hai đa thức có bậc tối đa 2n-2 nên cần g^0..g^(2n-2)

    def nhan(p1, p2):
        ket_qua = 0
        for i in range(n):
            if (p1 >> i) & 1:           # P1 có số hạng g^i
                for j in range(n):
                    if (p2 >> j) & 1:   # P2 có số hạng g^j
                        ket_qua ^= bang[i + j]   # g^i * g^j = g^(i+j), tra bảng rồi cộng (XOR)
        return ket_qua                  # XOR cũng là "bậc nào xuất hiện chẵn lần thì mất"
    return nhan


def gf_mul(p1, p2, m):
    """Nhân P1 * P2 trong GF(2^n) (dùng khi chỉ cần nhân một lần)."""
    return tao_phep_nhan(m)(p1, p2)


# ============ THUẬT TOÁN ĐỐI CHỨNG: nhân thường rồi chia lấy dư ============

def nhan_thuong(a, b):
    """Nhân hai đa thức bình thường (không rút gọn), hệ số theo mod 2."""
    kq = 0
    for i in range(b.bit_length()):     # duyệt từng bit của b
        if (b >> i) & 1:                # b có số hạng x^i
            kq = kq ^ (a << i)          # cộng (XOR) a * x^i
    return kq


def chia_du(a, m):
    """Dư của phép chia đa thức a cho m (chia dài, trừ = XOR)."""
    while a != 0 and bac(a) >= bac(m):  # còn chia được khi bậc a >= bậc m
        s = bac(a) - bac(m)             # thương có số hạng x^s
        a = a ^ (m << s)                # trừ m * x^s để xoá số hạng cao nhất của a
    return a


def gf_mul_cach1(p1, p2, m):
    """(P1 * P2) mod m(x), dùng để kiểm tra chéo."""
    return chia_du(nhan_thuong(p1, p2), m)


# ============ Đa thức tối giản và phần tử sinh ============

def la_toi_gian(m):
    """m(x) tối giản nếu KHÔNG chia hết cho đa thức nào có bậc từ 1 đến n/2."""
    n = bac(m)
    for d in range(1, n // 2 + 1):      # bậc của ước thử
        for thap in range(1 << d):      # các hệ số bậc thấp của ước
            uoc = (1 << d) | thap       # ước có bậc đúng d
            if chia_du(m, uoc) == 0:    # chia hết -> không tối giản
                return False
    return True


def ds_toi_gian(n):
    """Liệt kê mọi đa thức tối giản bậc n (để chọn khi cô bảo đổi)."""
    return [(1 << n) | thap for thap in range(1 << n) if la_toi_gian((1 << n) | thap)]


def chu_ky_cua_x(m):
    """Số k nhỏ nhất > 0 để x^k = 1. Nếu k = 2^n - 1 thì x là phần tử sinh (slide 30-31)."""
    v, k = 2, 1                         # v = x^1 (số 2 = 0b10 là đa thức x)
    while v != 1:
        v = nhan_x(v, m)                # v = x^(k+1)
        k += 1
    return k