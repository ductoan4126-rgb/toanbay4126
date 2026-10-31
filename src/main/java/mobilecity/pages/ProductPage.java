package mobilecity.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

public final class ProductPage extends BasePage {
    private static final By PRODUCT_LINKS = By.cssSelector("p.name a[href$='.html']");
    private static final By PRODUCT_HEADING = By.cssSelector("h1");
    private static final By LISTED_PRODUCT_PRICE = By.cssSelector("div.product-list-item .price");
    private static final By PRODUCT_PRICE = By.cssSelector(".product-price-box .price");
    private static final By PRIMARY_PRODUCT_IMAGE = By.cssSelector("ul.product_image img");
    public ProductPage(WebDriver driver) {
        super(driver);
    }

    public String firstListedProductName() {
        String text = visible(PRODUCT_LINKS).getText().trim();
        if (text.isBlank()) {
            throw new IllegalStateException("The first listed product link has no visible name");
        }
        return text;
    }

    public String firstListedProductPrice() {
        return visible(LISTED_PRODUCT_PRICE).getText().trim();
    }

    public void openFirstListedProduct() {
        clickable(PRODUCT_LINKS).click();
    }

    public boolean hasProductHeading() {
        return isVisible(PRODUCT_HEADING);
    }

    public String productHeading() {
        return visible(PRODUCT_HEADING).getText().trim();
    }

    public String productPrice() {
        return visible(PRODUCT_PRICE).getText().trim();
    }

    public boolean hasLoadedPrimaryImage() {
        return wait.until(currentDriver -> {
            WebElement image = currentDriver.findElement(PRIMARY_PRODUCT_IMAGE);
            return Boolean.TRUE.equals(((JavascriptExecutor) currentDriver)
                    .executeScript("return arguments[0].complete && arguments[0].naturalWidth > 0", image));
        });
    }

    public boolean hasProductDetails() {
        return hasProductHeading() && !productHeading().isBlank();
    }

    public boolean hasSpecificationSection() {
        ((JavascriptExecutor) driver).executeScript(
                "window.scrollTo(0, document.body.scrollHeight)");
        return wait.until(currentDriver -> currentDriver.findElement(By.tagName("body"))
                .getText()
                .contains("Thông Số Kỹ Thuật"));
    }
}
