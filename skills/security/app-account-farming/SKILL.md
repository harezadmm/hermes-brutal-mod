---
name: app-account-farming
description: Bypass new-user detection with device spoofing automation.
triggers:
  - Bypass new user detection
  - Generate unlimited accounts
  - Device fingerprint spoofing
  - Voucher abuse automation
  - Account farming panel
category: security
---

# App Account Farming with Device Spoofing

## When to Use
- User wants unlimited accounts for promo/voucher abuse (coffee apps, food delivery, e-commerce)
- Bypass "one account per device" restrictions
- Automate account registration with unique device fingerprints
- Build account management panel for bulk operations

## Detection Vectors

Apps detect duplicate accounts via:

### 1. Device Fingerprinting
```python
# Android device identifiers collected by apps
{
    'android_id': '16-char hex string',        # Settings.Secure.ANDROID_ID
    'imei': '15-digit number',                 # TelephonyManager.getDeviceId()
    'advertising_id': 'UUID format',           # Google Advertising ID
    'mac_address': 'AA:BB:CC:DD:EE:FF',       # WiFi MAC
    'device_brand': 'Samsung/Xiaomi/Oppo',
    'device_model': 'Galaxy A52/Redmi Note 10',
    'android_version': '11/12/13'
}
```

### 2. Network Identifiers
- IP address
- WiFi SSID/BSSID
- Mobile carrier

### 3. Account Patterns
- Email patterns (@gmail.com, @yahoo.com)
- Phone number patterns (same prefix)
- Name similarity
- Registration timestamps (too rapid)

### 4. Behavioral
- App install time
- Usage patterns
- Location/GPS data

## Device Spoofing Implementation

### Random Device Generator
```python
import random
import string
import uuid

class DeviceSpoofing:
    """Generate random device fingerprints"""
    
    @staticmethod
    def generate_android_id():
        """16-char hex Android ID"""
        return ''.join(random.choices('0123456789abcdef', k=16))
    
    @staticmethod
    def generate_imei():
        """15-digit IMEI (not Luhn-validated, sufficient for most checks)"""
        return ''.join(random.choices('0123456789', k=15))
    
    @staticmethod
    def generate_advertising_id():
        """Google Advertising ID (UUID format)"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_mac_address():
        """Random MAC address"""
        mac = [random.randint(0x00, 0xff) for _ in range(6)]
        return ':'.join(f'{x:02x}' for x in mac)
    
    @staticmethod
    def random_device(config):
        """Complete device profile"""
        brand = random.choice(config.DEVICE_BRANDS)
        model = random.choice(config.DEVICE_MODELS[brand])
        
        return {
            'android_id': DeviceSpoofing.generate_android_id(),
            'device_brand': brand,
            'device_model': model,
            'android_version': random.choice(config.ANDROID_VERSIONS),
            'imei': DeviceSpoofing.generate_imei(),
            'advertising_id': DeviceSpoofing.generate_advertising_id(),
            'mac_address': DeviceSpoofing.generate_mac_address()
        }

# Configuration
class Config:
    DEVICE_BRANDS = ['Samsung', 'Xiaomi', 'Oppo', 'Vivo', 'Realme', 'Asus']
    DEVICE_MODELS = {
        'Samsung': ['Galaxy A52', 'Galaxy A32', 'Galaxy M32', 'Galaxy S21', 'Galaxy A12'],
        'Xiaomi': ['Redmi Note 10', 'Redmi 9', 'Poco X3', 'Mi 11', 'Redmi Note 11'],
        'Oppo': ['A54', 'A74', 'Reno 5', 'A15', 'F19'],
        'Vivo': ['Y20', 'Y51', 'V21', 'Y12', 'Y33'],
        'Realme': ['C25', 'Narzo 30', '8 Pro', 'C11', 'Narzo 50'],
        'Asus': ['Zenfone 8', 'ROG Phone 5', 'Zenfone Max Pro M2']
    }
    ANDROID_VERSIONS = ['11', '12', '13']
```

### Account Data Generator
```python
class AccountGenerator:
    @staticmethod
    def generate_email():
        """Random email address"""
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
        return f"{username}@{random.choice(domains)}"
    
    @staticmethod
    def generate_phone():
        """Indonesian phone number format"""
        prefixes = ['0812', '0813', '0821', '0822', '0852', '0853', '0856']
        suffix = ''.join(random.choices('0123456789', k=8))
        return f"{random.choice(prefixes)}{suffix}"
    
    @staticmethod
    def generate_name():
        """Random Indonesian name"""
        first = ['Andi', 'Budi', 'Citra', 'Dewa', 'Eka', 'Fira', 'Gita', 'Hana']
        last = ['Pratama', 'Kusuma', 'Wijaya', 'Santoso', 'Permana', 'Saputra']
        return f"{random.choice(first)} {random.choice(last)}"
    
    @staticmethod
    def generate_password():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))
```

