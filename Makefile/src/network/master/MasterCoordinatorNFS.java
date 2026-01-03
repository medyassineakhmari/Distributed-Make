package network.master;

import java.util.concurrent.TimeUnit;

public class MasterCoordinatorNFS {
    public static int executeOnWorker(String command, String workerHost, int workerPort) {
        try {
            String sshCmd = String.format("ssh -o StrictHostKeyChecking=no %s 'bash -c \"%s\"'",
                workerHost, command.replace("\"", "\\\""));
            
            System.out.println("[DEBUG] SSH: " + sshCmd);
            long start = System.currentTimeMillis();
            
            Process p = Runtime.getRuntime().exec(new String[]{"bash", "-c", sshCmd});
            
            boolean finished = p.waitFor(60, TimeUnit.SECONDS);
            
            if (!finished) {
                p.destroy();
                System.err.println("[DEBUG] TIMEOUT after 60s");
                return -1;
            }
            
            int exitCode = p.exitValue();
            System.out.println("[DEBUG] Done in " + (System.currentTimeMillis()-start) + "ms, exit=" + exitCode);
            return exitCode;
        } catch (Exception e) {
            e.printStackTrace();
            return -1;
        }
    }
    
    public static boolean isLocalhost(String hostname) {
        return hostname != null && hostname.equals("localhost");
    }
}
