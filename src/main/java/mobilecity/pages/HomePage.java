package mobilecity.pages;

import mobilecity.config.TestConfig;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public final class HomePage extends BasePage {
    private static final By HOME_LOGO = By.cssSelector("a[href='https://mobilecity.vn'] img[alt*='logo-mobilecity']");
    private static final By CATEGORY_LINK = By.cssSelector("a[href='https://mobilecity.vn/dien-thoai'], a[href='/dien-thoai']");
    private static final By SEARCH_INPUT = By.id("keyword");
    private static final By CART_LINK = By.xpath("//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'giỏ hàng') or contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cart')]");

    public HomePage(WebDriver driver) {
        super(driver);
    }

    public HomePage open() {
        driver.get(TestConfig.baseUrl());
        wait.until(d -> !"loading".equals(((org.openqa.selenium.JavascriptExecutor) d)
                .executeScript("return document.readyState")));
        return this;
    }

    public boolean hasTitle() {
        return driver.getTitle() != null && !driver.getTitle().isBlank();
    }

    public String title() {
        return driver.getTitle();
    }

    public boolean hasLogo() {
        return isVisible(HOME_LOGO);
    }

    public boolean hasPhoneCategoryLink() {
        return isVisible(CATEGORY_LINK);
    }

    public void openPhoneCategory() {
        clickable(CATEGORY_LINK).click();
    }

    public boolean hasSearchInput() {
        return isVisible(SEARCH_INPUT);
    }

    public SearchPage searchPage() {
        visible(SEARCH_INPUT);
        return new SearchPage(driver);
    }

    public boolean hasPublishedCartLink() {
        return isVisible(CART_LINK);
    }

    public void openPublishedCartLink() {
        clickable(CART_LINK).click();
    }
}
