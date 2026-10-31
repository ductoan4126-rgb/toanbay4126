package mobilecity.tests;

import mobilecity.base.BaseTest;
import mobilecity.pages.HomePage;
import mobilecity.pages.ProductPage;
import mobilecity.pages.SearchPage;
import mobilecity.utils.TestData;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class SearchTest extends BaseTest {
    @Test
    @DisplayName("TC-SEARCH-001 - Ô tìm kiếm hiển thị và chặn gửi khi để trống")
    void emptySearchInputIsRequired() {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();
        assertTrue(homePage.hasSearchInput(), "Trang công khai cần có ô tìm kiếm quan sát được");

        SearchPage searchPage = homePage.searchPage();
        assertTrue(searchPage.isEmptyInputRequired(),
                "Ô tìm kiếm bắt buộc không hợp lệ khi để trống");
    }

    @Test
    @DisplayName("TC-SEARCH-002 - Kết quả tìm kiếm phù hợp với từ khóa sản phẩm")
    void searchReturnsMatchingProducts() {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();
        SearchPage searchPage = homePage.searchPage()
                .submitTerm(TestData.required("search.sample"));
        assumeNoSiteChallenge();

        assertTrue(searchPage.hasResultsHeading(), "Trang tìm kiếm cần hiển thị tiêu đề kết quả");
        assertTrue(searchPage.hasProductResultMatching(TestData.required("search.sample")),
                "Ít nhất một sản phẩm trong kết quả cần khớp từ khóa");
    }

    @Test
    @DisplayName("TC-SEARCH-003 - Từ khóa không khớp hiển thị trạng thái rỗng")
    void searchShowsEmptyStateForNoMatch() {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();
        SearchPage searchPage = homePage.searchPage()
                .submitTerm(TestData.required("search.noMatch"));
        assumeNoSiteChallenge();

        assertTrue(searchPage.hasResultsHeading(), "Trang tìm kiếm cần hiển thị tiêu đề kết quả");
        assertTrue(searchPage.hasEmptyResultsMessage(),
                "Trang cần nêu rõ khi không tìm thấy sản phẩm phù hợp");
    }

    @Test
    @DisplayName("TC-SEARCH-004 - Mở chi tiết sản phẩm từ kết quả tìm kiếm")
    void searchResultOpensProductDetails() {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();
        SearchPage searchPage = homePage.searchPage()
                .submitTerm(TestData.required("search.sample"));
        assumeNoSiteChallenge();
        String resultName = searchPage.firstResultName();
        searchPage.openFirstResult();
        assumeNoSiteChallenge();
        ProductPage productPage = new ProductPage(driver);

        assertTrue(productPage.hasProductDetails(), "Liên kết kết quả cần mở trang chi tiết");
        assertTrue(productPage.productHeading().toLowerCase().contains(resultName.toLowerCase()),
                "Tên trên trang chi tiết cần khớp kết quả đã chọn");
    }
}
