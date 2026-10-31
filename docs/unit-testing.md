# Unit test JUnit 5 — cấu hình kiểm thử

## 1. Module được chọn và ranh giới kiểm thử

Website `mobilecity.vn` là hệ thống bên ngoài; dự án này **không có mã nguồn backend MobileCity** và không có quyền truy cập logic nội bộ của website. Bộ unit test dưới đây chỉ kiểm thử mã do dự án Selenium phát triển: lớp cấu hình `mobilecity.config.TestConfig`, không mở Chrome, không gửi HTTP và không kết nối website.

Hai phương thức nghiệp vụ/cấu hình được kiểm thử trực tiếp:

- `TestConfig.waitTimeout()`: đọc số giây, phân tích số nguyên, áp dụng miền hợp lệ `[1, 120]`, ném lỗi với giá trị ngoài miền/không phải số.
- `TestConfig.keepBrowserOpenSeconds()`: đọc số giây, phân tích số nguyên, áp dụng miền hợp lệ `[0, 300]`, ném lỗi với giá trị ngoài miền/không phải số.

`resolveValue(systemValue, environmentValue, fallback)` là phép phân giải ưu tiên nguồn cấu hình được tách thành hàm thuần package-private để có thể kiểm tra đầy đủ các nhánh một cách xác định mà không phải sửa biến môi trường toàn tiến trình. Luồng đọc giá trị vẫn giữ nguyên thứ tự property → environment → fallback và hành vi trim trước đây.

### Mã phương thức phân tích: `waitTimeout()`

Mã nguồn tại `src/main/java/mobilecity/config/TestConfig.java`:

```java
public static Duration waitTimeout() {
    String configured = value("mobilecity.waitSeconds", "MOBILECITY_WAIT_SECONDS", "15");
    try {
        long seconds = Long.parseLong(configured);
        if (seconds < 1 || seconds > 120) {
            throw new IllegalArgumentException("mobilecity.waitSeconds must be between 1 and 120");
        }
        return Duration.ofSeconds(seconds);
    } catch (NumberFormatException e) {
        throw new IllegalArgumentException("mobilecity.waitSeconds must be an integer", e);
    }
}
```

#### Câu lệnh, điều kiện và CFG

| Nút | Lệnh/điều kiện |
|---|---|
| N1 | Lấy cấu hình có thứ tự ưu tiên từ property/environment/mặc định. |
| N2 | Phân tích `configured` thành `long seconds`. |
| N3 | Điều kiện thứ nhất: `seconds < 1`? |
| N4 | Nếu N3 false, điều kiện thứ hai: `seconds > 120`? |
| N5 | Ném `IllegalArgumentException` nếu nằm ngoài `[1, 120]`. |
| N6 | Trả `Duration.ofSeconds(seconds)` nếu hợp lệ. |
| N7 | Bắt `NumberFormatException` khi chuỗi không phải số nguyên. |
| N8 | Ném `IllegalArgumentException` loại dữ liệu, giữ exception gốc làm cause. |

```text
                         ┌──────────────┐
                         │ N1: đọc cấu hình │
                         └──────┬───────┘
                                v
                         ┌──────────────┐
                         │ N2: parse long│
                         └───┬──────┬───┘
                        hợp lệ    NumberFormatException
                            v              v
                    ┌──────────────┐   ┌──────────────┐
                    │ N3: seconds<1│   │ N7: catch    │
                    └──┬────────┬──┘   └──────┬───────┘
                    True       False           v
                      v          v       ┌──────────────┐
                 ┌────────┐ ┌──────────────┐│ N8: throw loại │
                 │ N5 throw│ │ N4: seconds>120│└──────────────┘
                 └────────┘ └──┬────────┬──┘
                              True       False
                                v          v
                           ┌────────┐ ┌──────────────┐
                           │ N5 throw│ │ N6: return   │
                           └────────┘ └──────────────┘
```

- N3 true: giá trị nhỏ hơn 1, như `0`.
- N3 false, N4 true: giá trị lớn hơn 120, như `121`.
- N3 false, N4 false: giá trị thuộc miền `[1, 120]`, bao gồm cả hai biên.
- Parse thất bại: không có giá trị số để xét biên; đi qua catch và ném lỗi cấu hình.
- Các đường cơ sở độc lập: chuỗi hợp lệ trong miền; chuỗi số thấp hơn miền; chuỗi số cao hơn miền; chuỗi không parse được.

