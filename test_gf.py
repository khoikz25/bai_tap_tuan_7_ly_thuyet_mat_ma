"""test_gf.py - Chạy: python3 test_gf.py
Tính các ví dụ nhân tay (đã viết ra giấy và chụp ảnh) bằng chương trình, rồi so với kết quả tay."""
import os
from gf import bac, dang_da_thuc, tu_so_mu, bang_luy_thua, tao_phep_nhan, gf_mul_cach1

# ===== CÁC VÍ DỤ NHÂN TAY: (số mũ của m(x), P1, P2, kết quả tính tay, ảnh bài làm) =====
CA_TAY = [
    ([4, 1, 0],       0b0111,       0b1001,       0b1010,       "images/tay_gf24_1.jpg"),
    ([4, 1, 0],       0b1010,       0b0101,       0b0100,       "images/tay_gf24_2.jpg"),
    ([8, 4, 3, 1, 0], 0b00100011,   0b00011000,   0b00000101,   "images/tay_gf28_1.jpg"),
]

KIEM_TRA_THEM = False   # đổi thành True để chạy thêm bước kiểm tra chéo trên mọi cặp (a, b)


def minh_hoa(p1, p2, m):
    """In từng bước nhân P1*P2 giống bài viết tay: bảng g^k, quy x thành g, nhân, tra bảng, đếm chẵn/lẻ."""
    n = bac(m)
    bang = bang_luy_thua(m, 2 * n - 1)
    print("  Bước 0 - bảng g^k (g = x):")
    for k, v in enumerate(bang):
        print("      g^%-2d = %-30s -> %s" % (k, dang_da_thuc(v), format(v, "0%db" % n)))
    mu1 = [i for i in range(n) if (p1 >> i) & 1]
    mu2 = [j for j in range(n) if (p2 >> j) & 1]
    print("  Bước 1 - quy x thành g: P1 = %s ; P2 = %s" % (" + ".join("g^%d" % i for i in mu1), " + ".join("g^%d" % j for j in mu2)))
    dem = [0] * n
    print("  Bước 2 và 3 - nhân (cộng số mũ) rồi tra bảng g^k -> đa thức:")
    for i in mu1:
        for j in mu2:
            print("      g^%d * g^%d = g^%d = %s" % (i, j, i + j, dang_da_thuc(bang[i + j])))
            for d in range(n):
                dem[d] += (bang[i + j] >> d) & 1
    print("  Bước 4 - bậc xuất hiện chẵn lần thì mất, lẻ lần thì giữ:")
    kq = 0
    for d in range(n - 1, -1, -1):
        print("      x^%d xuất hiện %d lần -> %s" % (d, dem[d], "giữ" if dem[d] % 2 else "mất"))
        kq |= (dem[d] % 2) << d
    print("  => kết quả = %s" % dang_da_thuc(kq))


def chay_ca_tay():
    """Với mỗi ví dụ: in các bước, rồi so kết quả chương trình với kết quả tính tay."""
    ok_het = True
    for stt, (ds_so_mu, p1, p2, kq_tay, anh) in enumerate(CA_TAY, 1):
        m = tu_so_mu(ds_so_mu)
        n = bac(m)
        print("\n" + "=" * 72)
        print("VÍ DỤ %d: GF(2^%d), m(x) = %s" % (stt, n, dang_da_thuc(m)))
        print("  P1 = %s" % dang_da_thuc(p1))
        print("  P2 = %s" % dang_da_thuc(p2))
        print("=" * 72)
        minh_hoa(p1, p2, m)
        kq = tao_phep_nhan(m)(p1, p2)                   # kết quả của chương trình
        ok = (kq == kq_tay)                             # so với kết quả tính tay
        ok_het &= ok
        print("\n  Kết quả tính tay    : %s" % dang_da_thuc(kq_tay))
        print("  Kết quả chương trình: %s" % dang_da_thuc(kq))
        print("  [%s] %s" % ("PASS" if ok else "FAIL", "chương trình khớp kết quả tính tay" if ok else "KHÔNG KHỚP, kiểm tra lại bài làm tay"))
        print("  Ảnh bài làm tay: %s (%s)" % (anh, "có file" if os.path.exists(anh) else "CHƯA CÓ FILE ẢNH"))
    return ok_het


def kiem_tra_them():
    """(Tuỳ chọn) So phép nhân với cách nhân thường rồi chia dư trên MỌI cặp (a, b) của từng trường."""
    print("\n" + "=" * 72)
    print("KIỂM TRA THÊM: so với phép nhân thường rồi chia dư trên mọi cặp (a, b)")
    print("=" * 72)
    ok_het = True
    for ds_so_mu in sorted({tuple(c[0]) for c in CA_TAY}):      # mỗi trường kiểm tra một lần
        m = tu_so_mu(list(ds_so_mu))
        nhan = tao_phep_nhan(m)
        s = 1 << bac(m)
        ok = all(nhan(a, b) == gf_mul_cach1(a, b, m) for a in range(s) for b in range(s))
        ok_het &= ok
        print("  [%s] GF(2^%d), m(x) = %s: %d cặp" % ("PASS" if ok else "FAIL", bac(m), dang_da_thuc(m), s * s))
    return ok_het


if __name__ == "__main__":
    ok = chay_ca_tay()
    if KIEM_TRA_THEM:
        ok &= kiem_tra_them()
    print("\n%s" % ("HOÀN TẤT: mọi ví dụ đều khớp" if ok else "CÓ VÍ DỤ BỊ LỆCH"))