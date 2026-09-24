// Pilih link GForm dari sheet LINKS sesuai nama yang diminta AI (data-driven)
const rows = $('Query LINKS for GForm').all().map(i => i.json);
const proc = $('Process All').first().json;
const phone = $('Chat Counter').first().json.user_wa || proc.user_wa || '';
const requested = String(proc.gformLinkName || '').trim();

const norm = s => String(s || '').toLowerCase().replace(/\s+/g, ' ').trim();
const activeRows = rows.filter(r => /aktif|active|on|ya/i.test(String(r['Status'] || '')));

let match = null;
if (requested) {
  const rq = norm(requested);
  match = activeRows.find(r => norm(r['Nama Link']) === rq)
       || activeRows.find(r => { const n = norm(r['Nama Link']); return n && (n.includes(rq) || rq.includes(n)); });
}

if (match && match['URL']) {
  const desc = String(match['Deskripsi'] || '').trim();
  const intro = desc
    ? `Berikut ${desc.charAt(0).toLowerCase() + desc.slice(1)}`
    : `Berikut link ${match['Nama Link']}`;
  const message = `Haii! 😊 ${intro} ya:\n\n👉 ${match['URL']}\n\nSilakan diisi yaa, nanti tim kami follow up setelah form terisi. Ada yang mau ditanyain dulu sebelum isi? Santai aja tanya ke sini! 🙌`;
  console.log('✅ GForm link resolved:', match['Nama Link']);
  return [{ json: { ...proc, gformResolved: true, gformUrl: match['URL'], gformLinkName: match['Nama Link'], gformDesc: desc, phone, message } }];
}

// ── FALLBACK: nama kosong / tidak cocok -> tanya ulang link mana ──
const formRows = activeRows.filter(r => /gform|pendaftaran|mock/i.test(String(r['Nama Link'] || '')));
const listRows = formRows.length ? formRows : activeRows;
const opts = listRows.map(r => {
  const dsc = String(r['Deskripsi'] || '').trim();
  return dsc ? `• ${r['Nama Link']} (${dsc})` : `• ${r['Nama Link']}`;
}).join('\n');
const reason = requested ? `nama link "${requested}" tidak ketemu di LINKS` : 'AI tidak menyertakan nama link';
console.warn('⚠️ Pick GForm Link fallback (tanya ulang):', reason);
const message = opts
  ? `Boleh dibantu kirim link-nya 😊 Yang dimaksud yang mana ya:\n${opts}\n\nTinggal sebut salah satu, nanti langsung saya kirimkan.`
  : 'Boleh dibantu, link mana yang mau dikirim ya? Sebutkan program/keperluannya, nanti saya kirimkan.';
return [{ json: { ...proc, gformResolved: false, gformUrl: '', gformLinkName: requested, phone, message } }];

