const pptxgen = require("pptxgenjs");
const path = require("path");

// ─── PALETTE ────────────────────────────────────────────────────────────────
const C = {
  bg      : "0A0F1E",   // very dark navy
  card    : "111827",   // dark card bg
  card2   : "1B2538",   // card alt
  cyan    : "22D3EE",   // bright teal accent
  cyanDark: "0891B2",
  amber   : "F59E0B",
  green   : "10B981",
  red     : "EF4444",
  white   : "F8FAFC",
  muted   : "94A3B8",
  dim     : "475569",
  border  : "1E293B",
};

const OUT = "/sessions/friendly-funny-johnson/mnt/the scholars/enhancement mock booking/MockBooking_PitchDeck.pptx";

// ─── HELPERS ─────────────────────────────────────────────────────────────────

function mkShadow() {
  return { type: "outer", color: "000000", blur: 12, offset: 4, angle: 135, opacity: 0.35 };
}

/** Full-slide dark background */
function darkBg(slide) {
  slide.background = { color: C.bg };
}

/** Section divider band at top */
function topBand(slide, color = C.cyan) {
  slide.addShape("rect", { x: 0, y: 0, w: 10, h: 0.08, fill: { color } });
}

/** Card shape (rounded rectangle effect via RECTANGLE) */
function card(slide, x, y, w, h, fillColor = C.card2) {
  slide.addShape("rect", {
    x, y, w, h,
    fill: { color: fillColor },
    line: { color: C.border, width: 1 },
    shadow: mkShadow(),
  });
}

/** Small cyan dot accent */
function dot(slide, x, y) {
  slide.addShape("ellipse", { x, y, w: 0.12, h: 0.12, fill: { color: C.cyan } });
}

/** Slide number (bottom right) */
function slideNum(slide, n) {
  slide.addText(String(n), {
    x: 9.5, y: 5.3, w: 0.4, h: 0.2,
    fontSize: 9, color: C.dim, align: "right", margin: 0,
  });
}

/** Section label chip */
function chip(slide, label, x = 0.45, y = 0.18) {
  slide.addShape("rect", { x, y, w: label.length * 0.085 + 0.3, h: 0.25, fill: { color: C.cyanDark } });
  slide.addText(label.toUpperCase(), {
    x, y, w: label.length * 0.085 + 0.3, h: 0.25,
    fontSize: 8, bold: true, color: C.white, align: "center", charSpacing: 2, margin: 0,
  });
}

