# Phase 1 — Khảo sát dự án kiểm thử hiện có

## 1. Phạm vi khảo sát

Khảo sát cây thư mục của `D:\a1\mobilecity-selenium`, toàn bộ 21 file Java, `pom.xml`, dữ liệu test, workflow CI, README, tài liệu Markdown, log, ảnh và báo cáo sinh tự động. Tìm kiếm file DOCX/XLSX/PDF/ZIP trong `D:\a1` và `D:\b1`; không thấy bản `MobileCity-Testing-MASTER.zip` hoặc hồ sơ Office/PDF có sẵn. Không sửa mã trong giai đoạn kiểm kê. Sau kiểm kê đã chạy `mvn --batch-mode --no-transfer-progress clean verify` bằng JDK 17/Maven 3.9.9 portable.

## 2. Bảng đánh giá

| Hạng mục | Trạng thái hiện tại | Vấn đề/giới hạn | Hướng xử lý |
| --- | --- | --- | --- |
| Cấu trúc dự án | Có Maven project; `config`, `pages`, `utils`, `base`, `tests`, test resources, workflow và script xác thực UTF-8. 21 file Java. | Tên/lớp khác một số tên gợi ý trong đề, nhưng đã có chức năng tương đương cho cấu hình, driver, screenshot lỗi và Page Object. Không có `WarrantyPage`, `LoginTest`, `WarrantyTest` độc lập. | Giữ cấu trúc và tên hiện tại; chỉ thêm class khi có test được phép, không thêm lớp rỗng để khớp mẫu. |
| Tài liệu hiện có | Có 6 tài liệu Markdown: khảo sát, phân tích/phạm vi, 21 test hộp đen, unit test, integration test, system test. | Chưa có DOCX/XLSX/PDF theo định dạng bàn giao yêu cầu. | Giữ Markdown làm tài liệu chi tiết dễ kiểm tra; sinh các hồ sơ Office/PDF đồng bộ, kèm bảng và traceability. |
| DOCX/XLSX/PDF | Không tìm thấy file Word, Excel hoặc PDF trong các thư mục dự án được khảo sát. | Chưa có TestPlan, TestCases, DefectReport, TestReport, TraceabilityMatrix và FinalReport ở định dạng yêu cầu. | Tạo trong `Team/` và giữ cấu trúc mã nguồn hiện tại. |
| Phiên bản dự án/ZIP | Không tìm thấy ZIP dự án hoặc bản MASTER trong `D:\a1`/`D:\b1`. | Chỉ có một Maven repository hiện hữu; worktree có thay đổi chưa commit từ các phase trước. | Tiếp tục trong repository này; bảo toàn mọi thay đổi hiện hữu và đóng gói bản nộp độc lập, không commit hoặc xóa file gốc. |
| Mã nguồn Java | Java 17; Selenium WebDriver 4.29.0; Page Object; `WebDriverWait`; cấu hình tách khỏi website; credentials chỉ qua environment. | Một số chức năng website không có mã nguồn backend để unit/integration test; các page account/cart đòi hỏi quyền thử nghiệm. | Chỉ mô tả và kiểm thử phần UI có thể quan sát; không nhận đó là kiểm thử backend. |
| `pom.xml` | Java release 17, JUnit 5.11.4, Maven Surefire 3.5.2, JaCoCo 0.8.12. | JaCoCo chỉ lọc lớp `TestConfig`; coverage không đại diện cho toàn ứng dụng Selenium hay website. | Ghi rõ phạm vi coverage và số đo thực tế; không mở rộng kết luận. |
| Unit tests | 18 test độc lập: 16 `TestConfigTest`, 2 `EvidenceWriterTest`; không mở trình duyệt/website. | Chỉ 16 case có thiết kế chi tiết riêng trong unit-test report cũ. | Cập nhật báo cáo để bao gồm 18 test đã chạy và số liệu JaCoCo mới nhất. |
| Browser/system tests | Home 2, Search 4, Product 5, System 3; browser tests có thể chạy với Chrome. | Chưa có test đăng ký/bảo hành; thao tác giỏ cần tài khoản có quyền. | Dùng trang công khai; kiểm tra status theo báo cáo JUnit/log, ảnh cho system case. |
| Test toàn bộ baseline | `mvn clean verify` — BUILD SUCCESS, 33 tổng; 32 PASS, 0 FAIL, 0 ERROR, 1 BLOCKED. | `TC-CART-001` BLOCKED vì không có `MOBILECITY_USERNAME`/`MOBILECITY_PASSWORD`; không phát sinh thay đổi giỏ. | Giữ trạng thái BLOCKED, không đưa credentials vào báo cáo. |
| Coverage baseline | Báo cáo JaCoCo được tạo; `TestConfig`: 138/150 instructions (92.0%), 35/37 lines (94.6%), 19/26 branches (73.1%). | Đây là coverage của lớp cấu hình nội bộ, không phải coverage website; không phải mọi statement/branch toàn hệ thống. | Nêu đúng phạm vi trong hồ sơ unit test và PDF. |
| Log/ảnh/báo cáo máy | Có `reports/test-execution.log`, Surefire XML/text, JaCoCo XML/CSV/HTML; ảnh system có run ID `MC-20261031-100139`. | Log tích lũy nhiều lần chạy; cần chọn run ID mới nhất làm baseline và liên kết ảnh theo đúng run. | Giữ log nguyên trạng; tài liệu chính trích dẫn run mới nhất và các file bằng chứng tương ứng. |
| CI/CD | GitHub Actions workflow chạy `mvn clean test`, dùng secrets tùy chọn và upload report/log. | Kết quả CI không thay thế run cục bộ; website có thể chặn automation. | Báo cáo riêng kết quả thực tế của run cục bộ. |

