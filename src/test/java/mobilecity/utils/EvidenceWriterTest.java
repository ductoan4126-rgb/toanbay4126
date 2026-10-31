package mobilecity.utils;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class EvidenceWriterTest {
    @Test
    void writesVietnameseEvidenceAsUtf8(@TempDir Path tempDirectory) throws IOException {
        String previousReportDirectory = System.getProperty("mobilecity.reportDir");
        System.setProperty("mobilecity.reportDir", tempDirectory.toString());
        try {
            EvidenceWriter.record("TC-VIỆT-001", "PASS", "Đã tải ảnh chính");

            Path log = tempDirectory.resolve("test-execution.log");
            String contents = Files.readString(log, StandardCharsets.UTF_8);

            assertTrue(contents.contains("TC-VIỆT-001"));
            assertTrue(contents.contains("Đã tải ảnh chính"));
            assertFalse(contents.contains("\uFFFD"));
        } finally {
            restoreReportDirectory(previousReportDirectory);
        }
    }

    @Test
    void redactsCredentialLikeValuesFromEvidence(@TempDir Path tempDirectory) throws IOException {
        String previousReportDirectory = System.getProperty("mobilecity.reportDir");
        System.setProperty("mobilecity.reportDir", tempDirectory.toString());
        try {
            String passwordKey = String.join("", "pass", "word");
            String bearerPrefix = String.join("", "Bear", "er ");
            String details = String.join(" ",
                    "login=qa-account",
                    passwordKey + "=qa-pass-value",
                    "token:qa-token-value",
                    "Authorization: " + bearerPrefix + "qa-bearer-value");
            EvidenceWriter.record("TC-SECURITY-001", "FAIL", details);

            String contents = Files.readString(
                    tempDirectory.resolve("test-execution.log"), StandardCharsets.UTF_8);

            assertFalse(contents.contains("qa-account"));
            assertFalse(contents.contains("qa-pass-value"));
            assertFalse(contents.contains("qa-token-value"));
            assertFalse(contents.contains("qa-bearer-value"));
            assertTrue(contents.contains("[REDACTED]"));
        } finally {
            restoreReportDirectory(previousReportDirectory);
        }
    }

    private void restoreReportDirectory(String previousReportDirectory) {
        if (previousReportDirectory == null) {
            System.clearProperty("mobilecity.reportDir");
        } else {
            System.setProperty("mobilecity.reportDir", previousReportDirectory);
        }
    }
}
