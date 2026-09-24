/**
 * VIRA Dashboard — Backend (Google Apps Script)
 * The Scholars — Real-time WhatsApp Bot Control & Analytics Engine
 * Spreadsheet ID: 1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE
 *
 * Capabilities:
 *  - Global VIRA Toggle (ON / OFF) via CONFIG sheet
 *  - Per-User Bot Toggle (ON / OFF) via STATS sheet
 *  - Multi-sheet Realtime Sync (STATS, MOCK_INTERVIEW_BOOKING, MOCK_SLOTS, UNKNOWN, MSG_BUFFER, etc.)
 *  - CORS-friendly text/plain JSON API handler
 */

var CONFIG_APP = {
  SPREADSHEET_ID: '1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE',
  PIN: '', // Optional PIN (blank for single-user mode)
  STATS_SHEET: 'STATS',
  CONFIG_SHEET: 'CONFIG',
  AUDIT_SHEET: 'AUDIT_LOG',
  GLOBAL_KEY: 'VIRA_STATUS'
};

function doGet(e) {
  return handle_(e, (e && e.parameter) ? e.parameter : {});
}

function doPost(e) {
  var payload = {};
  try {
    if (e && e.postData && e.postData.contents) {
      payload = JSON.parse(e.postData.contents);
    }
  } catch (err) {
    return json_({ ok: false, error: 'BAD_JSON', message: 'Body is not valid JSON.' });
  }
  return handle_(e, payload);
}

function handle_(e, p) {
  var action = p.action || 'ping';
  try {
    // Validate PIN if configured
    if (CONFIG_APP.PIN && String(CONFIG_APP.PIN).trim() !== '') {
      if (action !== 'ping' && String(p.pin || '') !== String(CONFIG_APP.PIN)) {
        return json_({ ok: false, error: 'BAD_PIN', message: 'Invalid PIN.' });
      }
    }

    switch (action) {
      case 'ping':            return json_({ ok: true, service: 'VIRA Dashboard API', time: now_() });
      case 'getAllData':      return json_(getAllData_());
      case 'getStatus':       return json_(getStatus_());
      case 'setGlobalStatus': return json_(setGlobalStatus_(p));
      case 'listUsers':       return json_(listUsers_(p));
      case 'searchUser':      return json_(searchUser_(p));
      case 'setUserMode':     return json_(setUserMode_(p));
      case 'getStats':        return json_(getStats_());
      default:                return json_({ ok: false, error: 'UNKNOWN_ACTION', message: 'Unknown action: ' + action });
    }
  } catch (err) {
    return json_({ ok: false, error: 'SERVER_ERROR', message: String(err && err.message || err) });
  }
}

function ss_() {
  return SpreadsheetApp.openById(CONFIG_APP.SPREADSHEET_ID);
}

