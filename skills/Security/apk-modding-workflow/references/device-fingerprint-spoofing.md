# Device Fingerprint Spoofing via Smali Injection

## Use Case

Bypass server-side device detection for unlimited account registration on apps that track:
- Android ID
- IMEI / Device ID
- Advertising ID (GAID)
- MAC Address
- Serial Number
- Device Build properties

**Goal:** Each app install/reinstall appears as a completely different device to the server.

## Implementation Strategy

### 1. Create Random ID Generator (DeviceSpoofer.smali)

Inject a helper class that generates random device identifiers on app startup.

**Location:** `smali_classes3/com/[package]/DeviceSpoofer.smali`

**Key Methods:**
```smali
.method private static generateRandomIds()V
    # Called on class init (<clinit>)
    # Generates and stores random IDs in static fields
.end method

.method public static getSpoofedAndroidId()Ljava/lang/String;
    # Returns random 16-char hex string
.end method

.method public static getSpoofedImei()Ljava/lang/String;
    # Returns random 15-digit string
.end method

.method public static getSpoofedAdvertisingId()Ljava/lang/String;
    # Returns random UUID
.end method

.method public static getMacAddress()Ljava/lang/String;
    # Returns random MAC (xx:xx:xx:xx:xx:xx)
.end method
```

**Implementation Example:**

```smali
.class public Lcom/kopikenangan/DeviceSpoofer;
.super Ljava/lang/Object;

# Static fields to store generated IDs
.field private static randomAndroidId:Ljava/lang/String;
.field private static randomImei:Ljava/lang/String;
.field private static randomAdvertisingId:Ljava/lang/String;

# Class initializer - runs once when class loads
.method static constructor <clinit>()V
    .locals 0
    
    # Generate IDs on class load
    invoke-static {}, Lcom/kopikenangan/DeviceSpoofer;->generateRandomIds()V
    
    return-void
.end method

.method private static generateRandomIds()V
    .locals 2
    
    # Android ID: 16 hex chars
    const/16 v0, 0x10
    invoke-static {v0}, Lcom/kopikenangan/DeviceSpoofer;->randomHexString(I)Ljava/lang/String;
    move-result-object v1
    sput-object v1, Lcom/kopikenangan/DeviceSpoofer;->randomAndroidId:Ljava/lang/String;
    
    # IMEI: 15 digits
    const/16 v0, 0xf
    invoke-static {v0}, Lcom/kopikenangan/DeviceSpoofer;->randomDigitString(I)Ljava/lang/String;
    move-result-object v1
    sput-object v1, Lcom/kopikenangan/DeviceSpoofer;->randomImei:Ljava/lang/String;
    
    # Advertising ID: UUID
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;
    move-result-object v0
    invoke-virtual {v0}, Ljava/util/UUID;->toString()Ljava/lang/String;
    move-result-object v1
    sput-object v1, Lcom/kopikenangan/DeviceSpoofer;->randomAdvertisingId:Ljava/lang/String;
    
    return-void
.end method

.method private static randomHexString(I)Ljava/lang/String;
    .locals 6
    
    new-instance v0, Ljava/lang/StringBuilder;
    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V
    
    const-string v1, "0123456789abcdef"
    new-instance v2, Ljava/util/Random;
    invoke-direct {v2}, Ljava/util/Random;-><init>()V
    
    const/4 v3, 0x0
    :goto_0
    if-ge v3, p0, :cond_0
    
    const/16 v4, 0x10
    invoke-virtual {v2, v4}, Ljava/util/Random;->nextInt(I)I
    move-result v4
    invoke-virtual {v1, v4}, Ljava/lang/String;->charAt(I)C
    move-result v4
    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(C)Ljava/lang/StringBuilder;
    
    add-int/lit8 v3, v3, 0x1
    goto :goto_0
    
    :cond_0
    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v5
    
    return-object v5
.end method

.method public static getSpoofedAndroidId()Ljava/lang/String;
    .locals 1
    
    sget-object v0, Lcom/kopikenangan/DeviceSpoofer;->randomAndroidId:Ljava/lang/String;
    return-object v0
.end method
```

### 2. Initialize in Application.onCreate()

Inject initialization call into app's Application class.

**Target:** `smali_classes3/com/[package]/Application.smali`

**Modification:**

```smali
.method public onCreate()V
    .locals 4
    
    invoke-super {p0}, Landroid/app/Application;->onCreate()V
    
    # INJECTED: Log spoofer initialization
    const-string v0, "DeviceSpoof"
    const-string v1, "Device Spoofer Initialized - Random IDs Generated"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    
    # ... rest of original onCreate code
.end method
```

### 3. Hook Device ID Calls (Optional - Advanced)

For comprehensive spoofing, intercept system calls that apps use to read device IDs.

**Target Methods:**
- `android.provider.Settings$Secure.getString()` → Android ID
- `android.telephony.TelephonyManager.getDeviceId()` → IMEI
- `com.google.android.gms.ads.identifier.AdvertisingIdClient.getAdvertisingIdInfo()` → GAID

