"""test_gf.py - Chạy: python3 test_gf.py

Chương trình chia thành 4 NHÓM testcase cho mỗi trường GF(2^n):
  Nhóm 1: kiểm tra ĐA THỨC m(x) (có tối giản không).
  Nhóm 2: kết quả BIẾT TRƯỚC (tính tay được / có trong slide, chuẩn AES).
  Nhóm 3: SO SÁNH với một thuật toán khác (nhân thường rồi chia dư).
  Nhóm 4: TÍNH CHẤT của một trường (giao hoán, phần tử 0 và 1, nghịch đảo).
Cuối cùng là các ca tự nhân bằng tay (có ảnh).
"""
import os
from gf import (bac, dang_da_thuc, tu_so_mu, bang_luy_thua, tao_phep_nhan,
                gf_mul_cach1, la_toi_gian, chu_ky_cua_x)

# ===== CHỌN ĐA THỨC TỐI GIẢN Ở ĐÂY: muốn đổi đa thức chỉ cần sửa danh sách số mũ =====
DA_THUC = [
    [4, 1, 0],          # GF(2^4): x^4 + x + 1
    [8, 4, 3, 1, 0],    # GF(2^8): x^8 + x^4 + x^3 + x + 1  (đa thức của AES)
]

# ===== CÁC CA TỰ NHÂN BẰNG TAY: (số mũ của m(x), P1, P2, kết quả tính tay, ảnh minh chứng) =====
CA_TAY = [
    ([4, 1, 0],       0b0111,   0b1001,   0b1010,   "images/tay_gf24_1.jpg"),
    ([4, 1, 0],       0b1010,   0b0101,   0b0100,   "images/tay_gf24_2.jpg"),
    ([8, 4, 3, 1, 0], 0b00100011,   0b00011000,   0b00000101,   "images/tay_gf28_1.jpg"),
]


# ====================== NHÓM 1: kiểm tra đa thức m(x) ======================
# Mỗi testcase nhận (m, nhan), trả về None (không áp dụng) hoặc (đạt?, số ca, ca lỗi)

def t_toi_gian(m, nhan):
    """m(x) phải tối giản thì mới tạo được trường."""
    return la_toi_gian(m), 1, None


def t_doi_chung(m, nhan):
    """Đối chứng: x^n + 1 KHÔNG tối giản nên có hai phần tử khác 0 nhân ra 0 (không phải trường)."""
    n = bac(m)
    mx = (1 << n) | 1                                   # x^n + 1
    cap = next(((a, b) for a in range(1, 1 << n) for b in range(1, 1 << n)
                if gf_mul_cach1(a, b, mx) == 0), None)
    return (cap is not None and not la_toi_gian(mx)), 1, cap


# ====================== NHÓM 2: kết quả biết trước ======================

def t_don_thuc(m, nhan):
    """x^i * x^j = x^(i+j) nếu i+j < n; x^n = m(x) - x^n. Các giá trị này tự tính tay được."""
    n, dem = bac(m), 0
    for i in range(n):
        for j in range(n):
            if i + j < n:
                mong_doi = 1 << (i + j)
            elif i + j == n:
                mong_doi = m ^ (1 << n)
            else:
                continue
            dem += 1
            if nhan(1 << i, 1 << j) != mong_doi:
                return False, dem, (i, j)
    return True, dem, None


def t_slide31(m, nhan):
    """Bảng g^k ở slide 31 (GF(2^4), m = x^4+x+1, g = x). Chỉ áp dụng cho đa thức này."""
    if m != 0b10011:
        return None
    slide = [0b0001, 0b0010, 0b0100, 0b1000, 0b0011, 0b0110, 0b1100, 0b1011,
             0b0101, 0b1010, 0b0111, 0b1110, 0b1111, 0b1101, 0b1001]      # g^0 ... g^14
    bang = bang_luy_thua(m, 15)
    return bang == slide, len(slide), None


