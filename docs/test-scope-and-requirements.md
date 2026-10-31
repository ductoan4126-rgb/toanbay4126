# Phân tích hệ thống, phạm vi và yêu cầu kiểm thử MobileCity

## 1. Thông tin tài liệu và cơ sở khảo sát

| Thuộc tính | Nội dung |
| --- | --- |
| Hệ thống | MobileCity — https://mobilecity.vn/ |
| Loại tài liệu | Mô tả hệ thống, danh mục chức năng, yêu cầu nghiệp vụ và phạm vi kiểm thử |
| Ngày khảo sát giao diện | 31/10/2026 |
| Phương pháp | Duyệt website công khai bằng Chrome; đọc DOM/trạng thái hiển thị; đối chiếu mã Selenium hiện có trong dự án |
| Giới hạn khảo sát | Không đăng nhập, không gửi biểu mẫu chứa dữ liệu cá nhân, không thêm/xóa mặt hàng, không đặt hàng hoặc thanh toán |

Các mô tả dưới đây phản ánh giao diện quan sát được tại thời điểm khảo sát, không phải cam kết rằng nội dung, giá, tồn kho hoặc chương trình khuyến mại luôn cố định. Việc mở trang và quan sát giao diện là khảo sát thăm dò, **không phải kết quả chạy test case**; tài liệu này không đánh dấu test nào là PASS.

## 2. Mô tả hệ thống

### 2.1 Tổng quan và mục đích hoạt động

MobileCity là website bán lẻ và giới thiệu sản phẩm công nghệ. Trang chủ hiện có các lối điều hướng tới Điện thoại, Máy tính bảng, Laptop, Tivi, Phụ kiện, Đồng hồ thông minh và Tai nghe; đồng thời hiển thị sản phẩm nổi bật, ô tìm kiếm, lựa chọn khu vực, liên kết tài khoản và mục Tra cứu bảo hành. Website cũng giới thiệu dịch vụ sửa chữa và thông tin cửa hàng.

Trang danh mục Điện thoại hiển thị các thẻ sản phẩm có tên, ảnh, giá và nút/điểm tương tác “Mua”; có mục “Sắp xếp theo giá”. Trang chi tiết điện thoại được khảo sát có giá bán, nội dung mô tả/đánh giá và thông tin kỹ thuật. Đây là các luồng công khai giúp người mua tìm, so sánh và tìm hiểu sản phẩm trước khi liên hệ hoặc mua.

### 2.2 Đối tượng sử dụng

- Khách truy cập muốn tìm hiểu sản phẩm, giá được công bố, danh mục và địa chỉ cửa hàng.
- Người mua đang cân nhắc lựa chọn sản phẩm hoặc kiểm tra thông tin bảo hành.
- Khách hàng có tài khoản muốn đăng nhập và sử dụng các chức năng gắn với tài khoản, ví dụ xem thông tin đơn hàng/giỏ hàng.
- Khách hàng cần tham khảo dịch vụ sửa chữa hoặc liên hệ cửa hàng.

### 2.3 Nghiệp vụ chính và vai trò thương mại điện tử

1. **Trưng bày và phân loại hàng hóa:** điều hướng từ trang chủ tới danh mục/nhãn hàng; hiển thị sản phẩm, ảnh và giá.
2. **Tìm sản phẩm:** nhập từ khóa ở ô tìm kiếm; với từ khóa `Samsung`, khảo sát bằng giao diện đã mở trang “Tìm kiếm”, hiển thị tiêu đề “Kết quả tìm kiếm” và các sản phẩm Samsung.
3. **Cung cấp thông tin trước mua:** trang chi tiết trình bày giá và nội dung giới thiệu/thông số để hỗ trợ quyết định mua.
4. **Hỗ trợ giao dịch và tài khoản:** website cung cấp trang đăng nhập/đăng ký và gợi ý đăng nhập để kiểm tra đơn hàng. Khu vực giỏ hàng không được xác nhận bằng thao tác có tài khoản trong lần khảo sát này.
5. **Hỗ trợ sau bán:** mục “Tra cứu BH” dẫn tới `/tra-cuu-bao-hanh`; trang hiển thị hai ô nhập số điện thoại và IMEI cùng nút “Tìm kiếm”.
6. **Kết nối dịch vụ/cửa hàng:** liên kết sửa chữa, Zalo, điện thoại và đường đi tới các cửa hàng.

