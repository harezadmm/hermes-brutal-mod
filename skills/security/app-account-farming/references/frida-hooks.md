# Frida Hooks for Account Farming

## Network Capture (OkHttp)

Complete hook for Flutter apps using OkHttp:

```javascript
// network_capture.js
Java.perform(() => {
    console.log('[*] Hooking OkHttp...');
    
    // Hook Request URL
    const Request = Java.use('okhttp3.Request');
    Request.url.implementation = function() {
        const url = this.url();
        console.log('[API] URL: ' + url);
        return url;
    };
    
    // Hook Request Headers
    const Builder = Java.use('okhttp3.Request$Builder');
    Builder.addHeader.implementation = function(name, value) {
        console.log('[HEADER] ' + name + ': ' + value);
        return this.addHeader(name, value);
    };
    
    // Hook Request Body
    const RequestBody = Java.use('okhttp3.RequestBody');
    RequestBody.create.overload('okhttp3.MediaType', 'java.lang.String').implementation = function(mediaType, content) {
        console.log('[REQUEST BODY] ' + content);
        return this.create(mediaType, content);
    };
    
    // Hook Response
    const Response = Java.use('okhttp3.Response');
    Response.body.implementation = function() {
        const body = this.body();
        try {
            const content = body.string();
            console.log('[RESPONSE] ' + content.substring(0, 1000));
        } catch(e) {
            console.log('[RESPONSE ERROR] ' + e);
        }
        return body;
    };
});
```

## Device ID Hooks

Hook all device identification methods:

```javascript
// device_hooks.js
Java.perform(() => {
    console.log('[*] Hooking device identifiers...');
    
    // Android ID
    const Settings = Java.use('android.provider.Settings$Secure');
    Settings.getString.overload('android.content.ContentResolver', 'java.lang.String').implementation = function(resolver, name) {
        const result = this.getString(resolver, name);
        if (name === 'android_id') {
            console.log('[DEVICE] Android ID: ' + result);
        }
        return result;
    };
    
    // IMEI / Device ID
    const TelephonyManager = Java.use('android.telephony.TelephonyManager');
    
    if (TelephonyManager.getDeviceId) {
        TelephonyManager.getDeviceId.overload().implementation = function() {
            const imei = this.getDeviceId();
            console.log('[DEVICE] IMEI: ' + imei);
            return imei;
        };
    }
    
    if (TelephonyManager.getImei) {
        TelephonyManager.getImei.overload().implementation = function() {
            const imei = this.getImei();
            console.log('[DEVICE] IMEI: ' + imei);
            return imei;
        };
    }
    
    // Google Advertising ID
    try {
        const AdvertisingIdClient = Java.use('com.google.android.gms.ads.identifier.AdvertisingIdClient');
        AdvertisingIdClient.getAdvertisingIdInfo.implementation = function(context) {
            const info = this.getAdvertisingIdInfo(context);
            const adId = info.getId();
            console.log('[DEVICE] Advertising ID: ' + adId);
            return info;
        };
    } catch(e) {
        console.log('[!] Advertising ID hook failed: ' + e);
    }
    
    // MAC Address
    const WifiManager = Java.use('android.net.wifi.WifiManager');
    WifiManager.getConnectionInfo.implementation = function() {
        const info = this.getConnectionInfo();
        const mac = info.getMacAddress();
        console.log('[DEVICE] MAC Address: ' + mac);
        return info;
    };
    
    // Build info
    const Build = Java.use('android.os.Build');
    console.log('[DEVICE] Brand: ' + Build.BRAND.value);
    console.log('[DEVICE] Model: ' + Build.MODEL.value);
    console.log('[DEVICE] Android Version: ' + Build.VERSION.RELEASE.value);
});
```

## SSL Pinning Bypass

Universal SSL pinning bypass:

```javascript
// ssl_bypass.js
Java.perform(() => {
    console.log('[*] Bypassing SSL pinning...');
    
    // Bypass TrustManager
    const TrustManager = Java.use('javax.net.ssl.X509TrustManager');
    const SSLContext = Java.use('javax.net.ssl.SSLContext');
    
    const TrustManagerImpl = Java.registerClass({
        name: 'com.custom.TrustManagerImpl',
        implements: [TrustManager],
        methods: {
            checkClientTrusted: function(chain, authType) {},
            checkServerTrusted: function(chain, authType) {},
            getAcceptedIssuers: function() { return []; }
        }
    });
    
    SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').implementation = function(km, tm, random) {
        console.log('[SSL] Bypassing certificate validation');
        this.init(km, [TrustManagerImpl.$new()], random);
    };
    
    // Bypass OkHttp CertificatePinner
    try {
        const CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function(hostname, peerCertificates) {
            console.log('[SSL] Bypassing OkHttp pinning for: ' + hostname);
            return;
        };
    } catch(e) {}
});
```

