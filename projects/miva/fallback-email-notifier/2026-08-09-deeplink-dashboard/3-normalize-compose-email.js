// ============================================================
// GLOBAL EMAIL FALLBACK - normalisasi payload + compose email
// Menerima 2 bentuk input:
//   A) direct  : dipanggil Execute Workflow dari Error Notifier
//                saat Kirimi gagal  -> d.source === 'kirimi_fallback'
//   B) error   : dipicu sebagai Error Workflow n8n (lapis 2)
// ============================================================

// >>> WAJIB DIGANTI: base URL instance n8n, TANPA trailing slash <<<
const N8N_BASE = 'https://n8n.srv1270416.hstgr.cloud';
const DASH_BASE = 'https://n8n.chatminagent.workers.dev';   // n8n mobile dashboard

const d = $input.first().json || {};
const direct = d.source === 'kirimi_fallback';

// ---- tenant / penanda klien ----
const hay = String(direct ? (d.tenant || d.notifier_wf_name || '') : (d.workflow?.name || '')).toLowerCase();
let tenant = 'VIRA-?';
if (hay.includes('pcr') || hay.includes('persada')) tenant = 'VIRA-PCR';
else if (hay.includes('scholar') || hay.includes('v4')) tenant = 'VIRA-SCHOLARS';

// ---- notifier yang gagal ----
const notifierWf   = direct ? (d.notifier_wf_name || '-') : (d.workflow?.name || '-');
const notifierWfId = direct ? (d.notifier_wf_id || '')    : (d.workflow?.id || '');
const notifierExec = direct ? (d.notifier_exec_id || '')  : (d.execution?.id || '');
const failNode     = direct ? (d.fail_node || 'Notify Admin Error (Kirimi)') : (d.execution?.error?.node?.name || d.execution?.lastNodeExecuted || '-');
const failReason   = String(direct ? (d.fail_reason || 'unknown error') : (d.execution?.error?.message || 'unknown error')).slice(0, 600);
const kirimiResp   = String(d.kirimi_response || '').slice(0, 800);

// ---- error aslinya (hanya tersedia di jalur direct) ----
const origWf   = direct ? (d.orig_wf_name || '-') : '-';
const origWfId = direct ? (d.orig_wf_id || '')    : '';
const origExec = direct ? (d.orig_exec_id || '-') : '-';
const origNode = direct ? (d.orig_node || '-')    : '-';
const origErr  = String(direct ? (d.orig_error || '-') : '-').slice(0, 600);

const mkUrl = (wfId, execId) => (wfId && execId && execId !== '-') ? `${N8N_BASE}/workflow/${wfId}/executions/${execId}` : '';
const origUrl     = (direct && d.orig_exec_url) ? d.orig_exec_url : mkUrl(origWfId, origExec);
const notifierUrl = mkUrl(notifierWfId, notifierExec);

// Deep link dashboard: yang perlu di-retry adalah execution ASLI yang gagal,
// bukan execution notifier-nya.
const dashUrl = /^\d+$/.test(String(origExec)) ? `${DASH_BASE}/#/e/${origExec}` : '';

const waText = String(d.notif_text || '').trim();
const ts = new Date().toLocaleString('id-ID', { timeZone: 'Asia/Jakarta', dateStyle: 'full', timeStyle: 'medium' });

const headline = origWf !== '-' ? origWf : notifierWf;
const headExec = origExec !== '-' ? origExec : (notifierExec || '-');
const subject = `\u{1F6A8} [${tenant}] WA ALERT GAGAL TERKIRIM - ${headline} #${headExec}`;