Trong chuỗi thương mại điện tử, website đóng vai trò kênh trưng bày và tìm kiếm sản phẩm, cung cấp thông tin hỗ trợ quyết định, đồng thời kết nối người mua với tài khoản, cửa hàng và dịch vụ sau bán. Không suy diễn rằng mọi giao dịch hoặc bước thanh toán đều có thể hoàn tất từ giao diện đã khảo sát.

## 3. Danh mục chức năng và quyết định phạm vi

### 3.1 Chức năng được quan sát

| Mã | Chức năng | Quan sát thực tế | Trạng thái trong bộ test hiện có |
| --- | --- | --- | --- |
| F-01 | Trang chủ | Có logo, ô tìm kiếm, chọn khu vực, đăng nhập/đăng ký, điều hướng danh mục, sản phẩm nổi bật và Tra cứu BH. | PASS: TC-HOME-001 and TC-HOME-002 in run MC-20261031-100139. |
| F-02 | Danh mục và danh sách sản phẩm | `/dien-thoai` có tiêu đề, thẻ tên/ảnh/giá và tương tác “Mua”. | PASS: TC-HOME-003 in run MC-20261031-100139. |
| F-03 | Sắp xếp danh sách | Trang danh mục hiển thị mục “Sắp xếp theo giá”; nội dung trang tĩnh liệt kê Tất cả, Giá thấp đến cao và Giá cao đến thấp. Khảo sát chưa xác nhận thao tác chọn có sắp xếp dữ liệu đúng hay không. | NOT EXECUTED: no automated sort test; interaction order remains unverified. |
| F-04 | Tìm kiếm | Tìm kiếm bằng giao diện với từ khóa `Samsung` mở trang kết quả và hiển thị tên sản phẩm phù hợp. Hành vi từ khóa rỗng và trạng thái không có kết quả chưa được xác nhận trong khảo sát trực tiếp. | PASS: all four SearchTest cases in run MC-20261031-100139. |
| F-05 | Chi tiết sản phẩm | Trang sản phẩm OPPO A3x 5G được mở trực tiếp, có nội dung giá, mô tả và thông số/đánh giá. | PASS: all five ProductTest cases; search-to-detail assertion also passed. |
| F-06 | Đăng nhập | `/login` hiển thị trường tên đăng nhập/email/số điện thoại, mật khẩu và nút đăng nhập. | NOT EXECUTED: no independent login test; no credentials used. |
| F-07 | Đăng ký | `/register` hiển thị trường số điện thoại hoặc email và nút “Tiếp tục”. Không gửi biểu mẫu. | NOT EXECUTED: registration form was not submitted; no RegisterTest. |
| F-08 | Giỏ hàng | Truy cập `/gio-hang` khi chưa đăng nhập chuyển tới `/login`. Chưa quan sát giỏ đã xác thực. | BLOCKED: TC-CART-001 lacked authorized credentials; no cart mutation occurred. |
| F-09 | Tra cứu bảo hành | `/tra-cuu-bao-hanh` hiển thị trường số điện thoại, IMEI và nút “Tìm kiếm”. Chưa gửi dữ liệu hoặc xác nhận kết quả tra cứu. | NOT EXECUTED: warranty form was not submitted; no test data authorized. |
| F-10 | Sửa chữa/liên hệ | Có đường dẫn sửa chữa, Zalo, điện thoại và địa chỉ/đường đi cửa hàng. | NOT EXECUTED: repair/contact links are outside the executed suite. |

### 3.2 Chức năng được chọn

Phạm vi kiểm thử chức năng được chọn gồm:

1. Trang chủ và điều hướng danh mục.
2. Danh mục, thẻ sản phẩm và sắp xếp theo giá.
3. Tìm kiếm.
4. Trang chi tiết sản phẩm.
5. Giỏ hàng: chỉ kiểm tra số lượng của một mặt hàng trong tài khoản/phiên thử nghiệm được cho phép; phải khôi phục số lượng ban đầu.

Đăng nhập là điều kiện hỗ trợ cho luồng giỏ hàng, không đồng nghĩa đã xác nhận nghiệp vụ đăng nhập thành công. Đăng ký và tra cứu bảo hành được ghi nhận là chức năng hiện hữu, nhưng chưa đưa vào chạy tự động vì chưa có tài khoản/dữ liệu thử nghiệm được cho phép; biểu mẫu bảo hành yêu cầu dữ liệu cá nhân/IMEI. Các test sắp xếp, thêm/xóa mặt hàng và các kiểm tra form tài khoản vẫn cần triển khai hoặc xác minh riêng.

