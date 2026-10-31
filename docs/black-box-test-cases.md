# Thiết kế test case hộp đen — MobileCity

## 1. Mục đích và quy ước

Tài liệu thiết kế các test case chức năng hộp đen dựa trên yêu cầu trong [test-scope-and-requirements.md](test-scope-and-requirements.md) và giao diện đã khảo sát ngày 31/10/2026. Bộ test gồm **21 test case**, áp dụng ECP, BVA, Decision Table và State Transition Testing.

Đây là **thiết kế**, không phải kết quả thực thi. Cột Actual Result được ghi “Chưa thực thi”, trạng thái của mọi test case là `NOT EXECUTED`; không test nào được gán PASS. Những test cần tài khoản, dữ liệu được ủy quyền hoặc đặc tả giới hạn chưa xác nhận chỉ được chạy khi thỏa tiền điều kiện tương ứng.

### Quy ước trạng thái

- `PASS`: Đã chạy và kết quả thực tế khớp Expected Result, có log/báo cáo.
- `FAIL`: Đã chạy và có sai khác so với Expected Result; cần điều tra trước khi quy kết nguyên nhân.
- `BLOCKED`: Không thể tiếp tục an toàn hoặc thiếu tiền điều kiện (challenge, tài khoản, dữ liệu, kiểm soát chưa xác nhận).
- `NOT EXECUTED`: Chưa chạy.

## 2. Test case

