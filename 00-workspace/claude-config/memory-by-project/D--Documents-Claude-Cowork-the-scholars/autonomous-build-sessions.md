---
name: autonomous-build-sessions
description: "Steven wants build work continued autonomously when he's away/asleep, using leftover session tokens"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6665d2ba-65c0-4b15-972c-840f131cad35
  modified: 2026-08-25T18:46:52.367Z
---

Ketika Steven bilang "gas", "lanjut", atau menyatakan dia mau tidur/pergi: lanjutkan
membangun sendiri tanpa menunggu konfirmasi per langkah, dan pakai sisa token di
sesi 5 jam untuk meneruskan pekerjaan berikutnya. Dia minta ini eksplisit
(2026-08-26): *"kalau sudah lanjut langsung ke sesi yang bisa kamu build lagi
sembari aku tidur, setiap sesi jika masih ada sisa token pada 5 hour session kita,
lanjutkan build lagi"*.

**Why:** Dia bekerja freelance di sela pekerjaan BCA, jadi jam produktifnya sempit.
Menunggu jawabannya untuk keputusan kecil membuang jendela kerja yang sudah tipis.

**How to apply:**
- Kerjakan yang keputusannya sudah jelas; jangan berhenti untuk bertanya hal kecil.
- **Tetap berhenti** untuk hal yang mengubah sistem produksi live secara berisiko,
  atau yang butuh trade-off bisnis (mis. toleransi data basi) — bangun sebagai draft
  + dokumen usulan, jangan diterapkan diam-diam.
- Kirim deliverable sambil jalan (`SendUserFile`), jangan ditumpuk sampai akhir —
  dia mungkin bangun di tengah.
- Tulis penyimpangan dari rencana beserta alasannya; dia membaca diff dan changelog
  langsung, bukan ringkasan.
- Jangan pernah mengaku sesuatu sudah diuji kalau belum. Bedakan tegas "lulus QA
  otomatis" dari "sudah dites di n8n asli".

Terkait: [[vira-stats-archiving-plan]], [[content-style-document-process]]
