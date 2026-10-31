# Thiết kế kiểm thử hệ thống và báo cáo kết quả MobileCity

## 1. Thông tin lần chạy

| Thuộc tính | Nội dung |
| --- | --- |
| Hệ thống | Website công khai MobileCity |
| Kiểu kiểm thử | Kiểm thử hệ thống qua giao diện người dùng bằng Selenium WebDriver |
| Ngày chạy | 31/10/2026 |
| Run ID | `MC-20261031-100139` |
| Môi trường | Windows; Java 17; Maven; Selenium WebDriver 4.29.0; JUnit 5.11.4; Chrome 156.0.8078.76, headless |
| Lệnh | `mvn --batch-mode --no-transfer-progress clean verify` (full suite; `SystemTest` chạy trong suite) |
| Giới hạn truy cập | Website công khai; không đăng nhập, không sửa giỏ, không đặt hàng và không thanh toán |

Đây là kiểm thử các luồng sử dụng nhìn từ trình duyệt. Không có quyền truy cập mã nguồn backend, API nội bộ, cơ sở dữ liệu hoặc log máy chủ. Kết quả không chứng minh các tầng nội bộ hay mọi chức năng của website không có lỗi.

## 2. Luồng nghiệp vụ

### Luồng tìm sản phẩm và xem chi tiết

```text
[Bắt đầu: mở trang chủ]
          |
          v
[Nhập từ khóa công khai "Samsung" và gửi tìm kiếm]
          |
          v
[Trang kết quả: xác nhận tiêu đề và sản phẩm khớp từ khóa]
          |
          v
[Chọn liên kết sản phẩm đầu tiên]
          |
          v
[Trang chi tiết: so sánh tên với sản phẩm đã chọn]
          |
          +---- Hoàn tất khi tiêu đề trang đích khớp
          |
          +---- Nhánh giỏ hàng (chưa chạy):
                cần đăng nhập/tài khoản thử nghiệm được cấp phép,
                thêm/cập nhật dữ liệu, tải lại giỏ và xác minh số lượng
```

| Bước | Dữ liệu trao đổi | Kết quả được xác minh |
| --- | --- | --- |
| Mở trang chủ | URL gốc công khai | Trang mở được, không bị challenge ngăn kiểm tra. |
| Gửi tìm kiếm | Từ khóa `Samsung` | Trình duyệt mở trang kết quả tìm kiếm. |
| Đọc danh sách | Tên và liên kết sản phẩm đang hiển thị | Có kết quả khớp từ khóa; lưu tên của sản phẩm đầu tiên. |
| Chọn sản phẩm | Liên kết kết quả đầu tiên | Trang chi tiết hiển thị và tiêu đề chứa tên đã chọn. |
| Kết thúc | Tiêu đề trang chi tiết | Hoàn tất luồng tìm kiếm đến xem chi tiết; không tiếp tục sang giỏ hàng trong lần chạy này. |

Luồng ngoại lệ kiểm tra từ khóa không tìm thấy dùng dữ liệu `MC-QA-NONEXISTENT-000`; kết thúc khi trang kết quả hiển thị trạng thái không có sản phẩm phù hợp. Luồng trạng thái sau thao tác tải trực tiếp trang chi tiết sản phẩm cấu hình, ghi nhận tiêu đề và giá, tải lại trang, rồi xác nhận cùng tiêu đề và giá vẫn hiển thị.

## 3. Test case hệ thống

| Test ID | Mục tiêu | Điều kiện tiền đề | Dữ liệu kiểm thử | Các bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SYS-001 | Kiểm tra luồng tìm kiếm sản phẩm → danh sách kết quả → chi tiết | Website truy cập được; không cần đăng nhập. | `Samsung` | Mở trang chủ; gửi từ khóa; xác nhận tiêu đề kết quả và có sản phẩm khớp; chọn kết quả đầu; đối chiếu tên sản phẩm với tiêu đề trang chi tiết; chụp ảnh. | Tìm được kết quả khớp; trang chi tiết tải; tiêu đề khớp sản phẩm đã chọn. | Các assertion đạt; trang chi tiết hiển thị tên khớp với kết quả đã chọn. | **PASS** |
| SYS-002 | Kiểm tra luồng ngoại lệ khi không có sản phẩm phù hợp | Website truy cập được; không cần đăng nhập. | `MC-QA-NONEXISTENT-000` | Mở trang chủ; gửi từ khóa không khớp; xác nhận trang kết quả và thông báo không có kết quả; chụp ảnh. | Hiển thị trạng thái không có kết quả; không coi sản phẩm không liên quan là kết quả phù hợp. | Trang kết quả hiển thị “Không thấy kết quả phù hợp”. | **PASS** |
| SYS-003 | Kiểm tra nội dung sản phẩm sau khi tải lại trang | Trang sản phẩm công khai truy cập được. | URL `product.sample` trong test data. | Mở trang sản phẩm; ghi tiêu đề; xác nhận giá hiển thị; tải lại; xác nhận trang, cùng tiêu đề và giá hiển thị; chụp ảnh. | Sau tải lại, trang vẫn hiển thị đúng sản phẩm và giá. | Tiêu đề sản phẩm giữ nguyên; giá tiếp tục hiển thị sau tải lại. | **PASS** |
| SYS-004 | Kiểm tra sản phẩm trong giỏ và số lượng được lưu sau tải lại | Cần tài khoản/phiên thử nghiệm được cấp phép, sản phẩm khả dụng và liên kết giỏ hàng có thể truy cập. | Một sản phẩm thử nghiệm; số lượng ban đầu và số lượng sau cập nhật. | Đăng nhập bằng thông tin được cấp; thêm sản phẩm; mở giỏ qua điều hướng công khai; xác nhận sản phẩm/số lượng; cập nhật số lượng; tải lại và xác nhận được lưu; khôi phục dữ liệu ban đầu. | Giỏ chứa đúng sản phẩm và số lượng được lưu sau reload; dữ liệu được khôi phục sau test. | Không chạy: không có thông tin xác thực/phiên thử nghiệm được cấp trong nhiệm vụ này; không tự đăng nhập hoặc thay đổi dữ liệu. | **NOT EXECUTED** |

