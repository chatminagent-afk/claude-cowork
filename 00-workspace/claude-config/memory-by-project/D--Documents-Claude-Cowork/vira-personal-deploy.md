---
name: vira-personal-deploy
description: "VIRA Personal (bot pribadi Steven) — status rebuild pra-deploy per 2026-08-28, keputusan arsitektur, dan sisa pekerjaan"
metadata: 
  node_type: memory
  type: project
  originSessionId: f6ca17f2-bcfc-4752-befc-322afd3d566f
  modified: 2026-08-28T15:30:30.689Z
---

VIRA Personal = klien ke-3 setelah The Scholars dan Persada Cisoka Residence ([[vira-dashboard]], [[persada-cisoka-residence]]). Spreadsheet "VIRA Steven Database" (`1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk`), webhook path `wa-inbound-steven`.

Keputusan yang diambil Steven 2026-08-28:
- **Semua workflow Personal memakai kredensial n8n bersama `Google Service Account - VIRA Dashboard`** (id `5KD9A3Tef1H8UQKk`) — bukan service account sendiri seperti TS dan Persada. Konsekuensi: SA itu harus di-share Editor ke spreadsheet VIRA Steven Database.
- **MSG_BUFFER cleanup tidak pakai workflow sendiri** — didaftarkan sebagai job tenant `personal` di `GLOBAL - Sheet Cleanup`. File `VIRA-Personal-Buffer-Cleanup.json` sengaja tidak dideploy.
- **Error Notifier tetap per-klien** (di-rebuild lengkap jadi 8 node dengan rantai fallback email), bukan pindah ke draft `GLOBAL - VIRA Error Notifier`. Digabung nanti setelah Personal stabil.

Fakta arsitektur yang mudah salah diingat:
- **Tidak ada node Google Drive di seluruh workflow VIRA** (TS, Persada, Personal). Media diunduh HTTP Request polos ke URL publik Drive — jadi file Drive wajib "Anyone with the link", dan tidak ada kredensial Drive yang bisa diganti.
- **Kredensial Kirimi tidak disimpan sebagai credential n8n**, melainkan di tab CONFIG (`bot_wa_number` B7, `kirimi_user_code` B10, `kirimi_secret` B11, `kirimi_device_id` B12) lalu disebar node `Parse Config`. Nomor baris sudah bergeser dari checklist 2026-08-16 yang menyebut B11/B12.

Status per 2026-08-29 malam: B, D (1-6), E SUDAH. Landing page publik sudah dideploy ke Cloudflare (tinyurl.com/virapage) dan menggantikan rencana 5 dokumen Drive — tab LINKS tinggal 2 baris (landing-page + instagram, keduanya Tipe=website). STATS Cleanup aktif, GLOBAL Sheet Cleanup sudah menggantikan 3 cleanup lama. SISA: (a) import ABOUT_STEVEN.csv + LINKS.csv dari sheet/2026-08-29-import, (b) beli nomor WA + kredensial Kirimi -> CONFIG baris 7/10/11/12 + webhook wa-inbound-steven, (c) aktifkan Main, (d) uji error notifier dengan sengaja bikin gagal. Ditunda: Follow-up dan rotasi secret Kirimi.

Keputusan 2026-08-29: VIRA BOLEH menyebut nama klien (The Scholars, Persada Cisoka Residence) beserta tujuan sistemnya — baris PANTANGAN nama klien di ABOUT_STEVEN diganti jadi BATASAN data klien (nama boleh, isi percakapan/leads/angka penjualan tetap tidak boleh). Pantangan nama employer (bank) dan teknis internal TETAP berlaku.

Project TIM Interior (#673938546771) memang sudah tidak jalan — bukan masalah yang perlu dikejar.

Sisa pekerjaan ada di `VIRA\VIRA Steven\docs\2026-08-28-panduan-deploy-VIRA-Personal.md`. Yang paling menghambat: 5 baris tab LINKS (`company-profile`, `deck-vira`, `demo-video`, `portfolio`, `harga-ringkas`) semuanya masih menunjuk satu file Drive placeholder yang sama, dan Steven belum beli nomor WA baru untuk Kirimi.

Sudah diputuskan 2026-08-28: VIRA Personal MASUK VIRA Dashboard sebagai tenant ke-3 `personal`. Entri sudah ditambahkan ke `tenants.js`, akun super `steven` diberi akses (tanpa akun/password baru), workflow sudah di-rebuild. Perangkap yang ditemukan: Dashboard API yang live sekarang dibangun dari `tenants.js` SEBELUM field `logo` ada -- import ulang otomatis ikut menaikkan fitur logo, jadi logo The Scholars akan mulai tampil di dashboard mereka.

Jebakan kredensial (kena 2026-08-29): penggantian ke `Google Service Account - VIRA Dashboard` HANYA berlaku untuk node Google Sheets. Node `Kirim Email (Gmail)` di GLOBAL - Email Fallback Notifier harus tetap `Gmail account` (gmailOAuth2, `hC4iEn4w0FA6Tmxd`) — service account tidak punya mailbox, dan domain-wide delegation cuma ada di Google Workspace, bukan Gmail konsumen. Gejalanya: `400 FAILED_PRECONDITION`. Di seluruh workflow VIRA cuma ada 1 node email yang live.

Jebakan kredensial kedua (2026-08-29): credential n8n `Gmail account` memakai OAuth Client dari GCP project #673938546771 yang SUDAH DIHAPUS -> `403 PERMISSION_DENIED`. Nomor project itu = project TIM Interior (lihat TIM Interior/v4/2026-06-13-catatan-v4.md), bukan project VIRA (`vira-506713`). Artinya TIM Interior v4 kemungkinan ikut mati karena catatan yang sama menyebut project itu untuk kuota Sheets-nya — BELUM dicek. Steven pilih memperbaiki OAuth Gmail (bukan pindah ke Brevo/Resend). Wajib publish OAuth consent screen ke Production: scope gmail.send itu restricted, dan selama status Testing refresh token mati tiap 7 hari.
