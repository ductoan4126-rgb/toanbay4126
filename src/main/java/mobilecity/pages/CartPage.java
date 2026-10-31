package mobilecity.pages;

import java.util.List;
import java.util.Locale;

import org.openqa.selenium.By;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

public final class CartPage extends BasePage {
    private static final By QUANTITY_INPUTS = By.cssSelector("input[type='number']");
    private static final By ITEM_ROW = By.xpath(
            "./ancestor::*[self::tr or self::li or self::article "
                    + "or (contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'cart') "
                    + "and contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'item'))][1]");
    private static final By PRODUCT_LINKS = By.cssSelector("a[href$='.html']");
    private static final By UPDATE_BUTTON = By.xpath(
            ".//button[@type='submit' or not(@type)]"
                    + "[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'cập nhật') "
                    + "or contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'update') "
                    + "or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'cập nhật') "
                    + "or contains(translate(@title, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'cập nhật')]"
                    + " | .//input[@type='submit' or @type='button']"
                    + "[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'cập nhật') "
                    + "or contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'update')]");
    private static final By UPDATE_MESSAGES = By.cssSelector(
            "[role='alert'], [aria-live='polite'], [aria-live='assertive'], .alert, .toast");

    public CartPage(WebDriver driver) {
        super(driver);
    }

    public boolean hasCartPageLoadedFromPublishedLink() {
        return driver.getCurrentUrl().toLowerCase(Locale.ROOT).contains("cart")
                || driver.getTitle().toLowerCase(Locale.ROOT).contains("giỏ hàng");
    }

    public boolean hasFirstItemQuantityControl() {
        return firstItem() != null;
    }

    public boolean hasFirstItemUpdateButton() {
        CartItem item = firstItem();
        return item != null && findUpdateButton(item.row()).isPresent();
    }

    public boolean canIncreaseFirstItemQuantity() {
        CartItem item = firstItem();
        if (item == null || item.quantity() < 1) {
            return false;
        }
        String maximum = item.quantityInput().getDomAttribute("max");
        return maximum == null || maximum.isBlank()
                || item.quantity() < Integer.parseInt(maximum);
    }

    public void temporarilyIncreaseFirstItemQuantity() {
        CartItem initialItem = firstItem();
        if (initialItem == null) {
            throw new IllegalStateException("Không tìm thấy mặt hàng có ô số lượng trong giỏ.");
        }
        int originalQuantity = initialItem.quantity();
        if (originalQuantity < 1) {
            throw new IllegalStateException("Số lượng mặt hàng đầu tiên không hợp lệ.");
        }
        String maximum = initialItem.quantityInput().getDomAttribute("max");
        if (maximum != null && !maximum.isBlank()
                && originalQuantity >= Integer.parseInt(maximum)) {
            throw new IllegalStateException(
                    "Không thể tăng số lượng: mặt hàng đầu tiên đã đạt giới hạn cho phép.");
        }

        String productHref = initialItem.productHref();
        Throwable primaryFailure = null;
        try {
            submitQuantity(productHref, originalQuantity + 1);
            refreshAndVerifyQuantity(productHref, originalQuantity + 1);
        } catch (RuntimeException | Error failure) {
            primaryFailure = failure;
            throw failure;
        } finally {
            try {
                restoreQuantity(productHref, originalQuantity);
            } catch (RuntimeException | Error cleanupFailure) {
                if (primaryFailure != null) {
                    primaryFailure.addSuppressed(cleanupFailure);
                } else {
                    throw cleanupFailure;
                }
            }
        }
    }

    private void submitQuantity(String productHref, int quantity) {
        CartItem item = requireItem(productHref);
        WebElement updateButton = findUpdateButton(item.row())
                .orElseThrow(() -> new IllegalStateException(
                        "Không tìm thấy nút cập nhật số lượng; giỏ hàng chưa được thay đổi."));
        String previousFeedback = updateFeedback();
        WebElement productLink = item.productLink();

        item.quantityInput().clear();
        item.quantityInput().sendKeys(Integer.toString(quantity));
        wait.until(ExpectedConditions.elementToBeClickable(updateButton)).click();
        wait.until(currentDriver -> hasUpdateConfirmation(productLink, previousFeedback));
    }