### Phạm vi kết luận cho SYS-003

SYS-003 chỉ xác minh trang chi tiết công khai tải lại và vẫn hiển thị cùng sản phẩm/giá. Đây không phải xác minh dữ liệu giỏ hàng hay trạng thái giao dịch được lưu ở backend.

## 4. Mã chạy và bằng chứng

Các kịch bản được triển khai tại [SystemTest.java](../src/test/java/mobilecity/tests/SystemTest.java), dùng các Page Object và dữ liệu kiểm thử sẵn có. Mỗi test chụp ảnh màn hình sau khi assertion đạt; nếu chụp ảnh không ghi được, test cũng báo lỗi thay vì tạo bằng chứng thành công giả.

### Ảnh chụp màn hình

- SYS-001 — [Tìm kiếm đến trang chi tiết](../screenshots/MC-20261031-100139-SYS-001-search-to-product-detail.png)
- SYS-002 — [Trạng thái không có kết quả](../screenshots/MC-20261031-100139-SYS-002-search-empty-state.png)
- SYS-003 — [Trang chi tiết sau khi tải lại](../screenshots/MC-20261031-100139-SYS-003-product-detail-after-reload.png)

### Báo cáo máy và log

- [JUnit Surefire XML](../target/surefire-reports/TEST-mobilecity.tests.SystemTest.xml)
- [JUnit Surefire text report](../target/surefire-reports/mobilecity.tests.SystemTest.txt)
- [Execution log, gồm trạng thái và đường dẫn ảnh](../reports/test-execution.log)

Surefire ghi nhận `SystemTest`: **3 test, 3 PASS, 0 FAIL, 0 ERROR, 0 BLOCKED**, thời lượng 55.136 giây trong full suite. Maven `clean verify` kết thúc `BUILD SUCCESS`; toàn bộ baseline có 33 test, 32 PASS và 1 BLOCKED ở `CartTest` do thiếu credentials. XML kỹ thuật ghi một test abort/skipped cho `CartTest`; trạng thái báo cáo được ánh xạ thành `BLOCKED` theo log nguyên nhân. Các assertion trong ba luồng hệ thống đều thành công.

Selenium có cảnh báo không tìm thấy CDP implementation khớp Chrome 156. Các kịch bản này không dùng Chrome DevTools Protocol; WebDriver điều khiển được các thao tác và thu ảnh bằng chứng, nên cảnh báo được giữ lại như thông tin môi trường, không diễn giải thành lỗi website.

## 5. Báo cáo lỗi

Không lập defect report vì ba kịch bản đã thực thi không phát hiện lỗi có thể tái hiện. Không tạo lỗi giả từ cảnh báo tương thích CDP hoặc các chức năng chưa chạy. Điều này chỉ có nghĩa là **không ghi nhận lỗi trong phạm vi ba kịch bản và lần chạy cụ thể này**, không xác nhận website không có lỗi.

| Trường | Kết quả |
| --- | --- |
| Defect ID | Không có |
| Summary | Không có lỗi được xác nhận trong các kịch bản đã chạy |
| Environment | Windows; Java 17; Selenium 4.29.0; Chrome 156.0.8078.76; headless |
| Preconditions / Steps to Reproduce | Không áp dụng — không có lỗi được xác nhận |
| Expected / Actual Result | Không áp dụng — không có lỗi được xác nhận |
| Severity / Priority | Không áp dụng |
| Evidence | Ba ảnh SYS-001 đến SYS-003 và báo cáo Surefire ở trên |
| Status | Không có defect được mở |

## 6. Tổng hợp kết quả và giới hạn

| Chỉ số | Số lượng |
| --- | ---: |
| Kịch bản hệ thống được thiết kế trong bảng | 4 |
| Đã thực thi | 3 |
| PASS | 3 |
| FAIL | 0 |
| BLOCKED | 0 |
| NOT EXECUTED | 1 |
| Lỗi được xác nhận | 0 |

SYS-004 được phân loại `NOT EXECUTED`, không phải `BLOCKED`, vì kịch bản chưa được khởi chạy. Chưa thực hiện giỏ hàng do cần thông tin xác thực/phiên thử nghiệm được cấp phép và thao tác đó sẽ thay đổi dữ liệu. Cũng chưa kiểm thử đăng ký, thanh toán/đặt hàng thật, dữ liệu cá nhân/bảo hành, lỗi server, độ trễ/timeout có kiểm soát hoặc tích hợp backend.

Đánh giá: trong phạm vi luồng công khai tìm kiếm, xem kết quả, mở chi tiết, trạng thái không có kết quả và tải lại trang sản phẩm, ba kịch bản đều đạt và có ảnh/log kèm theo. Số lần chạy còn ít và không bao phủ giao dịch, giỏ hàng hoặc backend; do vậy chưa đủ cơ sở đánh giá chất lượng tổng thể của MobileCity.