## 2. Test case JUnit 5

Mã nguồn test: `src/test/java/mobilecity/config/TestConfigTest.java`. Mỗi test chỉ thay đổi system property cần thiết và khôi phục giá trị trước đó sau test, do đó độc lập với thứ tự chạy. Không dùng Mockito vì module được kiểm tra không có phụ thuộc cần mock.

| Unit Test ID | Phương thức | Điều kiện kiểm tra | Nhánh/đường đi | Kết quả mong đợi |
|---|---|---|---|---|
| UT-CONFIG-01 | `waitTimeout()` | Số giây hợp lệ bên trong miền: `15`. | N1 → N2 → N3 false → N4 false → N6. | `Duration.ofSeconds(15)`. |
| UT-CONFIG-02 | `waitTimeout()` | Biên dưới hợp lệ: `1`. | N1 → N2 → N3 false → N4 false → N6. | `Duration.ofSeconds(1)`. |
| UT-CONFIG-03 | `waitTimeout()` | Biên trên hợp lệ: `120`. | N1 → N2 → N3 false → N4 false → N6. | `Duration.ofSeconds(120)`. |
| UT-CONFIG-04 | `waitTimeout()` | Ngay dưới miền hợp lệ: `0`. | N1 → N2 → N3 true → N5. | Ném `IllegalArgumentException` với thông báo miền `[1, 120]`. |
| UT-CONFIG-05 | `waitTimeout()` | Ngay trên miền hợp lệ: `121`. | N1 → N2 → N3 false → N4 true → N5. | Ném `IllegalArgumentException` với thông báo miền `[1, 120]`. |
| UT-CONFIG-06 | `waitTimeout()` | Chuỗi không phải số nguyên: `many`. | N1 → N2 phát sinh `NumberFormatException` → N7 → N8. | Ném `IllegalArgumentException` loại dữ liệu; cause khác null. |
| UT-CONFIG-07 | `keepBrowserOpenSeconds()` | Số giây hợp lệ bên trong miền: `60`. | Parse → điều kiện dưới miền false → trên miền false → return. | Trả về `60`. |
| UT-CONFIG-08 | `keepBrowserOpenSeconds()` | Biên dưới: `0`. | Parse → dưới miền false → trên miền false → return. | Trả về `0`. |
| UT-CONFIG-09 | `keepBrowserOpenSeconds()` | Biên trên: `300`. | Parse → dưới miền false → trên miền false → return. | Trả về `300`. |
| UT-CONFIG-10 | `keepBrowserOpenSeconds()` | Ngay dưới miền: `-1`. | Parse → điều kiện `seconds < 0` true → throw. | Ném `IllegalArgumentException` với thông báo miền `[0, 300]`. |
| UT-CONFIG-11 | `keepBrowserOpenSeconds()` | Ngay trên miền: `301`. | Parse → dưới miền false → điều kiện `seconds > 300` true → throw. | Ném `IllegalArgumentException` với thông báo miền `[0, 300]`. |
| UT-CONFIG-12 | `keepBrowserOpenSeconds()` | Chuỗi không phải số nguyên: `later`. | Parse phát sinh `NumberFormatException` → catch → throw cấu hình. | Ném `IllegalArgumentException` loại dữ liệu; cause khác null. |
| UT-CONFIG-13 | `resolveValue(...)` | System property khác null và không blank; environment cũng có giá trị. | Điều kiện property true. | Dùng property sau trim, ưu tiên hơn environment. |
| UT-CONFIG-14 | `resolveValue(...)` | Property blank, environment khác blank. | Property false → environment null false → environment blank false. | Dùng environment sau trim. |
| UT-CONFIG-15 | `resolveValue(...)` | Property null, environment null. | Property false → điều kiện environment null true. | Dùng fallback. |
| UT-CONFIG-16 | `resolveValue(...)` | Property rỗng, environment blank. | Property false → environment null false → environment blank true. | Dùng fallback. |

### Liên kết test với câu lệnh và nhánh