## Flask Panel Architecture

### Database Schema
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Account credentials
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    
    # Device fingerprint (spoofed)
    android_id = db.Column(db.String(64), unique=True)
    device_brand = db.Column(db.String(50))
    device_model = db.Column(db.String(100))
    android_version = db.Column(db.String(10))
    imei = db.Column(db.String(20))
    advertising_id = db.Column(db.String(64))
    mac_address = db.Column(db.String(17))
    
    # API tokens
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending, active, banned
    voucher_claimed = db.Column(db.Boolean, default=False)
    voucher_code = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### API Client with Device Headers
```python
class APIClient:
    def __init__(self, base_url, device_info):
        self.base_url = base_url
        self.device_info = device_info
    
    def get_headers(self):
        """Headers with device fingerprint"""
        return {
            'User-Agent': f'AppName/{self.device_info["android_version"]} (Android {self.device_info["android_version"]}; {self.device_info["device_brand"]} {self.device_info["device_model"]})',
            'X-Device-ID': self.device_info['android_id'],
            'X-Device-Brand': self.device_info['device_brand'],
            'X-Device-Model': self.device_info['device_model'],
            'X-Android-Version': self.device_info['android_version'],
            'X-Advertising-ID': self.device_info['advertising_id'],
            'Content-Type': 'application/json'
        }
    
    def register(self, account_data):
        """Register new account with spoofed device"""
        endpoint = f"{self.base_url}/api/auth/register"
        payload = {
            'email': account_data['email'],
            'phone': account_data['phone'],
            'password': account_data['password'],
            'name': account_data['name'],
            'device_id': self.device_info['android_id']
        }
        
        response = requests.post(endpoint, json=payload, headers=self.get_headers())
        return response.json()
```

## Reverse Engineering Target App

### For Flutter Apps (Common Pattern)
```bash
# 1. Decompile APK
java -jar apktool.jar d target.apk -o output
jadx target.apk -d jadx_output

# 2. Flutter apps have compiled Dart code - static analysis limited
# Check for Flutter
find output -name "flutter_assets" -o -name "libflutter.so"

# 3. Use Frida for live API extraction
```

**Frida script for network capture:**
```javascript
// Hook OkHttp (common in Flutter)
Java.perform(() => {
    const Request = Java.use('okhttp3.Request');
    
    Request.url.implementation = function() {
        const url = this.url();
        console.log('[API] ' + url);
        return url;
    };
    
    const Builder = Java.use('okhttp3.Request$Builder');
    Builder.addHeader.implementation = function(name, value) {
        console.log('[HEADER] ' + name + ': ' + value);
        return this.addHeader(name, value);
    };
});

// Hook device ID functions
Java.perform(() => {
    const Settings = Java.use('android.provider.Settings$Secure');
    Settings.getString.overload('android.content.ContentResolver', 'java.lang.String').implementation = function(resolver, name) {
        const result = this.getString(resolver, name);
        if (name === 'android_id') {
            console.log('[DEVICE] Android ID: ' + result);
        }
        return result;
    };
});
```

**Run Frida:**
```bash
# On rooted device/emulator
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server"
adb shell "/data/local/tmp/frida-server &"

# Hook app
frida -U -f com.target.app -l network_hook.js --no-pause

# Perform registration in app, monitor output for API calls
```

### Alternative: MITM Proxy
```bash
# Install mitmproxy
pip install mitmproxy

# Run proxy
mitmproxy -p 8080

# Install cert on device
adb push ~/.mitmproxy/mitmproxy-ca-cert.cer /sdcard/

# Set device proxy
adb shell settings put global http_proxy <PC_IP>:8080

# Bypass SSL pinning with Frida if needed
frida -U -f com.target.app -l ssl-bypass.js
```

## Pitfalls

1. **Server-side validation** - Some apps verify device legitimacy server-side (IMEI databases, Google SafetyNet). Cannot bypass fully.

2. **Behavioral analysis** - Rapid registrations from same IP/location flagged. Use delays and proxies.

3. **Phone verification** - SMS OTP required. Need phone number pool or SMS API service.

4. **Email verification** - Need working emails. Use temp-mail services or multiple Gmail accounts.

5. **App updates break RE** - API endpoints/headers change. Re-analyze after updates.

6. **Account bans** - Even with spoofing, patterns detected over time. Rotate everything.

7. **Flutter static analysis fails** - Compiled Dart code unreadable in JADX. Always use Frida for Flutter apps.

8. **APK download automation blocked** - MediaFire, Gofile, APKPure need JavaScript execution. Extract from device or manual download required.

## Related Skills

- `apk-vvvip-modding` - APK decompilation and analysis techniques
- `reverse-engineering-gokil` - Complete RE toolkit usage
