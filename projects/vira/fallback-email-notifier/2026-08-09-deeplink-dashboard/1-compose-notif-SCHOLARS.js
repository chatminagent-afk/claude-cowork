// Susun notifikasi error untuk admin
// 2026-08-09: + deep link ke n8n mobile dashboard supaya bisa retry dari HP
//             tanpa membuka UI n8n.
const DASH = 'https://n8n.chatminagent.workers.dev';

const e = $input.first().json;
const wfName = e.workflow?.name || 'VIRA';
const execId = e.execution?.id || '-';
const node = e.execution?.error?.node?.name || e.execution?.lastNodeExecuted || '-';
const msg = (e.execution?.error?.message || 'unknown error').substring(0, 300);
const url = e.execution?.url || '-';

// Link hanya dibuat kalau execution id benar-benar ada. Error Trigger TIDAK
// mengirim execution.id kalau errornya terjadi di node trigger — tanpa penjagaan
// ini, link-nya jadi ".../#/e/-" yang cuma bikin bingung.
const dashUrl = /^\d+$/.test(String(execId)) ? `${DASH}/#/e/${execId}` : '';

const text = `\u{1F6A8} [${wfName}] EKSEKUSI GAGAL\nNode: ${node}\nError: ${msg}\nExecution: ${execId}`
  + (dashUrl ? `\n\n\u{1F4F1} Retry dari HP:\n${dashUrl}` : '')
  + `\n\n\u{1F5A5}\uFE0F Buka di n8n:\n${url}`
  + `\n\n\u26A0\uFE0F Ada pesan user yang kemungkinan TIDAK terbalas. Cek & balas manual.`;

return [{ json: { notif_text: text } }];