## 3. Kết quả baseline Maven

Run ID: `MC-20261031-100139`  
Lệnh: `mvn --batch-mode --no-transfer-progress clean verify`

| Test class | Tổng | PASS | FAIL | ERROR | BLOCKED |
| --- | ---: | ---: | ---: | ---: | ---: |
| `TestConfigTest` | 16 | 16 | 0 | 0 | 0 |
| `EvidenceWriterTest` | 2 | 2 | 0 | 0 | 0 |
| `HomeTest` | 2 | 2 | 0 | 0 | 0 |
| `SearchTest` | 4 | 4 | 0 | 0 | 0 |
| `ProductTest` | 5 | 5 | 0 | 0 | 0 |
| `SystemTest` | 3 | 3 | 0 | 0 | 0 |
| `CartTest` | 1 | 0 | 0 | 0 | 1 |
| **Tổng** | **33** | **32** | **0** | **0** | **1** |

Surefire biểu diễn test bị abort do thiếu điều kiện dưới dạng skipped trong XML; trong báo cáo nghiệp vụ, test tương ứng được ghi `BLOCKED` theo lý do được log, không được tính là PASS. Không phát hiện lỗi website trong phần test đã chạy; đây không phải kết luận về chất lượng tổng thể của website.

## 4. Tình trạng theo phase

| Phase | Tình trạng |
| --- | --- |
| 1 — Khảo sát dự án | Hoàn tất: kiểm kê, đọc cấu hình/mã/test/tài liệu/bằng chứng và chạy baseline. |
| 2 — Phân tích/thiết kế | Hoàn tất: 21 case hộp đen, 18 unit test, 7 case tích hợp, 4 case hệ thống và ma trận truy vết REQ → Function → Test Case. |
| 3 — Triển khai/thực thi | Hoàn tất trong phạm vi được phép: Selenium/JUnit baseline 32 PASS, 1 BLOCKED; không có giao dịch thật; các giới hạn được ghi rõ. |
| 4 — Hoàn thiện tài liệu | Hoàn tất: tài liệu Markdown và bộ DOCX/XLSX/PDF đã đồng bộ với log, Surefire, JaCoCo và ảnh hệ thống. |
| 5 — Kiểm tra/đóng gói | Hoàn tất: DOCX/XLSX/PDF mở và đọc được; trạng thái/truy vết khớp thiết kế; PDF có ảnh hệ thống; ZIP hợp lệ và chứa mã nguồn, báo cáo, bằng chứng, không chứa file `.env` bí mật. |
