# 🧩 UCTP - University Course Timetabling Problem

UCTP - University Course Timetabling Problem là bài toán tối ưu tổ hợp, được xếp vào nhóm bài toán **NP-hard**, với mục tiêu xây dựng một thời khóa biểu cho các lớp học tại trường đại học bằng cách gán mỗi lớp học phần vào khung thời gian và phòng học phù hợp, sao cho thỏa mãn các ràng buộc cứng và tối ưu các ràng buộc mềm.

# 🎯 Khung dữ liệu huấn luyện cho UCTP

Khung dữ liệu huấn luyện (Training Data Framework) là một quy trình dùng để tổ chức, chuẩn hóa và biểu diễn dữ liệu từ bài toán thực tế thành dữ liệu có cấu trúc, nhằm phục vụ cho việc huấn luyện các mô hình học máy.

Trong trường hợp bài toán UCTP, Khung dữ liệu huấn luyện xác định:

- Các đơn vị dữ liệu / Các lớp học trong thời khóa biểu.
- Đặc trưng nào được dùng / Các thông tin về lớp học.
- Cách lưu trữ dữ liệu để mô hình có thể học được.

## Mô tả dữ liệu

Dữ liệu gốc được lưu trong một tệp bảng tính (.xlsx) gồm nhiều trang tính (sheets). Trang tính được sử dụng trong quá trình xử lý chứa các trường dữ liệu chính sau:

| STT | Trường dữ liệu   | Kiểu dữ liệu  | Mô tả                                                                                 | Ví dụ                  |
| --- | ---------------- | ------------- | ------------------------------------------------------------------------------------- | ---------------------- |
| 1   | Mã MH            | String        | Mã định danh của môn học                                                              | 503073                 |
| 2   | Nhóm             | Integer       | Các sinh viên đăng ký cùng một môn học sẽ được chia vào các nhóm                      | 3                      |
| 3   | Tổ               | Integer       | Một nhóm có thể được chia thành các tổ để phục vụ cho giờ học thực hành               | 0                      |
| 4   | Tên môn          | String        | Tên môn học                                                                           | Cơ sở dữ liệu          |
| 5   | Sỉ số            | Integer       | Số lượng sinh viên trong một nhóm hoặc tổ                                             | 45                     |
| 6   | Thứ              | Integer       | Thứ học trong tuần                                                                    | 2                      |
| 7   | Ca/Tiết          | String        | Ca học của một nhóm, tổ                                                               | 123-------------       |
| 8   | Phòng            | String        | Phòng học được phân công                                                              | C203                   |
| 9   | Giảng viên       | String        | Họ tên giảng viên phụ trách giảng dạy                                                 | Nguyễn Văn A           |
| 10  | Email cá nhân    | String / Null | Địa chỉ email cá nhân của giảng viên, sử dụng khi giảng viên chưa có email của trường | nguyenvana@gmail.com   |
| 11  | Email TDTU       | String / Null | Địa chỉ email thuộc hệ thống của Trường                                               | nguyenvana@tdtu.edu.vn |
| 12  | Hệ ĐT/Hệ đào tạo | String        | Hệ đào tạo của sinh viên                                                              | Tiêu chuẩn             |

Sau khi hoàn tất, dữ liệu được lưu dưới định dạng JSON. File JSON có cấu trúc là một mảng các đối tượng, trong đó mỗi đối tượng đại diện cho một nhóm hoặc một tổ. Đồng thời, tên các trường dữ liệu được chuyển sang tiếng Anh nhằm tránh các vấn đề liên quan đến dấu tiếng Việt và khoảng trắng.

```
[
    {
        "CourseID":"503073",
        "CourseName":"Cấu trúc rời rạc",
        "Group":3,
        "SubGroup":0,
        "DayOfWeek":2,
        "TimeSlot":"123-------------",
        "RoomID":"C203",
        "Capacity":45,
        "Lecturer":"Nguyễn Văn A",
        "PersonalEmail":"nguyenvana@gmail.com",
        "UniversityEmail":"nguyenvana@tdtu.edu.vn",
        "Program":"Tiêu chuẩn"
    }
]
```

Bảng ánh xạ tên trường dữ liệu như sau:

| STT | Tên trường (English) | Tên trường tương ứng (Tiếng Việt) |
| --- | -------------------- | --------------------------------- |
| 1   | CourseID             | Mã MH                             |
| 2   | CourseName           | Tên môn                           |
| 3   | Group                | Nhóm                              |
| 4   | SubGroup             | Tổ                                |
| 5   | DayOfWeek            | Thứ                               |
| 6   | TimeSlot             | Ca/Tiết                           |
| 7   | RoomID               | Phòng                             |
| 8   | Capacity             | Sỉ số                             |
| 9   | Lecturer             | Giảng viên                        |
| 10  | PersonalEmail        | Email cá nhân                     |
| 11  | UniversityEmail      | Email TDTU                        |
| 12  | Program              | Hệ ĐT/Hệ đào tạo                  |

