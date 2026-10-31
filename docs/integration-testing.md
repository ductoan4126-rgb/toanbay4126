# Thiết kế và thực hiện kiểm thử tích hợp MobileCity

## 1. Cơ sở và giới hạn

| Thuộc tính | Nội dung |
| --- | --- |
| Hệ thống | Website công khai MobileCity |
| Kiểu kiểm thử | Tích hợp ở mức giao diện/điều hướng quan sát được bằng Selenium |
| Môi trường thực thi | Windows, Java 17, Maven, Selenium WebDriver 4.29.0, JUnit 5.11.4, Chrome headless |
| Ngày chạy | 31/10/2026 |
| Giới hạn | Không có mã nguồn backend, API nội bộ, log máy chủ hoặc quyền kiểm soát dữ liệu của MobileCity |

Các thành phần bên trong MobileCity được xem như một hộp đen. Tài liệu chỉ khẳng định sự kết nối giữa những trang và điều khiển công khai mà trình duyệt hiển thị. Không suy diễn rằng đã kiểm thử tích hợp giữa service, cơ sở dữ liệu hoặc API backend. Các luồng chạy thành công là kiểm thử tích hợp giao diện quan sát được, đồng thời có đặc điểm của kiểm thử end-to-end.

## 2. Sơ đồ và điểm tích hợp

```text
Điểm IP-01: tìm kiếm và mở chi tiết

[Trang chủ: form tìm kiếm]
       | người dùng nhập "Samsung" và gửi form
       v
[Trang kết quả tìm kiếm]
       | liên kết sản phẩm và tên hiển thị
       v
[Trang chi tiết sản phẩm]

Điểm IP-02: danh mục và mở chi tiết

[Trang danh mục /dien-thoai]
       | chọn liên kết sản phẩm đang hiển thị
       v
[Trang chi tiết sản phẩm]
```

### IP-01 — Form tìm kiếm → kết quả → chi tiết sản phẩm

| Nội dung | Mô tả có thể quan sát |
| --- | --- |
| Thành phần tham gia | Trình duyệt; form tìm kiếm ở trang công khai; trang kết quả; liên kết sản phẩm; trang chi tiết. Logic server xử lý tìm kiếm là thành phần hộp đen, không thể quan sát trực tiếp. |
| Dữ liệu đầu vào | Từ khóa công khai `Samsung`. |
| Dữ liệu trao đổi | Từ khóa được nhập/gửi qua giao diện; trình duyệt điều hướng tới trang kết quả; trang kết quả hiển thị tên và liên kết sản phẩm; tên sản phẩm được đối chiếu với tiêu đề trang chi tiết. Không thu thập payload hoặc endpoint nội bộ. |
| Kết quả đầu ra | Trang kết quả có tiêu đề, có sản phẩm khớp từ khóa; mở được chi tiết và tiêu đề chi tiết khớp tên sản phẩm đã chọn. |
| Lỗi có thể phát sinh | Form không gửi/điều hướng; kết quả không khớp; liên kết hỏng; chi tiết không tải hoặc tên ở trang đích không đồng bộ; trang bị chặn hoặc timeout. |

### IP-02 — Danh mục → chi tiết sản phẩm

| Nội dung | Mô tả có thể quan sát |
| --- | --- |
| Thành phần tham gia | Trình duyệt; trang danh mục `/dien-thoai`; thẻ/liên kết sản phẩm; trang chi tiết. |
| Dữ liệu đầu vào | URL danh mục đã cấu hình; sản phẩm đầu tiên đang hiển thị được chọn trong lúc chạy, không cố định theo giá/tồn kho. |
| Dữ liệu trao đổi | Tên hiển thị và liên kết của sản phẩm trên danh mục; điều hướng trình duyệt; tiêu đề trang chi tiết. |
| Kết quả đầu ra | Trang chi tiết có tiêu đề và tiêu đề chứa tên sản phẩm vừa chọn. |
| Lỗi có thể phát sinh | Danh mục không tải hoặc không có thẻ sản phẩm; liên kết lỗi; trang chi tiết thiếu tiêu đề; tên hiển thị giữa danh mục và trang đích không khớp; timeout/challenge. |

Giỏ hàng là một điểm tích hợp tiềm năng khác, nhưng test giỏ trong baseline bị `BLOCKED` trước đăng nhập vì không có credentials được cấp. Không có tài khoản nào được sử dụng và không phát sinh thay đổi giỏ.

