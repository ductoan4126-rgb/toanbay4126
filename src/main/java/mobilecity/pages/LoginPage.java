package mobilecity.pages;

import java.util.List;
import java.util.Locale;

import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

public final class LoginPage extends BasePage {
    private static final By LOGIN_INPUT = By.name("login");
    private static final By PASSWORD_INPUT = By.name("password");
    private static final By SUBMIT_BUTTON =
            By.cssSelector("form[action*='/login'] button[type='submit']");
    private static final By AUTHENTICATED_MARKER = By.xpath(
            "//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'đăng xuất') "
                    + "or contains(translate(@href, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'logout')]"
                    + " | //button[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                    + "'abcdefghijklmnopqrstuvwxyz'), 'đăng xuất')]");
    private static final By ALERTS = By.cssSelector(
            "[role='alert'], .alert-danger, .invalid-feedback, .text-danger");
    private static final By CHALLENGE_IFRAMES = By.cssSelector(
            "iframe[src*='captcha'], iframe[src*='recaptcha'], iframe[src*='hcaptcha']");

    public LoginPage(WebDriver driver) {
        super(driver);
    }

    public boolean isAuthenticated() {
        return driver.findElements(AUTHENTICATED_MARKER).stream().anyMatch(WebElement::isDisplayed);
    }

    public boolean hasRequiredFields() {
        return isVisible(LOGIN_INPUT) && isVisible(PASSWORD_INPUT);
    }

    public boolean fieldsAreRequired() {
        return visible(LOGIN_INPUT).getDomAttribute("required") != null
                && visible(PASSWORD_INPUT).getDomAttribute("required") != null;
    }

    public boolean emptyLoginFieldsAreInvalid() {
        WebElement login = visible(LOGIN_INPUT);
        WebElement password = visible(PASSWORD_INPUT);
        return !(Boolean) ((JavascriptExecutor) driver).executeScript(
                "return arguments[0].checkValidity() && arguments[1].checkValidity();",
                login, password);
    }

    public String passwordInputType() {
        return visible(PASSWORD_INPUT).getDomAttribute("type");
    }

    public LoginOutcome login(String username, String password) {
        try {
            visible(LOGIN_INPUT).sendKeys(username);
            visible(PASSWORD_INPUT).sendKeys(password);
            clickable(SUBMIT_BUTTON).click();
            return wait.until(currentDriver -> {
                LoginOutcome outcome = currentOutcome();
                return outcome == LoginOutcome.PENDING ? null : outcome;
            });
        } catch (org.openqa.selenium.TimeoutException e) {
            return LoginOutcome.TECHNICAL_ERROR;
        } finally {
            clearCredentialFields();
        }
    }

    private LoginOutcome currentOutcome() {
        if (isAuthenticated()) {
            return LoginOutcome.AUTHENTICATED;
        }
        if (requiresVerification()) {
            return LoginOutcome.VERIFICATION_REQUIRED;
        }
        String alerts = driver.findElements(ALERTS).stream()
                .filter(WebElement::isDisplayed)
                .map(WebElement::getText)
                .reduce("", (first, second) -> first + " " + second)
                .toLowerCase(Locale.ROOT);
        if (containsInvalidCredentialsMessage(alerts)) {
            return LoginOutcome.INVALID_CREDENTIALS;
        }
        if (!alerts.isBlank()) {
            return LoginOutcome.TECHNICAL_ERROR;
        }
        return LoginOutcome.PENDING;
    }

    public boolean requiresVerification() {
        if (driver.findElements(CHALLENGE_IFRAMES).stream().anyMatch(WebElement::isDisplayed)) {
            return true;
        }
        String content = driver.findElement(By.tagName("body")).getText().toLowerCase(Locale.ROOT);
        return content.contains("captcha")
                || content.contains("mã otp")
                || content.contains("mã xác minh")
                || content.contains("verification code")
                || content.contains("one-time password");
    }

    private boolean containsInvalidCredentialsMessage(String message) {
        return message.contains("sai mật khẩu")
                || message.contains("mật khẩu không đúng")
                || message.contains("tài khoản hoặc mật khẩu")
                || message.contains("thông tin đăng nhập không đúng")
                || message.contains("invalid credentials")
                || message.contains("incorrect password");
    }

    private void clearCredentialFields() {
        try {
            clearFields(driver.findElements(LOGIN_INPUT));
            clearFields(driver.findElements(PASSWORD_INPUT));
        } catch (org.openqa.selenium.WebDriverException e) {
            org.slf4j.LoggerFactory.getLogger(LoginPage.class)
                    .warn("Unable to access credential inputs during login cleanup");
        }
    }

    private void clearFields(List<WebElement> fields) {
        for (WebElement field : fields) {
            try {
                field.clear();
            } catch (org.openqa.selenium.WebDriverException e) {
                org.slf4j.LoggerFactory.getLogger(LoginPage.class)
                        .warn("Unable to clear a credential input after login processing");
            }
        }
    }

    public enum LoginOutcome {
        AUTHENTICATED,
        INVALID_CREDENTIALS,
        VERIFICATION_REQUIRED,
        TECHNICAL_ERROR,
        PENDING
    }
}
