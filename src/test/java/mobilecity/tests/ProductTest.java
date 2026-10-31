package mobilecity.tests;

import mobilecity.base.BaseTest;
import mobilecity.pages.HomePage;
import mobilecity.pages.ProductPage;
import mobilecity.utils.TestData;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

class ProductTest extends BaseTest {
    @Test
    @DisplayName("TC-HOME-003 - Danh mục hiển thị sản phẩm có tên và giá")
    void categoryShowsNamedProduct() {
        HomePage homePage = new HomePage(driver).open();
        assumeNoSiteChallenge();
        homePage.openPhoneCategory();
        assumeNoSiteChallenge();
        ProductPage products = new ProductPage(driver);

        assertTrue(products.firstListedProductName().length() > 0,
                "Danh mục cần hiển thị tên sản phẩm");
        assertTrue(products.firstListedProductPrice().matches("(?s).*\\d.*"),
                "Thẻ sản phẩm cần hiển thị giá nếu giá được công bố");
    }

    @Test
    @DisplayName("TC-PRODUCT-001 - Mở trang chi tiết từ danh mục")
    void listedProductOpensMatchingDetailPage() {
        driver.get(TestData.url("category.url"));
        assumeNoSiteChallenge();
        ProductPage products = new ProductPage(driver);
        String productName = products.firstListedProductName();
        products.openFirstListedProduct();
        assumeNoSiteChallenge();

        assertTrue(products.hasProductDetails(), "Trang sản phẩm cần hiển thị tiêu đề");
        assertTrue(products.productHeading().toLowerCase().contains(productName.toLowerCase()),
                "Tiêu đề chi tiết cần khớp sản phẩm được mở");
    }

    @Test
    @DisplayName("TC-PRODUCT-002 - Trang chi tiết hiển thị giá sản phẩm")
    void productDetailsShowPrice() {
        driver.get(TestData.url("product.sample"));
        assumeNoSiteChallenge();
        ProductPage productPage = new ProductPage(driver);

        assertTrue(productPage.productPrice().matches("(?s).*\\d.*"),
                "Trang chi tiết cần hiển thị giá nếu sản phẩm có giá công khai");
    }

    @Test
    @DisplayName("TC-PRODUCT-003 - Ảnh chính sản phẩm tải thành công")
    void productPrimaryImageIsLoaded() {
        driver.get(TestData.url("product.sample"));
        assumeNoSiteChallenge();
        ProductPage productPage = new ProductPage(driver);

        assertTrue(productPage.hasLoadedPrimaryImage(),
                "Ảnh chính của sản phẩm cần tải thành công");
    }

    @Test
    @DisplayName("TC-PRODUCT-004 - Trang chi tiết hiển thị phần thông số công khai")
    void productDetailsShowPublicSpecifications() {
        driver.get(TestData.url("product.sample"));
        assumeNoSiteChallenge();
        ProductPage productPage = new ProductPage(driver);

        assertTrue(productPage.hasProductDetails(),
                "Trang sản phẩm cần hiển thị tiêu đề trước khi kiểm tra thông số");
        assertTrue(productPage.hasSpecificationSection(),
                "Trang sản phẩm cần hiển thị phần thông số công khai");
    }
}
