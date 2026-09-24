---
name: feedback-vira-nama-tidak-menyapa
description: "VIRA tidak boleh memanggil prospek dengan nama — nama hanya disimpan untuk Steven, selalu sapa \"kak\" (bukan \"kamu\")"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4bc2ec08-26b2-4f86-8466-f971e8e4889e
  modified: 2026-09-15T07:29:59.333Z
---

Nama prospek (STATS.nama_lengkap) hanya **disimpan** untuk catatan Steven. VIRA **tidak pernah** memakainya di balasan: bukan "Halo Aldi" dan bukan "kak Aldi", cukup "kak". VIRA juga tidak memakai "kamu".

**Why:** Steven menyampaikannya 2026-09-15 setelah v3.8 membalas "Halo Aldi, senang kenal sama kamu". Alasannya untuk mengantisipasi hal yang tidak diinginkan, misalnya nama tertangkap salah ("Dengan Aldi") atau prospek merasa terlalu akrab.

**How to apply:** berlaku untuk semua teks yang sampai ke prospek: prompt, template follow-up (`CONFIG.followup_templates` masih memuat `{nama}`), dan fitur baru apa pun. Di VIRA Personal v3.9 aturan ini dijaga dua lapis: prompt, dan penghapusan nama di Process All sebelum kirim. Untuk tenant lain (The Scholars / Persada), tanyakan dulu sebelum menerapkannya.

Terkait: [[vira-stats-terisi-v3-8]]