| Test Case ID | Requirement ID | Test Objective | Preconditions | Test Data | Test Steps | Expected Result | Actual Result | Status | Technique |
|---|---|---|---|---|---|---|---|---|---|
| BB-HOME-01 | REQ-001 | Kiểm tra trang chủ tải và hiển thị thành phần điều hướng chính. | Có mạng; trang không bị challenge. | `https://mobilecity.vn/` | 1. Mở trang chủ. 2. Quan sát tiêu đề, logo và liên kết danh mục. | Trang tải; tiêu đề và logo hiện diện; điều hướng Điện thoại dùng được. | TC-HOME-001 passed in full run MC-20261031-100139; title, logo and category link assertions passed. | PASS | ECP — đầu vào URL hợp lệ |
| BB-HOME-02 | REQ-001 | Kiểm tra điều hướng từ trang chủ tới danh mục Điện thoại. | Trang chủ tải thành công. | Liên kết Điện thoại hiển thị. | 1. Mở trang chủ. 2. Chọn liên kết Điện thoại. 3. Kiểm tra URL và tiêu đề đích. | URL thuộc `/dien-thoai`; nội dung/tiêu đề xác định danh mục Điện thoại. | TC-HOME-002 passed in full run MC-20261031-100139; category navigation assertions passed. | PASS | State Transition — Trang chủ → Danh mục |
| BB-CAT-01 | REQ-002 | Kiểm tra thẻ sản phẩm hiển thị tên và thông tin giá công khai. | Danh mục tải và có sản phẩm. | Sản phẩm hiện trên danh mục tại thời điểm chạy. | 1. Mở `/dien-thoai`. 2. Chọn thẻ đầu tiên. 3. Quan sát tên, ảnh và giá nếu được công bố. | Tên không rỗng; ảnh/thẻ thuộc sản phẩm; giá có nội dung số nếu website công bố giá cho sản phẩm đó. | TC-HOME-003 passed in full run MC-20261031-100139; product name and price assertions passed. | PASS | ECP — lớp danh mục có sản phẩm |
| BB-SORT-01 | REQ-004 | Xác minh sắp xếp giá tăng dần. | Danh mục có ít nhất hai sản phẩm với giá hiển thị; các lựa chọn sắp xếp khả dụng. | Danh sách và giá thực tế tại thời điểm chạy. | 1. Ghi lại tên và giá các sản phẩm hiển thị. 2. Chọn “Giá thấp đến cao”. 3. Đợi danh sách cập nhật. 4. Đọc lại giá theo thứ tự. | Giá sản phẩm hiển thị theo thứ tự không giảm; danh sách vẫn gồm sản phẩm hợp lệ. Không đối chiếu với giá cố định trong tài liệu. | Chưa thực thi. | NOT EXECUTED | ECP — lựa chọn sắp xếp tăng dần |
| BB-SORT-02 | REQ-004 | Xác minh sắp xếp giá giảm dần. | Như BB-SORT-01. | Danh sách và giá thực tế tại thời điểm chạy. | 1. Ghi lại các giá đang hiển thị. 2. Chọn “Giá cao đến thấp”. 3. Đợi cập nhật và đọc lại thứ tự giá. | Giá sản phẩm hiển thị theo thứ tự không tăng. | Chưa thực thi. | NOT EXECUTED | ECP — lựa chọn sắp xếp giảm dần |
| BB-SEARCH-01 | REQ-003 | Kiểm tra tìm kiếm cho lớp từ khóa có kết quả. | Trang chủ có ô tìm kiếm; không bị challenge. | `Samsung` (từ khóa đã dùng khi khảo sát giao diện). | 1. Nhập `Samsung`. 2. Chọn nút tìm kiếm. 3. Đợi kết quả. 4. Đọc tiêu đề và tên các kết quả. | Trang kết quả hiển thị; có ít nhất một sản phẩm phù hợp với từ khóa. | TC-SEARCH-002 passed in full run MC-20261031-100139; matching result was present. | PASS | ECP — lớp từ khóa hợp lệ, có kết quả |
| BB-SEARCH-02 | REQ-003 | Kiểm tra lớp từ khóa hợp lệ cú pháp nhưng không có sản phẩm tương ứng. | Tìm kiếm hoạt động; từ khóa được xác nhận không trùng sản phẩm/dịch vụ trước khi chạy. | `MC-QA-NONEXISTENT-000` (giá trị hiện có trong `src/test/resources/testdata/testdata.properties`; phải kiểm tra lại tính duy nhất khi chạy). | 1. Nhập từ khóa. 2. Gửi tìm kiếm. 3. Quan sát trang kết quả và trạng thái rỗng. | Trang tìm kiếm xử lý yêu cầu; không hiển thị sản phẩm không liên quan như thể là kết quả khớp; nếu không có kết quả, hiển thị trạng thái rỗng. | TC-SEARCH-003 passed in full run MC-20261031-100139; empty-result message was present. | PASS | ECP — lớp tìm kiếm không khớp |
| BB-SEARCH-03 | REQ-003 | Kiểm tra biên dưới của độ dài từ khóa (rỗng). | Ô tìm kiếm hiển thị; không bị challenge. | Chuỗi rỗng, độ dài `0`. | 1. Để trống ô tìm kiếm. 2. Thử gửi form bằng giao diện. 3. Kiểm tra URL/thông báo và giá trị ô nhập. | Không gửi truy vấn tìm kiếm rỗng; giao diện giữ người dùng ở form và/hoặc báo trường bắt buộc. Không yêu cầu thông báo cụ thể nếu website chưa có đặc tả. | TC-SEARCH-001 passed in full run MC-20261031-100139; empty required input was invalid. | PASS | BVA — độ dài 0 tại biên dưới |
| BB-PRODUCT-01 | REQ-005 | Xác minh liên kết danh mục mở đúng trang chi tiết sản phẩm đã chọn. | Danh mục tải và có sản phẩm có liên kết. | Một sản phẩm thực tế có trên danh mục tại thời điểm chạy. | 1. Ghi tên sản phẩm từ danh sách. 2. Mở liên kết sản phẩm. 3. Đọc tiêu đề trang chi tiết. | Trang chi tiết tải; tiêu đề khớp sản phẩm đã chọn (cho phép khác biệt định dạng/biến thể nếu tên vẫn nhận diện cùng sản phẩm). | TC-PRODUCT-001 passed in full run MC-20261031-100139; detail heading matched selected listing. | PASS | State Transition — Danh mục → Chi tiết |
| BB-PRODUCT-02 | REQ-005 | Kiểm tra thông tin công khai trên trang chi tiết. | Trang chi tiết của sản phẩm còn truy cập được. | Sản phẩm thực tế từ BB-PRODUCT-01. | 1. Mở trang chi tiết. 2. Quan sát tiêu đề, giá, ảnh chính và phần thông số nếu được công bố. | Tên hiện diện; giá có nội dung số nếu được công bố; ảnh chính tải; thông số hiện diện nếu thuộc nội dung trang được chọn. | TC-PRODUCT-002/003/004 passed in full run MC-20261031-100139; price, primary image and specifications assertions passed. | PASS | ECP — lớp sản phẩm có trang chi tiết |
| BB-ACCOUNT-01 | REQ-007 | Kiểm tra giao diện đăng nhập mà không xác thực tài khoản. | Trang `/login` truy cập được. | Không nhập credentials. | 1. Mở `/login`. 2. Kiểm tra trường tên đăng nhập/email/số điện thoại, trường mật khẩu và nút đăng nhập. | Hai trường và nút hiển thị; không có phiên đăng nhập mới được tạo. | Chưa thực thi. | NOT EXECUTED | ECP — lớp form đăng nhập hiện diện |
| BB-ACCOUNT-02 | REQ-007 | Kiểm tra giao diện đăng ký mà không tạo tài khoản. | Trang `/register` truy cập được. | Không gửi email/số điện thoại. | 1. Mở `/register`. 2. Kiểm tra trường số điện thoại/email và nút “Tiếp tục”. 3. Không submit. | Form đăng ký hiển thị trường đầu vào và nút tiếp tục; không tạo tài khoản hoặc kích hoạt OTP. | Chưa thực thi. | NOT EXECUTED | ECP — lớp form đăng ký hiện diện |
| BB-CART-01 | REQ-006 | Thay đổi tạm thời số lượng hợp lệ, xác minh sau tải lại và khôi phục giá trị ban đầu. | Có tài khoản/phiên thử nghiệm được ủy quyền; giỏ có mặt hàng; ô số lượng và nút cập nhật nhận diện được; không có challenge. | Số lượng ban đầu `q` thực đọc từ giỏ; giá trị thử `q+1`, chỉ khi không vượt giới hạn công bố. | 1. Ghi `q`. 2. Đặt `q+1` và cập nhật. 3. Tải lại, xác minh `q+1`. 4. Khôi phục `q`, tải lại và xác minh `q`. | Cập nhật hợp lệ được lưu; sau test số lượng trở lại chính xác `q`. Dừng và ghi lỗi rõ nếu không thể khôi phục; không checkout. | TC-CART-001 was blocked before login/cart mutation because no authorized credentials were configured; see run MC-20261031-100139. | BLOCKED | BVA (`q`, `q+1`); State Transition |
| BB-CART-02 | REQ-006 | Kiểm tra giá trị dưới biên số lượng tối thiểu mà không làm thay đổi giỏ. | Phiên thử nghiệm được ủy quyền; ô số lượng đang hiển thị; giới hạn tối thiểu từ `min`/đặc tả đã được ghi nhận. | `min-1`; nếu quy tắc xác nhận là số lượng dương tối thiểu `1`, giá trị này là `0`. | 1. Nhập `min-1` vào ô số lượng. 2. Đọc validity/thông báo. 3. **Không bấm cập nhật** nếu có thể làm ẩn/xóa sản phẩm. | Giá trị dưới giới hạn bị đánh dấu không hợp lệ hoặc có chỉ dẫn; không phát sinh cập nhật/xóa mặt hàng. Nếu form không thể kiểm tra an toàn ở client, dừng; cần môi trường giỏ staging để kiểm tra xử lý server. | Chưa thực thi. | NOT EXECUTED | BVA — ngay dưới biên dưới; không submit |
| BB-CART-03 | REQ-006 | Kiểm tra giá trị tại biên dưới số lượng hợp lệ. | Phiên thử nghiệm được ủy quyền; giới hạn hợp lệ `min` đã được xác nhận; có thể khôi phục số lượng. | `min`; nếu nghiệp vụ xác nhận min là `1`, dùng `1`. | 1. Đặt số lượng đúng `min`. 2. Cập nhật. 3. Tải lại và xác minh. 4. Khôi phục `q` ban đầu và xác minh lại. | Giá trị đúng biên dưới được chấp nhận; không có mặt hàng bị xóa; kết thúc với số lượng ban đầu `q`. | Chưa thực thi. | NOT EXECUTED | BVA — tại biên dưới |
| BB-CART-04 | REQ-006 | Kiểm tra giá trị ngay trên giới hạn tối đa mà không cập nhật giỏ. | Phiên thử nghiệm được ủy quyền; ô số lượng công bố `max=M` hoặc có đặc tả giới hạn tối đa; môi trường cho phép kiểm tra validity an toàn. | `M+1`. | 1. Nhập `M+1`. 2. Đọc validity/thông báo. 3. Không bấm cập nhật. | Giá trị vượt giới hạn bị đánh dấu không hợp lệ hoặc giao diện nêu rõ giới hạn; giỏ không thay đổi. Nếu không có `max`/đặc tả, ghi `BLOCKED` hoặc `NOT EXECUTED`, không tự chọn M. | Chưa thực thi; chưa biết giới hạn max của giỏ được xác thực. | NOT EXECUTED | BVA — ngay trên biên trên; không submit |
| BB-CART-05 | REQ-006 | Xác minh quyết định an toàn khi người dùng chưa đăng nhập. | Không có phiên đăng nhập. | Truy cập công khai `/gio-hang`; không gửi credentials. | 1. Mở `/gio-hang`. 2. Quan sát URL và trạng thái. 3. Không đăng nhập. | Người dùng được đưa tới đăng nhập/yêu cầu xác thực; không lộ giỏ của tài khoản khác. Đây là quan sát hiện có, nhưng test case chưa được chạy theo quy trình JUnit. | Chưa thực thi như test case; khảo sát thăm dò trước đó thấy chuyển tới `/login`. | NOT EXECUTED | Decision Table — điều kiện chưa xác thực |
| BB-CART-06 | REQ-006 | Xác minh thiếu mặt hàng thì không cập nhật dữ liệu giỏ. | Tài khoản thử nghiệm được phép; giỏ rỗng do người dùng/QA xác nhận, không tự xóa mặt hàng để tạo tiền đề. | Giỏ rỗng. | 1. Mở giỏ bằng điều hướng công khai sau khi đăng nhập hợp lệ. 2. Kiểm tra trạng thái rỗng và không có ô số lượng. 3. Không thực hiện cập nhật. | Hiển thị trạng thái giỏ rỗng; không có thay đổi dữ liệu. | Chưa thực thi; cần tài khoản có giỏ rỗng được cấp phép. | NOT EXECUTED | Decision Table — không có mặt hàng |
| BB-CART-07 | REQ-006 | Xác minh thiếu điều khiển cập nhật thì luồng dừng trước khi sửa giỏ. | Tài khoản thử nghiệm được phép; giỏ có thể thiếu ô số lượng hoặc nút cập nhật; chỉ dùng trạng thái tự nhiên của tài khoản/test fixture an toàn. | Mặt hàng hiện tại; quan sát ô số lượng và nút cập nhật gắn với mặt hàng. | 1. Mở giỏ. 2. Kiểm tra cả ô số lượng và nút cập nhật gắn với đúng mặt hàng. 3. Nếu thiếu một trong hai điều khiển, không thay đổi ô và không submit. | Luồng báo không đủ điều kiện/blocked; không phát sinh cập nhật số lượng. | Chưa thực thi; cần trạng thái UI an toàn có thể tái hiện. | NOT EXECUTED | Decision Table — thiếu điều khiển |
| BB-CART-08 | REQ-006 | Kiểm tra chuyển trạng thái giỏ theo vòng đời cập nhật có hoàn nguyên. | Đủ tiền điều kiện của BB-CART-01. | Giỏ ban đầu `q`; giá trị hợp lệ `q+1`. | 1. Bắt đầu ở giỏ với `q`. 2. Cập nhật `q+1`. 3. Tải lại để xác minh lưu. 4. Khôi phục `q`. 5. Tải lại và xác minh. | Chuyển đúng `Giỏ ban đầu → Đang cập nhật → Đã lưu tạm → Đang khôi phục → Giỏ ban đầu`; không checkout và không để lại thay đổi. | Chưa thực thi. | NOT EXECUTED | State Transition |
| BB-WARRANTY-01 | REQ-008 | Kiểm tra form tra cứu bảo hành và xử lý gửi form rỗng, không dùng dữ liệu cá nhân. | `/tra-cuu-bao-hanh` truy cập được. | Số điện thoại rỗng; IMEI rỗng. | 1. Mở trang tra cứu. 2. Kiểm tra hai trường và nút tìm kiếm. 3. Để trống cả hai trường và chọn tìm kiếm. 4. Quan sát phản hồi, không nhập dữ liệu thật. | Form nêu rõ trường bắt buộc/định dạng hoặc không trả dữ liệu bảo hành cho truy vấn rỗng; không hiển thị thông tin của khách hàng/thiết bị. Lưu phản hồi quan sát được để xác nhận oracle trước khi báo lỗi. | Chưa thực thi; mới chỉ quan sát sự hiện diện của form. | NOT EXECUTED | BVA — độ dài 0 cho hai trường |

