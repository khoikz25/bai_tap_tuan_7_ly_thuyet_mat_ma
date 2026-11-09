"""test_gf.py - Chạy: python3 test_gf.py
Mỗi trường GF(2^n) dùng 1 đa thức tối giản (chọn ở DA_THUC), nhân bằng BẢNG PHẦN TỬ SINH (slide 30-32),
rồi so với hai cách nhân khác và kiểm tra các tính chất của trường."""
import os
import random
from gf import (bac, dang_da_thuc, gf_mul, gf_mul_cach1, la_toi_gian, tu_so_mu,
                tim_phan_tu_sinh, lap_bang, gf_mul_bang, gf_chia_bang, gf_nghich_dao_bang)

# ===== CHỌN ĐA THỨC TỐI GIẢN Ở ĐÂY: muốn đổi đa thức chỉ cần sửa danh sách số mũ =====
DA_THUC = [
    [4, 1, 0],          # GF(2^4): x^4 + x + 1
    [8, 4, 3, 1, 0],    # GF(2^8): x^8 + x^4 + x^3 + x + 1  (đa thức của AES)
]

# ===== TESTCASE TỰ NHÂN BẰNG TAY: ghi kết quả bạn tự tính + tên file ảnh minh chứng =====
# Mỗi dòng: (số mũ của m(x), P1, P2, kết quả tính tay, đường dẫn ảnh chụp bài làm tay)
CA_TAY = [
    ([4, 1, 0],       0b0111,   0b1001,   0b1010,   "images/tay_gf24_1.jpg"),   # GF(2^4)
    ([4, 1, 0],       0b1010,   0b0101,   0b0100,   "images/tay_gf24_2.jpg"),   # GF(2^4)
    ([8, 4, 3, 1, 0], 0x57,     0x83,     0xC1,     "images/tay_gf28_1.jpg"),   # GF(2^8)
]

SO_DONG_BANG = 16       # in bao nhiêu dòng đầu của bảng g^k (đổi thành 255 để in đủ GF(2^8))

random.seed(2026)       # cố định số ngẫu nhiên để chạy lại luôn ra cùng kết quả


# ------------------ testcase chung: nhận m và hàm nhan(a, b) ------------------
# Mỗi hàm trả về (đạt?, số ca đã kiểm tra, ca lỗi nếu có)

def tc_don_thuc(m, nhan):
    """x^i * x^j: nếu i+j < n thì = x^(i+j); nếu i+j = n thì = m(x) - x^n (tính tay được)."""
    n, dem = bac(m), 0
    for i in range(n):
        for j in range(n):
            if i + j < n:
                mong_doi = 1 << (i + j)             # x^(i+j), chưa vượt bậc n
            elif i + j == n:
                mong_doi = m ^ (1 << n)             # x^n = phần còn lại của m(x)
            else:
                continue                            # i+j > n: tính tay phức tạp hơn, bỏ qua
            dem += 1
            kq = nhan(1 << i, 1 << j)
            if kq != mong_doi:
                return False, dem, (i, j, kq, mong_doi)
    return True, dem, None


def tc_cach1(m, nhan):
    """Bảng phải cho kết quả giống cách 1 (nhân thường rồi chia dư) với MỌI cặp."""
    s, dem = 1 << bac(m), 0
    for a in range(s):
        for b in range(s):
            dem += 1
            if nhan(a, b) != gf_mul_cach1(a, b, m):
                return False, dem, (a, b)
    return True, dem, None


def tc_cach2(m, nhan):
    """Bảng phải cho kết quả giống cách 2 (nhân dần với x, dịch trái + XOR) với MỌI cặp."""
    s, dem = 1 << bac(m), 0
    for a in range(s):
        for b in range(s):
            dem += 1
            if nhan(a, b) != gf_mul(a, b, m):
                return False, dem, (a, b)
    return True, dem, None


def tc_giao_hoan(m, nhan):
    """a*b = b*a với mọi cặp."""
    s, dem = 1 << bac(m), 0
    for a in range(s):
        for b in range(a, s):
            dem += 1
            if nhan(a, b) != nhan(b, a):
                return False, dem, (a, b)
    return True, dem, None


def tc_0_va_1(m, nhan):
    """0*a = 0 và 1*a = a với mọi a."""
    s, dem = 1 << bac(m), 0
    for a in range(s):
        dem += 2
        if nhan(0, a) != 0 or nhan(1, a) != a:
            return False, dem, (a,)
    return True, dem, None


