package mobilecity.tests;

import mobilecity.base.BaseTest;
import mobilecity.pages.HomePage;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class HomeTest extends BaseTest {
    @Test
    @DisplayName("TC-HOME-001 - Trang chủ tải và hiển thị tiêu đề")
    void homepageLoadsWithTitle() {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();

        assertTrue(homePage.hasTitle(), "Trang chủ cần có tiêu đề trang");
        assertTrue(homePage.hasLogo(), "Trang chủ cần hiển thị logo MobileCity");
        assertTrue(homePage.hasPhoneCategoryLink(), "Trang chủ cần hiển thị liên kết danh mục Điện thoại");
    }

    @Test
    @DisplayName("TC-HOME-002 - Điều hướng từ trang chủ đến danh mục điện thoại")
    void homepageOpensPhoneCategory() {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();
        homePage.openPhoneCategory();
        assumeNoSiteChallenge();

        assertTrue(driver.getCurrentUrl().contains("/dien-thoai"),
                "Liên kết danh mục cần mở trang Điện thoại");
        assertTrue(driver.getTitle().toLowerCase().contains("điện thoại"),
                "Trang danh mục cần có tiêu đề phù hợp");
    }
}