## 3. Giải thích kỹ thuật thiết kế

### 3.1 Equivalence Class Partitioning (ECP)

**Áp dụng:** tìm kiếm, trang chủ/danh mục, trang sản phẩm và form tài khoản.

- Với tìm kiếm, chia lớp đầu vào theo hành vi cần kiểm tra:
  - **EC-S1 — từ khóa có kết quả:** ví dụ `Samsung`, từ khóa công khai đã được thấy trong kết quả khảo sát. Đại diện bằng `BB-SEARCH-01`.
  - **EC-S2 — từ khóa hợp lệ cú pháp nhưng không có kết quả:** đại diện bằng giá trị dự án đã khai báo `MC-QA-NONEXISTENT-000` trong `BB-SEARCH-02`; cần kiểm tra lại tính duy nhất trước khi chạy vì danh mục website thay đổi. Nếu giá trị có sản phẩm khớp, chọn dữ liệu thay thế có kiểm soát và ghi rõ, không giả định kết quả rỗng.
  - **EC-S3 — từ khóa rỗng:** thuộc lớp không hợp lệ theo yêu cầu chặn gửi rỗng; kiểm tra tại `BB-SEARCH-03`.
- Với trang chủ/danh mục/sản phẩm, chia lớp theo trang có thể truy cập và có dữ liệu hiển thị so với trang không tải, trang bị challenge hoặc không có dữ liệu. Lớp challenge/thiếu tiền điều kiện phải được ghi `BLOCKED`, không gộp thành lỗi chức năng.
- Với đăng nhập/đăng ký, test trong tài liệu chỉ xác nhận lớp giao diện/form hiện diện. Không suy diễn rằng tài khoản hợp lệ được xác thực thành công vì chưa gửi credentials.

