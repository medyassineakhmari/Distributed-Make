import java.rmi.*;
import java.rmi.registry.*;
import java.rmi.server.*;
import java.net.InetAddress;
import java.nio.file.*;
import java.util.Arrays;

public class Worker extends UnicastRemoteObject implements PingPongService {
    
    public Worker() throws RemoteException {
        super();
    }
    
    public byte[] ping(byte[] data) throws RemoteException {
        return new byte[]{1}; // Pong
    }
    
    public byte[] pingWithIO(String filePath) throws RemoteException {
        try {
            // Lire le fichier
            byte[] content = Files.readAllBytes(Paths.get(filePath));
            
            // Écrire dans un nouveau fichier (simuler I/O)
            String outPath = filePath.replace(".txt", "_received.txt");
            Files.write(Paths.get(outPath), content);
            
            return new byte[]{1}; // Pong
        } catch (Exception e) {
            throw new RemoteException("I/O error: " + e.getMessage());
        }
    }
    
    public void createTestFile(String filePath, int sizeKB) throws RemoteException {
        try {
            Files.createDirectories(Paths.get(filePath).getParent());
            byte[] data = new byte[sizeKB * 1024];
            Arrays.fill(data, (byte) 'a');
            Files.write(Paths.get(filePath), data);
        } catch (Exception e) {
            throw new RemoteException("Cannot create file: " + e.getMessage());
        }
    }
    
    public String hello() throws RemoteException {
        try {
            return "Worker on " + InetAddress.getLocalHost().getHostName();
        } catch (Exception e) {
            return "Worker";
        }
    }
    
    public static void main(String[] args) {
        try {
            Registry registry = LocateRegistry.createRegistry(1099);
            Worker worker = new Worker();
            registry.rebind("PingPong", worker);
            System.out.println("Worker ready!");
            Thread.currentThread().join();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}