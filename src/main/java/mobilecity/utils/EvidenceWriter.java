package mobilecity.utils;

import mobilecity.config.TestConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public final class EvidenceWriter {
    private static final Logger LOGGER = LoggerFactory.getLogger(EvidenceWriter.class);
    private static final DateTimeFormatter TIMESTAMP = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    private EvidenceWriter() {
    }

    public static synchronized void record(String testName, String status, String details) {
        Path log = Path.of(TestConfig.reportDirectory(), "test-execution.log");
        String safeTestName = sanitize(testName);
        String safeDetails = sanitize(details);
        String line = "%s | %s | %s | %s | %s%n".formatted(
                TestRunContext.runId(),
                LocalDateTime.now().format(TIMESTAMP),
                safeTestName,
                status,
                safeDetails);
        try {
            Files.createDirectories(log.getParent());
            Files.writeString(log, line, StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);
            LOGGER.info("{} {}: {}", status, safeTestName, safeDetails);
        } catch (IOException e) {
            LOGGER.error("Unable to write test execution log to {}", log, e);
            throw new IllegalStateException("Unable to persist test execution evidence", e);
        }
    }

    private static String sanitize(String value) {
        if (value == null) {
            return "";
        }
        String sanitized = value;
        for (String secretName : new String[] {
                "MOBILECITY_USERNAME", "MOBILECITY_PASSWORD", "LT_USERNAME", "LT_ACCESS_KEY"
        }) {
            String secret = System.getenv(secretName);
            if (secret != null && !secret.isEmpty()) {
                sanitized = sanitized.replace(secret, "[REDACTED]");
            }
        }
        return sanitized
                .replaceAll(
                        "(?i)([\"']?(?:username|login|password|passwd|access[_-]?key|token|secret)"
                                + "[\"']?\\s*[:=]\\s*[\"']?)[^&\\s,\"'}]+",
                        "$1[REDACTED]")
                .replaceAll("(?i)(bearer\\s+)[A-Za-z0-9._~+/=-]+", "$1[REDACTED]")
                .replaceAll("[\\r\\n]+", " ")
                .trim();
    }

    public static Path screenshotPath(String testName) throws IOException {
        Path directory = Path.of(TestConfig.screenshotDirectory());
        Files.createDirectories(directory);
        String safeName = testName.replaceAll("[^A-Za-z0-9._-]", "_");
        return directory.resolve(TestRunContext.runId() + "-" + safeName + ".png");
    }
}
