# Membungkus Kertas jadi APK Android

Tujuannya satu: **pengingat yang tetap berbunyi saat Kertas ditutup total.**

Di browser dan PWA itu tidak mungkin — penjadwalannya cuma hidup selama tabnya hidup. Di dalam APK, jadwal alarmnya dititipkan ke penjadwal Android, sama seperti alarm bawaan HP. Tidak butuh server, tidak butuh Firebase, tidak butuh Play Store.

Isi kodenya sudah siap. Yang belum ada cuma perkakas build-nya di komputermu.

---

## Sebelum mulai, satu hal yang harus kamu putuskan

**Login Google kemungkinan besar tidak jalan di dalam APK.**

Google memblokir alur login OAuth yang dijalankan di dalam *WebView* aplikasi — itu kebijakan keamanan mereka, berlaku untuk semua app, bukan cuma Kertas. Yang muncul biasanya `403: disallowed_useragent`. Capacitor memakai WebView.

Jadi APK versi pertama ini realistisnya:

| | Jalan? |
|---|---|
| Menulis catatan & tugas | ✅ |
| **Pengingat saat app tertutup** | ✅ ← ini yang kita kejar |
| Simpan offline di HP | ✅ |
| Sinkron ke Google Drive | ⚠️ mungkin tertolak |

Tiga sikap yang masuk akal, pilih satu:

1. **Coba dulu, lihat hasilnya.** Ada kemungkinan lolos. Kalau tertolak, APK-nya tetap berguna sebagai app pengingat, dan sinkron Drive kamu kerjakan lewat versi PWA di browser — datanya sama karena disimpan per perangkat lalu naik ke Drive.
2. **Benahi auth-nya dulu.** Alur login dipindah ke Chrome Custom Tabs (`@capacitor/browser` + deep link balik ke app). Ini pekerjaan tambahan yang nyata, dan tidak bisa saya uji tanpa Android Studio di komputermu.
3. **APK khusus Android, PWA untuk sisanya.** Di iPhone dan laptop tetap pakai PWA seperti biasa.

Saya sarankan **nomor 1** — buktikan dulu, jangan mengarang masalah sebelum kelihatan.

---

## Yang perlu dipasang lebih dulu

Komputermu sekarang belum punya satu pun dari ini.

| Perkakas | Untuk apa | Dari mana |
|---|---|---|
| **Node.js LTS** | menjalankan Capacitor | [nodejs.org](https://nodejs.org) |
| **JDK 21** | mengompilasi Android | ikut terpasang bersama Android Studio |
| **Android Studio** | SDK Android + pembuat APK | [developer.android.com/studio](https://developer.android.com/studio) |

Android Studio besar (±1 GB) dan pemasangannya lama. Sekali saja.

Setelah Android Studio terpasang, buka sekali, biarkan ia mengunduh **Android SDK Platform 35** lewat *SDK Manager*.

---

## Langkah build

Semua dijalankan dari folder `Kertas` (yang berisi `capacitor.config.json`).

### 1. Pasang dependensi

```bash
npm install
```

### 2. Buat proyek Android

```bash
npx cap add android
```

Muncul folder `android/` baru. Itu proyek Android asli — boleh dibuka di Android Studio.

### 3. Beri izin alarm & notifikasi

Buka `android/app/src/main/AndroidManifest.xml`. Di dalam `<manifest>` tapi **di luar** `<application>`, tambahkan:

```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
```

Fungsinya berurutan: boleh menampilkan notifikasi (wajib sejak Android 13), boleh menjadwalkan alarm **tepat waktu** (bukan digeser-geser demi hemat baterai), dan alarmnya **selamat melewati HP di-restart**.

### 4. Salin isi app ke proyek Android

```bash
npx cap sync android
```

Perintah ini menyalin seluruh isi folder `pwa/` ke dalam proyek Android. **Ulangi tiap kali kamu mengubah `pwa/index.html`.**

### 5. Bikin APK-nya

```bash
npx cap open android
```

Android Studio terbuka. Tunggu Gradle selesai (pertama kali bisa 5–10 menit), lalu menu **Build → Build Bundle(s) / APK(s) → Build APK(s)**.

Hasilnya di:

```
android/app/build/outputs/apk/debug/app-debug.apk
```

### 6. Pasang di HP

Salin APK ke HP, ketuk berkasnya, izinkan *install from unknown sources*. Atau colok HP lewat kabel dengan USB debugging menyala, lalu:

```bash
npx cap run android
```

---

## Setelah terpasang

1. Buka Kertas → tab **Sync** → bagian **Pengingat** akan berbunyi **"Notifikasi Kertas — dijadwalkan oleh Android"**. Kalau tulisannya masih "hanya bunyi selama app terbuka", berarti kamu membuka versi PWA, bukan APK-nya.
2. Nyalakan sakelarnya, izinkan notifikasi.
3. Uji beneran: bikin tugas dengan pengingat **2 menit lagi**, lalu **tutup Kertas sepenuhnya** — usap keluar dari daftar app terbaru. Kalau notifikasinya tetap muncul, selesai.

Kalau alarmnya meleset beberapa menit, HP-mu kemungkinan mengoptimasi baterai app ini. Setelan → Aplikasi → Kertas → Baterai → **Tidak dibatasi**. Ini khas HP Xiaomi, Oppo, Vivo, dan Samsung.

---

## Catatan teknis

- **Batas 64 alarm.** Android membatasi jumlah alarm tertunda per app. Kertas menjadwalkan 64 pengingat terdekat; kalau ada lebih, sisanya dicatat di **Catatan aktivitas** — tidak dibuang diam-diam, dan ikut terjadwal begitu yang di depan berbunyi.
- **Ikon notifikasi.** Sekarang memakai ikon app, yang oleh Android dirender jadi siluet putih. Kalau mau ikon khusus, taruh PNG putih-transparan di `android/app/src/main/res/drawable/ic_stat_kertas.png`, lalu tambahkan `"smallIcon": "ic_stat_kertas"` di bagian `LocalNotifications` pada `capacitor.config.json`.
- **iPhone.** Folder `ios/` sengaja tidak dibuat. Membangun app iOS butuh Mac untuk menjalankan Xcode dan langganan Apple Developer $99/tahun untuk memasangnya lebih dari 7 hari. Di iPhone, pakai PWA + pengingat Google Calendar seperti sebelumnya.
- **Satu berkas untuk dua-duanya.** `pwa/index.html` tidak bercabang jadi dua versi. Ia memeriksa apakah Capacitor ada; kalau tidak ada, semuanya kembali ke perilaku web lama persis seperti semula.