## 4. Yêu cầu nghiệp vụ và điều kiện kiểm thử

> “Quan sát” mô tả điều đã thấy trên giao diện; “cần xác minh” là quy tắc mong đợi cần được kiểm tra bằng test có bằng chứng. Không coi quy tắc chưa xác minh là kết luận về hành vi website.

### REQ-001 — Trang chủ và điều hướng danh mục

- **Mô tả:** Người dùng truy cập trang chủ và mở danh mục sản phẩm từ điều hướng công khai.
- **Điều kiện đầu vào:** Kết nối website hoạt động; URL cơ sở là `https://mobilecity.vn/`.
- **Quy tắc xử lý:** Trang chủ tải và hiển thị nội dung; liên kết danh mục đưa người dùng tới đúng danh mục.
- **Đầu ra mong đợi:** Tiêu đề trang không rỗng, logo/điều hướng hiển thị; chọn Điện thoại mở trang `/dien-thoai`.
- **Hợp lệ:** Mở trang chủ và bấm liên kết Điện thoại hiển thị trên trang.
- **Không hợp lệ/ngoại lệ:** Trang không truy cập được, trả về trang thử thách hoặc không có nội dung phù hợp. Khi có anti-bot/challenge, ghi `BLOCKED`, không quy kết thành lỗi chức năng.
- **Bằng chứng trong mã:** `HomeTest` — `TC-HOME-001`, `TC-HOME-002`.

### REQ-002 — Danh mục và thẻ sản phẩm

- **Mô tả:** Người dùng mở danh mục và xem sản phẩm được công bố.
- **Điều kiện đầu vào:** Danh mục Điện thoại truy cập được và có sản phẩm.
- **Quy tắc xử lý:** Mỗi thẻ được kiểm tra phải gắn với một sản phẩm và hiển thị tên; giá được xác minh khi sản phẩm có giá công khai.
- **Đầu ra mong đợi:** Tên sản phẩm không rỗng; giá hiển thị có nội dung số khi giá được công bố.
- **Hợp lệ:** Mở `/dien-thoai` và chọn sản phẩm đang hiển thị.
- **Không hợp lệ/ngoại lệ:** URL danh mục không hợp lệ hoặc trang trả lỗi; danh sách rỗng/challenge không được tự coi là lỗi của catalog nếu chưa điều tra nguyên nhân.
- **Bằng chứng trong mã:** `ProductTest` — `TC-HOME-003`.

### REQ-003 — Tìm kiếm sản phẩm

- **Mô tả:** Người dùng tìm kiếm bằng tên hoặc từ khóa sản phẩm.
- **Điều kiện đầu vào:** Trang có ô tìm kiếm; dùng từ khóa công khai, không chứa dữ liệu cá nhân.
- **Quy tắc xử lý:** Từ khóa hợp lệ được gửi và website hiển thị trang kết quả; kết quả được đối chiếu với từ khóa. Quy tắc xử lý truy vấn rỗng và trường hợp không có kết quả cần được xác nhận lại từ lần chạy thực tế.
- **Đầu ra mong đợi:** Với `Samsung`, khảo sát giao diện đã hiển thị trang “Kết quả tìm kiếm” cùng các tên sản phẩm Samsung. Kết quả này chỉ là quan sát, không phải PASS của test tự động.
- **Hợp lệ:** Từ khóa đã biết có sản phẩm công khai tương ứng.
- **Không hợp lệ:** Để trống hoặc dùng từ khóa không khớp. Mong đợi test: không gửi truy vấn rỗng nếu ràng buộc được xác nhận; hiển thị trạng thái rỗng rõ ràng với từ khóa không khớp. Hai quy tắc này chưa được xác nhận trong khảo sát trực tiếp.
- **Bằng chứng trong mã:** `SearchTest` — `TC-SEARCH-001` đến `TC-SEARCH-004`. Test không khớp dùng dữ liệu trong `testdata.properties`; chưa xác nhận trạng thái rỗng trực tiếp trong phiên khảo sát.

### REQ-004 — Sắp xếp danh mục theo giá

