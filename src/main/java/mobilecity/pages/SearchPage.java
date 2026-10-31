package mobilecity.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;

public final class SearchPage extends BasePage {
    private static final By SEARCH_INPUT = By.id("keyword");
    private static final By SEARCH_BUTTON = By.cssSelector("form#form_submit button[type='submit']");
    private static final By RESULTS_HEADING = By.xpath("//h1[normalize-space()='Kết quả tìm kiếm']");
    private static final By RESULT_LINKS = By.cssSelector("p.name a[href$='.html']");
    private static final By EMPTY_RESULTS = By.xpath("//*[normalize-space()='Không thấy kết quả phù hợp']");

    public SearchPage(WebDriver driver) {
        super(driver);
    }

    public boolean isSearchInputVisible() {
        return isVisible(SEARCH_INPUT);
    }

    public String placeholder() {
        return visible(SEARCH_INPUT).getDomAttribute("placeholder");
    }

    public boolean isEmptyInputRequired() {
        WebElement input = visible(SEARCH_INPUT);
        return input.getDomAttribute("required") != null
                && Boolean.FALSE.equals(((org.openqa.selenium.JavascriptExecutor) driver)
                        .executeScript("return arguments[0].checkValidity()", input));
    }

    public void enterTermWithoutSubmitting(String term) {
        WebElement input = visible(SEARCH_INPUT);
        input.clear();
        input.sendKeys(term);
    }

    public SearchPage submitTerm(String term) {
        enterTermWithoutSubmitting(term);
        clickable(SEARCH_BUTTON).click();
        wait.until(ExpectedConditions.urlContains("/tim-kiem"));
        return this;
    }

    public String enteredTerm() {
        return visible(SEARCH_INPUT).getDomProperty("value");
    }

    public boolean hasResultsHeading() {
        return isVisible(RESULTS_HEADING);
    }

    public boolean hasEmptyResultsMessage() {
        return isVisible(EMPTY_RESULTS);
    }

    public boolean hasProductResultMatching(String term) {
        return driver.findElements(RESULT_LINKS).stream()
                .anyMatch(link -> link.getText().toLowerCase().contains(term.toLowerCase()));
    }

    public String firstResultName() {
        return visible(RESULT_LINKS).getText().trim();
    }

    public void openFirstResult() {
        clickable(RESULT_LINKS).click();
    }
}
