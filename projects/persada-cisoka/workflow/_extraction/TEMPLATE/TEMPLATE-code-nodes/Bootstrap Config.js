// ============================================================
// BOOTSTRAP CONFIG  (SATU-SATUNYA tempat edit per klien)
// Tempel Google Sheet ID milik klien di bawah ini. Semua config
// lain (persona, program, whitelist) ada di tab CONFIG sheet itu.
// ============================================================
const SHEET_ID = 'PASTE_CLIENT_GOOGLE_SHEET_ID_HERE';   // <-- EDIT INI per klien

const wh = $input.first() ? $input.first().json : {};
return [{ json: { ...wh, sheet_id: SHEET_ID } }];