def cac_bo_ba(n):
    """Toàn bộ bộ ba (a,b,c) nếu n nhỏ, ngược lại 20000 bộ ba ngẫu nhiên."""
    s = 1 << n
    if n <= 4:
        return [(a, b, c) for a in range(s) for b in range(s) for c in range(s)]
    return [(random.randrange(s), random.randrange(s), random.randrange(s)) for _ in range(20000)]


def tc_phan_phoi(m, nhan):
    """a*(b XOR c) = a*b XOR a*c."""
    dem = 0
    for a, b, c in cac_bo_ba(bac(m)):
        dem += 1
        if nhan(a, b ^ c) != nhan(a, b) ^ nhan(a, c):
            return False, dem, (a, b, c)
    return True, dem, None


def tc_ket_hop(m, nhan):
    """(a*b)*c = a*(b*c)."""
    dem = 0
    for a, b, c in cac_bo_ba(bac(m)):
        dem += 1
        if nhan(nhan(a, b), c) != nhan(a, nhan(b, c)):
            return False, dem, (a, b, c)
    return True, dem, None


def tc_nghich_dao(m, nhan):
    """Mỗi a != 0 có ĐÚNG MỘT b để a*b = 1 (nghĩa là chia được -> là trường)."""
    s, dem = 1 << bac(m), 0
    for a in range(1, s):
        dem += 1
        so_nghich_dao = sum(1 for b in range(1, s) if nhan(a, b) == 1)
        if so_nghich_dao != 1:
            return False, dem, (a, so_nghich_dao)
    return True, dem, None


def tc_fermat(m, nhan):
    """Trong GF(2^n): a^(2^n) = a. Tức bình phương a liên tiếp n lần phải về lại a."""
    n, dem = bac(m), 0
    for a in range(1 << n):
        dem += 1
        b = a
        for _ in range(n):
            b = nhan(b, b)
        if b != a:
            return False, dem, (a, b)
    return True, dem, None


TAT_CA = [("x^i * x^j (tính tay được)", tc_don_thuc),
          ("trùng cách 1 (nhân rồi chia dư)", tc_cach1),
          ("trùng cách 2 (dịch trái + XOR)", tc_cach2),
          ("giao hoán a*b = b*a", tc_giao_hoan),
          ("0*a = 0, 1*a = a", tc_0_va_1),
          ("phân phối a*(b+c) = a*b + a*c", tc_phan_phoi),
          ("kết hợp (a*b)*c = a*(b*c)", tc_ket_hop),
          ("mọi a != 0 có đúng 1 nghịch đảo", tc_nghich_dao),
          ("Fermat a^(2^n) = a", tc_fermat)]


# ------------------ testcase riêng cho bảng phần tử sinh ------------------

def tc_bang_phu_het(m, g, exp, log):
    """g^0, g^1, ..., g^(N-1) đôi một khác nhau và chạy hết N = 2^n - 1 phần tử khác 0."""
    N = (1 << bac(m)) - 1
    ok = len(set(exp)) == N and 0 not in exp and all(1 <= v < (1 << bac(m)) for v in exp)
    return ok, N, None


def tc_bang_log_exp(m, g, exp, log):
    """log và exp là hai hàm ngược nhau: log[exp[k]] = k và exp[log[v]] = v."""
    N, dem = (1 << bac(m)) - 1, 0
    for k in range(N):
        dem += 1
        if log[exp[k]] != k or exp[log[exp[k]]] != exp[k]:
            return False, dem, (k,)
    return True, dem, None


def tc_bang_chu_ky(m, g, exp, log):
    """g^N = 1, tức nhân thêm g vào g^(N-1) thì về lại 1 (bảng lặp lại sau N phần tử)."""
    return gf_mul_cach1(exp[-1], g, m) == 1, 1, None


def tc_bang_nghich_dao(m, g, exp, log):
    """a * (1/a) = 1 với mọi a != 0, trong đó 1/a lấy từ bảng."""
    dem = 0
    for a in range(1, 1 << bac(m)):
        dem += 1
        if gf_mul_cach1(a, gf_nghich_dao_bang(a, exp, log), m) != 1:
            return False, dem, (a,)
    return True, dem, None


