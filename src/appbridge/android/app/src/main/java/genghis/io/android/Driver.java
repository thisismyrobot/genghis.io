package genghis.io.android;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.util.Log;
import android.widget.Toast;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.Set;
import java.util.UUID;

/**
 * Created by Bob on 6/07/2014.
 */
public class Driver {
    private static OutputStream outputStream = null;
    private static InputStream inputStream = null;
    private static Set<BluetoothDevice> pairedDevices = null;
    private static BluetoothDevice device = null;
    private static BluetoothSocket socket = null;
    private static UUID uuid = UUID.fromString("00001101-0000-1000-8000-00805f9b34fb");
    private static BluetoothAdapter adapter = BluetoothAdapter.getDefaultAdapter();
    private static String bluetoothFilter = null;

    private static void connect(String bluetoothFilter) throws Exception {

        // Record the bluetoothFilter
        Driver.bluetoothFilter = bluetoothFilter;

        // Check we have Bluetooth capability
        if (adapter == null) {
            throw new Exception("No Bluetooth adapter");
        }

        // Check Bluetooth is enabled
        if (!adapter.isEnabled()) {
            throw new Exception("Bluetooth adapter disabled");
        }

        // Get the paired devices
        pairedDevices = adapter.getBondedDevices();

        // Check we have at least one paired device
        if (pairedDevices.size() == 0) {
            throw new Exception("No paired Bluetooth devices");
        }

        // Find the device if not already found
        if (device == null) {
            for (BluetoothDevice d : pairedDevices) {
                if (d.getName().startsWith("Sphero-")) {
                    device = d;
                    break;
                }
            }
        }
        if (device == null) {
            throw new Exception("Requested device not found");
        }

        // Connect to the serial port, if not already connected
        if (socket == null) {
            try {
                socket = device.createRfcommSocketToServiceRecord(uuid);
            } catch (Exception e) {
                throw new Exception("Could not create connection to device");
            }
            try {
                socket.connect();
            } catch (Exception e) {
                throw new Exception("Could not open connection to device");
            }
        }

        // Connect the output stream if not already connected
        if (outputStream == null) {
            try {
                outputStream = socket.getOutputStream();
            } catch (Exception e) {
                throw new Exception("Could not open control stream to device");
            }
        }

        // Connect the input stream if not already connected
        if (inputStream == null) {
            try {
                inputStream = socket.getInputStream();
            } catch (Exception e) {
                throw new Exception("Could not open input stream to device");
            }
        }
    }

    /*
        Attempts to connect if not already connected.
     */
    public static void doConnect(String bluetoothFilter) throws Exception {
        try {
            connect(bluetoothFilter);
        } catch (Exception e) {
            reset();
            throw e;
        }
    }

    private static byte[] hexStringToByteArray(String s) {
        int len = s.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(s.charAt(i), 16) << 4)
                    + Character.digit(s.charAt(i+1), 16));
        }
        return data;
    }

    /*
        Send data to the robot.
     */
    public static void send(String serialString) {
        if (bluetoothFilter == null) {
            return;
        }
        byte[] bytes = hexStringToByteArray(serialString);
        try {
            outputStream.write(bytes);
        }
        catch(Exception e) {
            try {
                doConnect(bluetoothFilter);
                outputStream.write(bytes);
            } catch (Exception e2) {
                //TODO: error
            }
        }
    }

    public static void reset() {
        try {
            socket.close();
        }
        catch(Exception e) {};
        outputStream = null;
        inputStream = null;
        socket = null;
        device = null;
        pairedDevices = null;
    }

}