// ─── SLIDE 1: COVER ──────────────────────────────────────────────────────────
function slide1(pres) {
  const s = pres.addSlide();
  darkBg(s);

  // Glowing accent lines
  s.addShape("rect", { x: 0, y: 0, w: 10, h: 5.625, fill: { color: "0A0F1E" } });
  s.addShape("rect", { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.cyan } });
  s.addShape("rect", { x: 0, y: 5.45, w: 10, h: 0.06, fill: { color: C.cyan } });

  // Badge
  s.addShape("rect", { x: 0.5, y: 0.55, w: 2.6, h: 0.3, fill: { color: C.cyanDark } });
  s.addText("THE SCHOLARS · MOCK INTERVIEW", {
    x: 0.5, y: 0.55, w: 2.6, h: 0.3,
    fontSize: 7.5, bold: true, color: C.white, align: "center", charSpacing: 1.5, margin: 0,
  });

  // Main title
  s.addText("The Future of", {
    x: 0.5, y: 1.1, w: 8, h: 0.6,
    fontSize: 22, color: C.cyan, italic: true, fontFace: "Georgia", margin: 0,
  });
  s.addText("Mock Interview Booking.", {
    x: 0.5, y: 1.65, w: 9, h: 1.4,
    fontSize: 48, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  // Tagline
  s.addText("Booking otomatis. Jadwal rapi. Sam fokus mengajar.", {
    x: 0.5, y: 3.3, w: 8, h: 0.45,
    fontSize: 15, color: C.muted, italic: true, fontFace: "Georgia", margin: 0,
  });

  // Separator
  s.addShape("rect", { x: 0.5, y: 3.85, w: 2.5, h: 0.025, fill: { color: C.cyan } });

  // Presenter
  s.addText("Presented by : Steven Leroy", {
    x: 0.5, y: 4.1, w: 5, h: 0.3,
    fontSize: 11, color: C.muted, margin: 0,
  });
}

// ─── SLIDE 2: AGENDA ─────────────────────────────────────────────────────────
function slide2(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);

  s.addText("Agenda", {
    x: 0.45, y: 0.22, w: 4, h: 0.55,
    fontSize: 32, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  const items = [
    ["01", "Introduction", "Apa itu Mock Booking System?"],
    ["02", "Pain Points", "Masalah yang terjadi tanpa sistem ini"],
    ["03", "Solution", "Bagaimana sistem ini menyelesaikannya"],
    ["04", "Features", "Fitur lengkap & cara kerjanya"],
    ["05", "Flow & Demo", "Step-by-step proses booking"],
    ["06", "Investment", "Harga setup & monthly fee"],
    ["07", "Advantages & ROI", "Kenapa ini investasi yang layak"],
    ["08", "Implementation", "Timeline go-live 30 hari"],
  ];

  const cols = [
    items.slice(0, 4),
    items.slice(4, 8),
  ];

  cols.forEach((col, ci) => {
    const bx = 0.45 + ci * 4.75;
    col.forEach(([num, title, sub], i) => {
      const by = 1.05 + i * 1.05;
      card(s, bx, by, 4.4, 0.85, C.card);
      s.addText(num, {
        x: bx + 0.15, y: by + 0.1, w: 0.5, h: 0.65,
        fontSize: 22, bold: true, color: C.cyan, fontFace: "Georgia", margin: 0,
      });
      s.addText(title, {
        x: bx + 0.7, y: by + 0.08, w: 3.5, h: 0.32,
        fontSize: 13, bold: true, color: C.white, margin: 0,
      });
      s.addText(sub, {
        x: bx + 0.7, y: by + 0.42, w: 3.5, h: 0.28,
        fontSize: 9.5, color: C.muted, margin: 0,
      });
    });
  });

  slideNum(s, 2);
}

// ─── SLIDE 3: QUOTE ──────────────────────────────────────────────────────────
function slide3(pres) {
  const s = pres.addSlide();
  darkBg(s);

  // Decorative large quotation mark
  s.addText("“", {
    x: 0.3, y: 0.0, w: 3, h: 2.5,
    fontSize: 200, color: C.cyanDark, fontFace: "Georgia", margin: 0,
    transparency: 70,
  });

  s.addText(
    "Waktu adalah sumber daya paling berharga yang kita punya.\nJangan habiskan untuk hal-hal yang bisa diotomatisasi.",
    {
      x: 1.2, y: 1.3, w: 7.5, h: 1.8,
      fontSize: 22, color: C.white, fontFace: "Georgia", italic: true,
      align: "center", valign: "middle", margin: 0,
    }
  );

  s.addShape("rect", { x: 3.5, y: 3.4, w: 3, h: 0.025, fill: { color: C.cyan } });

  s.addText("Setiap menit Sam habiskan untuk balas booking manual\nadalah menit yang bisa dipakai untuk mengajar.", {
    x: 1, y: 3.6, w: 8, h: 0.8,
    fontSize: 13, color: C.muted, align: "center", margin: 0,
  });

  slideNum(s, 3);
}

// ─── SLIDES 4-5: PAIN POINTS ─────────────────────────────────────────────────
function slide4(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);
  chip(s, "Pain Points");

  s.addText("Pain Points", {
    x: 0.45, y: 0.25, w: 6, h: 0.55,
    fontSize: 30, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  const pains = [
    {
      icon: "📩",
      title: "BOOKING MANUAL & RAWAN ERROR",
      body: "Sam harus balas WA satu per satu, catat jadwal secara manual — rawan salah catat dan missed message.",
    },
    {
      icon: "⚠️",
      title: "SLOT BENTROK",
      body: "2 murid bisa submit booking untuk jadwal yang sama secara bersamaan → salah satu kecewa.",
    },
    {
      icon: "🔄",
      title: "TIDAK ADA NOTIFIKASI OTOMATIS",
      body: "Murid tidak tahu apakah booking mereka diterima atau ditolak kecuali Sam membalas manual.",
    },
    {
      icon: "💸",
      title: "INFO PEMBAYARAN DIKIRIM MANUAL",
      body: "Setiap booking dikonfirmasi, Sam harus kirim ulang info rekening, nominal, dan deadline — berulang tanpa henti.",
    },
  ];

  const positions = [[0.45, 1.0], [5.2, 1.0], [0.45, 3.1], [5.2, 3.1]];
  pains.forEach((p, i) => {
    const [px, py] = positions[i];
    card(s, px, py, 4.5, 1.9, C.card2);
    s.addText(p.icon, { x: px + 0.18, y: py + 0.18, w: 0.6, h: 0.55, fontSize: 26, margin: 0 });
    s.addText(p.title, {
      x: px + 0.85, y: py + 0.18, w: 3.45, h: 0.38,
      fontSize: 10, bold: true, color: C.amber, charSpacing: 0.5, margin: 0,
    });
    s.addText(p.body, {
      x: px + 0.18, y: py + 0.65, w: 4.1, h: 1.1,
      fontSize: 11.5, color: C.muted, margin: 0,
    });
  });

  slideNum(s, 4);
}

function slide5(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);
  chip(s, "Pain Points");

  s.addText("Pain Points", {
    x: 0.45, y: 0.25, w: 6, h: 0.55,
    fontSize: 30, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  const pains = [
    {
      icon: "📅",
      title: "SLOT TIDAK TERKELOLA",
      body: "Tidak ada tampilan real-time jadwal yang tersedia. Murid tidak tahu slot mana yang kosong.",
    },
    {
      icon: "⏱️",
      title: "ADMIN OVERLOAD",
      body: "Sam harus ingat, catat, konfirmasi, dan follow up semua booking sendiri → waktu produktif terkuras.",
    },
    {
      icon: "🚪",
      title: "LOST REVENUE FROM SLOW RESPONSE",
      body: "Booking yang lama diproses atau tidak dibalas = murid memilih tempat lain. Revenue bocor diam-diam.",
    },
  ];

  const positions = [[0.35, 1.1], [3.57, 1.1], [6.79, 1.1]];
  pains.forEach((p, i) => {
    const [px, py] = positions[i];
    card(s, px, py, 2.75, 3.5, C.card2);
    s.addText(p.icon, { x: px + 0.18, y: py + 0.2, w: 0.6, h: 0.55, fontSize: 30, margin: 0 });
    s.addText(p.title, {
      x: px + 0.18, y: py + 0.9, w: 2.42, h: 0.55,
      fontSize: 9.5, bold: true, color: C.amber, charSpacing: 0.5, margin: 0,
    });
    s.addText(p.body, {
      x: px + 0.18, y: py + 1.55, w: 2.42, h: 1.7,
      fontSize: 11.5, color: C.muted, margin: 0,
    });
  });

  slideNum(s, 5);
}

// ─── SLIDE 6: SOLUTION INTRO ─────────────────────────────────────────────────
function slide6(pres) {
  const s = pres.addSlide();
  darkBg(s);

  s.addShape("rect", { x: 0, y: 0, w: 10, h: 5.625, fill: { color: C.bg } });
  s.addShape("rect", { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.cyan } });

  // Glow circles (decorative)
  s.addShape("ellipse", { x: 6.5, y: -0.5, w: 5, h: 5, fill: { color: C.cyanDark, transparency: 88 } });

  s.addText("Introducing:", {
    x: 0.5, y: 1.0, w: 8, h: 0.5,
    fontSize: 16, color: C.cyan, italic: true, fontFace: "Georgia", margin: 0,
  });
  s.addText("Mock Booking System", {
    x: 0.5, y: 1.5, w: 9, h: 1.2,
    fontSize: 46, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("A Smart WhatsApp-Based Booking Automation\nfor The Scholars Mock Interview", {
    x: 0.5, y: 2.85, w: 7.5, h: 0.9,
    fontSize: 15, color: C.muted, margin: 0,
  });

  s.addShape("rect", { x: 0.5, y: 3.9, w: 2.5, h: 0.025, fill: { color: C.cyan } });
  s.addText("Dibangun di atas n8n + Google Sheets + WhatsApp API · Terintegrasi penuh dengan workflow Sam.", {
    x: 0.5, y: 4.05, w: 8.5, h: 0.4,
    fontSize: 10.5, color: C.dim, italic: true, margin: 0,
  });
}

// ─── SLIDE 7: WHY ────────────────────────────────────────────────────────────
function slide7(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);

  s.addText("WHY?", {
    x: 0.45, y: 0.18, w: 3, h: 0.65,
    fontSize: 36, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("Kenapa harus pakai Mock Booking System\ndibanding tetap manual?", {
    x: 0.45, y: 0.85, w: 9, h: 0.6,
    fontSize: 14, color: C.muted, margin: 0,
  });

  const reasons = [
    { n: "01", h: "Zero Human Error", b: "Sistem mencatat semua data secara otomatis. Tidak ada booking yang terlewat atau salah catat." },
    { n: "02", h: "Instant Response 24/7", b: "Murid bisa submit booking kapan saja. Sam tidak perlu online untuk memproses request masuk." },
    { n: "03", h: "Conflict-Free Scheduling", b: "Race condition protection memastikan tidak ada 2 murid yang bisa mendapatkan slot yang sama." },
    { n: "04", h: "Full Control di Tangan Sam", b: "Sam tetap punya kendali penuh — konfirmasi atau tolak dengan 1 tap. Bot tidak bekerja tanpa approval Sam." },
    { n: "05", h: "Data Tersimpan Rapi", b: "Semua booking, nama, kontak, dan info tersinkron otomatis ke Google Sheets yang bisa diakses kapan saja." },
    { n: "06", h: "Scalable", b: "Mau 5 booking atau 50 booking per bulan — sistem bekerja dengan kapasitas yang sama tanpa biaya tambahan." },
  ];

  const cols = [reasons.slice(0, 3), reasons.slice(3, 6)];
  cols.forEach((col, ci) => {
    col.forEach((r, ri) => {
      const bx = 0.45 + ci * 4.8;
      const by = 1.65 + ri * 1.2;
      card(s, bx, by, 4.45, 1.0, C.card2);
      s.addText(r.n, {
        x: bx + 0.15, y: by + 0.12, w: 0.48, h: 0.75,
        fontSize: 20, bold: true, color: C.cyan, fontFace: "Georgia", margin: 0,
      });
      s.addText(r.h, {
        x: bx + 0.72, y: by + 0.1, w: 3.5, h: 0.32,
        fontSize: 12, bold: true, color: C.white, margin: 0,
      });
      s.addText(r.b, {
        x: bx + 0.72, y: by + 0.44, w: 3.6, h: 0.44,
        fontSize: 10, color: C.muted, margin: 0,
      });
    });
  });

  slideNum(s, 7);
}

// ─── SLIDE 8: CORE FEATURES OVERVIEW ─────────────────────────────────────────
function slide8(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);
  chip(s, "Core Features");

  s.addText("Core Features", {
    x: 0.45, y: 0.25, w: 8, h: 0.55,
    fontSize: 30, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("Mock Booking System", {
    x: 0.45, y: 0.8, w: 8, h: 0.3,
    fontSize: 12, color: C.cyan, margin: 0,
  });

  const features = [
    ["✅", "WhatsApp Booking Form", "Form booking via link — murid isi data lengkap, submit, dan langsung terekam."],
    ["✅", "Smart Slot Management", "Tampilkan slot tersedia secara real-time. Slot yang sudah dibook otomatis hilang dari pilihan."],
    ["✅", "Instant Sam Notification", "Sam langsung terima WA berisi data lengkap murid + link Konfirmasi & Tolak."],
    ["✅", "One-Click Confirm / Reject", "Sam konfirmasi atau tolak booking hanya dengan 1 tap di WA — tanpa buka aplikasi lain."],
    ["✅", "Auto WA Confirmation", "Info pembayaran (bank, rekening, nominal, deadline) otomatis terkirim ke murid saat dikonfirmasi."],
    ["✅", "Auto WA Rejection + Re-open Slot", "Murid diberi tahu & diarahkan rebook. Slot otomatis terbuka kembali untuk murid lain."],
    ["✅", "Monthly Auto-Generate Slots", "Slot bulan berikutnya dibuat otomatis setiap tanggal 1 — Sam tidak perlu input manual."],
    ["✅", "Race Condition Protection", "Jika 2 murid submit slot yang sama bersamaan, sistem memastikan hanya 1 yang diproses."],
    ["✅", "Human-in-the-Loop", "Sam tetap pemegang keputusan. Semua konfirmasi & penolakan butuh approval Sam."],
    ["✅", "Google Sheets Sync", "Semua data booking tersimpan otomatis ke Google Sheets — siap diakses, difilter, atau dianalisis."],
  ];

  const colA = features.slice(0, 5);
  const colB = features.slice(5, 10);

  [colA, colB].forEach((col, ci) => {
    col.forEach((f, i) => {
      const fx = 0.45 + ci * 4.8;
      const fy = 1.18 + i * 0.85;
      s.addText(f[0] + " " + f[1], {
        x: fx, y: fy, w: 4.4, h: 0.3,
        fontSize: 11.5, bold: true, color: C.white, margin: 0,
      });
      s.addText(f[2], {
        x: fx + 0.22, y: fy + 0.3, w: 4.1, h: 0.38,
        fontSize: 9.5, color: C.muted, margin: 0,
      });
      s.addShape("rect", { x: fx, y: fy + 0.72, w: 4.4, h: 0.008, fill: { color: C.border } });
    });
  });

  slideNum(s, 8);
}

// ─── SLIDE 9: THE FLOW ────────────────────────────────────────────────────────
function slide9(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);
  chip(s, "The Flow");

  s.addText("The Flow", {
    x: 0.45, y: 0.25, w: 6, h: 0.55,
    fontSize: 30, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  const steps = [
    { n: "1", label: "Murid Buka\nBooking Form", detail: "Link dibagikan\nvia WhatsApp\natau media sosial", color: C.cyan },
    { n: "2", label: "Pilih Slot\n& Submit", detail: "Form otomatis\ncek ketersediaan\nslot real-time", color: C.cyan },
    { n: "3", label: "Sam Terima\nNotifikasi WA", detail: "Notif instan berisi\nnama, kelas, sekolah\n& tombol konfirmasi", color: C.amber },
    { n: "4", label: "Sam Konfirmasi\natau Tolak", detail: "Satu klik dari\nWA — tidak perlu\nbuka dashboard", color: C.amber },
    { n: "5", label: "Murid Terima\nWA Otomatis", detail: "Pesan konfirmasi\natau penolakan\ndikirim otomatis", color: C.green },
    { n: "6", label: "Data Tersimpan\ndi Google Sheets", detail: "Nama, slot, status\nlangsung tercatat\ntanpa input manual", color: C.green },
  ];

  const boxW = 1.3, boxH = 3.2, startX = 0.45, y = 1.35, gap = 1.45;

  steps.forEach((st, i) => {
    const bx = startX + i * gap;
    card(s, bx, y, boxW, boxH, C.card2);
    // Color top bar
    s.addShape("rect", { x: bx, y, w: boxW, h: 0.07, fill: { color: st.color } });
    // Number circle
    s.addShape("ellipse", { x: bx + 0.4, y: y + 0.15, w: 0.5, h: 0.5, fill: { color: st.color } });
    s.addText(st.n, {
      x: bx + 0.4, y: y + 0.15, w: 0.5, h: 0.5,
      fontSize: 16, bold: true, color: C.bg, align: "center", valign: "middle", margin: 0,
    });
    s.addText(st.label, {
      x: bx + 0.08, y: y + 0.82, w: boxW - 0.16, h: 0.8,
      fontSize: 10, bold: true, color: C.white, align: "center", margin: 0,
    });
    s.addText(st.detail, {
      x: bx + 0.08, y: y + 1.72, w: boxW - 0.16, h: 1.35,
      fontSize: 8.5, color: C.muted, align: "center", margin: 0,
    });

    // Arrow between steps
    if (i < steps.length - 1) {
      s.addShape("rect", {
        x: bx + boxW + 0.04, y: y + 0.63, w: 0.11, h: 0.14,
        fill: { color: C.muted },
      });
    }
  });

  // Annotations
  s.addText("Murid", { x: 0.45, y: 1.1, w: 2.75, h: 0.22, fontSize: 10, bold: true, color: C.cyan, align: "center", margin: 0 });
  s.addText("Sam (Human-in-the-loop)", { x: 2.9, y: 1.1, w: 2.9, h: 0.22, fontSize: 10, bold: true, color: C.amber, align: "center", margin: 0 });
  s.addText("Sistem Otomatis", { x: 5.8, y: 1.1, w: 3.75, h: 0.22, fontSize: 10, bold: true, color: C.green, align: "center", margin: 0 });

  // Bottom legend
  s.addText("Dari form link booking hingga data tersimpan di sheet — semua berjalan otomatis dalam hitungan detik.", {
    x: 0.45, y: 4.72, w: 9.1, h: 0.3,
    fontSize: 9.5, color: C.dim, italic: true, align: "center", margin: 0,
  });

  slideNum(s, 9);
}

// ─── SLIDES 10-19: INDIVIDUAL FEATURES ───────────────────────────────────────

function featureSlide(pres, num, chipLabel, title, subtitle, icon, highlights, detail, slideN) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);
  chip(s, chipLabel);

  // Left column: Feature title
  s.addText(icon, { x: 0.45, y: 0.3, w: 0.7, h: 0.55, fontSize: 28, margin: 0 });
  s.addText(title, {
    x: 1.2, y: 0.22, w: 7.8, h: 0.65,
    fontSize: 26, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText(subtitle, {
    x: 0.45, y: 0.92, w: 9.1, h: 0.38,
    fontSize: 11.5, color: C.muted, italic: true, margin: 0,
  });

  // Highlight cards (2 per row, up to 4)
  highlights.forEach((h, i) => {
    const hx = 0.45 + (i % 2) * 4.75;
    const hy = 1.45 + Math.floor(i / 2) * 1.2;
    card(s, hx, hy, 4.4, 1.0, C.card2);
    s.addText(h.icon + " " + h.label, {
      x: hx + 0.18, y: hy + 0.1, w: 4.0, h: 0.3,
      fontSize: 11.5, bold: true, color: C.white, margin: 0,
    });
    s.addText(h.desc, {
      x: hx + 0.18, y: hy + 0.44, w: 4.0, h: 0.46,
      fontSize: 10, color: C.muted, margin: 0,
    });
  });

  if (detail) {
    s.addText(detail, {
      x: 0.45, y: 4.88, w: 9.1, h: 0.4,
      fontSize: 9.5, color: C.dim, italic: true, margin: 0,
    });
  }

  slideNum(s, slideN);
}

function slide10(pres) {
  featureSlide(pres, 10, "Feature 01", "WhatsApp Booking Form",
    "Murid mengisi form booking lewat link — tidak perlu DM manual ke Sam lagi.",
    "📋",
    [
      { icon: "🔗", label: "Link Booking Universal", desc: "Satu link pendek (contoh: tinyurl.com/mockbooking) dibagikan di bio, grup, atau langsung via WA." },
      { icon: "📱", label: "Mobile-First Design", desc: "Form didesain untuk smartphone — loading cepat, input mudah, tanpa perlu install aplikasi." },
      { icon: "✅", label: "Validasi Data Otomatis", desc: "Nomor WA, field wajib, dan format data divalidasi sebelum submit — data yang masuk selalu bersih." },
      { icon: "⚡", label: "Real-Time Slot Display", desc: "Slot yang tampil hanya yang benar-benar tersedia — tidak ada slot yang sudah dibook atau penuh." },
    ],
    "Tech stack: HTML + JavaScript + n8n Webhook | Data langsung masuk ke Google Sheets saat submit.",
    10
  );
}

function slide11(pres) {
  featureSlide(pres, 11, "Feature 02", "Smart Slot Management",
    "Slot jadwal dikelola otomatis — Sam tidak perlu update manual setiap ada booking masuk.",
    "🗓️",
    [
      { icon: "🔄", label: "Auto-Hide Booked Slots", desc: "Begitu slot dikonfirmasi, slot tersebut otomatis hilang dari tampilan form booking murid lain." },
      { icon: "♻️", label: "Auto Re-open on Reject", desc: "Jika Sam menolak booking, slot langsung terbuka kembali dan bisa dipilih murid lain." },
      { icon: "📆", label: "Monthly Auto-Generate", desc: "Slot bulan depan dibuat otomatis setiap tanggal 1 — berdasarkan jadwal Senin, Selasa, Kamis, Jumat." },
      { icon: "🔢", label: "Unique Slot ID System", desc: "Setiap slot punya ID unik (SLOT-YYYYMMDD) untuk tracking yang akurat dan bebas duplikasi." },
    ],
    "Sheet: MOCK_SLOTS — kolom: ID | Tanggal | JamMulai | JamSelesai | Booked | NamaPemesan | NoWaPemesan",
    11
  );
}

function slide12(pres) {
  featureSlide(pres, 12, "Feature 03", "Instant Sam Notification",
    "Sam langsung terima WA notifikasi lengkap setiap ada booking masuk — tidak ada yang terlewat.",
    "🔔",
    [
      { icon: "⚡", label: "Notifikasi Instan via WA", desc: "Begitu murid submit, Sam langsung terima WhatsApp berisi semua data booking dalam hitungan detik." },
      { icon: "📋", label: "Data Lengkap dalam 1 Pesan", desc: "Nama anak, orang tua, no WA, sekolah, kelas, kurikulum, target universitas, dan jadwal — semua dalam 1 WA." },
      { icon: "🔗", label: "Link Aksi Siap Klik", desc: "Di bawah notifikasi ada 2 link: ✅ KONFIRMASI dan ❌ TOLAK — Sam tinggal tap, langsung diproses." },
      { icon: "🆔", label: "ID Booking Unik", desc: "Setiap booking punya ID unik untuk tracking — memudahkan Sam jika perlu cari data di sheet." },
    ],
    "Notifikasi dikirim via WhatsApp API (Kirimi.id) ke nomor WA Sam yang terdaftar.",
    12
  );
}

function slide13(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);
  chip(s, "Feature 04");

  s.addText("✅ One-Click Confirm / Reject", {
    x: 0.45, y: 0.22, w: 9, h: 0.65,
    fontSize: 26, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("Sam tidak perlu buka apps lain. Satu tap di WA → proses selesai.", {
    x: 0.45, y: 0.9, w: 9, h: 0.35,
    fontSize: 11.5, color: C.muted, italic: true, margin: 0,
  });

  // KONFIRMASI card
  card(s, 0.45, 1.4, 4.2, 3.8, C.card2);
  s.addShape("rect", { x: 0.45, y: 1.4, w: 4.2, h: 0.07, fill: { color: C.green } });
  s.addText("✅  TAP KONFIRMASI", {
    x: 0.65, y: 1.55, w: 3.8, h: 0.42,
    fontSize: 14, bold: true, color: C.green, margin: 0,
  });
  const confirmSteps = [
    "Status booking → Confirmed di Google Sheets",
    "Slot ditandai Booked (tidak tampil ke murid lain)",
    "WA otomatis terkirim ke murid berisi:",
    "   · Info pembayaran (bank, rekening, nominal)",
    "   · Deadline transfer",
    "   · Pesan selamat & sampai jumpa",
  ];
  confirmSteps.forEach((t, i) => {
    s.addText((i < 2 || i === 2 ? "→ " : "") + t, {
      x: 0.65, y: 2.1 + i * 0.47, w: 3.8, h: 0.4,
      fontSize: 11, color: i >= 3 ? C.muted : C.white, margin: 0,
    });
  });

  // TOLAK card
  card(s, 5.15, 1.4, 4.2, 3.8, C.card2);
  s.addShape("rect", { x: 5.15, y: 1.4, w: 4.2, h: 0.07, fill: { color: C.red } });
  s.addText("❌  TAP TOLAK", {
    x: 5.35, y: 1.55, w: 3.8, h: 0.42,
    fontSize: 14, bold: true, color: C.red, margin: 0,
  });
  const rejectSteps = [
    "Status booking → Rejected di Google Sheets",
    "Slot otomatis terbuka kembali",
    "WA otomatis terkirim ke murid berisi:",
    "   · Pemberitahuan slot tidak tersedia",
    "   · Link untuk rebook jadwal lain",
    "   · Pesan sopan dari Sam",
  ];
  rejectSteps.forEach((t, i) => {
    s.addText((i < 2 || i === 2 ? "→ " : "") + t, {
      x: 5.35, y: 2.1 + i * 0.47, w: 3.8, h: 0.4,
      fontSize: 11, color: i >= 3 ? C.muted : C.white, margin: 0,
    });
  });

  slideNum(s, 13);
}

function slide14(pres) {
  featureSlide(pres, 14, "Feature 05", "Auto WA Confirmation",
    "Begitu Sam tap Konfirmasi, murid langsung terima WhatsApp berisi semua info yang dibutuhkan.",
    "💬",
    [
      { icon: "💳", label: "Info Pembayaran Otomatis", desc: "Nama bank, nomor rekening, atas nama, nominal, dan deadline terkirim otomatis tanpa Sam ketik ulang." },
      { icon: "🎉", label: "Pesan Personal", desc: "WA dikirim atas nama Sam dengan sapaan nama murid — terasa personal, bukan bot generic." },
      { icon: "⚙️", label: "Konfigurasi Fleksibel", desc: "Nominal, rekening, dan deadline bisa diubah Sam kapan saja via sheet CONFIG — langsung berlaku." },
      { icon: "📝", label: "Reminder Upload Bukti", desc: "Murid diminta kirim bukti transfer ke nomor Sam — closing loop pembayaran dilakukan manusia." },
    ],
    "Konfigurasi di sheet CONFIG: NOMINAL_BIAYA | NAMA_BANK | NOMOR_REKENING | ATAS_NAMA | DEADLINE_HARI",
    14
  );
}

function slide15(pres) {
  featureSlide(pres, 15, "Feature 06", "Auto WA Rejection & Slot Reopen",
    "Penolakan booking ditangani sistem — slot langsung terbuka kembali, murid langsung diarahkan rebook.",
    "🔄",
    [
      { icon: "📤", label: "Notifikasi Penolakan Sopan", desc: "Murid terima WA berisi alasan umum & link untuk booking ulang di jadwal lain yang masih tersedia." },
      { icon: "♻️", label: "Slot Langsung Terbuka", desc: "Kolom Booked di MOCK_SLOTS dikosongkan otomatis — slot bisa dipilih murid lain saat itu juga." },
      { icon: "🔗", label: "Link Rebook Langsung", desc: "WA penolakan sudah berisi link form booking — murid tidak perlu cari-cari sendiri." },
      { icon: "📊", label: "Tetap Tercatat", desc: "Booking yang ditolak tetap tersimpan di sheet dengan status Rejected — data tidak hilang." },
    ],
    "Slot di-free atomically: Booked='', NamaPemesan='', NoWaPemesan='' — siap untuk booking berikutnya.",
    15
  );
}

function slide16(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);
  chip(s, "Feature 07");

  s.addText("📆 Monthly Auto-Generate Slots", {
    x: 0.45, y: 0.22, w: 9, h: 0.65,
    fontSize: 26, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("Slot bulan berikutnya dibuat otomatis setiap tanggal 1 — Sam tidak perlu input manual apapun.", {
    x: 0.45, y: 0.92, w: 9, h: 0.35,
    fontSize: 11.5, color: C.muted, italic: true, margin: 0,
  });

  // Schedule logic card
  card(s, 0.45, 1.45, 4.5, 3.7, C.card2);
  s.addText("Jadwal yang Di-generate:", {
    x: 0.65, y: 1.6, w: 4.1, h: 0.35,
    fontSize: 12, bold: true, color: C.cyan, margin: 0,
  });
  const sched = [
    "📅  Hari   : Senin, Selasa, Kamis, Jumat",
    "⏰  Waktu  : 19:30 — 21:30 WIB",
    "🔁  Trigger : Otomatis tanggal 1 setiap bulan",
    "🆔  Slot ID  : SLOT-YYYYMMDD (unik per hari)",
    "📋  Sheet   : MOCK_SLOTS (append otomatis)",
  ];
  sched.forEach((t, i) => {
    s.addText(t, {
      x: 0.65, y: 2.1 + i * 0.6, w: 4.1, h: 0.48,
      fontSize: 11, color: C.white, margin: 0,
    });
  });

  // Impact card
  card(s, 5.3, 1.45, 4.2, 3.7, C.card2);
  s.addText("Impact:", {
    x: 5.5, y: 1.6, w: 3.8, h: 0.35,
    fontSize: 12, bold: true, color: C.amber, margin: 0,
  });

  const impacts = [
    { n: "0", unit: "menit", label: "Sam input manual\nper bulan" },
    { n: "~20", unit: "slot", label: "Dibuat otomatis\nsetiap bulan" },
    { n: "100%", unit: "akurat", label: "Tidak ada slot yang\nterlewat atau salah hari" },
  ];
  impacts.forEach((imp, i) => {
    const ix = 5.5 + i * 1.38;
    s.addText(imp.n, {
      x: ix, y: 2.1, w: 1.2, h: 0.7,
      fontSize: 28, bold: true, color: C.cyan, fontFace: "Georgia", align: "center", margin: 0,
    });
    s.addText(imp.unit, {
      x: ix, y: 2.78, w: 1.2, h: 0.25,
      fontSize: 10, color: C.muted, align: "center", margin: 0,
    });
    s.addText(imp.label, {
      x: ix, y: 3.1, w: 1.2, h: 0.55,
      fontSize: 9, color: C.dim, align: "center", margin: 0,
    });
    if (i < 2) s.addShape("rect", { x: ix + 1.3, y: 2.1, w: 0.04, h: 1.4, fill: { color: C.border } });
  });

  s.addText("Rabu dan akhir pekan dikecualikan otomatis dari generate slot.", {
    x: 5.5, y: 3.8, w: 3.8, h: 0.9,
    fontSize: 10, color: C.muted, margin: 0,
  });

  slideNum(s, 16);
}

function slide17(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s, C.amber);
  chip(s, "Feature 08");

  s.addText("⚡ Race Condition Protection", {
    x: 0.45, y: 0.22, w: 9, h: 0.65,
    fontSize: 26, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("Perlindungan canggih untuk skenario 2 murid submit slot yang sama di waktu bersamaan.", {
    x: 0.45, y: 0.92, w: 9, h: 0.35,
    fontSize: 11.5, color: C.muted, italic: true, margin: 0,
  });

  // Scenario visual
  const scenarios = [
    {
      title: "Tanpa Perlindungan ❌",
      color: C.red,
      steps: [
        "Murid A & B submit slot yang sama bersamaan",
        "Keduanya masuk sebagai Pending",
        "Sam konfirmasi A → jadwal penuh",
        "Sam konfirmasi B → SLOT BENTROK! 💥",
        "Booking double untuk 1 slot",
      ],
    },
    {
      title: "Dengan Mock Booking System ✅",
      color: C.green,
      steps: [
        "Murid A & B submit slot yang sama bersamaan",
        "Sistem detect: A sudah dikonfirmasi untuk slot ini",
        "Sam buka link B → muncul halaman peringatan",
        "Tampil info: slot sudah dibooked oleh Murid A",
        "Sam bisa tolak B tanpa bebaskan slot milik A",
      ],
    },
  ];

  scenarios.forEach((sc, i) => {
    const bx = 0.45 + i * 4.75;
    card(s, bx, 1.45, 4.4, 3.7, C.card2);
    s.addShape("rect", { x: bx, y: 1.45, w: 4.4, h: 0.07, fill: { color: sc.color } });
    s.addText(sc.title, {
      x: bx + 0.2, y: 1.6, w: 4.0, h: 0.38,
      fontSize: 12, bold: true, color: sc.color, margin: 0,
    });
    sc.steps.forEach((st, si) => {
      s.addText((si + 1) + ".  " + st, {
        x: bx + 0.2, y: 2.15 + si * 0.58, w: 3.95, h: 0.5,
        fontSize: 10.5, color: si === 4 && i === 0 ? C.red : (si >= 1 && i === 1 ? C.white : C.muted),
        bold: si === 4, margin: 0,
      });
    });
  });

  slideNum(s, 17);
}

function slide18(pres) {
  featureSlide(pres, 18, "Feature 09", "Human-in-the-Loop",
    "Sistem tidak bekerja sendiri. Setiap konfirmasi butuh approval Sam — kontrol tetap di tangan manusia.",
    "🧑‍💼",
    [
      { icon: "🔐", label: "Sam Pemegang Keputusan", desc: "Tidak ada booking yang dikonfirmasi tanpa Sam tap link konfirmasi. Bot tidak bisa auto-approve." },
      { icon: "🛑", label: "Override Kapan Saja", desc: "Sam bisa reject booking apapun kapan saja — sistem mengikuti keputusan Sam, bukan sebaliknya." },
      { icon: "⚡", label: "Aksi Minimal, Dampak Maksimal", desc: "Sam hanya perlu 1 tap untuk memproses booking. Sisanya ditangani sistem secara otomatis." },
      { icon: "📋", label: "Audit Trail Lengkap", desc: "Setiap action Sam (confirm/reject) tercatat dengan timestamp di Google Sheets — transparan & akuntabel." },
    ],
    "Filosofi: Otomasi menghemat waktu Sam, bukan menggantikan judgment Sam.",
    18
  );
}

function slide19(pres) {
  featureSlide(pres, 19, "Feature 10", "Google Sheets Sync",
    "Semua data booking tersinkron otomatis ke Google Sheets — database yang familiar dan mudah diakses.",
    "📊",
    [
      { icon: "🗃️", label: "Database Real-Time", desc: "Setiap booking masuk langsung append ke sheet MOCK_INTERVIEW_BOOKING dengan semua field terisi otomatis." },
      { icon: "🔍", label: "Filter & Cari Mudah", desc: "Sam bisa filter berdasarkan tanggal, status, nama murid, atau sekolah langsung dari Google Sheets." },
      { icon: "📈", label: "History Tersimpan Selamanya", desc: "Booking yang confirmed, rejected, maupun pending semua tersimpan dengan status & timestamp akurat." },
      { icon: "⚙️", label: "Config dari Sheet", desc: "Sam bisa update nominal biaya, rekening, dan deadline langsung dari sheet CONFIG — efektif saat itu juga." },
    ],
    "Sheets: MOCK_SLOTS (jadwal) · MOCK_INTERVIEW_BOOKING (semua booking) · CONFIG (pengaturan sistem)",
    19
  );
}

// ─── SLIDE 20: INVESTMENT ─────────────────────────────────────────────────────
function slide20(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s, C.amber);

  s.addText("Investment", {
    x: 0.45, y: 0.15, w: 6, h: 0.65,
    fontSize: 36, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  // Setup fee
  card(s, 0.45, 0.95, 4.2, 4.0, C.card2);
  s.addShape("rect", { x: 0.45, y: 0.95, w: 4.2, h: 0.07, fill: { color: C.cyan } });
  s.addText("One-Time Setup", {
    x: 0.65, y: 1.1, w: 3.8, h: 0.35,
    fontSize: 11, bold: true, color: C.cyan, charSpacing: 1, margin: 0,
  });
  s.addText("Rp 2.500.000", {
    x: 0.65, y: 1.5, w: 3.8, h: 0.75,
    fontSize: 38, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("Bayar sekali, sistem milik Anda selamanya.", {
    x: 0.65, y: 2.3, w: 3.8, h: 0.35,
    fontSize: 10, color: C.muted, margin: 0,
  });
  const setupIncludes = [
    "✅  Setup n8n workflow lengkap",
    "✅  Booking form HTML kustom",
    "✅  Integrasi Google Sheets",
    "✅  Integrasi WhatsApp API",
    "✅  Testing & QA end-to-end",
    "✅  Handover & training Sam",
  ];
  setupIncludes.forEach((t, i) => {
    s.addText(t, {
      x: 0.65, y: 2.8 + i * 0.36, w: 3.8, h: 0.3,
      fontSize: 10, color: C.white, margin: 0,
    });
  });

  // Monthly fee
  card(s, 5.0, 0.95, 4.2, 4.0, C.card2);
  s.addShape("rect", { x: 5.0, y: 0.95, w: 4.2, h: 0.07, fill: { color: C.amber } });
  s.addText("Monthly Fee", {
    x: 5.2, y: 1.1, w: 3.8, h: 0.35,
    fontSize: 11, bold: true, color: C.amber, charSpacing: 1, margin: 0,
  });
  s.addText("Rp 1.000.000", {
    x: 5.2, y: 1.5, w: 3.8, h: 0.7,
    fontSize: 36, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("per bulan", {
    x: 5.2, y: 2.42, w: 3.8, h: 0.28,
    fontSize: 13, color: C.muted, margin: 0,
  });
  const monthlyIncludes = [
    "✅  Maintenance & monitoring sistem",
    "✅  Update workflow jika ada perubahan",
    "✅  WhatsApp API running cost",
    "✅  Priority support via WA",
    "✅  Monthly health check",
    "✅  Minor adjustment request",
  ];
  monthlyIncludes.forEach((t, i) => {
    s.addText(t, {
      x: 5.2, y: 2.8 + i * 0.36, w: 3.8, h: 0.3,
      fontSize: 10, color: C.white, margin: 0,
    });
  });

  // Note
  s.addText("*Harga sudah termasuk automation services, WhatsApp API, integrasi Google Sheets, dan ongoing maintenance.", {
    x: 0.45, y: 5.22, w: 9.1, h: 0.3,
    fontSize: 9, color: C.dim, italic: true, margin: 0,
  });

  slideNum(s, 20);
}

// ─── SLIDE 21: BEFORE vs AFTER ────────────────────────────────────────────────
function slide21(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);

  s.addText("Before  vs  After", {
    x: 0.45, y: 0.1, w: 9, h: 0.55,
    fontSize: 30, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  const befores = [
    "Sam balas WA satu per satu untuk tiap booking",
    "Slot bisa bentrok — 2 murid dapat jadwal yang sama",
    "Info pembayaran diketik ulang manual setiap konfirmasi",
    "Slot jadwal tidak terlihat — murid harus tanya dulu",
    "Tidak ada notifikasi otomatis ke murid",
    "Data booking disimpan di otak atau catatan pribadi",
    "Slot bulan baru dibuat manual di awal bulan",
  ];
  const afters = [
    "Semua booking masuk otomatis — Sam hanya tap 1 kali",
    "Race condition protection — hanya 1 murid per slot",
    "Info pembayaran terkirim otomatis saat dikonfirmasi",
    "Form menampilkan slot tersedia secara real-time",
    "WA konfirmasi/penolakan otomatis terkirim ke murid",
    "Semua data tersinkron otomatis ke Google Sheets",
    "Slot auto-generate setiap tanggal 1 — zero effort",
  ];

  // Headers
  card(s, 0.45, 0.72, 4.2, 0.4, "2D0A0A");
  s.addShape("rect", { x: 0.45, y: 0.72, w: 4.2, h: 0.07, fill: { color: C.red } });
  s.addText("❌  Sebelum", { x: 0.65, y: 0.72, w: 4.0, h: 0.4, fontSize: 13, bold: true, color: C.red, align: "center", margin: 0 });

  card(s, 5.35, 0.72, 4.2, 0.4, "0A2D1A");
  s.addShape("rect", { x: 5.35, y: 0.72, w: 4.2, h: 0.07, fill: { color: C.green } });
  s.addText("✅  Sesudah", { x: 5.55, y: 0.72, w: 4.0, h: 0.4, fontSize: 13, bold: true, color: C.green, align: "center", margin: 0 });

  befores.forEach((b, i) => {
    const ry = 1.22 + i * 0.6;
    card(s, 0.45, ry, 4.2, 0.5, C.card2);
    s.addText("✗  " + b, { x: 0.65, y: ry + 0.05, w: 3.8, h: 0.4, fontSize: 10, color: C.muted, margin: 0 });
  });

  afters.forEach((a, i) => {
    const ry = 1.22 + i * 0.6;
    card(s, 5.35, ry, 4.2, 0.5, C.card2);
    s.addText("✓  " + a, { x: 5.55, y: ry + 0.05, w: 3.8, h: 0.4, fontSize: 10, color: C.white, margin: 0 });
  });

  slideNum(s, 21);
}

// ─── SLIDES 22-25: ADVANTAGES ─────────────────────────────────────────────────
function advantageSlide(pres, num, n, title, quote, body, metric, metricLabel, color, slideN) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s, color);

  s.addText(n, {
    x: 0.45, y: 0.15, w: 1.4, h: 1.0,
    fontSize: 70, bold: true, color: color, fontFace: "Georgia", margin: 0,
    transparency: 20,
  });
  s.addText(title, {
    x: 0.45, y: 1.25, w: 8.5, h: 0.8,
    fontSize: 36, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  s.addText('"' + quote + '"', {
    x: 0.45, y: 2.12, w: 9, h: 0.55,
    fontSize: 13, color: C.muted, italic: true, fontFace: "Georgia", margin: 0,
  });

  s.addText(body, {
    x: 0.45, y: 2.95, w: 6.65, h: 1.5,
    fontSize: 12.5, color: C.white, margin: 0,
  });

  // Metric callout
  card(s, 7.35, 2.95, 2.2, 1.5, C.card2);
  s.addShape("rect", { x: 7.35, y: 2.95, w: 2.2, h: 0.07, fill: { color } });
  s.addText(metric, {
    x: 7.35, y: 3.02, w: 2.2, h: 0.9,
    fontSize: 38, bold: true, color, fontFace: "Georgia", align: "center", margin: 0,
  });
  s.addText(metricLabel, {
    x: 7.35, y: 3.92, w: 2.2, h: 0.45,
    fontSize: 9.5, color: C.muted, align: "center", margin: 0,
  });

  slideNum(s, slideN);
}

function slide22(pres) {
  advantageSlide(pres, 22, "#1", "Time Freedom",
    "Waktu adalah aset paling berharga. Jangan habiskan untuk hal yang bisa diotomatisasi.",
    "Estimasi konservatif: Sam habiskan minimal 30–45 menit/hari untuk proses booking manual — balas WA, catat, kirim info pembayaran.\n\n30 menit × 26 hari kerja = 13 jam/bulan yang bisa dialihkan untuk:\n→  Persiapan materi & strategi mengajar\n→  Pengembangan kurikulum The Scholars\n→  Networking & partnership\n→  Strategi marketing & growth",
    "13 jam", "kembali ke tangan Sam\nsetiap bulan", C.cyan, 22
  );
}

function slide23(pres) {
  advantageSlide(pres, 23, "#2", "Zero Booking Error",
    "Sistem tidak lelah, tidak lupa, dan tidak salah catat.",
    "Dengan booking manual, risiko human error selalu ada:\n→  Slot dobel karena 2 WA masuk bersamaan\n→  Lupa balas konfirmasi ke murid\n→  Salah kirim info rekening\n→  Data murid tidak tercatat lengkap\n\nMock Booking System mengeliminasi semua risiko ini. Race condition protection, validasi otomatis, dan notifikasi instan memastikan setiap booking diproses dengan sempurna.",
    "0", "human error\ndalam proses booking", C.green, 23
  );
}

function slide24(pres) {
  advantageSlide(pres, 24, "#3", "Scalability Without Complexity",
    "Bisnis grow? Sistem tidak perlu diganti — cukup tambah slot.",
    "Solusi konvensional saat booking makin banyak: hire admin tambahan (Rp3–5 juta/bulan/orang).\n\nDengan Mock Booking System:\n→  Dari 5 booking jadi 50 booking/bulan? Biaya tetap sama.\n→  Tidak ada onboarding, training, atau koordinasi tambahan.\n→  Sistem bekerja 24/7 tanpa gaji, tanpa sakit, tanpa resign.\n\nSam bisa fokus scale kualitas, bukan scale administrasi.",
    "Rp 0", "biaya tambahan\nsaat volume naik", C.amber, 24
  );
}

function slide25(pres) {
  advantageSlide(pres, 25, "#4", "Professional Brand Image",
    "First impression dimulai dari bagaimana kamu merespons.",
    "Murid & orang tua menilai profesionalisme The Scholars dari pengalaman booking mereka:\n→  Respons instan (< 5 detik setelah submit) vs nunggu balasan WA berjam-jam\n→  Notifikasi rapi dan terstruktur vs chat informal\n→  Sistem yang seamless = kepercayaan lebih tinggi\n→  Kepercayaan lebih tinggi = berani bayar lebih mahal\n\nProfesionalisme bukan tentang ukuran bisnis — tapi tentang pengalaman yang diberikan.",
    "+30%", "persepsi profesionalisme\ndari calon murid", C.cyan, 25
  );
}

// ─── SLIDE 26: ROI CALC ───────────────────────────────────────────────────────
function slide26(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s, C.green);

  s.addText("Advantages & ROI", {
    x: 0.45, y: 0.12, w: 8, h: 0.55,
    fontSize: 30, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });

  // ROI Calculation
  card(s, 0.45, 0.8, 5.6, 4.4, C.card2);
  s.addText("Contoh Perhitungan ROI", {
    x: 0.65, y: 0.92, w: 5.2, h: 0.38,
    fontSize: 13, bold: true, color: C.green, margin: 0,
  });

  const calcs = [
    ["Prospek masuk per bulan", "20 murid"],
    ["Harga 1 sesi Mock Interview", "Rp 500.000"],
    ["Potensi omzet/bulan", "Rp 10.000.000"],
    ["Tanpa sistem — 15% hilang krn slow response", "−Rp 1.500.000"],
    ["Dengan sistem — recovery 100%", "+Rp 1.500.000"],
    ["Monthly fee sistem", "−Rp 1.000.000"],
    ["Net gain per bulan", "≥ Rp 500.000"],
  ];
  calcs.forEach((row, i) => {
    const ry = 1.42 + i * 0.52;
    s.addShape("rect", { x: 0.65, y: ry, w: 5.2, h: 0.48, fill: { color: i === 6 ? "0A2D1A" : C.bg } });
    s.addText(row[0], {
      x: 0.75, y: ry + 0.06, w: 3.5, h: 0.36,
      fontSize: 10.5, color: i === 6 ? C.white : C.muted, bold: i === 6, margin: 0,
    });
    s.addText(row[1], {
      x: 4.3, y: ry + 0.06, w: 1.45, h: 0.36,
      fontSize: 10.5, color: i === 3 ? C.red : (i === 4 || i === 6 ? C.green : C.white),
      bold: i >= 4, align: "right", margin: 0,
    });
  });

  s.addText("ROI bulan pertama sudah positif.\nSetup fee kembali dalam ≤ 3 bulan.", {
    x: 0.65, y: 5.05, w: 5.2, h: 0.4,
    fontSize: 10, color: C.dim, italic: true, margin: 0,
  });

  // Stat callouts (right)
  const stats = [
    { n: "Rp 1jt", l: "Monthly fee\n(setara 2 sesi Mock)", c: C.amber },
    { n: "< 3bln", l: "Break-even\nsetup fee", c: C.cyan },
    { n: "∞", l: "Skalabilitas\ntanpa biaya tambahan", c: C.green },
  ];
  stats.forEach((st, i) => {
    const sx = 6.3;
    const sy = 0.85 + i * 1.45;
    card(s, sx, sy, 3.2, 1.2, C.card2);
    s.addShape("rect", { x: sx, y: sy, w: 3.2, h: 0.07, fill: { color: st.c } });
    s.addText(st.n, {
      x: sx, y: sy + 0.1, w: 3.2, h: 0.68,
      fontSize: 32, bold: true, color: st.c, fontFace: "Georgia", align: "center", margin: 0,
    });
    s.addText(st.l, {
      x: sx, y: sy + 0.8, w: 3.2, h: 0.38,
      fontSize: 9, color: C.muted, align: "center", margin: 0,
    });
  });

  slideNum(s, 26);
}

// ─── SLIDE 27: IMPLEMENTATION ─────────────────────────────────────────────────
function slide27(pres) {
  const s = pres.addSlide();
  darkBg(s);
  topBand(s);

  s.addText("Implementation", {
    x: 0.45, y: 0.1, w: 6, h: 0.6,
    fontSize: 30, bold: true, color: C.white, fontFace: "Georgia", margin: 0,
  });
  s.addText("Go-live dalam 30 hari.", {
    x: 0.45, y: 0.72, w: 6, h: 0.3,
    fontSize: 13, color: C.muted, italic: true, margin: 0,
  });

  // Timeline
  const phases = [
    { d: "Day 1", label: "Kickoff", items: ["Finalisasi kebutuhan Sam", "Setup Google Sheets database", "Konfigurasi n8n instance"], c: C.cyan },
    { d: "Day 7", label: "Build", items: ["Build booking form HTML", "Setup workflow n8n", "Integrasi WhatsApp API"], c: C.cyan },
    { d: "Day 15", label: "Testing", items: ["End-to-end testing", "Uji skenario edge case", "Fix & refinement"], c: C.amber },
    { d: "Day 25", label: "Finalisasi", items: ["Training Sam (1 sesi)", "Finalisasi konten WA", "Dry run bersama"], c: C.amber },
    { d: "Day 30", label: "Go Live 🚀", items: ["Sistem aktif & live", "Monitoring H+1", "Maintenance mode"], c: C.green },
  ];

  // Timeline bar
  s.addShape("rect", { x: 0.42, y: 1.42, w: 9.1, h: 0.04, fill: { color: C.border } });

  phases.forEach((ph, i) => {
    const px = 0.42 + i * 1.85;
    const cw = 1.6;
    // Dot
    s.addShape("ellipse", { x: px + 0.69, y: 1.32, w: 0.22, h: 0.22, fill: { color: ph.c } });
    // Date label
    s.addText(ph.d, {
      x: px, y: 1.6, w: cw, h: 0.28,
      fontSize: 10, bold: true, color: ph.c, align: "center", margin: 0,
    });
    // Phase card
    card(s, px, 1.95, cw, 2.8, C.card2);
    s.addShape("rect", { x: px, y: 1.95, w: cw, h: 0.07, fill: { color: ph.c } });
    s.addText(ph.label, {
      x: px + 0.1, y: 2.08, w: cw - 0.2, h: 0.35,
      fontSize: 11, bold: true, color: C.white, margin: 0,
    });
    ph.items.forEach((item, ii) => {
      s.addText("· " + item, {
        x: px + 0.1, y: 2.55 + ii * 0.65, w: cw - 0.2, h: 0.58,
        fontSize: 9, color: C.muted, margin: 0,
      });
    });
  });

  // Maintenance note
  s.addText("Setelah Go Live: ongoing maintenance, monitoring, dan support tersedia via monthly fee.", {
    x: 0.45, y: 5.2, w: 9.1, h: 0.3,
    fontSize: 9.5, color: C.dim, italic: true, margin: 0,
  });

  slideNum(s, 27);
}

// ─── SLIDE 28: GUARANTEE ──────────────────────────────────────────────────────
function slide28(pres) {
  const s = pres.addSlide();
  darkBg(s);

  s.addShape("ellipse", { x: 2.5, y: 0.5, w: 5, h: 5, fill: { color: C.cyanDark, transparency: 90 } });





  s.addText("100%", {
    x: 1, y: 0.5, w: 8, h: 1.6,
    fontSize: 100, bold: true, color: C.white, fontFace: "Georgia", align: "center", margin: 0,
    transparency: 8,
  });

  s.addText("Satisfaction Guarantee", {
    x: 1, y: 1.9, w: 8, h: 0.65,
    fontSize: 28, bold: true, color: C.white, fontFace: "Georgia", align: "center", margin: 0,
  });

  s.addShape("rect", { x: 3.5, y: 2.68, w: 3, h: 0.025, fill: { color: C.cyan } });

  s.addText(
    "Jika dalam 30 hari pertama sistem belum berjalan sesuai ekspektasi,\n" +
    "kami akan terus melakukan penyesuaian dan optimasi\n" +
    "tanpa biaya tambahan hingga sistem benar-benar fit\n" +
    "dengan workflow The Scholars.",
    {
      x: 1, y: 2.85, w: 8, h: 1.6,
      fontSize: 14, color: C.muted, align: "center", fontFace: "Georgia", italic: true, margin: 0,
    }
  );

  slideNum(s, 28);
}

// ─── SLIDE 29: CLOSING CTA ────────────────────────────────────────────────────
function slide29(pres) {
  const s = pres.addSlide();
  darkBg(s);

  s.addShape("rect", { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.cyan } });
  s.addShape("rect", { x: 0, y: 5.45, w: 10, h: 0.06, fill: { color: C.cyan } });

  s.addText("Let's", {
    x: 0.5, y: 0.8, w: 9, h: 0.9,
    fontSize: 52, color: C.muted, fontFace: "Georgia", italic: true, align: "center", margin: 0,
  });
  s.addText("Start.", {
    x: 0.5, y: 1.6, w: 9, h: 1.2,
    fontSize: 72, bold: true, color: C.white, fontFace: "Georgia", align: "center", margin: 0,
  });

  s.addText("Mock Booking System", {
    x: 0.5, y: 2.9, w: 9, h: 0.5,
    fontSize: 18, color: C.cyan, align: "center", margin: 0,
  });

  s.addShape("rect", { x: 3.5, y: 3.52, w: 3, h: 0.025, fill: { color: C.cyan } });

  s.addText("Presented by : Steven Leroy", {
    x: 0.5, y: 3.7, w: 9, h: 0.32,
    fontSize: 12, color: C.muted, align: "center", margin: 0,
  });
  s.addText("Thank you for your time & attention", {
    x: 0.5, y: 4.1, w: 9, h: 0.3,
    fontSize: 11, color: C.dim, align: "center", italic: true, margin: 0,
  });

  s.addText("+628155202354  ·  chatminagent@gmail.com", {
    x: 0.5, y: 4.55, w: 9, h: 0.3,
    fontSize: 11, color: C.cyan, align: "center", margin: 0,
  });
}

// ─── BUILD ────────────────────────────────────────────────────────────────────
async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "Mock Booking System — Pitch Deck";
  pres.author = "Steven Leroy";

  slide1(pres);   // Cover
  slide2(pres);   // Agenda
  slide3(pres);   // Quote
  slide4(pres);   // Pain Points 1
  slide5(pres);   // Pain Points 2
  slide6(pres);   // Solution Intro
  slide7(pres);   // Why?
  slide8(pres);   // Core Features Overview
  slide9(pres);   // The Flow
  slide10(pres);  // Feature 01: Booking Form
  slide11(pres);  // Feature 02: Slot Management
  slide12(pres);  // Feature 03: Sam Notification
  slide13(pres);  // Feature 04: Confirm/Reject
  slide14(pres);  // Feature 05: Auto WA Confirmation
  slide15(pres);  // Feature 06: Rejection + Re-open
  slide16(pres);  // Feature 07: Monthly Auto-Generate
  slide17(pres);  // Feature 08: Race Condition Protection
  slide18(pres);  // Feature 09: Human-in-the-Loop
  slide19(pres);  // Feature 10: Google Sheets Sync
  slide20(pres);  // Investment
  slide21(pres);  // Before vs After
  slide22(pres);  // Advantage #1: Time Freedom
  slide23(pres);  // Advantage #2: Zero Error
  slide24(pres);  // Advantage #3: Scalability
  slide25(pres);  // Advantage #4: Brand Image
  slide26(pres);  // ROI Calc
  slide27(pres);  // Implementation
  slide28(pres);  // Guarantee
  slide29(pres);  // Closing CTA

  await pres.writeFile({ fileName: OUT });
  console.log("Done! Slides: 29 | Output:", OUT);
}

main().catch(e => { console.error(e); process.exit(1); });
