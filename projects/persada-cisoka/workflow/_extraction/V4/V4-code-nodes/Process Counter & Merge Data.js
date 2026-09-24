// ====================================================================
// PROCESS COUNTER & MERGE DATA (V4)
// Fix: (1) matching row No WA primer / lid backup (bukan lid-only),
//      (2) "Tanggal Chat Pertama" dibaca dari kolom yang benar
//          (dulu baca existingRow.Tanggal yang tidak ada -> tanggal
//          pertama ter-reset jadi hari ini setiap pesan),
//      (3) error -> stop (return []) alih-alih menulis row "ERROR".
// ====================================================================
const debugLog = [];

try {
    const allItems = $input.all();
    debugLog.push("Step 1: Received " + allItems.length + " items from Read STATS");

    const chatCounter = $('Chat Counter').first().json;
    const resolve = $('Resolve User Row').first().json;
    const resolvedKey = resolve.resolved_key;

    const userName = chatCounter.user_name || "User";
    const userMessage = chatCounter.original_message || "";
    const digits = v => String(v ?? '').replace(/\D/g, '');
    const phone = digits(chatCounter.user_phone);
    const lid = digits(chatCounter.user_lid);

    if (!resolvedKey) {
        console.warn("resolved_key kosong - skip update STATS");
        return [];
    }

    // Process sheet rows
    const sheetRows = allItems
        .filter(item => {
            const data = item?.json || item;
            if (!data || Object.keys(data).length === 0) return false;
            return !!(data['lid'] || data['No WA'] || data.no_wa || data.NoWA);
        })
        .map(item => item?.json || item);

    debugLog.push("Step 2: Sheet rows found: " + sheetRows.length);

    // Find existing row: No WA primer, lid backup (konsisten dgn Resolve User Row)
    let existingRow = null;
    if (phone) existingRow = sheetRows.find(r => digits(r['No WA']) === phone) || null;
    if (!existingRow && lid) {
        existingRow = sheetRows.find(r => digits(r['lid']) === lid)
                   || sheetRows.find(r => digits(r['No WA']) === lid)
                   || null;
    }

    const isNewUser = !existingRow;
    debugLog.push("Step 3: " + (isNewUser ? "NEW USER" : "EXISTING USER"));

    let counter, pesanPertama, tanggalPertama, intensitasChat;

    if (existingRow) {
        counter = parseInt(existingRow.Counter || existingRow.counter || 0) + 1;
        intensitasChat = parseInt(existingRow['Intensitas Chat'] || existingRow.intensitas_chat || 0) + 1;

        const pesanLama = existingRow['Pesan Pertama'] || existingRow.pesan_pertama;
        pesanPertama = (pesanLama && String(pesanLama).trim() !== '') ? pesanLama : userMessage;

        // V4 FIX: baca kolom yang benar
        const tglLama = existingRow['Tanggal Chat Pertama'];
        tanggalPertama = (tglLama && String(tglLama).trim() !== '') ? tglLama : null;
    } else {
        counter = 1;
        intensitasChat = 1;
        pesanPertama = userMessage;
        tanggalPertama = null;
    }

    if (!tanggalPertama) {
        tanggalPertama = new Date().toLocaleDateString('en-GB', {
            timeZone: 'Asia/Jakarta', day: '2-digit', month: '2-digit', year: 'numeric'
        });
    }

    const outputData = {
        "No WA": resolvedKey,
        "lid": lid,
        "Tanggal": tanggalPertama,
        "TanggalSekarang": new Date().toLocaleDateString('en-GB', {
            timeZone: 'Asia/Jakarta', day: '2-digit', month: '2-digit', year: 'numeric'
        }),
        "Nama": userName,
        "Pesan Pertama": pesanPertama,
        "Counter": counter,
        "Intensitas Chat": intensitasChat
    };

    return [{ json: outputData }];

} catch (error) {
    // V4 FIX: jangan menulis row "ERROR" ke sheet - cukup log & stop.
    console.error("Process Counter ERROR: " + error.message, debugLog);
    return [];
}

