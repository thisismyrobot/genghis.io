package genghis.io.android;

import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * Created by Robert on 12/07/2014.
 */
public class NoCacheWebViewClient extends WebViewClient {
    @Override
    public void onPageFinished(WebView view, String url) {
        super.onPageFinished(view, url);
        view.clearCache(true);
    }
}