## Mô tả các bước xử lý dữ liệu

#### 1. Tiền xử lý dữ liệu

- Sử dụng `pathlib` và `pandas` để dò tìm tệp dữ liệu nguồn, đọc cấu trúc và lựa chọn trang tính có tên chứa từ khóa "final".
- Chuẩn hóa các giá trị trong cột Điện thoại và Lớp về kiểu dữ liệu chuỗi.
- Không xét đến các dòng dữ liệu mà:
  - Cột 'Tên môn' chứa giá trị 'Sinh hoạt chủ nhiệm'
  - Cột 'Hệ đào tạo'/'Hệ ĐT' chứa các giá trị 'Khánh Hòa/'Nha Trang'/'Bảo Lộc'/'4+1'
  - Cột 'Phòng' chứa giá trị 'TRUCTUYEN'
- Kiểm tra mỗi dòng dữ liệu có ít nhất một trong hai thông tin liên hệ của giảng viên: Email cá nhân hoặc Email của Trường.

<p align="center">
  <img src="screenshots/1.png" width="500">
</p>

#### 2. Xử lý dữ liệu mâu thuẫn
Trong dữ liệu thời khóa biểu có thể tồn tại các dòng dữ liệu mâu thuẫn với nhau, bao gồm:
  - Một giảng viên được phân công giảng dạy nhiều hơn một lớp tại cùng một thời điểm.
  - Một phòng học được sử dụng cho nhiều hơn một lớp tại cùng một thời điểm.

Với mỗi tập chứa các dòng dữ liệu xảy ra mâu thuẫn: $$ I = \{i_1, i_2, \ldots, i_n\} $$

lần lượt xem xét từng phương án giữ lại một dòng $i_j$ và loại bỏ các dòng còn lại:

$$
R_j = I \setminus \{i_j\}
$$

Việc lựa chọn dòng dữ liệu được giữ lại dựa trên hai tiêu chí:

1. Mức mất mát dữ liệu theo môn học.
2. Mức mất mát dữ liệu theo hệ đào tạo.

##### 2.1 Tỷ lệ mất mát dữ liệu theo môn học

Với mỗi môn học $c$, ký hiệu:

* $N_c$: số lớp của môn học $c$ trước khi xử lý dữ liệu.
* $N'_{c,j}$: số lớp của môn học $c$ còn lại sau khi giả định giữ dòng $i_j$ và loại các dòng còn lại trong tập mâu thuẫn.

Tỷ lệ dữ liệu mất mát của môn học $c$ được xác định bởi:

