# bai_tap_tuan_7_ly_thuyet_mat_ma
Cài đặt giải thuật thuật toán nhân 2 đa thức trong trường hữu hạn GF(2^4), GF(2^8) tương ứng với đa thức tối giản trong trường 
# Nhân hai đa thức trong GF(2^n)

- Sinh viên: Hoàng Tuấn Khôi - 20233468

## Đề bài
Cài đặt thuật toán nhân hai đa thức trong trường hữu hạn GF(2^4) và GF(2^8)
tương ứng với đa thức tối giản của trường.

## Đa thức tối giản đã chọn
| Trường | m(x) | Dạng nhị phân |
|---|---|---|
| GF(2^4) | x^4 + x + 1 | 10011 |
| GF(2^8) | x^8 + x^4 + x^3 + x + 1 | 100011011 |

## Thuật toán
Mỗi phần tử là đa thức nhị phân, lưu bằng số nguyên (bit i = hệ số của x^i).
Phép cộng là XOR.

Cách 1 (`gf_mul`): tính x^k (x) P2 cho k = 0..n-1.
Mỗi lần nhân với x là dịch trái 1 bit.
Nếu xuất hiện x^n thì XOR với m(x).
Kết quả là XOR các x^k (x) P2 mà hệ số của x^k trong P1 bằng 1.

Cách 2 (`gf_mul_reduce`): nhân hai đa thức thông thường (bậc tối đa 2n-2)
rồi lấy phần dư khi chia cho m(x). Dùng để kiểm tra chéo cách 1.

## Cách chạy
```bash
python3 gf_mul.py
```

## Kết quả kiểm thử
GF(2^8): (x) * (x^7) = x^4 + x^3 + x + 1  -> OK
GF(2^8): (0) * (x^7 + x^5 + x^3 + x + 1) = 0  -> OK
GF(2^8): (1) * (x^7 + x^5 + x^3 + x + 1) = x^7 + x^5 + x^3 + x + 1  -> OK
GF(2^4): hai cách khớp và giao hoán trên toàn bộ 256 cặp
GF(2^8): hai cách khớp và giao hoán trên toàn bộ 65536 cặp