// ---------------- plain text ----------------
const textBody = [
  `[${tenant}] WA ALERT GAGAL TERKIRIM`,
  `Waktu: ${ts} WIB`,
  '',
  '--- 1. ISI ALERT YANG GAGAL DIKIRIM KE WA ---',
  waText || '(tidak tersedia - buka execution notifier di bawah, lihat input node Error Trigger)',
  '',
  '--- 2. KENAPA WA-NYA GAGAL ---',
  `Notifier : ${notifierWf}`,
  `Node     : ${failNode}`,
  `Sebab    : ${failReason}`,
  kirimiResp ? `Response : ${kirimiResp}` : '',
  notifierUrl ? `Execution notifier: ${notifierUrl}` : '',
  '',
  '--- 3. ERROR ASLINYA ---',
  `Workflow : ${origWf}`,
  `Node     : ${origNode}`,
  `Error    : ${origErr}`,
  origUrl ? `Execution: ${origUrl}` : '',
  dashUrl ? `Retry dari HP: ${dashUrl}` : '',
  '',
  'Ada kemungkinan pesan user TIDAK terbalas. Cek & balas manual.'
].filter(Boolean).join('\n');

// ---------------- html ----------------
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const row = (k, v) => `<tr><td style="padding:5px 12px 5px 0;color:#5f6368;white-space:nowrap;vertical-align:top">${k}</td><td style="padding:5px 0;word-break:break-word"><code style="font:13px ui-monospace,Consolas,monospace">${esc(v)}</code></td></tr>`;
const btn = (url, label, bg) => url ? `<a href="${url}" style="display:inline-block;padding:10px 18px;margin:6px 8px 0 0;background:${bg};color:#fff;text-decoration:none;border-radius:6px;font:600 13px system-ui">${label}</a>` : '';
const h3 = (t) => `<h3 style="margin:22px 0 8px;font:700 14px system-ui;color:#202124">${t}</h3>`;

const html = `<div style="font:14px/1.6 system-ui,'Segoe UI',Arial,sans-serif;color:#202124;max-width:680px">
  <div style="background:#d93025;color:#fff;padding:16px 20px;border-radius:8px 8px 0 0">
    <div style="font-size:18px;font-weight:700">\u{1F6A8} ${tenant} &mdash; WA ALERT GAGAL TERKIRIM</div>
    <div style="font-size:12px;opacity:.9;margin-top:2px">${ts} WIB</div>
  </div>
  <div style="border:1px solid #dadce0;border-top:0;padding:18px 20px 24px;border-radius:0 0 8px 8px">
    <p style="margin:0">Email ini terkirim karena <b>notifikasi WhatsApp lewat Kirimi tidak berhasil dikirim</b>. Isi alert aslinya ada di bawah.</p>

    ${h3('1. Isi alert yang gagal dikirim ke WA')}
    <pre style="background:#f1f3f4;border:1px solid #dadce0;border-radius:6px;padding:12px;white-space:pre-wrap;word-break:break-word;font:13px/1.55 ui-monospace,Consolas,monospace;margin:0">${esc(waText || '(tidak tersedia \u2014 buka execution notifier di bawah, lihat input node Error Trigger)')}</pre>

    ${h3('2. Kenapa WA-nya gagal')}
    <table style="border-collapse:collapse;font-size:13px">
      ${row('Notifier', notifierWf)}
      ${row('Node', failNode)}
      ${row('Sebab', failReason)}
      ${kirimiResp ? row('Response', kirimiResp) : ''}
    </table>

    ${h3('3. Error aslinya')}
    <table style="border-collapse:collapse;font-size:13px">
      ${row('Workflow', origWf)}
      ${row('Node', origNode)}
      ${row('Error', origErr)}
      ${row('Execution', origExec)}
    </table>

    <div style="margin-top:18px">
      ${btn(dashUrl, '\u{1F4F1} Retry dari HP', '#1a73e8')}
      ${btn(origUrl, '\u2192 Buka execution yang error', '#d93025')}
      ${btn(notifierUrl, '\u2192 Buka execution notifier', '#5f6368')}
    </div>

    <p style="margin:22px 0 0;padding:12px 14px;background:#fef7e0;border-left:4px solid #f9ab00;border-radius:4px">
      \u26A0\uFE0F Ada kemungkinan pesan user <b>TIDAK terbalas</b>. Cek &amp; balas manual.
    </p>
  </div>
</div>`;

return [{ json: { tenant, subject, html, text: textBody } }];