ECP giúp chọn một đại diện cho mỗi lớp khác nhau thay vì lặp nhiều từ khóa/tài khoản cùng hành vi. Danh mục sản phẩm, trạng thái không kết quả, cũng như hành vi tài khoản có thể thay đổi theo thời gian và cần kiểm chứng tại lần chạy.

### 3.2 Boundary Value Analysis (BVA)

**Áp dụng:** độ dài chuỗi tìm kiếm, trường tra cứu rỗng và số lượng giỏ.

- Tìm kiếm: dữ liệu biên dưới hiện kiểm tra là độ dài `0` (`BB-SEARCH-03`). Chưa có `maxlength` được xác nhận, vì vậy không tự tạo ca biên độ dài lớn nhất.
- Tra cứu bảo hành: hai trường rỗng có độ dài `0` (`BB-WARRANTY-01`). Biên số ký tự điện thoại/IMEI chỉ bổ sung sau khi có quy tắc định dạng được xác nhận; không dùng dữ liệu thật.
- Số lượng: dự kiến kiểm tra `min-1`, `min`, và `max+1` khi giới hạn được công bố; `BB-CART-02` đến `BB-CART-04`. Nếu đặc tả được phê duyệt xác nhận số lượng tối thiểu là `1`, ba giá trị quanh biên dưới tương ứng `0, 1, 2`. Không khẳng định website hiện công bố `min=1` hoặc có `max` cho đến khi thuộc tính giao diện/đặc tả được quan sát.
- Giá trị `0` có thể làm ứng dụng xóa mặt hàng khi submit. Để tránh thay đổi dữ liệu, `BB-CART-02` chỉ kiểm tra validity mà **không** submit. Kiểm tra xử lý phía server với giá trị biên không hợp lệ cần staging/fixture và phê duyệt riêng.
- Test cập nhật số lượng hợp lệ phải dùng số lượng và giới hạn đọc từ giỏ tại lần chạy, rồi khôi phục giá trị gốc.

