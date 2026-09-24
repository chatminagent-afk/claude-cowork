// ====================================================================
// FINAL FIX: Handle empty strings dengan || operator
// ====================================================================

const debugLog = [];

try {
    const allItems = $input.all();
    debugLog.push("Step 1: Received " + allItems.length + " items from Read STATS");

    // ====================================================================
    // Ambil data dari Chat Counter
    // ====================================================================
    const chatCounterNode = $('Chat Counter').first();
    if (!chatCounterNode) {
        throw new Error("Chat Counter node not found!");
    }
    
    const chatCounter = chatCounterNode.json;
    if (!chatCounter) {
        throw new Error("Chat Counter json is empty!");
    }

    const searchNoWA = chatCounter.user_phone;   // nomor HP utk kolom No WA
    const searchLid  = chatCounter.user_lid;      // LID utk pencocokan
    const userName = chatCounter.user_name || "User";
    const userMessage = chatCounter.original_message || "";

    debugLog.push("Step 2: Chat Counter data OK");
    debugLog.push("  - No WA: " + searchNoWA);
    debugLog.push("  - Nama: " + userName);
    debugLog.push("  - Pesan: " + userMessage);

    if (!searchLid) {
        throw new Error("user_lid is missing!");
    }

    // ====================================================================
    // Process sheet rows
    // ====================================================================
    const sheetRows = allItems
        .filter(item => {
            const data = item?.json || item;
            if (!data || Object.keys(data).length === 0) {
                return false;
            }
            return !!(data['lid'] || data['No WA'] || data.no_wa || data.NoWA);
        })
        .map(item => item?.json || item);

    debugLog.push("Step 3: Sheet rows found: " + sheetRows.length);

    // ====================================================================
    // Find existing row
    // ====================================================================
    const searchLidStr = String(searchLid);
    const existingRow = sheetRows.find(row => {
        const rowLid = row['lid'] ?? row.LID;
        return rowLid && rowLid.toString() === searchLidStr;
    });

    const isNewUser = !existingRow;
    debugLog.push("Step 4: User status = " + (isNewUser ? "NEW USER" : "EXISTING USER"));

    // ====================================================================
    // Calculate values - FIXED: Pakai || untuk handle empty strings
    // ====================================================================
    let counter, pesanPertama, tanggalPertama, intensitasChat;

    if (existingRow) {
        // User sudah ada
        debugLog.push("Step 5a: Existing user - raw values:");
        debugLog.push("  - existingRow.Counter = '" + existingRow.Counter + "' (type: " + typeof existingRow.Counter + ")");
        debugLog.push("  - existingRow['Pesan Pertama'] = '" + existingRow['Pesan Pertama'] + "' (type: " + typeof existingRow['Pesan Pertama'] + ")");
        
        // FIX: Pakai || untuk handle empty string, bukan ??
        counter = parseInt(existingRow.Counter || existingRow.counter || 0) + 1;
        intensitasChat = parseInt(existingRow['Intensitas Chat'] || existingRow.intensitas_chat || 0) + 1;
        
        // FIX: Pakai || dan trim check untuk handle empty string
        const pesanLama = existingRow['Pesan Pertama'] || existingRow.pesan_pertama;
        pesanPertama = (pesanLama && pesanLama.trim() !== '') ? pesanLama : userMessage;
        
        tanggalPertama = existingRow.Tanggal || existingRow.tanggal || null;
        
        debugLog.push("Step 5b: Existing user processed");
        debugLog.push("  - Counter: " + counter);
        debugLog.push("  - Intensitas: " + intensitasChat);
        debugLog.push("  - Pesan Pertama: '" + pesanPertama + "'");
    } else {
        // User baru
        counter = 1;
        intensitasChat = 1;
        pesanPertama = userMessage;
        tanggalPertama = null;
        
        debugLog.push("Step 5: New user processed");
        debugLog.push("  - Counter: " + counter);
        debugLog.push("  - Intensitas: " + intensitasChat);
        debugLog.push("  - Pesan Pertama: '" + pesanPertama + "'");
    }

    // Verify
    debugLog.push("Step 6: Pre-return verification:");
    debugLog.push("  - counter value: " + counter + " (type: " + typeof counter + ")");
    debugLog.push("  - pesanPertama value: '" + pesanPertama + "' (length: " + pesanPertama.length + ")");

    // ====================================================================
    // Set tanggal
    // ====================================================================
    if (!tanggalPertama) {
        const now = new Date();
        tanggalPertama = now.toLocaleDateString('en-GB', {
            timeZone: 'Asia/Jakarta',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }

    const jamWIB = new Date().toLocaleTimeString('id-ID', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
        timeZone: 'Asia/Jakarta'
    }).replace('.', ':');

    // ====================================================================
    // Build output
    // ====================================================================
    const outputData = {
        "No WA": searchNoWA,
        "lid": searchLid,
        "Tanggal": tanggalPertama,
        "TanggalSekarang": new Date().toLocaleDateString('en-GB', {  // ← TAMBAH INI
            timeZone: 'Asia/Jakarta',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }),
        "Jam": jamWIB,
        "Nama": userName,
        "Pesan Pertama": pesanPertama,
        "Counter": counter,
        "Intensitas Chat": intensitasChat,
        "Last Timestamp": chatCounter.webhook_timestamp || Math.floor(Date.now()/1000),
        
        // DEBUG INFO - bisa hapus nanti kalau udah oke
        "_DEBUG": {
            "logs": debugLog,
            "isNewUser": isNewUser,
            "sheetRowsCount": sheetRows.length
        }
    };

    return [{
        json: outputData
    }];

} catch (error) {
    debugLog.push("ERROR: " + error.message);
    
    return [{
        json: {
            "No WA": "ERROR",
            "Counter": null,
            "Pesan Pertama": "",
            "Intensitas Chat": null,
            "_DEBUG": {
                "error": error.message,
                "logs": debugLog
            }
        }
    }];
}