| Câu lệnh/nhánh | Unit Test ID bao phủ |
|---|---|
| `waitTimeout`: đọc cấu hình, parse thành công, return `Duration` | UT-CONFIG-01, 02, 03 |
| `waitTimeout`: nhánh `seconds < 1` false | UT-CONFIG-01, 02, 03, 05 |
| `waitTimeout`: nhánh `seconds < 1` true | UT-CONFIG-04 |
| `waitTimeout`: nhánh `seconds > 120` false | UT-CONFIG-01, 02, 03 |
| `waitTimeout`: nhánh `seconds > 120` true | UT-CONFIG-05 |
| `waitTimeout`: bắt parse exception và tạo lỗi có cause | UT-CONFIG-06 |
| `keepBrowserOpenSeconds`: đọc, parse, return | UT-CONFIG-07, 08, 09 |
| `keepBrowserOpenSeconds`: điều kiện `< 0` false/true | UT-CONFIG-07, 08, 09, 11 / UT-CONFIG-10 |
| `keepBrowserOpenSeconds`: điều kiện `> 300` false/true | UT-CONFIG-07, 08, 09 / UT-CONFIG-11 |
| `keepBrowserOpenSeconds`: bắt parse exception và tạo lỗi có cause | UT-CONFIG-12 |
| `resolveValue`: ưu tiên property true/false | UT-CONFIG-13 / UT-CONFIG-14, 15, 16 |
| `resolveValue`: environment null/blank/nonblank | UT-CONFIG-15 / UT-CONFIG-16 / UT-CONFIG-14 |
| `resolveValue`: return fallback | UT-CONFIG-15, UT-CONFIG-16 |

## 3. Coverage và thực thi

JaCoCo được cấu hình trong Maven và giới hạn báo cáo vào `mobilecity/config/TestConfig*`. Điều này đo coverage cho mã cấu hình được unit test, không trộn kết quả với Selenium UI tests. Báo cáo HTML: [target/site/jacoco/index.html](../target/site/jacoco/index.html); dữ liệu XML: `target/site/jacoco/jacoco.xml`.

Chạy riêng lớp unit test và tạo báo cáo coverage:

```powershell
mvn -Dtest=TestConfigTest verify
```

Không dùng `mvn clean verify` để lấy báo cáo riêng unit test vì lệnh đó sẽ chạy toàn bộ Selenium test. Surefire XML cho test này nằm tại `target/surefire-reports/TEST-mobilecity.config.TestConfigTest.xml`.

### Kết quả thực thi

| Chỉ số | Kết quả |
|---|---|
| Thời điểm chạy | 31/10/2026, baseline full suite lúc 10:01–10:04 (UTC+7) |
| Môi trường chạy | Windows 11 x64; Microsoft OpenJDK 17.0.21.0.2; Maven 3.9.9; JUnit 5.11.4 |
| Lệnh | `mvn --batch-mode --no-transfer-progress clean verify` |
| Unit test `TestConfigTest` | 16 |
| Unit test hỗ trợ `EvidenceWriterTest` | 2 |
| Tổng số unit test đã chạy | 18 |
| PASS | 18 |
| FAIL | 0 |
| ERROR | 0 |
| BLOCKED | 0 |
| Thời lượng unit tests | 0.190 giây theo Surefire (0.125 giây + 0.065 giây) |

Hai unit test tiện ích được chạy bổ sung trong cùng build:

| Unit Test ID | Phương thức | Kết quả | Trạng thái |
|---|---|---|---|
| UT-EVIDENCE-01 | `writesVietnameseEvidenceAsUtf8` | Nhật ký UTF-8 giữ nguyên tiếng Việt, không có ký tự thay thế. | PASS |
| UT-EVIDENCE-02 | `redactsCredentialLikeValuesFromEvidence` | Giá trị username/password/token/Bearer không xuất hiện trong nhật ký; marker redaction được ghi. | PASS |

Kết quả từng test (đọc từ [Surefire XML](../target/surefire-reports/TEST-mobilecity.config.TestConfigTest.xml)):

