package com.gostudios.playtree;

import android.app.Activity;
import android.net.http.SslError;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.webkit.SslErrorHandler;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/**
 * PLAYTREE TV - full-screen WebView wrapper for the PLAYTREE TV page.
 * Loads the GitHub Pages hosted tv.html. Shows load errors on screen
 * instead of failing silently to a black screen.
 */
public class MainActivity extends Activity {
    private static final String TV_URL = "https://gostudios-real.github.io/PlayTree-Website/tv.html";
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                             WindowManager.LayoutParams.FLAG_FULLSCREEN);

        webView = new WebView(this);
        webView.setBackgroundColor(0xFF000000);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    showError("LOAD ERROR: " + error.getDescription()
                            + "\nURL: " + request.getUrl());
                }
            }

            @Override
            public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
                showError("SSL ERROR: " + error.toString());
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                android.util.Log.i("PLAYTREE", "Page loaded: " + url);
            }
        });
        webView.setWebChromeClient(new WebChromeClient());

        setContentView(webView);

        // Show a loading screen immediately so we never get a silent black screen.
        webView.loadDataWithBaseURL(null,
                "<html><body style='background:#000;color:#55ef78;font-family:sans-serif;"
                + "display:flex;align-items:center;justify-content:center;height:100vh;"
                + "flex-direction:column;text-align:center'>"
                + "<h1 style='font-size:64px;letter-spacing:.1em'>PLAYTREE</h1>"
                + "<p style='color:#e0c66a;letter-spacing:.3em'>AWAKEN &middot; REBUILD &middot; RESTORE BALANCE</p>"
                + "<p id='s' style='color:#9aafa0'>Loading...</p>"
                + "<script>setTimeout(function(){document.getElementById('s').textContent='Still loading...';},4000);</script>"
                + "</body></html>", "text/html", "utf-8", null);

        // Then load the real page after a short delay.
        webView.postDelayed(new Runnable() {
            @Override
            public void run() {
                webView.loadUrl(TV_URL);
            }
        }, 800);

        hideSystemUi();
    }

    private void showError(String msg) {
        android.util.Log.e("PLAYTREE", msg);
        if (webView != null) {
            String html = "<html><body style='background:#000;color:#ff6b6b;font-family:monospace;"
                    + "padding:40px;font-size:22px'>"
                    + "<h1 style='color:#55ef78'>PLAYTREE TV</h1>"
                    + "<p style='color:#e0c66a'>Could not load the page.</p>"
                    + "<pre style='color:#ff9f9f;white-space:pre-wrap'>" + msg.replace("&", "&amp;").replace("<", "&lt;") + "</pre>"
                    + "</body></html>";
            webView.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
        }
    }

    private void hideSystemUi() {
        webView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onResume() {
        super.onResume();
        hideSystemUi();
    }
}
