package mobilecity.config;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.PageLoadStrategy;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public final class DriverFactory {
    private DriverFactory() {
    }

    public static WebDriver createChromeDriver() {
        return createChromeDriver(null);
    }

    public static WebDriver createChromeDriver(String userDataDirectory) {
        ChromeOptions options = new ChromeOptions();
        options.setPageLoadStrategy(PageLoadStrategy.EAGER);
        String debuggerAddress = TestConfig.chromeDebuggerAddress();
        if (debuggerAddress != null) {
            options.setExperimentalOption("debuggerAddress", debuggerAddress);
        } else {
            options.addArguments("--window-size=1440,1000");
            options.addArguments("--disable-notifications");
            options.addArguments("--disable-popup-blocking");
            if (userDataDirectory != null && !userDataDirectory.isBlank()) {
                Path profile = Path.of(userDataDirectory).toAbsolutePath().normalize();
                try {
                    Files.createDirectories(profile);
                } catch (IOException e) {
                    throw new IllegalStateException("Unable to create the Chrome profile directory", e);
                }
                options.addArguments("--user-data-dir=" + profile);
            }
            if (TestConfig.headless()) {
                options.addArguments("--headless=new");
            }
        }
        return new ChromeDriver(options);
    }
}
