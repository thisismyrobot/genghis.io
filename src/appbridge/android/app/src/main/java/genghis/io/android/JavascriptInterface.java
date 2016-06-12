package genghis.io.android;

import android.webkit.WebView;
import android.widget.Toast;

/**
 * Created by Bob on 6/07/2014.
 */
public class JavascriptInterface {
    private final WebView webView;
    MainActivity activity;

    /** Instantiate the interface and set the context */
    JavascriptInterface(MainActivity a, WebView wv) {
        activity = a;
        webView = wv;
    }

    /*
        Scan a QR code.
     */
    public void scanQR() {
        activity.scan();
    }

    /*
        Connect to the robot, calling genghisio.notify.robotConnected() or
        genghisio.notify.robotConnectFailed()
    */
    public void connectRobot(String botId, String bluetoothFilter) {
        try {
            Driver.doConnect(bluetoothFilter);
            webView.loadUrl("javascript:genghisio.notify.robotConnected('" + botId + "')");
        }
        catch (Exception e) {
            webView.loadUrl("javascript:genghisio.notify.robotConnectError('" + e.getMessage() + "')");
        }
    }

    /*
        Display simple errors
    */
    public void toast(String message) {
        Toast.makeText(this.activity, message, Toast.LENGTH_LONG).show();
    }

    /*
        Called when a QR code has been scanned, call genghisio.notify.newSid() with it.
    */
    public void scanResult(String qrcode) {
        webView.loadUrl("javascript:genghisio.notify.newSid('" + qrcode + "')");
    }

    /*
        Called when the user wants to start over
    */
    public void reset() {
        activity.resetFromJS();
    }

    public void sendControl(String serialString) {
        Driver.send(serialString);
    }
}