def t_slide32(m, nhan):
    """Ví dụ slide 32: g^9 * g^11 = g^20 = g^5 (vì g^15 = 1). Chỉ áp dụng cho x^4+x+1."""
    if m != 0b10011:
        return None
    bang = bang_luy_thua(m, 15)
    return nhan(bang[9], bang[11]) == bang[5], 1, None


def t_aes(m, nhan):
    """Kết quả có sẵn của chuẩn AES (FIPS-197) và slide 24. Chỉ áp dụng cho đa thức AES."""
    if m != 0b100011011:
        return None
    ca = [(0x57, 0x83, 0xC1), (0x57, 0x13, 0xFE), (0x57, 0x02, 0xAE), (0x57, 0x04, 0x47),
          (0b00100110, 0b10011110, 0b00101111)]
    for a, b, mong_doi in ca:
        if nhan(a, b) != mong_doi:
            return False, len(ca), (a, b)
    return True, len(ca), None


# ====================== NHÓM 3: so với thuật toán khác ======================

def t_cach1(m, nhan):
    """Kết quả phải giống phép nhân thường rồi chia dư với MỌI cặp (a, b)."""
    s, dem = 1 << bac(m), 0
    for a in range(s):
        for b in range(s):
            dem += 1
            if nhan(a, b) != gf_mul_cach1(a, b, m):
                return False, dem, (a, b)
    return True, dem, None


# ====================== NHÓM 4: tính chất của trường ======================

def t_giao_hoan(m, nhan):
    """a*b = b*a."""
    s, dem = 1 << bac(m), 0
    for a in range(s):
        for b in range(a, s):
            dem += 1
            if nhan(a, b) != nhan(b, a):
                return False, dem, (a, b)
    return True, dem, None


def t_don_vi(m, nhan):
    """0*a = 0 và 1*a = a."""
    s = 1 << bac(m)
    for a in range(s):
        if nhan(0, a) != 0 or nhan(1, a) != a:
            return False, 2 * s, (a,)
    return True, 2 * s, None


def t_nghich_dao(m, nhan):
    """Mỗi a != 0 có ĐÚNG MỘT b để a*b = 1 (chia được -> là trường)."""
    s = 1 << bac(m)
    for a in range(1, s):
        if sum(1 for b in range(1, s) if nhan(a, b) == 1) != 1:
            return False, a, (a,)
    return True, s - 1, None


NHOM = [
    ("NHÓM 1 - Kiểm tra đa thức m(x)",
     [("m(x) là đa thức tối giản", t_toi_gian),
      ("đối chứng: x^n + 1 không tối giản thì có ước của 0", t_doi_chung)]),
    ("NHÓM 2 - Kết quả biết trước (tính tay / tài liệu)",
     [("x^i * x^j (tự tính tay được)", t_don_thuc),
      ("bảng g^k của slide 31", t_slide31),
      ("ví dụ slide 32: g^9 * g^11 = g^5", t_slide32),
      ("chuẩn AES (FIPS-197) và slide 24", t_aes)]),
    ("NHÓM 3 - So sánh với thuật toán khác",
     [("trùng phép nhân thường rồi chia dư (mọi cặp)", t_cach1)]),
    ("NHÓM 4 - Tính chất của một trường",
     [("giao hoán a*b = b*a", t_giao_hoan),
      ("phần tử 0 và 1", t_don_vi),
      ("mọi a != 0 có đúng 1 nghịch đảo", t_nghich_dao)]),
]


# ====================== minh hoạ từng bước (giống bài làm tay) ======================

