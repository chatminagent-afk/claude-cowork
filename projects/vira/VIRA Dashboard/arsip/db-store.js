/**
 * VIRA Dashboard — Client Data Engine (db-store.js)
 * Manages local database, filtering, metrics, and n8n API sync.
 * Toggle endpoints write directly to Google Sheets via n8n webhooks.
 */

window.ViraStore = (function() {
  let rawData = {
    STATS: [],
    PROGRAM: [],
    ABOUT_SAM: [],
    FAQ: [],
    UNKNOWN: [],
    LINKS: [],
    MSG_BUFFER: [],
    MOCK_SLOTS: [],
    MOCK_INTERVIEW_BOOKING: [],
    CONFIG: []
  };

  let activeFilters = {
    dateRange: 'all',
    customStart: null,
    customEnd: null,
    searchQuery: '',
    botMode: 'all',
    programInterest: 'all',
    kelasAnak: 'all'
  };

  let isLoaded = false;
  // n8n base URL — e.g. https://n8n.yourdomain.com/webhook
  let n8nBaseUrl = localStorage.getItem('vira_n8n_url') || '';
  let globalStatus = 'ON';

  // ── Helpers ──────────────────────────────────────────────────────────

  function normWA(v) {
    if (!v) return '';
    return String(v).trim().replace(/\.0$/, '').replace(/[^0-9]/g, '');
  }

  function parseDate(dStr) {
    if (!dStr) return null;
    if (typeof dStr === 'number') return new Date(dStr);
    let dt = new Date(dStr);
    if (!isNaN(dt.getTime())) return dt;
    let parts = String(dStr).split(/[\/\-,\s]+/);
    if (parts.length >= 3) {
      let day   = parseInt(parts[0], 10);
      let month = parseInt(parts[1], 10) - 1;
      let year  = parseInt(parts[2], 10);
      if (year < 100) year += 2000;
      let testDt = new Date(year, month, day);
      if (!isNaN(testDt.getTime())) return testDt;
    }
    return null;
  }

  function buildUrl(path) {
    const base = n8nBaseUrl.replace(/\/$/, '');
    return base ? `${base}/${path}` : null;
  }

  // ── Init & Sync ───────────────────────────────────────────────────────

  async function init() {
    // Load local database.json as baseline
    try {
      const res = await fetch('database.json?v=' + Date.now());
      if (res.ok) {
        const json = await res.json();
        rawData = Object.assign(rawData, json);
        isLoaded = true;
      }
    } catch (e) {
      console.warn('[ViraStore] Could not load database.json:', e);
    }

    // Load global status from local CONFIG
    const cfg = (rawData.CONFIG || []).find(c => c.Key === 'VIRA_STATUS');
    if (cfg && cfg.Value) {
      globalStatus = String(cfg.Value).trim().toUpperCase();
    }

    // Try live sync from n8n
    if (n8nBaseUrl) {
      await syncWithApi();
    }
  }

  async function syncWithApi() {
    const url = buildUrl('vira-getdata');
    if (!url) return { ok: false, message: 'n8n URL not configured' };

    try {
      const res = await fetch(url, { method: 'GET' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      if (data.ok && data.database) {
        rawData = Object.assign(rawData, data.database);
        if (data.globalStatus) globalStatus = data.globalStatus;
        return { ok: true, source: 'n8n-live' };
      }
      return { ok: false, message: 'Invalid response from n8n' };
    } catch (e) {
      console.warn('[ViraStore] Live sync failed, using local data:', e.message);
      return { ok: false, message: e.message };
    }
  }

  // ── Filtering ─────────────────────────────────────────────────────────

  function getFilteredLeads() {
    const stats = rawData.STATS || [];
    return stats.filter(item => {
      const wa      = normWA(item['No WA']);
      const name    = String(item['Nama'] || '').toLowerCase();
      const botMode = String(item['bot_mode'] || 'ON').trim().toUpperCase();
      const progInt = String(item['program_interest'] || '');
      const kelas   = String(item['kelas_anak'] || '');

      if (activeFilters.searchQuery) {
        const q      = activeFilters.searchQuery.toLowerCase().trim();
        const normQ  = q.replace(/[^0-9]/g, '');
        const matchWA   = normQ ? wa.includes(normQ) : false;
        const matchName = name.includes(q);
        if (!matchWA && !matchName) return false;
      }

      if (activeFilters.botMode !== 'all') {
        const modeNorm = botMode === 'OFF' ? 'OFF' : 'ON';
        if (modeNorm !== activeFilters.botMode) return false;
      }

      if (activeFilters.programInterest !== 'all') {
        if (!progInt.includes(activeFilters.programInterest)) return false;
      }

      if (activeFilters.kelasAnak !== 'all') {
        if (!kelas.includes(activeFilters.kelasAnak)) return false;
      }

      if (activeFilters.dateRange !== 'all') {
        const dt = parseDate(item['Tanggal Chat Terakhir'] || item['Tanggal Chat Pertama']);
        if (dt) {
          const now = new Date();
          if (activeFilters.dateRange === 'today') {
            if (dt.toDateString() !== now.toDateString()) return false;
          } else if (activeFilters.dateRange === '7d') {
            const cutoff = new Date(now.getTime() - 7 * 86400000);
            if (dt < cutoff) return false;
          } else if (activeFilters.dateRange === '30d') {
            const cutoff = new Date(now.getTime() - 30 * 86400000);
            if (dt < cutoff) return false;
          } else if (activeFilters.dateRange === 'custom') {
            if (activeFilters.customStart && dt < activeFilters.customStart) return false;
            if (activeFilters.customEnd   && dt > activeFilters.customEnd)   return false;
          }
        }
      }

      return true;
    });
  }

  // ── Metrics ───────────────────────────────────────────────────────────

  function getSummaryMetrics() {
    const leads = getFilteredLeads();
    let botOn = 0, botOff = 0, totalChats = 0, gformSent = 0, gformFilled = 0;
    const hourCounts = Array(24).fill(0);

    leads.forEach(l => {
      const mode = String(l['bot_mode'] || 'ON').trim().toUpperCase();
      if (mode === 'OFF') botOff++; else botOn++;

      totalChats += Number(l['Counter']) || 0;
      if (l['gform_sent_ts']) gformSent++;
      if (l['gform_filled'] && String(l['gform_filled']).trim() && String(l['gform_filled']) !== 'None') gformFilled++;

      const jam = l['Jam Chat Terakhir'];
      if (jam) {
        const h = parseInt(String(jam).split(':')[0], 10);
        if (!isNaN(h) && h >= 0 && h < 24) hourCounts[h]++;
      }
    });

    let peakHour = null, maxHourChats = 0;
    hourCounts.forEach((c, idx) => { if (c > maxHourChats) { maxHourChats = c; peakHour = idx; } });

    const gformConversion = gformSent > 0 ? ((gformFilled / gformSent) * 100).toFixed(1) : '0.0';

    return {
      totalLeads: leads.length,
      totalChats,
      botOn,
      botOff,
      gformSent,
      gformFilled,
      gformConversion,
      peakHour,
      mockBookingsCount: (rawData.MOCK_INTERVIEW_BOOKING || []).length,
      unknownCount: (rawData.UNKNOWN || []).length,
      bufferCount: (rawData.MSG_BUFFER || []).length,
      globalStatus
    };
  }

  function getDailyTrend() {
    const dayMap = {};
    getFilteredLeads().forEach(l => {
      const dt = parseDate(l['Tanggal Chat Pertama'] || l['Tanggal Chat Terakhir']);
      if (dt) {
        const key = dt.toISOString().split('T')[0];
        dayMap[key] = (dayMap[key] || 0) + 1;
      }
    });
    return Object.keys(dayMap).sort().map(k => ({ date: k, count: dayMap[k] }));
  }

  function getHourlyDistribution() {
    const hours = Array(24).fill(0);
    getFilteredLeads().forEach(l => {
      const jam = l['Jam Chat Terakhir'];
      if (jam) {
        const h = parseInt(String(jam).split(':')[0], 10);
        if (!isNaN(h) && h >= 0 && h < 24) hours[h]++;
      }
    });
    return hours.map((count, hour) => ({ hour, count }));
  }

  function getProgramDistribution() {
    const dist = { Junior: 0, Intermediate: 0, Seniors: 0, Unspecified: 0 };
    getFilteredLeads().forEach(l => {
      const pi = String(l['program_interest'] || '');
      if (pi.includes('Junior'))       dist.Junior++;
      if (pi.includes('Intermediate')) dist.Intermediate++;
      if (pi.includes('Senior'))       dist.Seniors++;
      if (!pi || pi === 'None')        dist.Unspecified++;
    });
    return dist;
  }

  function getKelasDistribution() {
    const dist = { 'SD 6': 0, 'SMP 1': 0, 'SMP 2': 0, 'SMP 3': 0, 'SMA 10/11': 0, 'SMA 12': 0, 'Other/None': 0 };
    getFilteredLeads().forEach(l => {
      const k = String(l['kelas_anak'] || '');
      if      (k.includes('SD 6'))    dist['SD 6']++;
      else if (k.includes('SMP 1'))   dist['SMP 1']++;
      else if (k.includes('SMP 2'))   dist['SMP 2']++;
      else if (k.includes('SMP 3'))   dist['SMP 3']++;
      else if (k.includes('SMA 10/11')) dist['SMA 10/11']++;
      else if (k.includes('SMA 12'))  dist['SMA 12']++;
      else                            dist['Other/None']++;
    });
    return dist;
  }

  // ── Toggle Actions (write to Google Sheets via n8n) ───────────────────

  /**
   * Toggle bot_mode for a single WA user.
   * Optimistically updates local state immediately, then POSTs to n8n.
   * @param {string} wa - WA number (digits only)
   * @param {string} targetMode - 'ON' or 'OFF'
   * @returns {{ ok: boolean, mode: string, source: string }}
   */
  async function toggleUserMode(wa, targetMode) {
    wa = normWA(wa);
    targetMode = targetMode.toUpperCase();

    // 1. Optimistic local update so UI responds instantly
    const lead = (rawData.STATS || []).find(x => normWA(x['No WA']) === wa);
    if (lead) lead['bot_mode'] = targetMode;

    // 2. POST to n8n if configured
    const url = buildUrl('vira-toggle-user');
    if (!url) {
      return { ok: true, mode: targetMode, source: 'local-only', warn: 'n8n URL not configured' };
    }

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ wa, mode: targetMode })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.ok) return { ok: true, mode: data.bot_mode || targetMode, source: 'google-sheets' };
      throw new Error(data.error || 'n8n returned ok:false');
    } catch (e) {
      console.warn('[ViraStore] toggleUserMode n8n call failed:', e.message);
      return { ok: false, mode: targetMode, source: 'local-only', error: e.message };
    }
  }

  /**
   * Set global VIRA bot status.
   * @param {string} targetStatus - 'ON' or 'OFF'
   */
  async function setGlobalStatus(targetStatus) {
    targetStatus = targetStatus.toUpperCase();

    // 1. Optimistic local update
    globalStatus = targetStatus;
    const cfg = (rawData.CONFIG || []).find(c => c.Key === 'VIRA_STATUS');
    if (cfg) cfg.Value = targetStatus;
    else rawData.CONFIG.push({ Key: 'VIRA_STATUS', Value: targetStatus });

    // 2. POST to n8n if configured
    const url = buildUrl('vira-toggle-global');
    if (!url) {
      return { ok: true, status: targetStatus, source: 'local-only', warn: 'n8n URL not configured' };
    }

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: targetStatus })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.ok) return { ok: true, status: data.status || targetStatus, source: 'google-sheets' };
      throw new Error(data.error || 'n8n returned ok:false');
    } catch (e) {
      console.warn('[ViraStore] setGlobalStatus n8n call failed:', e.message);
      return { ok: false, status: targetStatus, source: 'local-only', error: e.message };
    }
  }

  // ── Public API ────────────────────────────────────────────────────────

  return {
    init,
    syncWithApi,
    getRawData:            () => rawData,
    getFilters:            () => activeFilters,
    setFilters:            (f) => Object.assign(activeFilters, f),
    getFilteredLeads,
    getSummaryMetrics,
    getDailyTrend,
    getHourlyDistribution,
    getProgramDistribution,
    getKelasDistribution,
    toggleUserMode,
    setGlobalStatus,
    getGlobalStatus:       () => globalStatus,
    setN8nUrl:             (url) => { n8nBaseUrl = url.replace(/\/$/, ''); localStorage.setItem('vira_n8n_url', n8nBaseUrl); },
    getN8nUrl:             () => n8nBaseUrl,
    normWA
  };
})();
