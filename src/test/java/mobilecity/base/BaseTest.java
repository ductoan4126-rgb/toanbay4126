package mobilecity.base;

import mobilecity.config.DriverFactory;
import mobilecity.config.TestConfig;
import mobilecity.utils.TestRunContext;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Assumptions;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Path;

public abstract class BaseTest {
    private static final Logger LOGGER = LoggerFactory.getLogger(BaseTest.class);
    private static final String SHUTDOWN_HOOK_NAME = "mobilecity-visible-chrome-shutdown";

    protected static volatile WebDriver driver;
    private static boolean shutdownHookRegistered;
    private static String activeProfileDirectory;

    @RegisterExtension
    private final FailureEvidenceExtension evidenceExtension =
            new FailureEvidenceExtension(() -> driver);

    protected String persistentChromeProfileDirectory() {
        return null;
    }

    @BeforeEach
    void startBrowser() {
        String requestedBrowserConfiguration = browserConfigurationKey();
        if (driver != null && !java.util.Objects.equals(
                activeProfileDirectory, requestedBrowserConfiguration)) {
            throw new IllegalStateException(
                    "Chrome configuration changed while a WebDriver session is active");
        }
        if (driver == null) {
            LOGGER.info("Starting run {} with Chrome; headless={}",
                    TestRunContext.runId(), TestConfig.headless());
            driver = DriverFactory.createChromeDriver(
                    normalizeProfileDirectory(persistentChromeProfileDirectory()));
            activeProfileDirectory = requestedBrowserConfiguration;
            driver.manage().timeouts().implicitlyWait(java.time.Duration.ZERO);
            driver.manage().timeouts().pageLoadTimeout(TestConfig.waitTimeout().multipliedBy(2));
            if (!isAttachedToExistingChrome()) {
                registerVisibleBrowserShutdownHook();
            }
        }
        if (!preservesBrowserSession()) {
            clearBrowserSession();
        }
    }

    @AfterEach
    void stopBrowser() {
        try {
            if (!preservesBrowserSession()) {
                clearBrowserSession();
            }
        } catch (org.openqa.selenium.WebDriverException e) {
            LOGGER.warn("Unable to clear browser session after test ({})",
                    e.getClass().getSimpleName());
        } finally {
            if (isAttachedToExistingChrome()) {
                LOGGER.info("Leaving the attached Chrome browser open");
            } else if (TestConfig.keepBrowserOpenSeconds() == 0) {
                closeBrowser();
            } else if (preservesBrowserSession()) {
                LOGGER.info("Keeping the Chrome window open with the authenticated profile preserved");
            } else {
                LOGGER.info("Keeping the Chrome window open with cookies and site storage cleared");
            }
        }
    }

    private boolean preservesBrowserSession() {
        return persistentChromeProfileDirectory() != null || isAttachedToExistingChrome();
    }

    private static boolean isAttachedToExistingChrome() {
        return TestConfig.chromeDebuggerAddress() != null;
    }

    private String browserConfigurationKey() {
        String debuggerAddress = TestConfig.chromeDebuggerAddress();
        if (debuggerAddress != null) {
            return "debugger:" + debuggerAddress;
        }
        String profileDirectory = normalizeProfileDirectory(persistentChromeProfileDirectory());
        return profileDirectory == null ? "default" : "profile:" + profileDirectory;
    }

    private static String normalizeProfileDirectory(String profileDirectory) {
        return profileDirectory == null || profileDirectory.isBlank()
                ? null
                : Path.of(profileDirectory).toAbsolutePath().normalize().toString();
    }

    private static void clearBrowserSession() {
        if (driver == null) {
            return;
        }
        driver.manage().deleteAllCookies();
        String currentUrl = driver.getCurrentUrl();
        if (sameOrigin(currentUrl, TestConfig.baseUrl())) {
            ((JavascriptExecutor) driver).executeScript(
                    "window.localStorage.clear(); window.sessionStorage.clear();");
        }
    }

    private static boolean sameOrigin(String firstUrl, String secondUrl) {
        try {
            java.net.URI first = java.net.URI.create(firstUrl);
            java.net.URI second = java.net.URI.create(secondUrl);
            return first.getScheme().equalsIgnoreCase(second.getScheme())
                    && first.getHost().equalsIgnoreCase(second.getHost())
                    && effectivePort(first) == effectivePort(second);
        } catch (RuntimeException e) {
            LOGGER.warn("Unable to compare browser origin while clearing test session");
            return false;
        }
    }

    private static int effectivePort(java.net.URI uri) {
        if (uri.getPort() >= 0) {
            return uri.getPort();
        }
        return "https".equalsIgnoreCase(uri.getScheme()) ? 443 : 80;
    }

    private static synchronized void registerVisibleBrowserShutdownHook() {
        int keepOpenSeconds = TestConfig.keepBrowserOpenSeconds();
        if (keepOpenSeconds == 0 || shutdownHookRegistered) {
            return;
        }
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            LOGGER.info("Keeping the final Chrome page visible for {} seconds", keepOpenSeconds);
            try {
                Thread.sleep(java.time.Duration.ofSeconds(keepOpenSeconds).toMillis());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                LOGGER.warn("Chrome hold-open period was interrupted");
            } finally {
                closeBrowser();
            }
        }, SHUTDOWN_HOOK_NAME));
        shutdownHookRegistered = true;
    }

    private static synchronized void closeBrowser() {
        if (driver != null) {
            try {
                driver.quit();
            } catch (RuntimeException e) {
                LOGGER.error("Unable to close Chrome cleanly", e);
                throw e;
            } finally {
                driver = null;
                activeProfileDirectory = null;
            }
        }
    }

    protected void assumeNoSiteChallenge() {
        String pageContent = driver.getTitle() + " " + driver.findElement(By.tagName("body")).getText();
        String normalized = pageContent.toLowerCase();
        Assumptions.assumeFalse(
                normalized.contains("security verification")
                        || normalized.contains("checking your browser")
                        || normalized.contains("verify you are human"),
                "BLOCKED: website access challenge prevents evaluating the requested page");
    }
}
