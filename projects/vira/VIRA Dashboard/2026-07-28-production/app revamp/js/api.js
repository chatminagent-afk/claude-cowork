/* ============================================================================
 * api.js — TRANSPORT
 *
 * Satu endpoint, satu method, satu bentuk request. Tidak menyentuh DOM.
 *
 * Aturan yang tidak boleh dilanggar:
 *   1. Header HANYA Content-Type: text/plain;charset=UTF-8. Header lain akan
 *      memicu preflight OPTIONS yang tidak ditangani webhook.
 *   2. Token dikirim di body, bukan di header Authorization (alasan sama).
 *   3. Client TIDAK PERNAH mengirim `tenant`. Satu-satunya pengecualian adalah
 *      action `switch_tenant`, dan itu pun divalidasi ulang di server.
 *
 * `call()` tidak pernah reject. Kegagalan jaringan dikemas menjadi objek
 * { ok:false, error:'NETWORK', message:'...' } supaya pemanggil hanya perlu
 * satu jalur penanganan.
 * ========================================================================== */
'use strict';

var VDApi = (function (global) {

  var cfg = global.VDConfig || {};
  var baseUrl = cfg.API_URL || '';

  /* Cadangan kalau localStorage diblokir (mode privat / iframe ketat). */
  var memoryToken = '';

  function store() {
    try { return global.localStorage; } catch (e) { return null; }
  }

  /**
   * Kunci penyimpanan token mengikuti origin API yang sedang aktif.
   * Konsekuensinya: mengganti alamat API berarti tidak ada token untuk dikirim,
   * sehingga token produksi tidak pernah sampai ke endpoint lain.
   */
  function storageKey() {
    if (typeof cfg.tokenKey === 'function') return cfg.tokenKey(baseUrl);
    return cfg.STORAGE_TOKEN || 'vd.token';
  }

  function getToken() {
    var s = store();
    if (s) { try { return s.getItem(storageKey()) || ''; } catch (e) { /* jatuh ke memori */ } }
    return memoryToken;
  }

  function setToken(t) {
    var v = t ? String(t) : '';
    memoryToken = v;
    var s = store();
    if (s) { try { v ? s.setItem(storageKey(), v) : s.removeItem(storageKey()); } catch (e) {} }
    return v;
  }

  function clearToken() { return setToken(''); }

  function setBaseUrl(url) {
    var next = url ? String(url) : '';
    if (next !== baseUrl) memoryToken = '';   // token milik alamat lama
    baseUrl = next;
    return baseUrl;
  }

  function getBaseUrl() { return baseUrl; }

  function text(key, fallback) {
    var t = cfg.TEXT || {};
    return t[key] || fallback;
  }

  function fail(code, message) {
    return { ok: false, error: code, message: message };
  }

  /** Susun body request. `action` selalu menang atas isi `body`. */
  function buildBody(action, body) {
    var out = {};
    if (body && typeof body === 'object') {
      for (var k in body) {
        if (Object.prototype.hasOwnProperty.call(body, k)) out[k] = body[k];
      }
    }
    out.action = action;
    if (action !== 'login') {
      if (!out.token) {
        var t = getToken();
        if (t) out.token = t;
      }
    } else {
      delete out.token;
    }
    return out;
  }

  /**
   * Titik suntik payload uji. Kalau `window.__VD_MOCK__` ada, seluruh lapisan
   * fetch dilewati. Aman ditinggal di produksi: tidak pernah aktif kecuali ada
   * yang menyetelnya dengan sengaja dari konsol atau dari harness QA.
   *
   * Bentuk yang diterima:
   *   - function(body) -> respons | Promise<respons>
   *   - object { login: {...}, stats: {...} }  (dipilih berdasarkan action)
   */
  function injected(payload) {
    var hook = global.__VD_MOCK__;
    if (!hook) return null;
    if (typeof hook === 'function') return Promise.resolve(hook(payload));
    if (typeof hook === 'object') {
      var r = hook[payload.action];
      if (typeof r === 'function') return Promise.resolve(r(payload));
      if (r) return Promise.resolve(r);
      return Promise.resolve(fail('BAD_REQUEST', 'Action tidak tersedia.'));
    }
    return null;
  }

  function call(action, body) {
    var payload = buildBody(action, body);

    var hooked = injected(payload);
    if (hooked) {
      return hooked.then(normalize).catch(function () {
        return fail(cfg.CLIENT_ERRORS ? cfg.CLIENT_ERRORS.BAD_RESPONSE : 'BAD_RESPONSE',
                    text('badResponse', 'Respons tidak bisa dibaca.'));
      });
    }

    if (!baseUrl) {
      return Promise.resolve(fail('NETWORK', text('network', 'Alamat server belum diatur.')));
    }

    var ctl = null, timer = null;
    var init = {
      method: 'POST',
      headers: { 'Content-Type': cfg.CONTENT_TYPE || 'text/plain;charset=UTF-8' },
      body: JSON.stringify(payload)
    };

    if (typeof global.AbortController === 'function') {
      ctl = new global.AbortController();
      init.signal = ctl.signal;
      timer = global.setTimeout(function () { try { ctl.abort(); } catch (e) {} },
                                cfg.REQUEST_TIMEOUT_MS || 25000);
    }

    return global.fetch(baseUrl, init)
      .then(function (res) { return res.text(); })
      .then(function (raw) {
        if (timer) global.clearTimeout(timer);
        var parsed;
        try { parsed = JSON.parse(raw); }
        catch (e) { return fail('BAD_RESPONSE', text('badResponse', 'Respons tidak bisa dibaca.')); }
        return normalize(parsed);
      })
      .catch(function () {
        if (timer) global.clearTimeout(timer);
        return fail('NETWORK', text('network', 'Tidak bisa menghubungi server.'));
      });
  }

  /** Pastikan bentuk minimum ada, dan isi `message` kalau server tidak mengirim. */
  function normalize(res) {
    if (!res || typeof res !== 'object') {
      return fail('BAD_RESPONSE', text('badResponse', 'Respons tidak bisa dibaca.'));
    }
    if (res.ok === true) return res;
    var code = res.error || 'BAD_REQUEST';
    var msg = res.message;
    if (!msg) {
      var table = cfg.ERROR_TEXT || {};
      msg = table[code] || text('unknown', 'Terjadi kesalahan.');
    }
    return { ok: false, action: res.action, error: code, message: msg, data: res };
  }

  /** true kalau error menandakan sesi tidak lagi sah -> frontend harus keluar. */
  function isAuthError(code) {
    if (!code) return false;
    var re = cfg.AUTH_ERRORS || /^TOKEN_|^TENANT_|^ROLE_CHANGED$/;
    return re.test(String(code));
  }

  return {
    setBaseUrl: setBaseUrl,
    getBaseUrl: getBaseUrl,
    call: call,
    getToken: getToken,
    setToken: setToken,
    clearToken: clearToken,
    isAuthError: isAuthError,
    normalize: normalize
  };

})(typeof window !== 'undefined' ? window : this);

if (typeof window !== 'undefined') window.VDApi = VDApi;
if (typeof module !== 'undefined' && module.exports) module.exports = VDApi;