def tc_bang_chia(m, g, exp, log):
    """(a / b) * b = a với mọi a và mọi b != 0."""
    s, dem = 1 << bac(m), 0
    for a in range(s):
        for b in range(1, s):
            dem += 1
            if gf_mul_cach1(gf_chia_bang(a, b, exp, log), b, m) != a:
                return False, dem, (a, b)
    return True, dem, None


TEST_BANG = [("g^k đôi một khác nhau, phủ đủ phần tử", tc_bang_phu_het),
             ("log và exp là hai hàm ngược nhau", tc_bang_log_exp),
             ("g^(2^n - 1) = 1 (bảng lặp lại)", tc_bang_chu_ky),
             ("a * (1/a) = 1 (nghịch đảo từ bảng)", tc_bang_nghich_dao),
             ("(a / b) * b = a (chia từ bảng)", tc_bang_chia)]


# ------------------ phần minh hoạ và đối chứng ------------------

def in_bang(g, exp, n):
    """In bảng g^k giống slide 31: k, đa thức, nhị phân."""
    print("  Phần tử sinh g = %s (nhị phân %s). Bảng g^k:" % (dang_da_thuc(g), format(g, "0%db" % n)))
    for k in range(min(SO_DONG_BANG, len(exp))):
        print("    g^%-3d = %-30s -> %s" % (k, dang_da_thuc(exp[k]), format(exp[k], "0%db" % n)))
    if SO_DONG_BANG < len(exp):
        print("    ... (còn %d dòng nữa, tăng SO_DONG_BANG để in đủ)" % (len(exp) - SO_DONG_BANG))


def minh_hoa(p1, p2, exp, log, n):
    """Nhân P1*P2 bằng bảng, từng bước (giống cách làm tay ở slide 32)."""
    i, j = log[p1], log[p2]
    k = (i + j) % len(exp)
    print("  Minh hoạ nhân bằng bảng: (%s) * (%s)" % (dang_da_thuc(p1), dang_da_thuc(p2)))
    print("    tra bảng: P1 = g^%d, P2 = g^%d" % (i, j))
    print("    cộng số mũ: %d + %d = %d, lấy mod %d = %d" % (i, j, i + j, len(exp), k))
    print("    tra bảng ngược: g^%d = %s" % (k, dang_da_thuc(exp[k])))


def vector_chuan(m, nhan):
    """Kết quả có sẵn trong tài liệu (chuẩn AES FIPS-197 + slide), chỉ đúng với đa thức AES."""
    if m != 0b100011011:
        print("  (Bỏ qua phần đối chiếu chuẩn AES vì đa thức đang chọn không phải đa thức AES)")
        return True
    ca = [(0x57, 0x83, 0xC1, "FIPS-197 / slide 19: 0x57 * 0x83"),
          (0x57, 0x02, 0xAE, "FIPS-197: 0x57 * 0x02"),
          (0x57, 0x04, 0x47, "FIPS-197: 0x57 * 0x04"),
          (0x57, 0x13, 0xFE, "FIPS-197: 0x57 * 0x13"),
          (0b00100110, 0b10011110, 0b00101111, "slide 24: (x^5+x^2+x)*(x^7+x^4+x^3+x^2+x)")]
    print("  Đối chiếu kết quả có sẵn:")
    ok_het = True
    for a, b, mong_doi, ten in ca:
        kq = nhan(a, b)
        ok_het &= (kq == mong_doi)
        print("    [%s] %-50s = 0x%02X (mong đợi 0x%02X)" % ("PASS" if kq == mong_doi else "FAIL", ten, kq, mong_doi))
    return ok_het


def vi_du_slide32(m, exp, log):
    """Ví dụ slide 32 (GF(2^4), m = x^4+x+1, g = x): g^9*g^11 = g^5 và g^3/g^8 = g^10."""
    if m != 0b10011:
        return True
    print("  Ví dụ slide 32:")
    ok1 = gf_mul_bang(exp[9], exp[11], exp, log) == exp[5]
    ok2 = gf_chia_bang(exp[3], exp[8], exp, log) == exp[10]
    print("    [%s] g^9 * g^11 = g^5 = %s" % ("PASS" if ok1 else "FAIL", dang_da_thuc(exp[5])))
    print("    [%s] g^3 / g^8  = g^10 = %s" % ("PASS" if ok2 else "FAIL", dang_da_thuc(exp[10])))
    return ok1 and ok2


