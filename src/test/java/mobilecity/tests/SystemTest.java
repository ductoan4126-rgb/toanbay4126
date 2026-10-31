package mobilecity.tests;

import mobilecity.base.BaseTest;
import mobilecity.pages.HomePage;
import mobilecity.pages.ProductPage;
import mobilecity.pages.SearchPage;
import mobilecity.utils.EvidenceWriter;
import mobilecity.utils.TestData;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SystemTest extends BaseTest {
    @Test
    @DisplayName("SYS-001 - Tìm kiếm sản phẩm và mở đúng trang chi tiết")
    void searchAndOpenMatchingProductDetails() throws IOException {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();
        SearchPage searchPage = homePage.searchPage()
                .submitTerm(TestData.required("search.sample"));
        assumeNoSiteChallenge();

        assertTrue(searchPage.hasResultsHeading(), "Cần hiển thị trang kết quả tìm kiếm");
        assertTrue(searchPage.hasProductResultMatching(TestData.required("search.sample")),
                "Danh sách cần có sản phẩm khớp từ khóa");
        String selectedProduct = searchPage.firstResultName();
        assertFalse(selectedProduct.isBlank(), "Sản phẩm được chọn cần có tên");

        searchPage.openFirstResult();
        assumeNoSiteChallenge();
        ProductPage productPage = new ProductPage(driver);
        assertTrue(productPage.hasProductDetails(), "Cần mở được trang chi tiết sản phẩm");
        assertTrue(productPage.productHeading().toLowerCase()
                        .contains(selectedProduct.toLowerCase()),
                "Tên sản phẩm ở trang chi tiết cần khớp kết quả đã chọn");
        captureEvidence("SYS-001-search-to-product-detail");
    }

    @Test
    @DisplayName("SYS-002 - Từ khóa không tồn tại hiển thị trạng thái không có kết quả")
    void unknownSearchTermShowsEmptyState() throws IOException {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();
        SearchPage searchPage = homePage.searchPage()
                .submitTerm(TestData.required("search.noMatch"));
        assumeNoSiteChallenge();

        assertTrue(searchPage.hasResultsHeading(), "Cần hiển thị trang kết quả tìm kiếm");
        assertTrue(searchPage.hasEmptyResultsMessage(),
                "Cần thông báo rõ khi không tìm thấy sản phẩm");
        captureEvidence("SYS-002-search-empty-state");
    }

    @Test
    @DisplayName("SYS-003 - Trang chi tiết vẫn hiển thị đúng sản phẩm sau khi tải lại")
    void productDetailsRemainAvailableAfterReload() throws IOException {
        driver.get(TestData.url("product.sample"));
        assumeNoSiteChallenge();
        ProductPage productPage = new ProductPage(driver);
        assertTrue(productPage.hasProductDetails(), "Trang sản phẩm cần hiển thị tiêu đề");
        String initialHeading = productPage.productHeading();
        assertFalse(initialHeading.isBlank(), "Tiêu đề sản phẩm không được để trống");
        assertTrue(productPage.productPrice().matches("(?s).*\\d.*"),
                "Trang chi tiết cần hiển thị giá có chữ số");

        driver.navigate().refresh();
        assumeNoSiteChallenge();
        ProductPage reloadedProductPage = new ProductPage(driver);
        assertTrue(reloadedProductPage.hasProductDetails(),
                "Trang chi tiết cần tải lại thành công");
        assertEquals(initialHeading, reloadedProductPage.productHeading(),
                "Sau khi tải lại vẫn phải hiển thị cùng sản phẩm");
        assertTrue(reloadedProductPage.productPrice().matches("(?s).*\\d.*"),
                "Sau khi tải lại giá vẫn phải được hiển thị");
        captureEvidence("SYS-003-product-detail-after-reload");
    }

    private void captureEvidence(String testId) throws IOException {
        Path screenshot = EvidenceWriter.screenshotPath(testId);
        Files.write(screenshot, ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES));
        EvidenceWriter.record(testId, "SCREENSHOT", screenshot.toAbsolutePath().toString());
    }
}