| Unit Test ID | Phương thức JUnit | Actual Result | Status |
|---|---|---|---|
| UT-CONFIG-01 | `waitTimeoutAcceptsInteriorValue` | Trả về `Duration.ofSeconds(15)`. | PASS |
| UT-CONFIG-02 | `waitTimeoutAcceptsLowerBoundary` | Trả về `Duration.ofSeconds(1)`. | PASS |
| UT-CONFIG-03 | `waitTimeoutAcceptsUpperBoundary` | Trả về `Duration.ofSeconds(120)`. | PASS |
| UT-CONFIG-04 | `waitTimeoutRejectsValueBelowLowerBoundary` | Ném `IllegalArgumentException` đúng thông báo miền `[1, 120]`. | PASS |
| UT-CONFIG-05 | `waitTimeoutRejectsValueAboveUpperBoundary` | Ném `IllegalArgumentException` đúng thông báo miền `[1, 120]`. | PASS |
| UT-CONFIG-06 | `waitTimeoutRejectsNonIntegerValue` | Ném lỗi loại số nguyên, cause được giữ lại. | PASS |
| UT-CONFIG-07 | `keepBrowserOpenAcceptsInteriorValue` | Trả về `60`. | PASS |
| UT-CONFIG-08 | `keepBrowserOpenAcceptsLowerBoundary` | Trả về `0`. | PASS |
| UT-CONFIG-09 | `keepBrowserOpenAcceptsUpperBoundary` | Trả về `300`. | PASS |
| UT-CONFIG-10 | `keepBrowserOpenRejectsValueBelowLowerBoundary` | Ném `IllegalArgumentException` đúng thông báo miền `[0, 300]`. | PASS |
| UT-CONFIG-11 | `keepBrowserOpenRejectsValueAboveUpperBoundary` | Ném `IllegalArgumentException` đúng thông báo miền `[0, 300]`. | PASS |
| UT-CONFIG-12 | `keepBrowserOpenRejectsNonIntegerValue` | Ném lỗi loại số nguyên, cause được giữ lại. | PASS |
| UT-CONFIG-13 | `resolveValuePrefersAndTrimsNonBlankSystemProperty` | Ưu tiên property và trim khoảng trắng. | PASS |
| UT-CONFIG-14 | `resolveValueUsesAndTrimsEnvironmentWhenSystemPropertyIsBlank` | Dùng environment và trim khoảng trắng. | PASS |
| UT-CONFIG-15 | `resolveValueUsesFallbackWhenEnvironmentIsNull` | Dùng fallback khi environment null. | PASS |
| UT-CONFIG-16 | `resolveValueUsesFallbackWhenEnvironmentIsBlank` | Dùng fallback khi environment blank. | PASS |

### Báo cáo JaCoCo

JaCoCo 0.8.12 chỉ đưa `mobilecity.config.TestConfig` vào báo cáo. Toàn class đạt 92.0% instruction, 94.6% line và 73.1% branch coverage; phần còn thiếu thuộc các getter khác chưa được kiểm thử. Ba phương thức trọng tâm đạt 100% instruction/line/branch coverage. Không được diễn giải các số liệu này thành coverage toàn dự án.

| Phạm vi | JaCoCo instructions | JaCoCo lines | Branches |
|---|---:|---:|---:|
| Toàn class `TestConfig` | 138/150 = **92.0%** | 35/37 = **94.6%** | 19/26 = **73.1%** |
| `waitTimeout()` | 31/31 = **100%** | 7/7 = **100%** | 4/4 = **100%** |
| `keepBrowserOpenSeconds()` | 27/27 = **100%** | 7/7 = **100%** | 4/4 = **100%** |
| `resolveValue(...)` | 18/18 = **100%** | 5/5 = **100%** | 8/8 = **100%** |

JaCoCo báo cáo instruction/line/branch coverage, không có bộ đếm source-statement riêng; instruction coverage được nêu đúng tên thay vì gắn nhãn sai là statement coverage. Mọi nhánh của các phương thức trọng tâm đã được thực thi. Các phương thức `TestConfig` ngoài phạm vi trên chưa được unit test trong lượt này.

Không thay thế số liệu coverage của unit test bằng coverage của Selenium. Nếu website hoặc môi trường CI không truy cập được, điều đó không ảnh hưởng tới unit test này vì test chỉ gọi logic Java cục bộ.
