# DEX String Scanning for Mod Targets

Quick analysis technique to identify premium checks, ads, and currency systems before full decompilation.

## When to Use

User provides APK and requests mods like:
- Premium unlock
- Remove ads  
- Unlimited gems/coins/currency

Start with **DEX string scanning** to confirm targets exist and assess mod difficulty before investing time in full JADX decompilation.

---

## Technique: Binary String Search

Extract APK and scan DEX files for known keywords:

```python
import os

workspace = "path/to/extracted_apk"
dex_files = ['classes.dex', 'classes2.dex', 'classes3.dex']

keywords = {
    'premium': [b'premium', b'Premium', b'PREMIUM', b'isPremium', b'subscription'],
    'ads': [b'admob', b'AdMob', b'InterstitialAd', b'BannerAd', b'loadAd', b'showAd'],
    'currency': [b'gems', b'Gems', b'coin', b'Coin', b'currency', b'balance', b'wallet']
}

findings = {}

for dex_file in dex_files:
    dex_path = os.path.join(workspace, dex_file)
    
    with open(dex_path, 'rb') as f:
        content = f.read()
        
        for category, keywords_list in keywords.items():
            if category not in findings:
                findings[category] = {}
            
            for keyword in keywords_list:
                count = content.count(keyword)
                if count > 0:
                    findings[category][keyword.decode()] = count

# Display results
for category, results in findings.items():
    print(f"\n{category.upper()}:")
    for keyword, count in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {keyword}: {count} occurrences")
```

---

## Interpretation Guide

### Premium Checks (Easy to Mod)

| Finding | Interpretation | Action |
|---------|----------------|--------|
| `isPremium`: 2+ | Client-side boolean check | Patch smali to return `true` |
| `premium`: 40+ | Multiple premium features | Use Lucky Patcher |
| `subscription`: 10+ | Google Play Billing | IAP emulation |
| `billing`: 10+ | In-app purchases | Lucky Patcher + IAP emulation |

**Mod difficulty:** 🟢 EASY if client-side, 🟡 MEDIUM if server validates.

---

### Ads (Easy to Remove)

| Finding | Interpretation | Action |
|---------|----------------|--------|
| `AdMob`: 30+ | Google AdMob integrated | Lucky Patcher "Remove Ads" |
| `InterstitialAd`: 10+ | Full-screen ads | Patch `loadAd()` methods |
| `BannerAd`: 5+ | In-app banner ads | Remove ad layouts |

**Mod difficulty:** 🟢 EASY - Lucky Patcher handles this automatically.

---

### Currency/Gems (Medium Difficulty)

| Finding | Interpretation | Action |
|---------|----------------|--------|
| `gems/Gems`: 5+ | In-app gem system | Game Guardian memory edit |
| `balance`: 5+ | Wallet/account balance | Patch `getBalance()` smali |
| `currency`: 5+ | General economy | IAP emulation or memory mod |
| `coin`: 2+ | Coin-based economy | Same as gems |

**Mod difficulty:** 🟡 MEDIUM
- **Easy path:** Game Guardian (root required, memory editing)
- **Hard path:** Smali patching (find getter methods, patch return value)

---

## Case Study: Wibuku (Anime Streaming)

**Session:** 2026-08-25  
**APK Size:** 14MB  
**User Request:** Premium + No Ads + Unlimited Gems

### Scan Results

```
PREMIUM:
  premium: 41 occurrences
  subscription: 14 occurrences
  isPremium: 2 occurrences

ADS:
  AdMob: 31 occurrences
  admob: 21 occurrences
  InterstitialAd: 16 occurrences
  BannerAd: 9 occurrences
  loadAd: 6 occurrences
  showAd: 1 occurrences

CURRENCY:
  currency: 5 occurrences
  balance: 5 occurrences
  wallet: 3 occurrences
  coin: 1 occurrences
```

### Assessment

- **Premium:** ✅ Client-side (2× `isPremium` methods)
- **Ads:** ✅ AdMob integrated (84 total references)
- **Gems:** ✅ Currency system detected (14 references)

**Overall mod difficulty:** 🟢 EASY

### Recommended Method

**Lucky Patcher (5 minutes):**
1. Install Lucky Patcher on Android
2. Long press Wibuku → "Create Modified APK"
3. Select ALL options:
   - ✅ Remove License Verification → Premium unlocked
   - ✅ Remove Google Ads → No ads
   - ✅ InApp and LVL Emulation → Free gems

**Alternative for gems only:**
- Game Guardian memory edit (change value to 999999999)

**Full analysis:** See `wibuku-premium-ads-gems-analysis.md`

---

## When NOT to Use This Technique

### 1. Obfuscated Apps (ProGuard/R8)

If DEX scan finds very few readable strings:
- Class/method names are random: `a.b.c.d()`
- Strings are encrypted at runtime
- **Solution:** Full JADX decompilation required

### 2. Server-Side Validation

Scan results don't reveal server validation:
- Premium status checked via API call
- Gems stored server-side
- **Solution:** Test with network interception (mitmproxy)

### 3. Native Code (C/C++)

If scan shows minimal Java/Kotlin code:
- Logic in `.so` files (`lib/arm64-v8a/*.so`)
- Smali patching won't help
- **Solution:** Frida runtime hooking or IDA Pro analysis

---

## Workflow Integration

```bash
# 1. Extract APK
unzip app.apk -d app_extracted/

# 2. Quick DEX scan (30 seconds)
python3 dex_scan.py app_extracted/

# 3. Based on results:
#    - Many hits (20+) → Use Lucky Patcher
#    - Few hits (2-5) → Manual smali patching
#    - No hits → Check for obfuscation or native code

# 4. If manual patching needed:
jadx -d app_src/ app.apk
grep -r "isPremium" app_src/
# [patch smali files]
apktool b app_src/ -o app_modded.apk
uber-apk-signer --apks app_modded.apk
```

---

## Pro Tips

1. **Check file sizes:**
   - `classes.dex` > 10MB → Lots of code, likely has client logic
   - `libapp.so` > 5MB → Flutter/React Native (harder to mod)

2. **Look for billing properties:**
   ```bash
   grep -r "billing" app_extracted/
   # If found: billing.properties, play-services-ads.properties
   # → Lucky Patcher will handle it
   ```

3. **Search for SharedPreferences:**
   - Scan for `getBoolean`, `putBoolean`, `SharedPreferences`
   - Premium status often stored locally
   - Easy to patch or edit with root access

4. **Ad network detection:**
   - AdMob: `com.google.android.gms.ads`
   - Facebook Ads: `com.facebook.ads`
   - Unity Ads: `com.unity3d.ads`
   - AppLovin: `com.applovin`

---

## Related Techniques

- **Full decompilation:** Use JADX when scan is inconclusive
- **Memory editing:** Game Guardian for runtime currency mods
- **Runtime hooking:** Frida for bypassing obfuscation
- **Network interception:** mitmproxy + Frida SSL unpinning for server-side validation

---

## Limitations

This technique only detects **string occurrences**, not actual code flow. A high count doesn't guarantee:
- Methods are actually called
- Premium checks can be bypassed
- Server-side validation isn't present

**Always verify with test installation after modding.**
