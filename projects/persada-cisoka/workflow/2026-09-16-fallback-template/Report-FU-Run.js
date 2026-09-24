// ====================================================================
// REPORT FU RUN (2026-08-27)
// Dipasang di output "done" Loop Kandidat yang selama ini menganggur.
// DIAM TOTAL kalau tidak ada kegagalan - ini alarm, bukan laporan rutin.
// Tanpa ini, satu lead yang konteksnya selalu bikin AI melanggar akan
// dicoba ulang tiap jam selamanya tanpa ada yang tahu.
// ====================================================================
let gagal = [];
try {
  const sd = $getWorkflowStaticData('global');
  gagal = Array.isArray(sd.fu_ai_fail) ? sd.fu_ai_fail.slice() : [];
  sd.fu_ai_fail = [];
} catch (e) {}

let total = 0;
try { total = $('Filter Kandidat').all().length; } catch (e) {}
let antrian = 0;
try { antrian = Number($('Filter Kandidat').first().json.antrian_total || 0); } catch (e) {}

// Mode uji WAJIB selalu dilaporkan, walau tidak ada kegagalan - kalau lupa
// dikosongkan, follow-up berhenti menjangkau lead sungguhan tanpa gejala apa pun.
let ujiInfo = '';
try {
  const tn = $('Parse Config FU').first().json.config.test_numbers || [];
  if (tn.length) ujiInfo = tn.join(', ');
} catch (e) {}
const modeUji = !!ujiInfo;

// (2026-09-13) Penolakan guard (penanda FU_AI_DITOLAK_GUARD dari "Validate FU Message")
// TIDAK di-rollback ke jadwal lama: "Rollback STATS FU (AI)" menunda nomor itu ke jadwal
// follow-up berikutnya, jadi tidak muncul lagi tiap jam. Gagal teknis (AI/credential)
// tetap di-rollback dan dicoba lagi run berikutnya - teks lamanya dipertahankan.
const isGuard = g => String(g.alasan || '').indexOf('FU_AI_DITOLAK_GUARD') !== -1;
// (2026-09-16) Penanda dari "Validate FU Message": kalimat AI ditolak guard TAPI lead
// tetap dikirimi template rotasi. Itu bukan kegagalan - jangan dihitung "dilewati".
const isFallback = g => String(g.alasan || '').indexOf('FU_AI_FALLBACK_TEMPLATE') !== -1;
const tampil = g => isFallback(g)
  ? String(g.alasan).replace('FU_AI_FALLBACK_TEMPLATE', 'dikirim pakai template, kalimat AI ditolak guard').replace(/\s*\[line [^\]]*\]\s*$/, '')
  : (isGuard(g)
    ? String(g.alasan).replace('FU_AI_DITOLAK_GUARD', 'ditolak guard').replace(/\s*\[line [^\]]*\]\s*$/, '')
    : g.alasan);
const nFallback = gagal.filter(isFallback).length;
const nGuard = gagal.filter(isGuard).length;
const nTeknis = gagal.length - nGuard - nFallback;
const nDilewati = nGuard + nTeknis;
let intervalJam = 0;
try { intervalJam = Number($('Parse Config FU').first().json.config.followup_interval_hours || 0); } catch (e) {}

const baris = gagal.slice(0, 10).map(g => '- ' + g.no_wa + ': ' + tampil(g)).join('\n');
const sisa = gagal.length > 10 ? ('\n... dan ' + (gagal.length - 10) + ' lagi') : '';

const penutup = [];
if (nFallback) {
  penutup.push('Nomor yang "dikirim pakai template" TETAP menerima pesan - hanya kalimat '
    + 'AI-nya yang ditolak guard, lalu diganti template rotasi CONFIG. follow_up_count '
    + 'naik seperti biasa. Kalau nomor yang sama muncul terus, periksa kolom Nama dan '
    + 'konteks-nya di STATS.');
}
if (nGuard) {
  penutup.push('Nomor yang "ditolak guard" TIDAK dikirimi pesan dan DITUNDA ke jadwal follow-up berikutnya'
    + (intervalJam ? (' (' + intervalJam + ' jam lagi)') : '') + ', jadi tidak diulang tiap jam.');
}
if (nTeknis) {
  penutup.push(((nGuard || nFallback) ? 'Sisanya' : 'Nomor-nomor itu') + ' TIDAK dikirimi pesan dan klaimnya sudah di-rollback, jadi akan dicoba lagi run berikutnya. Kalau nomor yang sama muncul terus tiap jam, konteksnya perlu diperiksa manual.');
}

const infoAntrian = (antrian > total)
  ? (' (cap ' + total + ' per run; antrian layak follow-up masih ' + antrian + ')')
  : '';
// Tanpa fallback, judul ini sama persis dengan versi lama.
const judul = nFallback
  ? ('[PCR] FOLLOW-UP AI: ' + nFallback + ' dari ' + total + ' kandidat dikirim pakai template'
     + (nDilewati ? (', ' + nDilewati + ' dilewati') : '') + infoAntrian)
  : ('[PCR] FOLLOW-UP AI: ' + gagal.length + ' dari ' + total + ' kandidat dilewati' + infoAntrian);
const notif_text = judul + '\n\n' + baris + sisa +
  (penutup.length ? ('\n\n' + penutup.join('\n\n')) : '\n\nNomor-nomor itu TIDAK dikirimi pesan dan klaimnya sudah di-rollback, jadi akan dicoba lagi run berikutnya. Kalau nomor yang sama muncul terus tiap jam, konteksnya perlu diperiksa manual.');

const peringatanUji = modeUji
  ? ('\n\nMODE UJI masih AKTIF - hanya ' + ujiInfo + ' yang di-follow-up. '
     + 'Lead sungguhan TIDAK tersentuh. Kosongkan CONFIG followup_test_numbers '
     + 'kalau sudah selesai menguji.')
  : '';

return [{ json: {
  perlu_notif: gagal.length > 0 || modeUji,
  mode_uji: modeUji,
  ada_gagal: gagal.length > 0,
  jumlah_gagal: gagal.length,
  jumlah_fallback: nFallback,
  jumlah_dilewati: nDilewati,
  total_kandidat: total,
  notif_text: notif_text + peringatanUji
}}];
