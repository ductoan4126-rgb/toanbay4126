package mobilecity.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;

public final class RegisterPage extends BasePage {
    private static final By REGISTRATION_INPUT = By.name("phone");
    private static final By CONTINUE_BUTTON =
            By.cssSelector("form[action*='/register'] button[type='submit']");

    public RegisterPage(WebDriver driver) {
        super(driver);
    }

    public boolean hasRegistrationInput() {
        return isVisible(REGISTRATION_INPUT);
    }

    public String registrationPlaceholder() {
        return visible(REGISTRATION_INPUT).getDomAttribute("placeholder");
    }

    public boolean hasContinueButton() {
        return isVisible(CONTINUE_BUTTON);
    }
}
