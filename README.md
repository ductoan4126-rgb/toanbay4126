# Bộ kiểm thử giao diện Selenium cho MobileCity

Dự án Maven cung cấp bộ kiểm thử giao diện Selenium WebDriver cho các chức năng trang chủ/danh mục, tìm kiếm, chi tiết sản phẩm và giỏ hàng của [MobileCity](https://mobilecity.vn/). Bộ kiểm thử sử dụng Java 25+, JUnit 5 và mô hình Page Object.

## Hồ sơ phân tích và phạm vi

Kết quả khảo sát baseline của repository, cấu hình, tài liệu, evidence và full Maven run được ghi tại [docs/project-assessment.md](docs/project-assessment.md).

Tài liệu mô tả hệ thống, chức năng đã khảo sát, yêu cầu nghiệp vụ, phạm vi kiểm thử, môi trường và ma trận truy vết được lưu tại [docs/test-scope-and-requirements.md](docs/test-scope-and-requirements.md). Tài liệu phân biệt các chức năng quan sát được với test đã triển khai/chưa chạy; không xem khảo sát giao diện là kết quả PASS.

Thiết kế 21 test case hộp đen, giải thích ECP/BVA/Decision Table/State Transition được lưu tại [docs/black-box-test-cases.md](docs/black-box-test-cases.md). Trạng thái đã đối chiếu với baseline `MC-20261031-100139`: 8 PASS, 1 BLOCKED, 12 NOT EXECUTED.

Thiết kế unit test JUnit 5 cho logic cấu hình, CFG, JaCoCo và kết quả 18 unit test được mô tả tại [docs/unit-testing.md](docs/unit-testing.md). Chạy riêng TestConfig bằng `mvn -Dtest=TestConfigTest verify`; không cần truy cập website.

Khi chạy test, console ghi tên từng testcase lúc bắt đầu và kết quả `PASS`, `FAIL` hoặc `BLOCKED/SKIPPED` lúc kết thúc. Surefire cũng lưu kết quả từng testcase trong `target/surefire-reports/`.

Thiết kế kiểm thử tích hợp ở mức giao diện quan sát được, 7 test case và bằng chứng chạy thật cho hai luồng tìm kiếm/danh mục được lưu tại [docs/integration-testing.md](docs/integration-testing.md). Đây không phải kiểm thử tích hợp backend.

Thiết kế kiểm thử hệ thống, các luồng nghiệp vụ, trạng thái thực thi và giới hạn kiểm thử được lưu tại [docs/system-testing.md](docs/system-testing.md). Chạy các kịch bản hệ thống bằng `mvn -Dtest=SystemTest test`; ảnh chụp được tạo trong `screenshots/`.

Các báo cáo Surefire/JaCoCo và log được tạo cục bộ trong `target/` và `reports/`, không commit các kết quả build này. Có thể tạo lại hồ sơ coursework sau khi có test evidence mới:

```powershell
python -m pip install -r scripts/reporting-requirements.txt
python scripts/generate_coursework_deliverables.py
```

Lệnh Maven chuẩn là `mvn clean test`; JaCoCo HTML/XML được kết xuất ở lifecycle `verify`, ví dụ `mvn clean verify`.

## Mục tiêu và an toàn

- Kiểm tra điều hướng và sản phẩm hiển thị trên trang chủ/danh mục.
- Kiểm tra tìm kiếm hợp lệ, trạng thái không có kết quả, ràng buộc từ khóa rỗng và điều hướng từ kết quả đến chi tiết.
- Kiểm tra tên, giá và ảnh chính trên trang chi tiết sản phẩm.
- Đăng nhập bằng thông tin được cung cấp tạm thời qua biến môi trường, mở giỏ hàng qua liên kết website hiển thị, tăng số lượng mặt hàng đầu tiên một đơn vị rồi tải lại giỏ để xác minh và khôi phục số lượng ban đầu.
- Không gửi OTP, mua hàng, đặt đơn, checkout hay thanh toán.
- Tái sử dụng bộ chọn phần tử và cấu hình trình duyệt trong các lớp page/configuration.
- Lưu kết quả Maven thực tế và bằng chứng khi kiểm thử thất bại sau mỗi lần chạy.
- Chỉ gửi truy vấn tìm kiếm công khai không chứa dữ liệu cá nhân; thông tin đăng nhập chỉ được đọc từ biến môi trường khi chạy test và không được ghi vào log.
- Không vượt CAPTCHA hoặc cơ chế chống bot. Ghi nhận luồng bị chặn là `BLOCKED`; không đánh dấu bài kiểm thử chưa chạy là `PASS`.
- Đây là bộ kiểm thử khói trên trang công khai, không phải bằng chứng rằng toàn bộ trang web không có lỗi.

## Phạm vi kiểm thử hiện tại

| Module | Phạm vi |
| --- | --- |
| `HOME` | Tải trang chủ, logo, điều hướng đến danh mục điện thoại và thẻ sản phẩm/giá công khai |
| `SEARCH` | Trường bắt buộc, kết quả khớp từ khóa, trạng thái không có kết quả và mở chi tiết từ kết quả |
| `PRODUCT` | Mở trang chi tiết từ danh mục; kiểm tra giá và ảnh chính |
| `CART` | Đăng nhập bằng tài khoản thử nghiệm, tìm liên kết giỏ hàng trên trang đã đăng nhập, mở giỏ, tăng số lượng mặt hàng đầu tiên một đơn vị và khôi phục số lượng cũ; `BLOCKED` nếu thiếu credentials, CAPTCHA/OTP hoặc không xác minh được điều khiển số lượng |

Kiểm thử giỏ hàng cần một tài khoản thử nghiệm đã được phép sử dụng. Nó không xóa sản phẩm và không tiến hành mua hàng; thay đổi số lượng được khôi phục về giá trị ban đầu. Các thao tác giỏ chỉ được thực hiện nếu trang hiển thị ô số lượng và nút cập nhật gắn với một mặt hàng.

## Công nghệ

| Thành phần | Công dụng |
| --- | --- |
| Java 25+ (LTS) | Cài đặt bài kiểm thử và Page Object; phiên bản biên dịch Maven được đặt là 25 |
| Maven | Quản lý phụ thuộc và vòng đời build/kiểm thử |
| Selenium WebDriver | Tự động hóa trình duyệt; Selenium Manager xử lý ChromeDriver |
| JUnit 5 | Framework kiểm thử và các phép khẳng định |
| Chrome | Trình duyệt chạy cục bộ và trên GitHub Actions |
| Maven Surefire | Chạy JUnit và tạo báo cáo XML/văn bản |
| GitHub Actions | Chạy bộ kiểm thử trên máy ảo Ubuntu do GitHub cung cấp |

`pom.xml` khai báo các phụ thuộc, phiên bản, phiên bản Java biên dịch và cấu hình Surefire. Đây là tệp mô tả dự án Maven; chỉnh sửa tệp này khi cần thay đổi phụ thuộc hoặc plugin build.

## Cấu trúc dự án

```text
.
├── .github/workflows/selenium-test.yml  # Quy trình CI
├── pom.xml                              # Phụ thuộc và cấu hình build/kiểm thử Maven
├── src/
│   ├── main/java/mobilecity/
│   │   ├── config/                      # Cấu hình trình duyệt và kiểm thử
│   │   ├── pages/                       # Các Page Object
│   │   └── utils/                       # Tiện ích dữ liệu kiểm thử và bằng chứng
│   └── test/
│       ├── java/mobilecity/
│       │   ├── base/                    # Vòng đời WebDriver và bằng chứng lỗi
│       │   └── tests/                   # Các lớp kiểm thử JUnit
│       └── resources/testdata/          # Dữ liệu kiểm thử giả lập/công khai
├── screenshots/                         # Ảnh lỗi và ảnh system-test sau assertion (được tạo tự động)
├── reports/                             # Nhật ký chạy cục bộ (được tạo tự động)
├── target/surefire-reports/             # Báo cáo XML và văn bản của Maven Surefire
├── .env.example                         # Chỉ chứa tên biến/giá trị mẫu, không có bí mật
└── .gitignore
```

`src/test/java` chứa các lớp kiểm thử. `src/main/java` chứa Page Object, cấu hình và tiện ích có thể tái sử dụng. Maven Surefire tạo `target/surefire-reports/`; thư mục này sẽ bị xóa và tạo lại khi chạy `mvn clean`. `screenshots/` lưu ảnh khi test thất bại (nếu an toàn) và ảnh system-test được chụp sau assertion thành công. `reports/test-execution.log` lưu kết quả kiểm thử cục bộ.

## Yêu cầu và thiết lập

- JDK 25 trở lên (`java -version`).
- Maven 3.9+ được cài đặt và có trong `PATH` (`mvn -version`). Maven đã có sẵn trên máy ảo Ubuntu của GitHub-hosted runners; quy trình CI không cần cài Maven riêng.
- Cài Google Chrome để chạy cục bộ.
- Có kết nối mạng tới MobileCity và, trong lần chạy đầu, tới các địa chỉ Selenium Manager dùng để tải/tìm ChromeDriver.

Selenium Manager đi kèm Selenium và thường tự chọn/tải ChromeDriver tương thích. Thông thường không cần cài `chromedriver` riêng. Không tắt bảo mật trình duyệt hoặc vượt cơ chế chống bot của trang web để làm cho bài kiểm thử chạy qua.

Có thể cung cấp cấu hình tùy chọn bằng thuộc tính Maven hoặc biến môi trường; thuộc tính Maven được ưu tiên:

| Thuộc tính Maven | Biến môi trường | Mặc định |
| --- | --- | --- |
| `mobilecity.baseUrl` | `MOBILECITY_BASE_URL` | `https://mobilecity.vn/` |
| `mobilecity.headless` | `MOBILECITY_HEADLESS` | `true` |
| `mobilecity.waitSeconds` | `MOBILECITY_WAIT_SECONDS` | `15` |
| `mobilecity.screenshotDir` | `MOBILECITY_SCREENSHOT_DIR` | `screenshots` |
| `mobilecity.reportDir` | `MOBILECITY_REPORT_DIR` | `reports` |
| `mobilecity.keepBrowserOpenSeconds` | `MOBILECITY_KEEP_BROWSER_OPEN_SECONDS` | `0` |
| `mobilecity.cartChromeProfileDir` | `MOBILECITY_CART_CHROME_PROFILE_DIR` | Không bật |
| `mobilecity.chromeDebuggerAddress` | `MOBILECITY_CHROME_DEBUGGER_ADDRESS` | Không bật |

Kiểm thử giỏ hàng đọc riêng hai biến môi trường `MOBILECITY_USERNAME` và `MOBILECITY_PASSWORD`. Workflow dùng GitHub Secrets cùng tên; nếu secrets vắng mặt hoặc PR đến từ fork không được cấp secrets, test giỏ được ghi `BLOCKED` (Surefire kỹ thuật có thể biểu diễn assumption-abort là skipped), không giả thành `PASS`. Không truyền thông tin đăng nhập bằng tham số Maven, không lưu chúng trong `.env`, dữ liệu kiểm thử, mã nguồn, README hoặc nhật ký.

Mặc định test giỏ vẫn đăng nhập mới ở mỗi lần chạy. Để lưu phiên đăng nhập qua các lần chạy cục bộ, hãy đặt `MOBILECITY_CART_CHROME_PROFILE_DIR` tới một thư mục riêng cho Selenium (không dùng thư mục Chrome cá nhân), ví dụ `.runtime/mobilecity-cart-profile`. Lần chạy đầu cần `MOBILECITY_USERNAME` và `MOBILECITY_PASSWORD`; những lần sau test sẽ tái sử dụng phiên nếu website còn đăng nhập, và chỉ cần credentials lại khi phiên hết hạn. Thư mục `.runtime/` được Git bỏ qua và không bị xóa bởi `mvn clean`. Profile chứa cookie/thông tin xác thực của website: không chia sẻ hoặc commit thư mục này, không chạy đồng thời nhiều Chrome/test dùng chung profile, và logout/xóa profile khi không còn cần. Test thông thường không dùng profile này và vẫn xóa phiên trình duyệt như trước.

Để test giỏ thao tác ngay trong một cửa sổ Chrome bạn mở (thay vì để ChromeDriver tự tạo cửa sổ khác), phải mở Chrome với cổng remote debugging rồi cấu hình `MOBILECITY_CHROME_DEBUGGER_ADDRESS=127.0.0.1:9222` trong cùng cửa sổ PowerShell chạy Maven. Chrome hiện tại cần được đóng hết trước khi mở lại bằng lệnh dưới đây; Chrome được kết nối sẽ không bị test đóng hay xóa cookie:

```powershell
$chrome = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
$profile = (Join-Path (Get-Location).Path ".runtime\mobilecity-cart-profile")
Start-Process -FilePath $chrome -ArgumentList @("--remote-debugging-port=9222", "--user-data-dir=`"$profile`"", "https://mobilecity.vn/")
```

Sau khi lệnh trên mở Chrome và bạn xác nhận đã đăng nhập MobileCity, chạy test trong cùng thư mục dự án, trong một cửa sổ PowerShell khác:

```powershell
$env:MOBILECITY_CHROME_DEBUGGER_ADDRESS = "127.0.0.1:9222"
mvn "-Dtest=CartTest" "-Dmobilecity.headless=false" test
```

Test sẽ thao tác trên tab Chrome đã kết nối; sau khi chạy xong Chrome vẫn mở. Đóng mọi cửa sổ Chrome trước khi khởi chạy bằng remote debugging để chắc chắn cổng 9222 và profile được áp dụng. Chỉ bật cổng này trên máy tin cậy; không mở cổng remote debugging ra mạng.

## Mở dự án bằng IntelliJ IDEA hoặc Eclipse

1. Mở/nhập thư mục này (`mobilecity-selenium`) dưới dạng một dự án Maven hiện có.
2. Chọn JDK 25+ cho dự án và Maven importer.
3. Cho phép Maven tải các phụ thuộc từ `pom.xml`.
4. Chạy một lớp kiểm thử trong `src/test/java` hoặc sử dụng các lệnh Maven bên dưới.

Trong IntelliJ IDEA, chọn **File → Open** rồi chọn thư mục này hoặc `pom.xml`. Trong Eclipse, chọn **File → Import → Existing Maven Projects**, chọn thư mục dự án rồi hoàn tất.

## Chạy kiểm thử trên máy

Chạy toàn bộ bộ kiểm thử tự động đã được triển khai từ thư mục dự án:

```powershell
mvn clean test
```

Chạy một lớp kiểm thử:

```powershell
mvn -Dtest=HomeTest test
```

Để chạy test giỏ hàng trong PowerShell, nhập tài khoản khi được nhắc. Mật khẩu được nhập ẩn, biến môi trường sẽ bị xóa sau khi Maven kết thúc:

```powershell
$env:MOBILECITY_CART_CHROME_PROFILE_DIR = ".runtime/mobilecity-cart-profile"
$env:MOBILECITY_USERNAME = Read-Host "Tên đăng nhập / email / số điện thoại"
$securePassword = Read-Host "Mật khẩu" -AsSecureString
$passwordPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
try {
    $env:MOBILECITY_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($passwordPointer)
    mvn "-Dtest=CartTest" "-Dmobilecity.headless=false" test
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($passwordPointer)
    Remove-Item Env:MOBILECITY_USERNAME -ErrorAction SilentlyContinue
    Remove-Item Env:MOBILECITY_PASSWORD -ErrorAction SilentlyContinue
    $securePassword.Dispose()
}
```

Sau lần đăng nhập thành công đầu tiên, có thể bỏ bước nhập credentials ở các lần chạy sau nếu phiên trong profile còn hiệu lực:

```powershell
$env:MOBILECITY_CART_CHROME_PROFILE_DIR = ".runtime/mobilecity-cart-profile"
mvn "-Dtest=CartTest" "-Dmobilecity.headless=false" test
```

Test giỏ tìm liên kết hiển thị sau đăng nhập, không tự đoán URL. Nếu trang yêu cầu CAPTCHA/OTP hoặc thiếu nút cập nhật đã nhận diện, test dừng với `BLOCKED` và không thay đổi giỏ. Khi tự động tăng số lượng, test chờ xác nhận giao diện, tải lại giỏ để kiểm tra số lượng đã lưu, sau đó thử khôi phục và tải lại để xác nhận giá trị gốc. Ảnh chụp bị tắt cho các test đăng nhập/giỏ để tránh lưu thông tin tài khoản hoặc dữ liệu giỏ riêng tư; mọi test khác vẫn chụp khi thất bại nếu WebDriver hỗ trợ.

Một số lệnh khác:

```powershell
mvn -Dtest=SearchTest test
mvn test -Dmobilecity.headless=false
mvn test -Dmobilecity.baseUrl=https://mobilecity.vn/
```

Muốn dùng **một cửa sổ Chrome** xuyên suốt bộ test và giữ trang cuối mở thêm 60 giây sau khi chạy xong:

```powershell
mvn "-Dmobilecity.headless=false" "-Dmobilecity.keepBrowserOpenSeconds=60" --batch-mode --no-transfer-progress clean test
```

Trong lúc chạy, URL vẫn đổi vì mỗi test mở trang cần kiểm tra, nhưng các test sẽ dùng lại cùng cửa sổ Chrome. Khi suite kết thúc, trình duyệt giữ trang cuối trong số giây đã đặt rồi tự đóng. Có thể đổi `60` thành `0`–`300`; mặc định `0` giữ hành vi đóng Chrome như trước. Surefire được cấu hình chờ đủ lâu cho thời gian giữ tối đa.

`mvn clean test` xóa kết quả Maven cũ trong `target/`, sau đó biên dịch và chạy bộ kiểm thử. Lệnh này không thể khiến một trang không truy cập được hoặc một bài kiểm thử bị chặn trở thành thành công. Hãy kiểm tra báo cáo Surefire và nhật ký sau mỗi lần chạy.

## Xem kết quả và ảnh chụp

- **Báo cáo Surefire:** `target/surefire-reports/` (`TEST-*.xml` và `*.txt`).
- **Nhật ký chạy cục bộ:** `reports/test-execution.log`.
- **Ảnh chụp khi thất bại:** `screenshots/`.
- **Bằng chứng GitHub Actions:** mở lần chạy workflow và tải artifact `mobilecity-test-results-*`. Artifact bao gồm báo cáo Surefire, nhật ký chạy và mọi ảnh chụp đã được tạo.

Một bài kiểm thử giỏ hàng bị JUnit hủy sẽ được ghi là bỏ qua trong Surefire và phân loại là `BLOCKED` trong sổ theo dõi dự án. Việc thiếu tệp artifact hoặc ảnh chụp không chứng minh bài kiểm thử thành công. Khi cập nhật hồ sơ dự án, hãy lưu cùng nhau Test Run ID, môi trường, phạm vi chính xác, kết quả và bằng chứng.

Các tệp văn bản trong run dùng UTF-8: `.editorconfig` đặt UTF-8 cho tệp văn bản, Maven được cấu hình qua `.mvn/jvm.config`, JVM và báo cáo Surefire được cấu hình riêng trong `pom.xml`, và `EvidenceWriter` ghi log bằng `StandardCharsets.UTF_8`. Kiểm thử hồi quy `EvidenceWriterTest` đọc lại nội dung tiếng Việt. Trên GitHub Actions, validator hiện quét nội dung văn bản và XML trong các báo cáo, tài liệu thuộc kho mã; các hồ sơ bàn giao bên ngoài thư mục kho không nằm trong phạm vi quét của CI. Nếu phát hiện lỗi mã hóa, workflow sẽ thất bại nhưng vẫn tải lên artifact kiểm thử để hỗ trợ điều tra. Khi chạy cục bộ, thực hiện validator sau Maven để kiểm tra kết quả:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate_run_documents.ps1 -Directory .
```

Khi xem log trên Windows, mở bằng công cụ hỗ trợ UTF-8 hoặc đặt terminal ở UTF-8; không chuyển mã file sang ANSI.

Các hồ sơ TestPlan/Run được tạo ngoài Maven không tự động nhận cấu hình mã hóa JVM. Khi tạo chúng bằng PowerShell, dùng `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))` hoặc `[System.IO.File]::WriteAllLines(..., [System.Text.UTF8Encoding]::new($false))`; không chuyển chuỗi UTF-8 qua code page ANSI. Đặt hồ sơ trong kho để validator tự động quét ở CI, hoặc chạy validator trên đúng thư mục hồ sơ trước khi phát hành, ví dụ `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validate_run_documents.ps1 -Directory "<thư_mục_run>"`. Validator đọc UTF-8 ở chế độ nghiêm ngặt, quét nội dung text và phần XML trong DOCX/XLSX, đồng thời trả mã lỗi khác 0 nếu phát hiện byte không hợp lệ, mojibake hoặc dấu `?` thay thế nằm giữa ký tự chữ; không phát hành run nếu bước này thất bại.

## Kho GitHub và đẩy thay đổi

Kho mã nguồn là [dotuananh0206-sudo/mobilecity-selenium](https://github.com/dotuananh0206-sudo/mobilecity-selenium). Thư mục dự án này là thư mục gốc của kho. Không khởi tạo hoặc đẩy thư mục bài tập cha lên kho: các workbook nội bộ, báo cáo, ảnh chụp cũ và thông tin cá nhân không thuộc kho mã nguồn công khai.

Xem lại và đẩy thay đổi từ thư mục này:

```powershell
git status --short --branch
git add .github src pom.xml README.md .gitignore .env.example
git status --short
git commit -m "Describe the reviewed change"
git push
```

Trước khi commit, kiểm tra danh sách tệp đã stage để chắc chắn chỉ chứa mã nguồn/cấu hình/tài liệu dự kiến. Nếu kho từ xa có commit mới, hãy fetch và hòa giải lịch sử trước khi đẩy. Không tùy tiện force-push hoặc ghi đè lịch sử từ xa. Không commit `.env`, thông tin xác thực, kết quả `target/` được tạo tự động, ảnh chụp hoặc báo cáo cục bộ.

## GitHub Actions và artifact

Tệp workflow: `.github/workflows/selenium-test.yml`.

- Chạy khi có push lên `main` và pull request nhắm tới `main`.
- Hỗ trợ chạy thủ công bằng `workflow_dispatch`.
- Sử dụng máy ảo `ubuntu-latest` do GitHub cung cấp, Temurin Java 25 và Chrome stable.
- Chạy `mvn --batch-mode --no-transfer-progress clean test`.
- Giới hạn thời gian mỗi job là 20 phút.
- Tải báo cáo Surefire, nhật ký và ảnh chụp lên artifact `mobilecity-test-results-*`, kể cả khi Maven test hoặc kiểm tra UTF-8 thất bại.
- Kết quả Maven khác 0 sẽ làm workflow thất bại; tải artifact không biến một lần chạy thất bại thành thành công.

GitHub Actions chạy trên máy ảo của GitHub; nó **không** chạy bên trong trang kho mã hoặc IDE cục bộ của bạn. Để xem một lần chạy, mở tab **Actions** của kho, chọn **MobileCity Selenium Tests**, rồi mở lần chạy tương ứng với commit cần xem. Để tải bằng chứng, mở **Summary** của lần chạy đã hoàn tất và tải artifact. Artifact được lưu trong 14 ngày; hãy tải xuống trước khi hết hạn nếu cần dùng cho báo cáo.

Lịch sử CI đã được xác minh trước khi thay đổi phạm vi:

- [Lần chạy #1](https://github.com/dotuananh0206-sudo/mobilecity-selenium/actions/runs/38047040851): **FAIL**, 4 lỗi kiểm thử, 2 lỗi thực thi, 1 bài bị chặn/bỏ qua trong 7 phương thức đã triển khai; artifact `mobilecity-test-results-1`.
- [Lần chạy #2](https://github.com/dotuananh0206-sudo/mobilecity-selenium/actions/runs/38047533363): **FAIL**, 4 lỗi kiểm thử, 2 lỗi thực thi, 1 bài bị chặn/bỏ qua trong 7 phương thức đã triển khai; artifact `mobilecity-test-results-2`.
- [Lần chạy #3](https://github.com/dotuananh0206-sudo/mobilecity-selenium/actions/runs/38049266948): **FAIL**, 4 lỗi kiểm thử, 2 lỗi thực thi, 1 bài bị chặn/bỏ qua trong 7 phương thức; artifact `mobilecity-test-results-3`.

Các lần chạy CI và browser test nêu trên là lịch sử, có thể không phản ánh trạng thái hiện tại của website. Lần chạy local đầy đủ được ghi nhận là `MC-20261031-100139`: 33 test JUnit, **32 PASS / 0 FAIL / 0 ERROR / 1 BLOCKED** (18 unit test PASS; 14 kiểm thử trình duyệt PASS; `TC-CART-001` BLOCKED do thiếu credentials). Trong 21 case hộp đen, 8 PASS, 1 BLOCKED và 12 NOT EXECUTED. Lần chạy lịch sử này dùng Java 17 và không chứng minh hành vi giỏ hàng hoặc website hiện không có lỗi. Sau khi nâng cấp runtime, 18 unit test được xác minh trên Temurin Java 25; full browser suite chưa chạy lại trên Java 25. Kết quả mới nhất cần được xác nhận qua lần chạy CI tương ứng với commit được push.

## Sự cố thường gặp

| Hiện tượng | Cần kiểm tra |
| --- | --- |
| Không nhận diện được `mvn` hoặc `java` | Cài JDK 25+ và Maven 3.9+, thêm chúng vào `PATH`, mở lại terminal rồi kiểm tra `java -version` / `mvn -version`. |
| Selenium Manager không tìm thấy/tải được ChromeDriver | Xác nhận Chrome đã cài và mạng/proxy cho phép Selenium Manager tải xuống. Đọc lỗi Selenium/Maven; không thay bằng tệp driver chưa được xác minh. |
| Chrome không khởi động trong môi trường headless cục bộ | Xác nhận Chrome đã cài và cập nhật; thử `mvn test -Dmobilecity.headless=false` để quan sát trình duyệt. Không thêm cờ trình duyệt thiếu an toàn khi chưa hiểu tác động. |
| Chờ phần tử hết thời gian hoặc không thấy thành phần | Kiểm tra ảnh chụp, XML Surefire và trang/DOM thực tế. Trang có thể đã thay đổi hoặc trả về chuyển hướng/trang thử thách. Chỉ cập nhật bộ chọn dựa trên bằng chứng DOM quan sát được. |
| CAPTCHA, thử thách chống bot, hạn chế truy cập | Dừng tương tác và ghi trường hợp đó là `BLOCKED` hoặc `NOT EXECUTED`; tuyệt đối không tìm cách vượt cơ chế kiểm soát. |
| Kiểm thử cục bộ thành công nhưng GitHub Actions thất bại | So sánh thông tin trình duyệt/runtime, commit chính xác, ảnh chụp CI và báo cáo Surefire. Thành công cục bộ không chứng minh CI hoặc trang web chạy thành công trong môi trường khác. |
| Một bài kiểm thử bị bỏ qua | Kiểm tra XML/văn bản Surefire và nhật ký chạy. Bài kiểm thử giỏ hàng chủ động hủy nếu không tìm thấy liên kết giỏ hàng công khai; trạng thái là `BLOCKED`, không phải kiểm thử giỏ hàng thành công. |
| Không thấy ảnh chụp | Ảnh chụp được tạo khi test trình duyệt thất bại (nếu phiên còn hoạt động); các system test đã xác minh cũng chụp ảnh sau assertion. Hãy dùng báo cáo Surefire và nhật ký chạy làm bằng chứng bổ sung. |

## Lưu ý về kết quả đã xác minh

Kết quả chạy phụ thuộc vào thời điểm và môi trường. Hãy xem hồ sơ chạy đã được lưu trong dự án cùng báo cáo kiểm thử hiện tại để biết lần chạy mới nhất đã hoàn tất; không dùng lại kết quả `PASS` cũ làm kết quả của lần chạy mới. Không có kết quả kiểm thử nào trong tài liệu này chứng nhận MobileCity không có lỗi.
