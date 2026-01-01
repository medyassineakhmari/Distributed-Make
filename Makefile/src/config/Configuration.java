package config;

public class Configuration {
    public static final int RMI_REGISTRY_PORT = 3000;
    public static final String RMI_SERVICE_NAME = "WorkerService";

    public static final int SCHEDULER_POLL_INTERVAL_MS = 500;
    public static final int SCHEDULER_TIMEOUT_HOURS = 1;

    public static final int TASK_RETRY_BASE_WAIT_MS = 100;
    public static final int TASK_RETRY_RANDOM_RANGE_MS = 100;

    public static final int MIN_WORKER_NODES = 2;
    public static final int MAX_WORKER_NODES = 1000;

    private Configuration() {
        throw new UnsupportedOperationException("Configuration is a utility class");
    }

    public static String buildRmiUrl(String hostname) {
        return buildRmiUrl(hostname, RMI_REGISTRY_PORT);
    }

    public static String buildRmiUrl(String hostname, int port) {
        if (hostname == null || hostname.trim().isEmpty()) {
            throw new IllegalArgumentException("Hostname cannot be null or empty");
        }
        if (port < 1024 || port > 65535) {
            throw new IllegalArgumentException("Port must be between 1024 and 65535");
        }
        return String.format("rmi://%s:%d/%s", hostname, port, RMI_SERVICE_NAME);
    }
}