- **Mô tả:** Người dùng chọn thứ tự giá cho danh sách sản phẩm.
- **Điều kiện đầu vào:** Danh mục hiển thị mục “Sắp xếp theo giá” và danh sách có ít nhất hai sản phẩm có giá so sánh được.
- **Quy tắc xử lý:** Các lựa chọn được hiển thị trong nội dung trang gồm Tất cả, Giá thấp đến cao và Giá cao đến thấp. Hành vi thực tế sau khi chọn cần được kiểm tra trước khi xác nhận quy tắc xử lý.
- **Đầu ra mong đợi:** Danh sách sau khi chọn tăng dần/giảm dần theo giá; kiểm chứng thứ tự từ giá được hiển thị cho từng sản phẩm, không dựa vào giá cố định.
- **Hợp lệ:** Chọn một thứ tự có trên giao diện khi danh sách có nhiều sản phẩm.
- **Không hợp lệ/ngoại lệ:** Không có đủ giá để so sánh hoặc danh sách rỗng; không tự đặt quy tắc cho tham số sắp xếp lạ khi chưa có đặc tả.
- **Trạng thái:** Chưa triển khai test trong dự án hiện tại; mục sắp xếp có hiện diện nhưng thao tác và kết quả chưa được xác minh.

### REQ-005 — Xem chi tiết sản phẩm

- **Mô tả:** Người dùng mở trang chi tiết từ một sản phẩm hiển thị trong danh mục hoặc kết quả tìm kiếm.
- **Điều kiện đầu vào:** Sản phẩm có liên kết đang hoạt động.
- **Quy tắc xử lý:** Trang chi tiết phải tương ứng với sản phẩm đã chọn; xác minh các trường công khai có thể quan sát như tên, giá, ảnh chính và phần thông số khi trang cung cấp.
- **Đầu ra mong đợi:** Tên tiêu đề khớp sản phẩm đã chọn; giá có nội dung số khi được công bố; ảnh chính tải thành công; phần thông số hiện diện nếu được yêu cầu.
- **Hợp lệ:** Chọn sản phẩm còn truy cập được từ danh sách.
- **Không hợp lệ/ngoại lệ:** Liên kết sản phẩm sai/hết hiệu lực hoặc trang bị challenge; ghi nhận riêng điều kiện môi trường, không biến timeout do challenge thành kết luận rằng sản phẩm hỏng.
- **Bằng chứng trong mã:** `ProductTest` — `TC-PRODUCT-001` đến `TC-PRODUCT-004`; `SearchTest` — `TC-SEARCH-004`.

### REQ-006 — Cập nhật số lượng mặt hàng trong giỏ

- **Mô tả:** Khách hàng cập nhật số lượng một mặt hàng trong giỏ và hệ thống lưu số lượng đó.
- **Điều kiện đầu vào:** Có phiên/tài khoản thử nghiệm được phép sử dụng, giỏ có ít nhất một sản phẩm, và giao diện hiển thị ô số lượng cùng nút cập nhật gắn với mặt hàng.
- **Quy tắc xử lý:** Kiểm tra giá trị ban đầu hợp lệ; tăng một đơn vị; xác nhận phản hồi cập nhật và giá trị sau khi tải lại; cuối cùng khôi phục đúng số lượng ban đầu và xác minh lại.
- **Đầu ra mong đợi:** Giá trị mới được lưu sau tải lại; sau khi hoàn tất test, số lượng bằng đúng giá trị trước test.
- **Hợp lệ:** Số nguyên dương không vượt giới hạn `max` hiển thị trên ô nhập.
- **Không hợp lệ:** Số lượng 0, âm, không phải số hoặc lớn hơn giới hạn cần được từ chối/không lưu; quy tắc này chưa được kiểm tra trên website trong khảo sát.
- **Giới hạn an toàn:** Không xóa sản phẩm, không checkout/đặt hàng/thanh toán; nếu không thể xác minh hoặc khôi phục thì phải báo rõ, không ghi PASS.
- **Bằng chứng trong mã:** `CartTest` — `TC-CART-001`, phụ thuộc tài khoản/phiên thử nghiệm và mặt hàng đã có. Không có credentials trong môi trường khảo sát; giỏ chưa được thao tác.

### REQ-007 — Đăng nhập và đăng ký

