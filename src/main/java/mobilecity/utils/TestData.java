package mobilecity.utils;

import mobilecity.config.TestConfig;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.util.Properties;

public final class TestData {
    private static final Properties VALUES = load();

    private TestData() {
    }

    public static String required(String key) {
        String value = VALUES.getProperty(key);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException("Missing test data property: " + key);
        }
        return value.trim();
    }

    public static String url(String key) {
        if ("base.url".equals(key)) {
            return TestConfig.baseUrl();
        }
        return URI.create(TestConfig.baseUrl()).resolve(required(key)).toString();
    }

    private static Properties load() {
        Properties properties = new Properties();
        try (InputStream input = TestData.class.getResourceAsStream("/testdata/testdata.properties")) {
            if (input == null) {
                throw new IllegalStateException("Test data resource was not found");
            }
            properties.load(input);
            return properties;
        } catch (IOException e) {
            throw new IllegalStateException("Unable to load test data", e);
        }
    }
}