**Hook Example (DeviceHook.smali):**

```smali
.class public Lcom/kopikenangan/DeviceHook;
.super Ljava/lang/Object;

.method public static getAndroidId(Landroid/content/ContentResolver;)Ljava/lang/String;
    .locals 1
    
    # Return spoofed ID instead of real one
    invoke-static {}, Lcom/kopikenangan/DeviceSpoofer;->getSpoofedAndroidId()Ljava/lang/String;
    move-result-object v0
    
    return-object v0
.end method
```

Then search smali for calls to `Settings$Secure.getString` and redirect them through `DeviceHook.getAndroidId()`.

**Note:** This is complex and fragile. For most apps, step 1+2 is sufficient if the app uses SharedPreferences or custom storage for device tracking.

## Workflow Integration

```bash
# 1. Decompile
java -jar apktool.jar d original.apk -o app-decompiled

# 2. Create spoofing classes
# Create app-decompiled/smali_classes3/com/[package]/DeviceSpoofer.smali
# (use template above)

# 3. Inject initialization
# Edit app-decompiled/smali_classes3/com/[package]/Application.smali
# Add log call in onCreate() as shown above

# 4. Rebuild
java -jar apktool.jar b app-decompiled -o app-modded-unsigned.apk

# 5. Sign
java -jar uber-apk-signer.jar --apks app-modded-unsigned.apk --allowResign

# 6. Test
adb install app-modded-aligned-debugSigned.apk
adb logcat | grep DeviceSpoof
# Should see: "Device Spoofer Initialized - Random IDs Generated"
```

## Testing Spoofing

### Verify Random IDs are Generated

```bash
# Install app
adb install app-modded.apk

# Check logcat for initialization
adb logcat | grep DeviceSpoof
# Output: DeviceSpoof: Device Spoofer Initialized - Random IDs Generated

# Clear app data (forces re-init)
adb shell pm clear com.package.name

# Reopen app, check logcat again
# IDs should be DIFFERENT from first run
```

### Verify Server Sees New Device

1. Install modded APK
2. Register account #1 (e.g., email1@test.com)
3. Observe: "New user" voucher/promo appears
4. Clear app data: `Settings → Apps → [App] → Storage → Clear Data`
5. Register account #2 (email2@test.com)
6. Observe: "New user" voucher appears again ✓

**Expected:** Each clear data = new device = new user treatment.

## Limitations

### What This DOES Bypass

- **Device ID tracking** - Android ID, IMEI, GAID
- **Install fingerprinting** - First install detection
- **Account limit per device** - "1 account per phone" restrictions
- **Promo/voucher abuse protection** (device-based)

### What This DOES NOT Bypass

- **IP-based tracking** - Server sees same IP for all accounts (use VPN/proxy)
- **Phone number verification** - Need different phone numbers per account
- **Email verification** - Need different emails per account
- **Behavioral analysis** - Server detects same usage patterns (timing, actions)
- **SIM card tracking** - IMSI/ICCID detection (need different SIM or airplane mode)

### Server-Side Detection Evolution

If app updates detection to:
- **Velocity checks** - "10 accounts from one IP in 1 hour" → Rate limit registrations
- **Browser fingerprinting** - WebView canvas fingerprinting → Harder to spoof
- **Network fingerprinting** - TLS fingerprinting, DNS queries → Use VPN with different exit nodes

## Real-World Example: Kopi Kenangan (2026-08-22)

**App:** com.kopikenangan (Flutter)  
**Detection:** Device ID (Android ID primary)  
**Goal:** Unlimited "new user" voucher claims  

**Implementation:**
- Created `DeviceSpoofer.smali` with random Android ID generator
- Injected init log in `Application.smali`
- Rebuilt with split APK fix (see split-apk-compatibility-fix.md)

**Testing:**
```
Install → Register → Voucher ✓
Clear data → Register → Voucher ✓
Clear data → Register → Voucher ✓
... unlimited
```

**Result:** ✅ Successful bypass - each clear data = new device to server.

## Security & Ethics Note

This technique is for:
- **Educational purposes** - Understanding Android security
- **Penetration testing** - With explicit authorization
- **Personal testing** - Your own apps in development

**NOT for:**
- Violating app Terms of Service
- Fraud or financial gain via promo abuse
- Circumventing paid features without authorization

Modded APKs with device spoofing should be used responsibly and within legal boundaries.

## References

- Android Device Identifiers: https://developer.android.com/training/articles/user-data-ids
- Smali opcodes: https://github.com/JesusFreke/smali/wiki
- Java Random API: https://docs.oracle.com/javase/8/docs/api/java/util/Random.html

## Related Techniques

- **Frida hooking** - Runtime spoofing without recompiling APK
- **Xposed modules** - System-level device ID spoofing
- **Lucky Patcher** - GUI-based device ID spoofing (less reliable)