def minh_hoa(p1, p2, m):
    """In từng bước nhân P1*P2: quy x thành g, nhân, tra bảng, đếm bậc chẵn/lẻ."""
    n = bac(m)
    bang = bang_luy_thua(m, 2 * n - 1)
    mu1 = [i for i in range(n) if (p1 >> i) & 1]
    mu2 = [j for j in range(n) if (p2 >> j) & 1]
    print("  Minh hoạ: (%s) * (%s)" % (dang_da_thuc(p1), dang_da_thuc(p2)))
    print("    Bước 1 - quy x thành g: P1 = %s ; P2 = %s" % (" + ".join("g^%d" % i for i in mu1), " + ".join("g^%d" % j for j in mu2)))
    dem = [0] * n
    print("    Bước 2 và 3 - nhân (cộng số mũ) rồi tra bảng g^k -> đa thức:")
    for i in mu1:
        for j in mu2:
            print("      g^%d * g^%d = g^%d = %s" % (i, j, i + j, dang_da_thuc(bang[i + j])))
            for d in range(n):
                dem[d] += (bang[i + j] >> d) & 1
    print("    Bước 4 - bậc xuất hiện chẵn lần thì mất, lẻ lần thì giữ:")
    kq = 0
    for d in range(n - 1, -1, -1):
        print("      x^%d xuất hiện %d lần -> %s" % (d, dem[d], "giữ" if dem[d] % 2 else "mất"))
        kq |= (dem[d] % 2) << d
    print("    => kết quả = %s" % dang_da_thuc(kq))


# ====================== chạy ======================

def chay_mot_truong(ds_so_mu):
    m = tu_so_mu(ds_so_mu)
    n = bac(m)
    print("\n" + "=" * 72)
    print("GF(2^%d), m(x) = %s (nhị phân %s)" % (n, dang_da_thuc(m), format(m, "0%db" % (n + 1))))
    print("=" * 72)
    if not la_toi_gian(m):                              # chặn đa thức nhập sai
        print("LỖI: m(x) này KHÔNG tối giản, không tạo được trường. Hãy chọn lại ở DA_THUC.")
        return False
    bang = bang_luy_thua(m, 2 * n - 1)
    print("Bảng g^k (g = x) dùng để nhân:")
    for k, v in enumerate(bang):
        print("  g^%-2d = %-32s -> %s" % (k, dang_da_thuc(v), format(v, "0%db" % n)))
    k = chu_ky_cua_x(m)
    print("x có chu kỳ %d (%s phần tử sinh, vì 2^n - 1 = %d)" % (k, "là" if k == (1 << n) - 1 else "KHÔNG là", (1 << n) - 1))
    minh_hoa(0x7 if n == 4 else 0x57, 0x9 if n == 4 else 0x83, m)
    nhan = tao_phep_nhan(m)
    ok_het = True
    for ten_nhom, ds_test in NHOM:
        print("\n" + ten_nhom)
        for ten, ham in ds_test:
            kq = ham(m, nhan)
            if kq is None:                              # testcase này không áp dụng cho đa thức đang chọn
                continue
            ok, so_ca, loi = kq
            ok_het &= ok
            print("  [%s] %-52s %6d ca %s" % ("PASS" if ok else "FAIL", ten, so_ca, "" if ok else "lỗi tại %s" % (loi,)))
    print("\n=> GF(2^%d): %s" % (n, "TẤT CẢ ĐỀU ĐẠT" if ok_het else "CÓ TESTCASE LỖI"))
    return ok_het


def chay_ca_tay():
    print("\n" + "=" * 72)
    print("CÁC CA TỰ NHÂN BẰNG TAY (so với kết quả chương trình)")
    print("=" * 72)
    ok_het = True
    for ds_so_mu, p1, p2, kq_tay, anh in CA_TAY:
        m = tu_so_mu(ds_so_mu)
        kq = tao_phep_nhan(m)(p1, p2)
        ok = (kq == kq_tay)
        ok_het &= ok
        print("  [%s] GF(2^%d): (%s) * (%s)" % ("PASS" if ok else "FAIL", bac(m), dang_da_thuc(p1), dang_da_thuc(p2)))
        print("         tay = %s | chương trình = %s | ảnh: %s (%s)" % (
            dang_da_thuc(kq_tay), dang_da_thuc(kq), anh, "có file" if os.path.exists(anh) else "CHƯA CÓ FILE ẢNH"))
    return ok_het


if __name__ == "__main__":
    ket_qua = [chay_mot_truong(ds) for ds in DA_THUC]
    ket_qua.append(chay_ca_tay())
    print("\n%s" % ("HOÀN TẤT: mọi phần đều đạt" if all(ket_qua) else "CÓ PHẦN BỊ LỖI"))