function sheet_(name) {
  var ss = ss_();
  var sh = ss.getSheetByName(name);
  if (!sh) throw new Error('Sheet "' + name + '" not found in spreadsheet.');
  return sh;
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function now_() {
  return Utilities.formatDate(new Date(), 'GMT+7', 'yyyy-MM-dd HH:mm:ss');
}

/** Fetch all database sheets in one call */
function getAllData_() {
  var ss = ss_();
  var sheets = ss.getSheets();
  var db = {};
  
  sheets.forEach(function(sh) {
    var name = sh.getName();
    if (name === CONFIG_APP.AUDIT_SHEET) return;
    var values = sh.getDataRange().getValues();
    if (values.length <= 1) {
      db[name] = [];
      return;
    }
    var headers = values[0].map(function(h) { return String(h).trim(); });
    var rows = [];
    for (var i = 1; i < values.length; i++) {
      var r = values[i];
      if (!r.some(function(c) { return c !== '' && c !== null; })) continue;
      var obj = {};
      for (var j = 0; j < headers.length; j++) {
        var h = headers[j];
        var val = r[j];
        if (val instanceof Date) {
          val = Utilities.formatDate(val, 'GMT+7', "yyyy-MM-dd'T'HH:mm:ss");
        }
        obj[h] = val;
      }
      rows.push(obj);
    }
    db[name] = rows;
  });

  var statusRes = getStatus_();

  return {
    ok: true,
    globalStatus: statusRes.status,
    database: db,
    syncedAt: now_()
  };
}

/** Read Global VIRA Status */
function getStatus_() {
  var sh = sheet_(CONFIG_APP.CONFIG_SHEET);
  var data = sh.getDataRange().getValues();
  var status = null, rowIdx = -1;
  for (var i = 1; i < data.length; i++) {
    if (String(data[i][0]).trim() === CONFIG_APP.GLOBAL_KEY) {
      status = String(data[i][1]).trim().toUpperCase();
      rowIdx = i + 1;
      break;
    }
  }
  if (rowIdx === -1) {
    sh.appendRow([CONFIG_APP.GLOBAL_KEY, 'ON']);
    status = 'ON';
  }
  if (status !== 'ON' && status !== 'OFF') status = 'ON';
  return { ok: true, status: status };
}

/** Set Global VIRA Status */
function setGlobalStatus_(p) {
  var target = String(p.status || '').trim().toUpperCase();
  if (target !== 'ON' && target !== 'OFF') {
    return { ok: false, error: 'BAD_STATUS', message: 'status must be ON or OFF.' };
  }
  var sh = sheet_(CONFIG_APP.CONFIG_SHEET);
  var data = sh.getDataRange().getValues();
  var rowIdx = -1;
  for (var i = 1; i < data.length; i++) {
    if (String(data[i][0]).trim() === CONFIG_APP.GLOBAL_KEY) { rowIdx = i + 1; break; }
  }
  if (rowIdx === -1) {
    sh.appendRow([CONFIG_APP.GLOBAL_KEY, target]);
  } else {
    sh.getRange(rowIdx, 2).setValue(target);
  }
  audit_(p.by || 'Sam', 'SET_GLOBAL', CONFIG_APP.GLOBAL_KEY, target);
  return { ok: true, status: target };
}

/** Normalize WhatsApp string */
function normWA_(v) {
  var s = String(v == null ? '' : v).trim();
  s = s.replace(/\.0$/, '').replace(/[^0-9]/g, '');
  return s;
}

function statsCtx_() {
  var sh = sheet_(CONFIG_APP.STATS_SHEET);
  var values = sh.getDataRange().getValues();
  var header = values[0].map(function (h) { return String(h).trim(); });
  var colWA = header.indexOf('No WA');
  var colMode = header.indexOf('bot_mode');
  var colNama = header.indexOf('Nama');
  var colCounter = header.indexOf('Counter');
  var colLast = header.indexOf('Tanggal Chat Terakhir');
  if (colWA === -1 || colMode === -1) {
    throw new Error('Columns "No WA" / "bot_mode" not found in STATS sheet.');
  }
  return { sh: sh, values: values, header: header, colWA: colWA, colMode: colMode,
           colNama: colNama, colCounter: colCounter, colLast: colLast };
}

function listUsers_(p) {
  var ctx = statsCtx_();
  var limit = Math.min(parseInt(p.limit || '300', 10) || 300, 2000);
  var out = [];
  for (var i = 1; i < ctx.values.length; i++) {
    var r = ctx.values[i];
    var wa = normWA_(r[ctx.colWA]);
    if (!wa) continue;
    out.push({
      row: i + 1,
      wa: wa,
      nama: ctx.colNama > -1 ? String(r[ctx.colNama] || '') : '',
      bot_mode: String(r[ctx.colMode] || 'ON').trim().toUpperCase() === 'OFF' ? 'OFF' : 'ON',
      counter: ctx.colCounter > -1 ? (Number(r[ctx.colCounter]) || 0) : 0,
      last: ctx.colLast > -1 ? String(r[ctx.colLast] || '') : ''
    });
  }
  out.sort(function (a, b) { return b.counter - a.counter; });
  return { ok: true, total: out.length, users: out.slice(0, limit) };
}

function searchUser_(p) {
  var q = normWA_(p.q || '');
  if (!q) return { ok: false, error: 'EMPTY_QUERY', message: 'Enter WA number.' };
  var ctx = statsCtx_();
  var out = [];
  for (var i = 1; i < ctx.values.length; i++) {
    var wa = normWA_(ctx.values[i][ctx.colWA]);
    if (wa && wa.indexOf(q) > -1) {
      var r = ctx.values[i];
      out.push({
        row: i + 1, wa: wa,
        nama: ctx.colNama > -1 ? String(r[ctx.colNama] || '') : '',
        bot_mode: String(r[ctx.colMode] || 'ON').trim().toUpperCase() === 'OFF' ? 'OFF' : 'ON',
        counter: ctx.colCounter > -1 ? (Number(r[ctx.colCounter]) || 0) : 0,
        last: ctx.colLast > -1 ? String(r[ctx.colLast] || '') : ''
      });
    }
  }
  return { ok: true, total: out.length, users: out.slice(0, 50) };
}

function setUserMode_(p) {
  var wa = normWA_(p.wa || '');
  var target = String(p.mode || '').trim().toUpperCase();
  if (!wa) return { ok: false, error: 'EMPTY_WA', message: 'Empty WA number.' };
  if (target !== 'ON' && target !== 'OFF') return { ok: false, error: 'BAD_MODE', message: 'mode must be ON or OFF.' };

  var ctx = statsCtx_();
  var rowIdx = -1;
  for (var i = 1; i < ctx.values.length; i++) {
    if (normWA_(ctx.values[i][ctx.colWA]) === wa) { rowIdx = i + 1; break; }
  }
  if (rowIdx === -1) return { ok: false, error: 'NOT_FOUND', message: 'User not found in STATS.' };

  ctx.sh.getRange(rowIdx, ctx.colMode + 1).setValue(target);
  audit_(p.by || 'Sam', 'SET_USER_MODE', wa, target);
  return { ok: true, wa: wa, bot_mode: target };
}

function getStats_() {
  var ctx = statsCtx_();
  var totalUsers = 0, totalChats = 0, botOn = 0, botOff = 0;
  for (var i = 1; i < ctx.values.length; i++) {
    var r = ctx.values[i];
    var wa = normWA_(r[ctx.colWA]);
    if (!wa) continue;
    totalUsers++;
    totalChats += Number(r[ctx.colCounter]) || 0;
    var mode = String(r[ctx.colMode] || 'ON').trim().toUpperCase();
    if (mode === 'OFF') botOff++; else botOn++;
  }
  return {
    ok: true,
    summary: {
      totalUsers: totalUsers,
      totalChats: totalChats,
      botOn: botOn,
      botOff: botOff,
      generatedAt: now_()
    }
  };
}

function audit_(by, action, target, val) {
  try {
    var ss = ss_();
    var sh = ss.getSheetByName(CONFIG_APP.AUDIT_SHEET);
    if (!sh) {
      sh = ss.insertSheet(CONFIG_APP.AUDIT_SHEET);
      sh.appendRow(['Timestamp', 'User', 'Action', 'Target', 'Value']);
    }
    sh.appendRow([now_(), by, action, target, val]);
  } catch (e) {}
}
