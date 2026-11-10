"""nhap_tay.py - Chạy: python3 nhap_tay.py
Nhập 2 đa thức BẤT KỲ rồi nhân trong GF(2^4) hoặc GF(2^8) với đa thức tối giản tuỳ chọn.
Có thể nhập đa thức dạng chữ (x^3+x+1), nhị phân (1011 hoặc 0b1011) hoặc hex (0xB)."""
from gf import bac, dang_da_thuc, la_toi_gian, tao_phep_nhan, gf_mul_cach1
from test_gf import minh_hoa

MAC_DINH = {4: 0b10011, 8: 0b100011011}     # x^4 + x + 1 và x^8 + x^4 + x^3 + x + 1 (AES)


def doc_da_thuc(s):
    """Đọc đa thức từ chuỗi, trả về số nguyên. Nhập sai thì báo ValueError."""
    s = s.strip().lower().replace(" ", "")
    if s.startswith("0x"):                  # hex, ví dụ 0x57
        return int(s, 16)
    if s.startswith("0b"):                  # nhị phân có tiền tố, ví dụ 0b1011
        return int(s, 2)
    if s != "" and set(s) <= {"0", "1"}:    # chuỗi chỉ gồm 0 và 1 -> hiểu là nhị phân
        return int(s, 2)
    ket_qua = 0
    for so_hang in s.split("+"):            # tách các số hạng, ví dụ "x^3+x+1"
        if so_hang == "1":
            e = 0
        elif so_hang == "x":
            e = 1
        elif so_hang.startswith("x^") and so_hang[2:].isdigit():
            e = int(so_hang[2:])
        else:
            raise ValueError("không hiểu số hạng '%s'" % so_hang)
        ket_qua ^= 1 << e                   # XOR: số hạng xuất hiện 2 lần thì mất (1 + 1 = 0)
    return ket_qua


def hoi_da_thuc(cau_hoi, gioi_han):
    """Hỏi đến khi nhập đúng. Đa thức phải có bậc nhỏ hơn n (tức nhỏ hơn gioi_han). Enter trống = thoát."""
    while True:
        s = input(cau_hoi).strip()
        if s == "":
            return None
        try:
            p = doc_da_thuc(s)
        except ValueError as loi:
            print("  Lỗi: %s. Ví dụ hợp lệ: x^3+x+1, 1011, 0b1011, 0xB" % loi)
            continue
        if p >= gioi_han:
            print("  Lỗi: bậc phải nhỏ hơn %d (đa thức có tối đa %d bit)." % (bac(gioi_han), bac(gioi_han)))
            continue
        return p


def chon_truong():
    """Chọn n = 4 hoặc 8 và đa thức tối giản m(x) (Enter = dùng đa thức mặc định)."""
    while True:
        n = input("Chọn trường GF(2^n), nhập 4 hoặc 8: ").strip()
        if n in ("4", "8"):
            n = int(n)
            break
        print("  Chỉ nhận 4 hoặc 8.")
    while True:
        s = input("Đa thức tối giản m(x) bậc %d (Enter = mặc định %s): " % (n, dang_da_thuc(MAC_DINH[n]))).strip()
        if s == "":
            return n, MAC_DINH[n]
        try:
            m = doc_da_thuc(s)
        except ValueError as loi:
            print("  Lỗi: %s" % loi)
            continue
        if bac(m) != n:
            print("  Lỗi: m(x) phải có bậc đúng bằng %d." % n)
        elif not la_toi_gian(m):
            print("  Lỗi: %s KHÔNG tối giản, không tạo được trường. Hãy chọn lại." % dang_da_thuc(m))
        else:
            return n, m


def main():
    n, m = chon_truong()
    nhan = tao_phep_nhan(m)
    print("\nĐang làm việc trong GF(2^%d), m(x) = %s. Bỏ trống rồi Enter để thoát.\n" % (n, dang_da_thuc(m)))
    while True:
        p1 = hoi_da_thuc("Nhập P1 (bậc < %d): " % n, 1 << n)
        if p1 is None:
            break
        p2 = hoi_da_thuc("Nhập P2 (bậc < %d): " % n, 1 << n)
        if p2 is None:
            break
        print()
        minh_hoa(p1, p2, m)                             # các bước làm tay: quy x thành g, tra bảng, đếm chẵn lẻ
        kq = nhan(p1, p2)                               # kết quả bằng thuật toán chính
        kiem_tra = gf_mul_cach1(p1, p2, m)              # kết quả bằng cách khác để đối chiếu
        print("\n  P1 = %s  (0x%X)" % (dang_da_thuc(p1), p1))
        print("  P2 = %s  (0x%X)" % (dang_da_thuc(p2), p2))
        print("  P1 * P2 = %s  (nhị phân %s, hex 0x%X)" % (dang_da_thuc(kq), format(kq, "0%db" % n), kq))
        print("  Kiểm tra chéo bằng nhân thường rồi chia dư: %s\n" % ("KHỚP" if kq == kiem_tra else "KHÔNG KHỚP (có lỗi!)"))


if __name__ == "__main__":
    main()