BVA tập trung vào các điểm ngay sát ranh giới vì lỗi kiểm tra `min`/`max` thường xuất hiện tại đó. Khi giới hạn không được nêu rõ, test có điều kiện và không tự gán kết quả pass/fail.

### 3.3 Decision Table Testing

**Áp dụng:** tiền điều kiện của cập nhật số lượng giỏ. Hành động an toàn là chỉ thực hiện cập nhật khi mọi điều kiện bắt buộc đều có; nếu bất kỳ điều kiện nào thiếu, dừng trước khi thay đổi dữ liệu.

| Quy tắc | A: Có phiên thử nghiệm được xác thực/ủy quyền? | B: Có mặt hàng trong giỏ? | C: Có ô số lượng gắn với mặt hàng? | D: Có nút cập nhật khả dụng? | Hành động mong đợi | Test case |
|---|---|---|---|---|---|---|
| DT-1 | Có | Có | Có | Có | Thực hiện cập nhật hợp lệ, xác minh sau tải lại và khôi phục số lượng ban đầu. | BB-CART-01, BB-CART-08 |
| DT-2 | Không | — | — | — | Yêu cầu đăng nhập; không sửa/đọc giỏ của tài khoản khác. | BB-CART-05 |
| DT-3 | Có | Không | Không | Không | Báo trạng thái giỏ rỗng; không thử cập nhật. | BB-CART-06 |
| DT-4 | Có | Có | Không | — | Dừng/ghi nhận không có điều khiển số lượng; không thay đổi dữ liệu. | Thiết kế bổ sung nếu UI tái hiện được; BB-CART-07 là trường hợp nút cập nhật |
| DT-5 | Có | Có | Có | Không | Dừng; không submit hoặc sửa số lượng. | BB-CART-07 |

