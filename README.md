# Nhân hai đa thức trong trường hữu hạn GF(2ⁿ)

- **Sinh viên:** Hoàng Tuấn Khôi - **MSSV:** 2023348 -
## 1. Đề bài

Cài đặt thuật toán nhân hai đa thức trong trường hữu hạn GF(2⁴) và GF(2⁸) tương ứng với đa thức tối giản của trường. Chương trình có bộ testcase chạy tự động và minh chứng thực tế cho thấy thuật toán đúng.

## 2. Cấu trúc thư mục

```
gf.py          Thuật toán nhân, kiểm tra đa thức tối giản
test_gf.py     Bộ testcase chạy tự động (python3 test_gf.py)
nhap_tay.py    Nhập hai đa thức bất kỳ để nhân (python3 nhap_tay.py)
images/        Ảnh bài làm tay và ảnh kết quả chạy
README.md      Tài liệu này
```

## 3. Cơ sở lý thuyết

- Mỗi phần tử của GF(2ⁿ) là một đa thức có hệ số 0 hoặc 1 và bậc nhỏ hơn n. Trong code đa thức được lưu thành số nguyên: bit thứ i là hệ số của xⁱ (ví dụ x³ + x + 1 = `1011`).
- **Phép cộng là XOR**, vì 1 + 1 = 0.
- **Phép nhân** là nhân hai đa thức rồi lấy phần dư khi chia cho đa thức tối giản m(x), để kết quả vẫn có bậc nhỏ hơn n.
- m(x) phải **tối giản** (không phân tích được thành tích hai đa thức bậc nhỏ hơn). Nếu không, sẽ có hai phần tử khác 0 nhân ra 0 và không chia được, tức là không phải trường. Ví dụ x⁸ + 1 = (x + 1)⁸.

### Đa thức tối giản đã chọn

| Trường | m(x) | Nhị phân | x có là phần tử sinh? |
|---|---|---|---|
| GF(2⁴) | x⁴ + x + 1 | `10011` | Có (chu kỳ 15 = 2⁴ − 1) |
| GF(2⁸) | x⁸ + x⁴ + x³ + x + 1 (đa thức của AES) | `100011011` | Không (chu kỳ 51), nhưng bảng dùng để nhân vẫn đúng |

(Bậc 4 có 3 đa thức tối giản, bậc 8 có 30 đa thức. Muốn dùng đa thức khác xem mục 5.)

## 4. Thuật toán

Phương pháp "quy x thành g, nhân, tra bảng, bỏ bậc xuất hiện chẵn lần":

1. **Quy x thành g** trong hai đa thức cần nhân.
2. **Nhân** hai đa thức theo g: gⁱ · gʲ = gⁱ⁺ʲ cho từng cặp số hạng.
3. **Tra bảng** để đổi mỗi g^k về đa thức. Bảng g^k = x^k mod m(x), k từ 0 đến 2n − 2 (tích hai đa thức bậc ≤ n − 1 có bậc tối đa 2n − 2). Mỗi hàng của bảng tính từ hàng trước bằng cách nhân với x: dịch trái 1 bit, nếu tràn bậc n thì XOR với m(x).
4. **Rút gọn**: bậc x nào xuất hiện số lần chẵn thì mất (1 + 1 = 0), số lần lẻ thì giữ. Trong code đây là phép XOR các kết quả.

Các hàm trong `gf.py`: `nhan_x` (bước nhân với x), `bang_luy_thua` (lập bảng g^k), `tao_phep_nhan` (thực hiện bốn bước trên).

### Ví dụ: GF(2⁴), m(x) = x⁴ + x + 1

Bảng g^k:

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| g^k | 1 | x | x² | x³ | x + 1 | x² + x | x³ + x² |

Tính (x² + x + 1)(x³ + 1):

- Quy x thành g: (g² + g + 1)(g³ + 1).
- Nhân và tra bảng: g⁵ + g² + g⁴ + g + g³ + 1 = (x² + x) + x² + (x + 1) + x + x³ + 1.
- Đếm: x³ có 1 lần (giữ), x² có 2 lần (mất), x có 3 lần (giữ), 1 có 2 lần (mất).
- Kết quả: **x³ + x** (`1010`).

### Ví dụ: GF(2⁸), m(x) = x⁸ + x⁴ + x³ + x + 1

(x⁶ + x⁴ + x² + x + 1)(x⁷ + x + 1) = **x⁷ + x⁶ + 1** (0x57 × 0x83 = 0xC1), trùng ví dụ của chuẩn AES (FIPS-197).

## 5. Cách chạy

Chỉ cần Python 3, không cần cài thêm thư viện.

### Chạy bộ testcase

```bash
python3 test_gf.py
```

### Đổi đa thức tối giản

Mở `test_gf.py`, sửa danh sách số mũ ở đầu file, rồi chạy lại:

```python
DA_THUC = [
    [4, 1, 0],          # GF(2^4): x^4 + x + 1
    [8, 4, 3, 1, 0],    # GF(2^8): x^8 + x^4 + x^3 + x + 1
]
```

Chương trình tự suy ra n, tự lập lại bảng g^k và tự chạy lại testcase. Nếu đa thức không tối giản thì báo lỗi thay vì tính sai. Các testcase chỉ áp dụng cho một đa thức cụ thể (slide 31–32, chuẩn AES) sẽ tự bỏ qua khi đổi đa thức. Liệt kê các đa thức tối giản bậc 4:

```bash
python3 -c "from gf import *; print([dang_da_thuc(m) for m in ds_toi_gian(4)])"
```

### Nhập hai đa thức bất kỳ để nhân

```bash
python3 nhap_tay.py
```

Chương trình hỏi trường (4 hoặc 8), đa thức tối giản (Enter = mặc định), rồi hai đa thức P₁, P₂. Đa thức nhập được ở một trong ba dạng: chữ (`x^6+x^4+x^2+x+1`), nhị phân (`1010111` hoặc `0b1010111`), hex (`0x57`). Bậc phải nhỏ hơn n, nhập sai thì chương trình báo lỗi và hỏi lại. Với mỗi cặp, chương trình in từng bước làm tay, kết quả (dạng chữ, nhị phân, hex) và đối chiếu với phép nhân thường rồi chia dư (KHỚP / KHÔNG KHỚP). Bỏ trống rồi Enter để thoát.