## 3. Chiến lược kiểm thử

**Lựa chọn: tiếp cận top-down tại biên giao diện công khai.** Bắt đầu từ thao tác của người dùng trên trang chủ/danh mục, rồi kiểm tra dữ liệu và điều hướng ở các trang tiếp theo. Cách tiếp cận này phù hợp với các lát cắt người dùng có thể quan sát và Selenium có thể điều khiển.

Đây **không phải** top-down integration test ở mức mã nguồn: không có quyền truy cập module UI/backend nội bộ để thay bằng stub hoặc lần theo lời gọi giữa module. Cũng không thể thực hiện bottom-up do không có quyền gọi trực tiếp các module/API nội bộ; không thể thực hiện sandwich vì thiếu cả quyền tiếp cận tầng thấp lẫn seam để kết hợp tầng trên/dưới. Không dùng mock/stub trong lần chạy thật. Vì vậy không xác minh payload mạng, xử lý lỗi nội bộ, tính nhất quán cơ sở dữ liệu hoặc giao dịch backend.

## 4. Test case tích hợp

IT-01–IT-04 được xác minh bằng Selenium trong baseline `MC-20261031-100139`; IT-05–IT-07 chưa chạy vì cần fixture, stub hoặc độ trễ có kiểm soát. Không có lỗi hoặc dữ liệu không đồng bộ nào được giả lập trên website thật.

| Test ID | Điểm tích hợp | Thành phần | Dữ liệu đầu vào | Các bước | Kết quả mong đợi | Kết quả thực tế | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IT-01 | IP-01 | Form tìm kiếm → kết quả → chi tiết | `Samsung` | Mở trang chủ; gửi từ khóa; xác nhận tiêu đề và sản phẩm khớp; mở kết quả đầu tiên; so sánh tên kết quả với tiêu đề chi tiết. | Có kết quả phù hợp; liên kết mở đúng trang chi tiết; tên được đồng bộ. | TC-SEARCH-004 PASS in run MC-20261031-100139; assertions passed. | **PASS** |
| IT-02 | IP-02 | Danh mục → chi tiết | `/dien-thoai`; sản phẩm đầu tiên đang hiển thị | Mở danh mục; lưu tên sản phẩm đầu tiên; mở liên kết; so sánh với tiêu đề trang đích. | Chi tiết tải và tiêu đề khớp sản phẩm đã chọn. | TC-PRODUCT-001 PASS in run MC-20261031-100139; assertions passed. | **PASS** |
| IT-03 | IP-01 | Form tìm kiếm → xác thực đầu vào | Từ khóa rỗng | Mở trang chủ; mở form tìm kiếm; kiểm tra ràng buộc bắt buộc và validity khi rỗng. | Trình duyệt chặn gửi form rỗng; không trình bày dữ liệu rỗng như kết quả thành công. | TC-SEARCH-001 PASS in run MC-20261031-100139; required empty input was invalid. | **PASS** |
| IT-04 | IP-01 | Xử lý tìm kiếm → trạng thái không có kết quả | `MC-QA-NONEXISTENT-000` | Gửi từ khóa không khớp; kiểm tra tiêu đề và trạng thái rỗng. | Giao diện nêu rõ không có kết quả, không hiển thị sản phẩm không liên quan như kết quả khớp. | TC-SEARCH-003 PASS in run MC-20261031-100139; empty-result message was present. | **PASS** |
| IT-05 | IP-01 / IP-02 | Danh sách sản phẩm → nội dung chi tiết | Fixture có tên kết quả khác tên trang đích | Dùng fixture/môi trường kiểm thử được kiểm soát để làm lệch tên; chạy phép đối chiếu tên. | Test phát hiện sai lệch và FAIL; không chấp nhận liên kết như dữ liệu đồng bộ. | Không có fixture hoặc quyền thay đổi dữ liệu website; không thể tạo sai lệch an toàn trên site thật. | **NOT EXECUTED** |
| IT-06 | IP-01 | Thành phần trả kết quả → giao diện | Stub phản hồi lỗi hoặc môi trường được cho phép trả lỗi | Trong môi trường kiểm soát, làm thành phần tìm kiếm trả lỗi; quan sát trạng thái giao diện và bằng chứng lỗi. | Không đánh dấu kết quả cũ/rỗng là thành công; lỗi có thể nhận diện được và test báo lỗi rõ ràng. | Không có endpoint/stub được cấp phép; không gửi yêu cầu gây lỗi tới website thật. | **NOT EXECUTED** |
| IT-07 | IP-01 / IP-02 | Điều hướng/tải trang → chờ Selenium | Stub chậm hơn timeout hoặc môi trường timeout có kiểm soát | Trong môi trường kiểm soát, làm trang đích vượt quá thời gian chờ; ghi nhận timeout và trạng thái chạy. | Timeout được báo là lỗi/block phù hợp; không đánh dấu PASS khi thiếu trang đích. | Không có môi trường kiểm soát độ trễ; không cố ý gây tải hoặc làm gián đoạn website thật. | **NOT EXECUTED** |