`—` nghĩa là điều kiện phía sau không cần đánh giá vì một điều kiện trước đó đã khiến luồng phải dừng. DT-4 và DT-5 là các tình huống quan sát động: nếu môi trường thật không thể tái hiện chúng an toàn thì ghi `NOT EXECUTED`/`BLOCKED`, không sửa DOM hoặc giả lập kết quả để báo cáo.

### 3.4 State Transition Testing

**Áp dụng:** điều hướng trang và vòng đời giỏ hàng có thể khôi phục.

| Trạng thái hiện tại | Sự kiện/điều kiện | Trạng thái tiếp theo | Kiểm tra mong đợi | Test case |
|---|---|---|---|---|
| Trang chủ | Chọn liên kết Điện thoại | Danh mục Điện thoại | Đúng URL/tiêu đề danh mục | BB-HOME-02 |
| Danh mục | Chọn một sản phẩm | Chi tiết sản phẩm | Trang đích khớp sản phẩm được chọn | BB-PRODUCT-01 |
| Chưa đăng nhập | Mở giỏ hàng | Được yêu cầu đăng nhập | Không lộ giỏ hoặc dữ liệu tài khoản | BB-CART-05 |
| Giỏ ban đầu `(q)` | Gửi số lượng hợp lệ `q+1` | Đang cập nhật | Không được checkout | BB-CART-01, BB-CART-08 |
| Đang cập nhật | Website xác nhận và tải lại | Đã lưu tạm `(q+1)` | Giá trị còn sau tải lại | BB-CART-01, BB-CART-08 |
| Đã lưu tạm | Gửi giá trị ban đầu `q` | Đang khôi phục | Cập nhật khôi phục được xác nhận | BB-CART-08 |
| Đang khôi phục | Tải lại và xác minh | Giỏ ban đầu `(q)` | Trạng thái kết thúc trùng trạng thái đầu | BB-CART-01, BB-CART-08 |

