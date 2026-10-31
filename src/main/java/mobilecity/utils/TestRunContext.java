package mobilecity.utils;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public final class TestRunContext {
    private static final String RUN_ID = "MC-" + LocalDateTime.now()
            .format(DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss"));

    private TestRunContext() {
    }

    public static String runId() {
        return RUN_ID;
    }
}
