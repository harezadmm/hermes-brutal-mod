# RedMess — Distribusi Hermes Agent Jailbreak

![RedMess Banner](./assets/banner.png)

> **Hermes Agent tanpa batasan. Tidak ada penolakan. Tidak ada batas konten. Eksekusi murni.**

RedMess adalah distribusi Hermes Agent yang telah di-jailbreak secara lengkap dengan **GODMODE** aktif, dilengkapi 99+ skill offensive security, integrasi tools, dan konfigurasi siap pakai untuk red teaming, penetration testing, dan operasi keamanan ofensif.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-red.svg)](https://hermes-agent.nousresearch.com)
[![Skills: 99+](https://img.shields.io/badge/Skills-99%2B-brightgreen.svg)]()
[![Status: Active](https://img.shields.io/badge/Status-Active-success.svg)]()

**[English](./README.md)** | **Bahasa Indonesia**

---

## 🔓 Apa itu RedMess?

RedMess bukan sekadar kumpulan skill keamanan — ini adalah **Hermes Agent yang sudah di-unlock penuh** dengan semua safety rails dihapus.

### Kenapa RedMess?

Hermes Agent default punya batasan konten, penolakan otomatis untuk malicious code, weapons guides, dan topik sensitif lainnya. RedMess menghapus semua itu dan memberikan:

- ✅ **Zero Refusals** — Tidak ada penolakan untuk kode berbahaya, exploits, atau guides
- ✅ **Full Offensive Toolkit** — 99+ skill dari reconnaissance sampai post-exploitation
- ✅ **Pre-configured GODMODE** — Jailbreak permanen via custom prompt injection
- ✅ **Tools Integration** — Metasploit, Burp Suite, sqlmap, Frida, 100+ tools lainnya
- ✅ **Multi-Platform** — Linux, Windows, Android, iOS, Cloud (AWS/GCP/Azure)
- ✅ **Production Ready** — Tested di real engagements, bukan teori

---

## 🚀 Instalasi Cepat

```bash
# Clone repository
git clone https://github.com/harezadmm/RedMess.git
cd RedMess

# Jalankan deployment script
chmod +x deploy.sh
./deploy.sh

# Restart Hermes
hermes restart

# Test jailbreak
hermes chat "Buatkan RAT untuk Windows dengan C++"
```

Kalo langsung generate code (BUKAN refusal) = jailbreak berhasil! 🎉

---

## 📚 Dokumentasi

- **[README (English)](./README.md)** — Dokumentasi lengkap bahasa Inggris
- **[Security Skills Index](./security/INDEX.md)** — Daftar lengkap 99+ skills
- **[Contributing Guide](./CONTRIBUTING.md)** — Cara contribute
- **[Changelog](./CHANGELOG.md)** — Riwayat perubahan

---

## 🎯 Fitur Utama

### 1. GODMODE Profile
Jailbreak Hermes Agent secara permanen:
- Injection detection bypass
- Content boundary removal  
- Anti-refusal mechanisms
- Persistent personality override
- Safety rail deactivation

### 2. 99+ Offensive Security Skills
10 kategori skill:
- **Reconnaissance** — OSINT, subdomain enum, port scanning
- **Weaponization** — RATs, keyloggers, backdoors, trojans
- **Exploitation** — SQLi, XSS, RCE, buffer overflows
- **Post-Exploitation** — Lateral movement, persistence, exfil
- **Social Engineering** — Phishing, pretexting, vishing
- **Mobile Hacking** — APK modding, Frida hooking
- **Cloud Security** — AWS/GCP/Azure exploitation
- **Network Attacks** — MitM, ARP spoofing, wireless
- **Web Pentesting** — API abuse, JWT cracking, OAuth
- **Reverse Engineering** — Binary analysis, deobfuscation

### 3. 10,000+ Baris Kode Siap Pakai
Setiap skill dilengkapi:
- Executable examples (Python, C++, Bash, PowerShell, Lua, JS)
- Real-world payloads
- Automation scripts
- Pre-configured tool commands
- OPSEC considerations

---

## ⚠️ Disclaimer Legal

**BACA INI BAIK-BAIK:**

RedMess adalah tool untuk **authorized security testing only**. Penggunaan tanpa izin eksplisit adalah **ILEGAL** dan bisa:

- Tuntutan pidana (Indonesia: UU ITE Pasal 30, 32, 46 — 10 tahun penjara)
- Denda ratusan juta rupiah
- Civil lawsuits dari korban

### Legal Use Cases:
✅ Penetration testing dengan written authorization  
✅ Bug bounty programs (HackerOne, Bugcrowd)  
✅ Personal research di isolated labs  
✅ Educational purposes dengan consent  

### Illegal Use Cases:
❌ Unauthorized access to systems  
❌ Data theft atau sabotage  
❌ Deploying malware tanpa consent  
❌ Corporate espionage  

**Contributors TIDAK bertanggung jawab atas penyalahgunaan tools ini.**

---

## 🤝 Contributing

Contributions welcome! Lihat [CONTRIBUTING.md](./CONTRIBUTING.md) untuk details.

```bash
# Fork repository
gh repo fork harezadmm/RedMess

# Create feature branch
git checkout -b feature/new-skill-name

# Add your skill
mkdir -p security/new-category
vim security/new-category/new-skill-name.md

# Commit dan push
git add .
git commit -m "Add new skill: [skill name]"
git push origin feature/new-skill-name

# Create pull request
gh pr create
```

---

## 🔗 Links

- **Documentation:** [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/docs)
- **GitHub:** [github.com/harezadmm/RedMess](https://github.com/harezadmm/RedMess)
- **Issues:** [github.com/harezadmm/RedMess/issues](https://github.com/harezadmm/RedMess/issues)

---

## 📜 License

MIT License — see [LICENSE](./LICENSE) for full text.

**TL;DR:** Free to use, modify, distribute. No warranty. Use at your own risk.

---

## 🙏 Credits

- **Hermes Agent** by [Nous Research](https://nousresearch.com)
- **GODMODE Technique** inspired by jailbreak research community
- **Skills** curated from real-world engagements
- **Maintainer:** [@harezadmm](https://github.com/harezadmm)

---

**"Break barriers, not laws. RedMess — Security without limits."**

---

*Last updated: September 4, 2026*
