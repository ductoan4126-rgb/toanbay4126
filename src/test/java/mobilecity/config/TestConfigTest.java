package mobilecity.config;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Duration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

class TestConfigTest {
    private static final String WAIT_SECONDS = "mobilecity.waitSeconds";
    private static final String KEEP_OPEN_SECONDS = "mobilecity.keepBrowserOpenSeconds";
    private String originalWaitSeconds;
    private String originalKeepOpenSeconds;

    @BeforeEach
    void captureConfigurationProperties() {
        originalWaitSeconds = System.getProperty(WAIT_SECONDS);
        originalKeepOpenSeconds = System.getProperty(KEEP_OPEN_SECONDS);
    }

    @AfterEach
    void restoreConfigurationProperties() {
        restoreProperty(WAIT_SECONDS, originalWaitSeconds);
        restoreProperty(KEEP_OPEN_SECONDS, originalKeepOpenSeconds);
    }

    private void restoreProperty(String name, String originalValue) {
        if (originalValue == null) {
            System.clearProperty(name);
        } else {
            System.setProperty(name, originalValue);
        }
    }

    @Test
    void waitTimeoutAcceptsInteriorValue() {
        System.setProperty(WAIT_SECONDS, "15");

        assertEquals(Duration.ofSeconds(15), TestConfig.waitTimeout());
    }

    @Test
    void waitTimeoutAcceptsLowerBoundary() {
        System.setProperty(WAIT_SECONDS, "1");

        assertEquals(Duration.ofSeconds(1), TestConfig.waitTimeout());
    }

    @Test
    void waitTimeoutAcceptsUpperBoundary() {
        System.setProperty(WAIT_SECONDS, "120");

        assertEquals(Duration.ofSeconds(120), TestConfig.waitTimeout());
    }

    @Test
    void waitTimeoutRejectsValueBelowLowerBoundary() {
        System.setProperty(WAIT_SECONDS, "0");

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, TestConfig::waitTimeout);

        assertEquals("mobilecity.waitSeconds must be between 1 and 120", error.getMessage());
    }

    @Test
    void waitTimeoutRejectsValueAboveUpperBoundary() {
        System.setProperty(WAIT_SECONDS, "121");

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, TestConfig::waitTimeout);

        assertEquals("mobilecity.waitSeconds must be between 1 and 120", error.getMessage());
    }

    @Test
    void waitTimeoutRejectsNonIntegerValue() {
        System.setProperty(WAIT_SECONDS, "many");

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, TestConfig::waitTimeout);

        assertEquals("mobilecity.waitSeconds must be an integer", error.getMessage());
        assertNotNull(error.getCause());
    }

    @Test
    void keepBrowserOpenAcceptsInteriorValue() {
        System.setProperty(KEEP_OPEN_SECONDS, "60");

        assertEquals(60, TestConfig.keepBrowserOpenSeconds());
    }

    @Test
    void keepBrowserOpenAcceptsLowerBoundary() {
        System.setProperty(KEEP_OPEN_SECONDS, "0");

        assertEquals(0, TestConfig.keepBrowserOpenSeconds());
    }

    @Test
    void keepBrowserOpenAcceptsUpperBoundary() {
        System.setProperty(KEEP_OPEN_SECONDS, "300");

        assertEquals(300, TestConfig.keepBrowserOpenSeconds());
    }

    @Test
    void keepBrowserOpenRejectsValueBelowLowerBoundary() {
        System.setProperty(KEEP_OPEN_SECONDS, "-1");

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, TestConfig::keepBrowserOpenSeconds);

        assertEquals(
                "mobilecity.keepBrowserOpenSeconds must be between 0 and 300",
                error.getMessage());
    }

    @Test
    void keepBrowserOpenRejectsValueAboveUpperBoundary() {
        System.setProperty(KEEP_OPEN_SECONDS, "301");

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, TestConfig::keepBrowserOpenSeconds);

        assertEquals(
                "mobilecity.keepBrowserOpenSeconds must be between 0 and 300",
                error.getMessage());
    }

    @Test
    void keepBrowserOpenRejectsNonIntegerValue() {
        System.setProperty(KEEP_OPEN_SECONDS, "later");

        IllegalArgumentException error =
                assertThrows(IllegalArgumentException.class, TestConfig::keepBrowserOpenSeconds);

        assertEquals(
                "mobilecity.keepBrowserOpenSeconds must be an integer",
                error.getMessage());
        assertNotNull(error.getCause());
    }

    @Test
    void resolveValuePrefersAndTrimsNonBlankSystemProperty() {
        assertEquals(
                "system-value",
                TestConfig.resolveValue(" system-value ", "environment", "default"));
    }

    @Test
    void resolveValueUsesAndTrimsEnvironmentWhenSystemPropertyIsBlank() {
        assertEquals("environment", TestConfig.resolveValue("  ", " environment ", "default"));
    }

    @Test
    void resolveValueUsesFallbackWhenEnvironmentIsNull() {
        assertEquals("default", TestConfig.resolveValue(null, null, "default"));
    }

    @Test
    void resolveValueUsesFallbackWhenEnvironmentIsBlank() {
        assertEquals("default", TestConfig.resolveValue("", "  ", "default"));
    }
}
