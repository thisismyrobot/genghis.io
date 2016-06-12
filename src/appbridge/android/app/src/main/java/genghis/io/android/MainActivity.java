package genghis.io.android;

import android.content.Intent;
import android.preference.PreferenceManager;
import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.webkit.WebView;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;


public class MainActivity extends ActionBarActivity {

    private static JavascriptInterface JSInterface = null;
    private static WebView myWebView = null;
    private static boolean scanning = false;
    private static final String serverUrl = "http://genghis.io/android";
    private static NoCacheWebViewClient noCacheWebViewClient = new NoCacheWebViewClient();

    void resetFromJS() {
        Driver.reset();
        resetWebView();
    }

    private void resetWebView() {
        String url = PreferenceManager.getDefaultSharedPreferences(this).getString("pref_server", serverUrl);
        myWebView.loadUrl(url);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        myWebView = (WebView) findViewById(R.id.webview);
        myWebView.getSettings().setJavaScriptEnabled(true);
        myWebView.setWebViewClient(noCacheWebViewClient);
        JSInterface = new JavascriptInterface(this, myWebView);
        myWebView.addJavascriptInterface(JSInterface, "Android");

        resetWebView();
    }

    @Override
    protected void onPause() {
        super.onPause();

        // Reset the driver when we hide the window unless we're doing a QR scan, then we want to
        // *try* to keep it there.
        if (!scanning) {
            Driver.reset();
        }
        scanning = false;
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            startActivity(new Intent(this, Preferences.class));
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    public void scan() {
        scanning = true;
        IntentIntegrator integrator = new IntentIntegrator(this);
        integrator.initiateScan();
    }

    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        IntentResult scanResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
        if (scanResult != null && scanResult.getContents() != null) {
            if (JSInterface != null) {
                JSInterface.scanResult(scanResult.getContents());
            }
        }
        scanning = false;
    }
}
