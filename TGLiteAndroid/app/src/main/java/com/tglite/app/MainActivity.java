package com.tglite.app;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.graphics.Color;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import com.chaquo.python.PyObject;

public class MainActivity extends Activity {
    private WebView web;
    private Handler handler = new Handler(Looper.getMainLooper());
    private PyObject api;

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (!Python.isStarted()) Python.start(new AndroidPlatform(this));
        api = Python.getInstance().getModule("teleclient");
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(15, 23, 42));
        web.getSettings().setJavaScriptEnabled(true);
        web.getSettings().setDomStorageEnabled(true);
        web.setWebViewClient(new WebViewClient());
        web.setWebChromeClient(new WebChromeClient());
        web.addJavascriptInterface(new Bridge(), "Native");
        setContentView(web);
        web.loadUrl("file:///android_asset/index.html");
    }

    private String call(String fn, String... args) {
        try {
            PyObject result = api.callAttr(fn, (Object[]) args);
            return result == null ? "" : result.toString();
        } catch (Exception e) {
            return "{\"ok\":false,\"error\":" + quote(e.getMessage()) + "}";
        }
    }
    private String quote(String s) {
        if (s == null) s = "Unknown error";
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "\\r") + "\"";
    }
    private void js(String script) {
        handler.post(() -> web.evaluateJavascript(script, null));
    }

    public class Bridge {
        @JavascriptInterface public String init() { return call("init"); }
        @JavascriptInterface public String sendCode(String phone) { return call("send_code", phone); }
        @JavascriptInterface public String signIn(String code) { return call("sign_in", code); }
        @JavascriptInterface public String signInPassword(String password) { return call("sign_in_password", password); }
        @JavascriptInterface public String chats() { return call("get_chats"); }
        @JavascriptInterface public String messages(String id) { return call("get_messages", id); }
        @JavascriptInterface public String sendMessage(String id, String text) { return call("send_message", id, text); }
    }

    @Override public void onBackPressed() {
        js("goBackInApp()");
    }
}
