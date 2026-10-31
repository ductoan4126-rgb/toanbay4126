package mobilecity.tests;

import mobilecity.base.BaseTest;
import mobilecity.config.TestConfig;
import mobilecity.pages.CartPage;
import mobilecity.pages.HomePage;
import mobilecity.pages.LoginPage;
import mobilecity.pages.LoginPage.LoginOutcome;
import mobilecity.utils.TestData;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@SuppressWarnings("JUnitTestClassNamingConvention")
class CartTest extends BaseTest {
    @Override
    protected String persistentChromeProfileDirectory() {
        return TestConfig.cartChromeProfileDirectory();
    }

    @Test
    @DisplayName("TC-CART-001 - Đăng nhập nếu cần, mở giỏ và tăng rồi khôi phục số lượng mặt hàng đầu tiên")
    void loginAndTemporarilyChangeFirstCartItemQuantity() {
        driver.get(TestData.url("login.url"));
        assumeNoSiteChallenge();
        LoginPage loginPage = new LoginPage(driver);
        if (!loginPage.isAuthenticated()) {
            String username = TestConfig.loginUsername();
            String password = TestConfig.loginPassword();
            Assumptions.assumeTrue(username != null && !username.isBlank()
                            && password != null && !password.isBlank(),
                    "BLOCKED: cần đăng nhập trước hoặc đặt MOBILECITY_USERNAME và MOBILECITY_PASSWORD");

            LoginOutcome loginOutcome = loginPage.login(username, password);
            Assumptions.assumeFalse(loginOutcome == LoginOutcome.VERIFICATION_REQUIRED,
                    "BLOCKED: website yêu cầu CAPTCHA/OTP/xác minh; cần xử lý thủ công");
            assertEquals(LoginOutcome.AUTHENTICATED, loginOutcome,
                    loginOutcome == LoginOutcome.INVALID_CREDENTIALS
                            ? "Website từ chối thông tin đăng nhập đã cung cấp."
                            : "Không xác minh được đăng nhập thành công do lỗi kỹ thuật hoặc thiếu dấu hiệu xác nhận.");
        }
        assumeNoSiteChallenge();

        HomePage homePage = new HomePage(driver);
        Assumptions.assumeTrue(homePage.hasPublishedCartLink(),
                "BLOCKED: không thấy liên kết giỏ hàng sau đăng nhập; không đoán URL");
        homePage.openPublishedCartLink();
        assumeNoSiteChallenge();
        CartPage cartPage = new CartPage(driver);
        Assumptions.assumeTrue(cartPage.hasCartPageLoadedFromPublishedLink(),
                "BLOCKED: liên kết chưa dẫn đến trang giỏ hàng có thể nhận diện");
        Assumptions.assumeTrue(cartPage.hasFirstItemQuantityControl(),
                "BLOCKED: không tìm thấy ô số lượng gắn với mặt hàng trong giỏ");
        Assumptions.assumeTrue(cartPage.hasFirstItemUpdateButton(),
                "BLOCKED: không tìm thấy nút cập nhật số lượng; không thay đổi giỏ hàng");

        cartPage.temporarilyIncreaseFirstItemQuantity();
        assertTrue(cartPage.hasCartPageLoadedFromPublishedLink(),
                "Cần ở lại trang giỏ hàng sau khi khôi phục số lượng ban đầu");
    }
}