- **Mô tả:** Người dùng có thể mở các trang tài khoản; đăng nhập là điều kiện cần cho một số thao tác giỏ hàng.
- **Điều kiện đầu vào:** Trang đăng nhập hiển thị tên đăng nhập/email/số điện thoại và mật khẩu; trang đăng ký hiển thị trường số điện thoại hoặc email và nút “Tiếp tục”.
- **Quy tắc xử lý:** Việc xác thực thành công/thất bại phải được kiểm tra bằng tài khoản thử nghiệm được cấp quyền. Không gửi OTP hoặc đăng ký tài khoản dùng dữ liệu cá nhân nếu chưa được cho phép.
- **Đầu ra mong đợi:** Trang tài khoản hiển thị trạng thái phù hợp với kết quả xác thực; chi tiết thông báo và các ràng buộc đăng ký cần được kiểm tra riêng.
- **Hợp lệ:** Chỉ dùng credentials thử nghiệm được ủy quyền.
- **Không hợp lệ/ngoại lệ:** Thiếu credentials, credentials không hợp lệ, CAPTCHA/OTP hoặc challenge. CAPTCHA/OTP dẫn tới `BLOCKED`; không tìm cách vượt qua.
- **Trạng thái:** Form hiện diện đã được quan sát; không thực hiện gửi form trong khảo sát. Chưa có test đăng ký độc lập.

### REQ-008 — Tra cứu bảo hành

- **Mô tả:** Người dùng tra cứu thông tin bảo hành qua trang Tra cứu bảo hành.
- **Điều kiện đầu vào:** Trang `/tra-cuu-bao-hanh` có hai trường số điện thoại và IMEI cùng nút “Tìm kiếm”.
- **Quy tắc xử lý:** Cần xác định quy tắc định dạng, quan hệ giữa hai trường và phản hồi cho thiết bị có/không có dữ liệu từ nguồn đặc tả được phép. Chưa suy diễn các quy tắc đó từ việc thấy form.
- **Đầu ra mong đợi:** Khi có bộ dữ liệu ủy quyền, hệ thống trả trạng thái bảo hành tương ứng; đầu ra cụ thể chưa được xác minh.
- **Hợp lệ:** Chỉ dùng cặp số điện thoại/IMEI thử nghiệm được cấp phép, không thuộc khách hàng thật.
- **Không hợp lệ/ngoại lệ:** Thiếu/sai định dạng hoặc không tìm thấy hồ sơ; cần xác nhận cách báo lỗi. Không dùng dữ liệu cá nhân/IMEI thật để thử.
- **Trạng thái:** Trang và trường nhập được quan sát; không gửi yêu cầu tra cứu. Chưa có test trong dự án hiện tại.

## 5. Phạm vi kiểm thử

### 5.1 Trong phạm vi

- Kiểm tra giao diện công khai trang chủ, logo, điều hướng và danh mục.
- Kiểm tra danh sách sản phẩm, tên và giá được công bố.
- Kiểm tra tìm kiếm với từ khóa công khai; thiết kế kiểm tra truy vấn rỗng/không có kết quả nhưng chỉ kết luận sau khi chạy có bằng chứng.
- Kiểm tra thao tác sắp xếp theo giá ở mức danh sách; đây là hạng mục cần bổ sung test.
- Kiểm tra điều hướng tới chi tiết và các trường công khai như tên, giá, ảnh, thông số.
- Kiểm tra cập nhật số lượng giỏ có điều kiện, phải khôi phục trạng thái ban đầu.
- Kiểm tra hiển thị trang đăng nhập/đăng ký và trang tra cứu bảo hành; thao tác xác thực/tra cứu chỉ khi có dữ liệu thử nghiệm được ủy quyền.
- Ghi nhận ảnh chụp, log và báo cáo tự động khi có thực thi; phân biệt `PASS`, `FAIL`, `BLOCKED` và `NOT EXECUTED`.

### 5.2 Ngoài phạm vi

- Thanh toán bằng tiền thật, checkout hoặc đặt đơn thực tế.
- Tạo/xóa đơn hàng, xóa sản phẩm khỏi giỏ người dùng thật hoặc để lại thay đổi dữ liệu không được hoàn nguyên.
- Sử dụng dữ liệu cá nhân/IMEI của khách hàng thật hoặc đăng ký tài khoản không được cấp phép.
- Can thiệp cơ sở dữ liệu, hệ thống quản trị hoặc dịch vụ nội bộ.
- Vượt CAPTCHA, OTP, đăng nhập liên kết bên thứ ba hoặc cơ chế chống bot.
- Kiểm thử xâm nhập/khai thác lỗ hổng.
- Kết luận về chức năng không tiếp cận được hoặc không có môi trường/dữ liệu thử nghiệm phù hợp.

