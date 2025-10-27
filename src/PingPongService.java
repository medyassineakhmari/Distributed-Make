import java.rmi.Remote;
import java.rmi.RemoteException;

public interface PingPongService extends Remote {
    byte[] ping(byte[] data) throws RemoteException;
    byte[] pingWithIO(String filePath) throws RemoteException;
    void createTestFile(String filePath, int sizeKB) throws RemoteException;
    String hello() throws RemoteException;
}