### Ánh xạ test case sang mã nguồn

Hai luồng đã chạy tái sử dụng các bài Selenium JUnit hiện có, không tạo test trùng lặp:

| Test ID tích hợp | Mã test hiện hữu | Mã nguồn |
| --- | --- | --- |
| IT-01 | `TC-SEARCH-004` — mở chi tiết từ kết quả tìm kiếm | [SearchTest.java](../src/test/java/mobilecity/tests/SearchTest.java), phương thức `searchResultOpensProductDetails()` |
| IT-02 | `TC-PRODUCT-001` — mở chi tiết từ danh mục | [ProductTest.java](../src/test/java/mobilecity/tests/ProductTest.java), phương thức `listedProductOpensMatchingDetailPage()` |
| IT-03 | `TC-SEARCH-001` — kiểm tra từ khóa rỗng | [SearchTest.java](../src/test/java/mobilecity/tests/SearchTest.java), phương thức `emptySearchInputIsRequired()` |
| IT-04 | `TC-SEARCH-003` — trạng thái không có kết quả | [SearchTest.java](../src/test/java/mobilecity/tests/SearchTest.java), phương thức `searchShowsEmptyStateForNoMatch()` |

## 5. Thực thi và bằng chứng

Lệnh đã chạy từ thư mục dự án với JDK 17 và Maven portable:

```powershell
mvn --batch-mode --no-transfer-progress "-Dtest=SearchTest#searchResultOpensProductDetails,ProductTest#listedProductOpensMatchingDetailPage" test
```

| Kết quả chạy | Giá trị |
| --- | --- |
| Run ID chạy tập trung ban đầu | `MC-20261031-095353` |
| Test được chọn | 2 |
| PASS / FAIL / BLOCKED / NOT EXECUTED | 2 / 0 / 0 / 0 |
| `ProductTest` | 1 test; 7.836 giây theo Surefire |
| `SearchTest` | 1 test; 5.653 giây theo Surefire |
| Tổng thời gian Maven | 16.635 giây |
| Trình duyệt | Chrome 156.0.8078.76, headless |
| Lưu ý môi trường | Selenium in cảnh báo không có CDP implementation khớp Chrome 156; hai luồng WebDriver đã chạy và các assertion đều thành công. Không sử dụng Chrome DevTools Protocol trong các luồng này. |

Sau đó, full suite `MC-20261031-100139` chạy lại các test ánh xạ IT-01–IT-04; cả bốn đạt. Toàn suite gồm 33 test: 32 PASS, 0 FAIL, 0 ERROR và 1 BLOCKED (test giỏ hàng).

Bằng chứng thực thi:

- [Nhật ký PASS theo test và run ID](../reports/test-execution.log)
- [Surefire XML — ProductTest](../target/surefire-reports/TEST-mobilecity.tests.ProductTest.xml)
- [Surefire XML — SearchTest](../target/surefire-reports/TEST-mobilecity.tests.SearchTest.xml)
- [Surefire text — ProductTest](../target/surefire-reports/mobilecity.tests.ProductTest.txt)
- [Surefire text — SearchTest](../target/surefire-reports/mobilecity.tests.SearchTest.txt)

Nhật ký ghi nhận run tập trung ban đầu lúc 09:54 và full baseline lúc 10:01–10:04. Theo kết quả mới nhất, bốn case IT-01–IT-04 là `PASS`, IT-05–IT-07 là `NOT EXECUTED`. Kết quả chứng minh các trang công khai đã nối đúng qua trình duyệt trong các lần chạy đó, không chứng minh tích hợp backend hoặc độ ổn định lâu dài của website.