Với giỏ hàng, test không được kết thúc ở trạng thái đã cập nhật tạm. Nếu cập nhật ban đầu thất bại, vẫn phải kiểm tra/khôi phục nếu có thay đổi một phần; lỗi khôi phục phải được báo là lỗi nghiêm trọng của lần chạy, không được che thành PASS.

## 4. Traceability Matrix

| Requirement ID | Function ID | Test Case ID |
|---|---|---|
| REQ-001 | F-01 — Trang chủ/điều hướng | BB-HOME-01, BB-HOME-02 |
| REQ-002 | F-02 — Danh mục/thẻ sản phẩm | BB-CAT-01 |
| REQ-003 | F-04 — Tìm kiếm | BB-SEARCH-01, BB-SEARCH-02, BB-SEARCH-03 |
| REQ-004 | F-03 — Sắp xếp theo giá | BB-SORT-01, BB-SORT-02 |
| REQ-005 | F-05 — Chi tiết sản phẩm | BB-PRODUCT-01, BB-PRODUCT-02 |
| REQ-006 | F-08 — Giỏ hàng/cập nhật số lượng | BB-CART-01, BB-CART-02, BB-CART-03, BB-CART-04, BB-CART-05, BB-CART-06, BB-CART-07, BB-CART-08 |
| REQ-007 | F-06/F-07 — Đăng nhập/đăng ký | BB-ACCOUNT-01, BB-ACCOUNT-02 |
| REQ-008 | F-09 — Tra cứu bảo hành | BB-WARRANTY-01 |

**Bao phủ thiết kế:** mọi yêu cầu REQ-001–REQ-008 trong tài liệu phạm vi đều có ít nhất một test case liên kết. Ma trận này xác nhận độ bao phủ *thiết kế*, không chứng minh đã thực thi hoặc đạt yêu cầu.

## 5. Điều kiện để chuyển thiết kế sang thực thi

1. Xác nhận tài khoản thử nghiệm được ủy quyền và mặt hàng/giỏ có thể thay đổi rồi khôi phục; không dùng giỏ của khách hàng thật.
2. Xác nhận các giới hạn số lượng `min`/`max` từ DOM thực tế hoặc tài liệu nghiệp vụ trước khi chạy các ca biên tương ứng.
3. Kiểm tra dữ liệu không khớp tìm kiếm còn duy nhất tại ngày chạy.
4. Chạy bằng JDK 17+, Maven, Chrome và môi trường Selenium đã cấu hình; lưu XML Surefire, log và ảnh bằng chứng theo quy định.
5. Nếu gặp CAPTCHA/OTP/anti-bot hoặc trang không khả dụng, dừng luồng và ghi `BLOCKED`; không tìm cách vượt cơ chế kiểm soát.