def doi_chung(n):
    """Cho thấy vì sao PHẢI chọn đa thức tối giản: x^n + 1 không tối giản nên có ước của 0 và không có g."""
    m = (1 << n) | 1                                    # x^n + 1 (có nghiệm x = 1 nên chia hết cho x + 1)
    s = 1 << n
    cap = next(((a, b) for a in range(1, s) for b in range(1, s) if gf_mul(a, b, m) == 0), None)
    print("  Đối chứng với đa thức KHÔNG tối giản m(x) = %s:" % dang_da_thuc(m))
    if cap:
        a, b = cap
        print("    (%s) * (%s) = 0 dù cả hai khác 0 -> không chia được, không phải trường" % (dang_da_thuc(a), dang_da_thuc(b)))
    print("    tìm phần tử sinh: %s" % ("không có" if tim_phan_tu_sinh(m) is None else "có"))


# ------------------ chạy cho từng trường ------------------

def chay_mot_truong(ds_so_mu):
    m = tu_so_mu(ds_so_mu)                              # đổi danh sách số mũ sang số nguyên
    n = bac(m)                                          # bậc n quyết định trường GF(2^n)
    print("\n===== GF(2^%d) với m(x) = %s (nhị phân %s) =====" % (n, dang_da_thuc(m), format(m, "0%db" % (n + 1))))
    if not la_toi_gian(m):                              # chặn đa thức nhập sai
        print("  LỖI: m(x) này KHÔNG tối giản, không tạo được trường. Hãy chọn lại ở DA_THUC.")
        return False
    g, exp, log = lap_bang(m)                           # tìm phần tử sinh và lập bảng cho đúng m
    nhan = lambda a, b: gf_mul_bang(a, b, exp, log)     # phép nhân bằng bảng
    in_bang(g, exp, n)
    p1, p2 = (0x7, 0x9) if n == 4 else (0x57, 0x83)    # cặp mẫu để minh hoạ
    minh_hoa(p1 & ((1 << n) - 1), p2 & ((1 << n) - 1), exp, log, n)
    print("  Các testcase:")
    ok_het = True
    for ten, ham in TAT_CA:
        ok, so_ca, loi = ham(m, nhan)
        ok_het &= ok
        print("    [%s] %-40s %6d ca %s" % ("PASS" if ok else "FAIL", ten, so_ca, "" if ok else "lỗi tại %s" % (loi,)))
    for ten, ham in TEST_BANG:
        ok, so_ca, loi = ham(m, g, exp, log)
        ok_het &= ok
        print("    [%s] %-40s %6d ca %s" % ("PASS" if ok else "FAIL", ten, so_ca, "" if ok else "lỗi tại %s" % (loi,)))
    ok_het &= vector_chuan(m, nhan)
    ok_het &= vi_du_slide32(m, exp, log)
    doi_chung(n)
    print("  => GF(2^%d): %s" % (n, "TẤT CẢ ĐỀU ĐẠT" if ok_het else "CÓ TESTCASE LỖI"))
    return ok_het


def chay_ca_tay():
    """So kết quả chương trình với kết quả bạn tự nhân bằng tay (kèm ảnh minh chứng)."""
    print("\n===== Testcase tự nhân bằng tay =====")
    ok_het = True
    for ds_so_mu, p1, p2, kq_tay, anh in CA_TAY:
        m = tu_so_mu(ds_so_mu)
        n = bac(m)
        g, exp, log = lap_bang(m)
        kq = gf_mul_bang(p1, p2, exp, log)              # kết quả của chương trình (bằng bảng)
        ok = (kq == kq_tay)                             # so với kết quả tính tay
        ok_het &= ok
        print("  [%s] GF(2^%d), m(x) = %s" % ("PASS" if ok else "FAIL", n, dang_da_thuc(m)))
        print("       (%s) * (%s)" % (dang_da_thuc(p1), dang_da_thuc(p2)))
        print("       tay = %s | chương trình = %s" % (dang_da_thuc(kq_tay), dang_da_thuc(kq)))
        print("       ảnh: %s (%s)" % (anh, "có file" if os.path.exists(anh) else "CHƯA CÓ FILE ẢNH"))
    return ok_het


if __name__ == "__main__":
    ket_qua = [chay_mot_truong(ds) for ds in DA_THUC]
    ket_qua.append(chay_ca_tay())
    print("\n%s" % ("HOÀN TẤT: mọi trường đều đạt" if all(ket_qua) else "CÓ TRƯỜNG BỊ LỖI"))