### 5.3 Môi trường kiểm thử

| Thành phần | Cấu hình |
| --- | --- |
| Hệ thống | Website công khai `https://mobilecity.vn/`; nội dung và giá có thể thay đổi |
| Trình duyệt | Google Chrome |
| Hệ điều hành mục tiêu theo đề bài | Windows |
| Java | JDK 17 trở lên; Maven compiler cấu hình release 17 |
| Automation | Selenium WebDriver 4.x và Selenium Manager |
| Test framework/build | JUnit 5 và Apache Maven |
| Thiết kế | Page Object Model, `WebDriverWait` và `ExpectedConditions` |
| CI hiện có | GitHub Actions trên Ubuntu; là môi trường khác với Windows mục tiêu |

Baseline được chạy trên Windows bằng Microsoft OpenJDK 17.0.21.0.2 và Maven 3.9.9: `mvn --batch-mode --no-transfer-progress clean verify`, run ID `MC-20261031-100139`. Kết quả tổng hợp: 33 test, 32 PASS, 0 FAIL, 0 ERROR và 1 BLOCKED (`TC-CART-001`, thiếu credentials thử nghiệm). Báo cáo Surefire, JaCoCo và log được lưu trong `target/` và `reports/`; kết quả không bao gồm kiểm thử backend MobileCity.

## 6. Liên kết yêu cầu với chức năng kiểm thử

| Yêu cầu | Chức năng/test case hiện có | Tệp trong dự án | Tình trạng triển khai / bằng chứng |
| --- | --- | --- | --- |
| REQ-001 | `TC-HOME-001`, `TC-HOME-002` | `src/test/java/mobilecity/tests/HomeTest.java` | PASS: TC-HOME-001/002 in run MC-20261031-100139. |
| REQ-002 | `TC-HOME-003` | `src/test/java/mobilecity/tests/ProductTest.java` | PASS: TC-HOME-003 in run MC-20261031-100139. |
| REQ-003 | `TC-SEARCH-001`–`TC-SEARCH-004` | `src/test/java/mobilecity/tests/SearchTest.java` | PASS: TC-SEARCH-001..004 in run MC-20261031-100139. |
| REQ-004 | Chưa có test | Chưa có | NOT EXECUTED: sort behavior is not automated or verified. |
| REQ-005 | `TC-PRODUCT-001`–`TC-PRODUCT-004`; `TC-SEARCH-004` | `src/test/java/mobilecity/tests/ProductTest.java`; `src/test/java/mobilecity/tests/SearchTest.java` | PASS: ProductTest TC-PRODUCT-001..004 and TC-SEARCH-004 passed. |
| REQ-006 | `TC-CART-001` | `src/test/java/mobilecity/tests/CartTest.java` | BLOCKED: TC-CART-001; no authorized credentials, so no change was made. |
| REQ-007 | Đăng nhập là bước hỗ trợ trong `TC-CART-001`; chưa có test đăng ký | `src/test/java/mobilecity/tests/CartTest.java`; Page Object trong `src/main/java/mobilecity/pages/LoginPage.java`, `RegisterPage.java` | NOT EXECUTED: no independent login/register functional test was run. |
| REQ-008 | Chưa có test | Chưa có | NOT EXECUTED: no authorized warranty test data was provided. |

### 6.1 Quy ước trạng thái kết quả

- `PASS`: test đã được thực thi, assertion đạt và có báo cáo/log tương ứng.
- `FAIL`: test đã chạy và điều kiện kiểm thử thất bại; cần điều tra trước khi kết luận nguyên nhân thuộc website.
- `BLOCKED`: không thể tiếp tục an toàn/đúng điều kiện, ví dụ challenge, thiếu credentials hoặc thiếu dữ liệu thử nghiệm.
- `NOT EXECUTED`: test chưa được chạy.

Trạng thái trong ma trận phải dựa trên bằng chứng JUnit/log của run `MC-20261031-100139`, không dựa riêng vào khảo sát giao diện hoặc sự tồn tại của mã test. Test giỏ hàng bị BLOCKED do thiếu tài khoản được ủy quyền; sort, đăng ký và bảo hành là NOT EXECUTED.
