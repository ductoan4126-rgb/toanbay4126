package mobilecity.base;

import org.junit.jupiter.api.extension.BeforeTestExecutionCallback;
import org.junit.jupiter.api.extension.ExtensionContext;
import org.junit.jupiter.api.extension.TestWatcher;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

public final class TestProgressExtension implements BeforeTestExecutionCallback, TestWatcher {
    private static final Logger LOGGER = LoggerFactory.getLogger(TestProgressExtension.class);
    private static final ConcurrentMap<String, Long> START_TIMES = new ConcurrentHashMap<>();

    @Override
    public void beforeTestExecution(ExtensionContext context) {
        START_TIMES.put(context.getUniqueId(), System.nanoTime());
        LOGGER.info("[TEST START] {}.{} | {}",
                context.getRequiredTestClass().getSimpleName(),
                context.getRequiredTestMethod().getName(),
                context.getDisplayName());
    }

    @Override
    public void testSuccessful(ExtensionContext context) {
        reportResult(context, "PASS", null);
    }

    @Override
    public void testFailed(ExtensionContext context, Throwable cause) {
        reportResult(context, "FAIL", cause);
    }

    @Override
    public void testAborted(ExtensionContext context, Throwable cause) {
        reportResult(context, "BLOCKED/SKIPPED", cause);
    }

    @Override
    public void testDisabled(ExtensionContext context, Optional<String> reason) {
        LOGGER.info("[TEST BLOCKED/SKIPPED] {}.{}",
                context.getRequiredTestClass().getSimpleName(),
                context.getRequiredTestMethod().getName());
    }

    private void reportResult(ExtensionContext context, String status, Throwable cause) {
        Long startTime = START_TIMES.remove(context.getUniqueId());
        long durationMillis = startTime == null
                ? 0
                : (System.nanoTime() - startTime) / 1_000_000;
        String testName = context.getRequiredTestClass().getSimpleName() + "."
                + context.getRequiredTestMethod().getName();
        if (cause == null) {
            LOGGER.info("[TEST {}] {} ({} ms)", status, testName, durationMillis);
        } else {
            LOGGER.info("[TEST {}] {} ({} ms, {})",
                    status, testName, durationMillis, cause.getClass().getSimpleName());
        }
    }
}