## Device Spoofing (Active)

Actively spoof device identifiers (not just monitoring):

```javascript
// device_spoof.js
const SPOOFED_ANDROID_ID = '1234567890abcdef';
const SPOOFED_IMEI = '123456789012345';
const SPOOFED_AD_ID = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee';

Java.perform(() => {
    console.log('[*] Device spoofing active...');
    
    // Spoof Android ID
    const Settings = Java.use('android.provider.Settings$Secure');
    Settings.getString.overload('android.content.ContentResolver', 'java.lang.String').implementation = function(resolver, name) {
        if (name === 'android_id') {
            console.log('[SPOOF] Returning spoofed Android ID');
            return SPOOFED_ANDROID_ID;
        }
        return this.getString(resolver, name);
    };
    
    // Spoof IMEI
    const TelephonyManager = Java.use('android.telephony.TelephonyManager');
    if (TelephonyManager.getDeviceId) {
        TelephonyManager.getDeviceId.overload().implementation = function() {
            console.log('[SPOOF] Returning spoofed IMEI');
            return SPOOFED_IMEI;
        };
    }
    
    // Spoof Advertising ID
    try {
        const AdvertisingIdClient = Java.use('com.google.android.gms.ads.identifier.AdvertisingIdClient');
        const AdvertisingIdInfo = Java.use('com.google.android.gms.ads.identifier.AdvertisingIdClient$Info');
        
        AdvertisingIdClient.getAdvertisingIdInfo.implementation = function(context) {
            console.log('[SPOOF] Returning spoofed Advertising ID');
            return AdvertisingIdInfo.$new(SPOOFED_AD_ID, false);
        };
    } catch(e) {}
});
```

## Complete Analysis Script

All-in-one script for initial analysis:

```javascript
// complete_analysis.js
console.log('[*] Account Farming Analysis Script');
console.log('[*] Hooking network, device IDs, and SSL...');

Java.perform(() => {
    // Network capture
    const Request = Java.use('okhttp3.Request');
    Request.url.implementation = function() {
        const url = this.url();
        console.log('\n=== HTTP REQUEST ===');
        console.log('URL: ' + url);
        return url;
    };
    
    const Builder = Java.use('okhttp3.Request$Builder');
    Builder.addHeader.implementation = function(name, value) {
        console.log('Header: ' + name + ': ' + value);
        return this.addHeader(name, value);
    };
    
    const Response = Java.use('okhttp3.Response');
    Response.body.implementation = function() {
        const body = this.body();
        const content = body.string();
        console.log('\n=== HTTP RESPONSE ===');
        console.log(content.substring(0, 500));
        return body;
    };
    
    // Device IDs
    const Settings = Java.use('android.provider.Settings$Secure');
    Settings.getString.overload('android.content.ContentResolver', 'java.lang.String').implementation = function(resolver, name) {
        const result = this.getString(resolver, name);
        if (name === 'android_id') {
            console.log('\n[DEVICE CHECK] Android ID: ' + result);
        }
        return result;
    };
    
    // SSL bypass
    const SSLContext = Java.use('javax.net.ssl.SSLContext');
    SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').implementation = function(km, tm, random) {
        console.log('[SSL] Certificate validation bypassed');
        this.init(km, null, random);
    };
    
    console.log('[*] All hooks installed. Perform registration in app now...');
});
```

## Usage

```bash
# 1. Push Frida server to device
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# 2. Run analysis script
frida -U -f com.target.app -l complete_analysis.js --no-pause

# 3. Perform registration in app, monitor console output

# 4. Extract API endpoints, headers, device fields from logs

# 5. Implement in panel APIClient class
```

## Output Example

```
[*] Account Farming Analysis Script
[*] Hooking network, device IDs, and SSL...
[*] All hooks installed. Perform registration in app now...

[DEVICE CHECK] Android ID: a1b2c3d4e5f6g7h8

=== HTTP REQUEST ===
URL: https://api.example.com/v1/auth/register
Header: Content-Type: application/json
Header: X-Device-ID: a1b2c3d4e5f6g7h8
Header: X-Device-Brand: Samsung
Header: X-Device-Model: Galaxy A52
Header: User-Agent: AppName/1.2.3 (Android 12; Samsung Galaxy A52)

=== HTTP RESPONSE ===
{"success":true,"token":"eyJhbGc...", "user_id":12345}
```

## Notes

- Run Frida on rooted device or emulator
- For non-rooted devices, use frida-gadget injected into APK
- Update hooks for app-specific network libraries (Retrofit, Volley, etc.)
- Some apps detect Frida - use anti-detection techniques if needed