$$
L_c(i_j)
=
\frac{N_c-N'_{c,j}}{N_c}
\times 100
$$

Nếu việc loại bỏ các dòng trong $R_j$ ảnh hưởng đến nhiều môn học, tổng tỷ lệ mất mát theo môn học của phương án giữ $i_j$ được tính bằng:

$$
C_j
=
\sum_{c \in C(R_j)}
L_c(i_j)
$$

trong đó $C(R_j)$ là tập các môn học bị ảnh hưởng bởi việc loại bỏ các dòng thuộc $R_j$.

##### 2.2 Tỷ lệ mất mát dữ liệu theo hệ đào tạo

Tương tự, với mỗi hệ đào tạo $s$, ký hiệu:

* $N_s$: số lớp thuộc hệ đào tạo $s$ trước khi xử lý dữ liệu.
* $N'_{s,j}$: số lớp thuộc hệ đào tạo $s$ còn lại sau khi giả định giữ dòng $i_j$.

Tỷ lệ dữ liệu mất mát của hệ đào tạo $s$ được xác định bởi:

$$
L_s(i_j)
=
\frac{N_s-N'_{s,j}}{N_s}
\times 100
$$

Tổng tỷ lệ mất mát theo hệ đào tạo của phương án giữ $i_j$ được tính bằng:

$$
S_j
=
\sum_{s \in S(R_j)}
L_s(i_j)
$$

trong đó $S(R_j)$ là tập các hệ đào tạo bị ảnh hưởng bởi việc loại bỏ các dòng thuộc $R_j$.

##### 2.3 Lựa chọn dòng dữ liệu được giữ lại

Sau khi tính toán mức mất mát của từng phương án, xác định giá trị nhỏ nhất theo hai tiêu chí:

$$
C_{\min}
=
\min_{i_j \in I} C_j
$$

$$
S_{\min}
=
\min_{i_j \in I} S_j
$$

Tập các dòng có mức mất mát theo môn học nhỏ nhất:

$$
A_C
=
\{i_j \in I \mid C_j=C_{\min}\}
$$

Tập các dòng có mức mất mát theo hệ đào tạo nhỏ nhất:

$$
A_S
=
\{i_j \in I \mid S_j=S_{\min}\}
$$

**Trường hợp 1: Có dòng đồng thời tối ưu cả hai tiêu chí**

Nếu:

$$
A_C \cap A_S \neq \varnothing
$$

thì dòng dữ liệu thuộc giao của hai tập trên được ưu tiên giữ lại:

Trong trường hợp có nhiều dòng cùng thỏa mãn hai tiêu chí, dòng có chỉ số nhỏ nhất được lựa chọn.

**Trường hợp 2: Không có dòng đồng thời tối ưu cả hai tiêu chí**

Nếu:

$$
A_C \cap A_S = \varnothing
$$

thì ta tính tổng mức mất mát của mỗi phương án:

$$
T_j
=
C_j + S_j
$$

Dòng có tổng mức mất mát nhỏ nhất được giữ lại, tất cả các dòng còn lại trong tập mâu thuẫn sẽ bị loại bỏ.

Kết luận, quá trình xử lý mâu thuẫn ưu tiên giữ lại phương án làm giảm ít nhất sự phân bố dữ liệu ban đầu theo **môn học** và **hệ đào tạo**, qua đó hạn chế mức độ mất cân bằng dữ liệu.

#### 3. Các thao tác trực quan hóa dữ liệu

Trực quan hóa tổng số dòng dữ liệu bị loại trừ sau khi kết thúc 2 quá trình xử lý.

<p>
  <img src="screenshots/3.1.png" width="700">
</p>

<br>
Trực quan hóa số dòng dữ liệu bị loại trừ tại mỗi bước xử lý.
<p>
  <img src="screenshots/3.2.png" width="500">
</p>
<p>
  <img src="screenshots/3.3.png" width="700">
</p>

<br>
Trực quan hóa chi tiết số dòng dữ liệu bị loại trừ tại bước xử lý thứ 2.
<p>
  <img src="screenshots/3.4.png" width="700">
</p>
<p>
  <img src="screenshots/3.5.png" width="700">
</p>

## Hướng dẫn chạy dự án

#### 1. Điều kiện

- [Git](https://git-scm.com/)
- [parquet-viewer]() - Extensions để trực quan file .parquet, nếu dùng [Visual Studio Code]()

#### 2. Sao chép kho lưu trữ

```bash
git clone https://github.com/Thanh-Binhhh/UCTP-Public.git
```

#### 3. Khởi động dự án

Tiến hành chạy file `main.ipynb`

## Hướng dẫn sửa lỗi (nếu có)

#### 1. Trường `Email cá nhân` và `Email TDTU` rỗng

Bản chất dữ liệu của cột `Email cá nhân` và `Email TDTU` trong file Excel không phải dữ liệu tĩnh, mà được sinh ra từ công thức Excel, ví dụ `=VLOOKUP(N2, Email!B:D, 2, 0)`. Điều này có nghĩa là giá trị email không được lưu trực tiếp trong ô mà chỉ được tính toán tại thời điểm Excel thực hiện recalculation.

Trong khi đó, thư viện `pandas` không thực thi công thức Excel, mà chỉ đọc giá trị đã được Excel tính sẵn và lưu trong file (cached value), vì vậy, khi thực thi mã chương trình dùng để đọc file, ta sẽ thấy dữ liệu trong 2 cột nêu trên rỗng.

Để đảm bảo dữ liệu được `pandas` đọc chính xác, cần mở file Excel và nhấn `Save` thủ công bằng Microsoft Excel trước khi xử lý.

## Cấu trúc dự án

```
├── EDA/
│   ├── data/
│   │   ├── raw_data/                 // Chứa dữ liệu gốc
│   │   │   ├── 2022-2023/
│   │   │   │   ├── HK1/
│   │   │   │   │   ├── DSSV.xlsx
│   │   │   │   │   └── TKB.xlsx
│   │   │   │   └── HK2/
│   │   │   │       ├── DSSV.xlsx
│   │   │   │       └── TKB.xlsx
│   │   │   │
│   │   │   └── 2023-2024/
│   │   │       ├── HK1/
│   │   │       │   ├── DSSV.xlsx
│   │   │       │   └── TKB.xlsx
│   │   │       └── HK2/
│   │   │           ├── DSSV.xlsx
│   │   │           └── TKB.xlsx
│   │   │
│   │   └── training_ready_data/      // Chứa dữ liệu sau khi đã hoàn thành xử lý
│   │
│   ├── pipeline/
│   │   ├── data_inconsistency.py     // Xử lý dữ liệu mâu thuẫn
│   │   ├── data_preprocessing.py     // Tiền xử lý dữ liệu
│   │   ├── data_visualization.py     // Trực quan dữ liệu
│   │   └── helper_functions.py       // Các hàm bổ trợ
│   │
│   └── main.ipynb                    // Entry point
│
└── README.md

```

# 📝 Tác giả

- **Thanh Bình** - [Github](https://github.com/Thanh-Binhhh) | [Github Student](https://github.com/Thanh-Binhh)
