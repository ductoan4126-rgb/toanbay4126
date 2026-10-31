package mobilecity.config;

import java.time.Duration;

public final class TestConfig {
    private TestConfig() {
    }

    public static String baseUrl() {
        return value("mobilecity.baseUrl", "MOBILECITY_BASE_URL", "https://mobilecity.vn/");
    }

    public static boolean headless() {
        return Boolean.parseBoolean(value("mobilecity.headless", "MOBILECITY_HEADLESS", "true"));
    }

    public static Duration waitTimeout() {
        String configured = value("mobilecity.waitSeconds", "MOBILECITY_WAIT_SECONDS", "15");
        try {
            long seconds = Long.parseLong(configured);
            if (seconds < 1 || seconds > 120) {
                throw new IllegalArgumentException("mobilecity.waitSeconds must be between 1 and 120");
            }
            return Duration.ofSeconds(seconds);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("mobilecity.waitSeconds must be an integer", e);
        }
    }

    public static String screenshotDirectory() {
        return value("mobilecity.screenshotDir", "MOBILECITY_SCREENSHOT_DIR", "screenshots");
    }

    public static String reportDirectory() {
        return value("mobilecity.reportDir", "MOBILECITY_REPORT_DIR", "reports");
    }

    public static String cartChromeProfileDirectory() {
        String systemValue = System.getProperty("mobilecity.cartChromeProfileDir");
        if (systemValue != null && !systemValue.isBlank()) {
            return systemValue.trim();
        }
        String environmentValue = System.getenv("MOBILECITY_CART_CHROME_PROFILE_DIR");
        return environmentValue == null || environmentValue.isBlank()
                ? null
                : environmentValue.trim();
    }

    public static String chromeDebuggerAddress() {
        String configured = value("mobilecity.chromeDebuggerAddress",
                "MOBILECITY_CHROME_DEBUGGER_ADDRESS", "");
        return configured.isBlank() ? null : configured;
    }

    public static int keepBrowserOpenSeconds() {
        String configured = value("mobilecity.keepBrowserOpenSeconds",
                "MOBILECITY_KEEP_BROWSER_OPEN_SECONDS", "0");
        try {
            int seconds = Integer.parseInt(configured);
            if (seconds < 0 || seconds > 300) {
                throw new IllegalArgumentException(
                        "mobilecity.keepBrowserOpenSeconds must be between 0 and 300");
            }
            return seconds;
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException(
                    "mobilecity.keepBrowserOpenSeconds must be an integer", e);
        }
    }

    public static String loginUsername() {
        return System.getenv("MOBILECITY_USERNAME");
    }

    public static String loginPassword() {
        return System.getenv("MOBILECITY_PASSWORD");
    }

    private static String value(String property, String environment, String fallback) {
        String systemValue = System.getProperty(property);
        String environmentValue = System.getenv(environment);
        return resolveValue(systemValue, environmentValue, fallback);
    }

    static String resolveValue(String systemValue, String environmentValue, String fallback) {
        if (systemValue != null && !systemValue.isBlank()) {
            return systemValue.trim();
        }
        return environmentValue == null || environmentValue.isBlank()
                ? fallback
                : environmentValue.trim();
    }
}
