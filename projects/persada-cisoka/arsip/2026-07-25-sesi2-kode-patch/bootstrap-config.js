// ============================================================
// BOOTSTRAP CONFIG  — PATCH Sesi 2 (T1)
// SHEET_ID = spreadsheet "Persada_Cisoka_Database" (PCR_Database.xlsx).
// WAJIB sama dengan documentId di 23 node Google Sheets workflow ini.
// Kalau spreadsheet dipindah/diganti, ubah di SATU tempat ini + di node Sheets.
// ============================================================
const SHEET_ID = '1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o';
const wh = $input.first() ? $input.first().json : {};
return [{ json: { ...wh, sheet_id: SHEET_ID } }];