    private void refreshAndVerifyQuantity(String productHref, int expectedQuantity) {
        driver.navigate().refresh();
        wait.until(currentDriver -> "interactive".equals(((org.openqa.selenium.JavascriptExecutor)
                currentDriver).executeScript("return document.readyState"))
                || "complete".equals(((org.openqa.selenium.JavascriptExecutor)
                currentDriver).executeScript("return document.readyState")));

        int savedQuantity = requireItem(productHref).quantity();
        if (savedQuantity != expectedQuantity) {
            throw new IllegalStateException(
                    "Số lượng sau khi tải lại giỏ không khớp giá trị mong đợi.");
        }
    }

    private void restoreQuantity(String productHref, int originalQuantity) {
        driver.navigate().refresh();
        wait.until(currentDriver -> "interactive".equals(((org.openqa.selenium.JavascriptExecutor)
                currentDriver).executeScript("return document.readyState"))
                || "complete".equals(((org.openqa.selenium.JavascriptExecutor)
                currentDriver).executeScript("return document.readyState")));

        CartItem currentItem = requireItem(productHref);
        if (currentItem.quantity() != originalQuantity) {
            submitQuantity(productHref, originalQuantity);
            refreshAndVerifyQuantity(productHref, originalQuantity);
        }
    }

    private boolean hasUpdateConfirmation(WebElement productLink, String previousFeedback) {
        try {
            if (!productLink.isDisplayed()) {
                return true;
            }
            String currentFeedback = updateFeedback();
            return !currentFeedback.equals(previousFeedback)
                    && isPositiveUpdateMessage(currentFeedback);
        } catch (StaleElementReferenceException e) {
            return true;
        }
    }

    private boolean isPositiveUpdateMessage(String message) {
        String normalized = message.toLowerCase(Locale.ROOT);
        return normalized.contains("cập nhật thành công")
                || normalized.contains("đã cập nhật")
                || normalized.contains("updated successfully")
                || normalized.contains("cart updated");
    }

    private String updateFeedback() {
        return driver.findElements(UPDATE_MESSAGES).stream()
                .filter(WebElement::isDisplayed)
                .map(WebElement::getText)
                .filter(text -> !text.isBlank())
                .reduce("", (first, second) -> first + "\n" + second);
    }

    private CartItem firstItem() {
        for (WebElement quantityInput : driver.findElements(QUANTITY_INPUTS)) {
            if (!quantityInput.isDisplayed() || !quantityInput.isEnabled()) {
                continue;
            }
            List<WebElement> rows = quantityInput.findElements(ITEM_ROW);
            if (rows.isEmpty()) {
                continue;
            }
            List<WebElement> productLinks = rows.get(0).findElements(PRODUCT_LINKS);
            if (!productLinks.isEmpty()) {
                return new CartItem(rows.get(0), productLinks.get(0),
                        productLinks.get(0).getDomAttribute("href"), quantityInput);
            }
        }
        return null;
    }

    private CartItem requireItem(String productHref) {
        for (WebElement productLink : driver.findElements(PRODUCT_LINKS)) {
            if (!productHref.equals(productLink.getDomAttribute("href"))) {
                continue;
            }
            List<WebElement> rows = productLink.findElements(ITEM_ROW);
            if (rows.isEmpty()) {
                break;
            }
            List<WebElement> quantities = rows.get(0).findElements(QUANTITY_INPUTS);
            if (quantities.isEmpty()) {
                break;
            }
            return new CartItem(rows.get(0), productLink, productHref, quantities.get(0));
        }
        throw new IllegalStateException(
                "Không tìm thấy lại đúng mặt hàng trong giỏ để xác minh hoặc khôi phục số lượng.");
    }

    private java.util.Optional<WebElement> findUpdateButton(WebElement row) {
        return row.findElements(UPDATE_BUTTON).stream()
                .filter(WebElement::isDisplayed)
                .filter(WebElement::isEnabled)
                .findFirst();
    }

    private record CartItem(
            WebElement row, WebElement productLink, String productHref, WebElement quantityInput) {
        private int quantity() {
            String value = quantityInput.getDomProperty("value");
            try {
                return Integer.parseInt(value);
            } catch (NumberFormatException e) {
                throw new IllegalStateException("Số lượng mặt hàng không phải số nguyên.", e);
            }
        }
    }
}
