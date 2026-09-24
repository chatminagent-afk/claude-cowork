# ✅ QA CHECKLIST - TIM INTERIOR V2

**Project**: TIM Interior Proper History Fix  
**Version**: 2.0  
**Date**: _______________  
**Tester**: _______________

---

## 📋 INSTRUCTION

Checklist ini digunakan untuk memvalidasi bahwa semua fitur berfungsi dengan benar setelah implementasi V2.

**Cara Menggunakan**:
1. Ikuti setiap section berurutan
2. Centang [x] jika test PASSED
3. Tulis notes jika ada issue
4. Ulangi test yang FAILED sampai PASSED
5. Semua harus PASSED sebelum go-live

---

## 🔧 PRE-IMPLEMENTATION CHECKLIST

### Backup & Preparation

- [ ] **Backup Google Sheets** existing sudah dibuat
  - Nama backup: _______________________________
  - Date: _______________

- [ ] **Backup n8n workflow** existing sudah di-export
  - Filename: _______________________________
  - Date: _______________

- [ ] **Backup index.html** existing sudah disimpan
  - Location: _______________________________

- [ ] **Read IMPLEMENTATION_GUIDE.md** dari awal sampai akhir
  - Understood: Yes / No
  - Questions: _______________________________

---

## 📊 TAHAP 1: GOOGLE SHEETS VALIDATION

### Excel Structure

- [ ] **File TIM_Interior_v2.xlsx** sudah di-upload ke Google Drive
  - Google Sheets URL: _______________________________

- [ ] **Sheet "Database"** ada dan terisi data
  - Total rows (existing data): _______________

- [ ] **Sheet "Update_History"** ada dengan headers benar:
  - [ ] ID_Tiket
  - [ ] Update_Sequence
  - [ ] Tanggal_Update
  - [ ] Status_Pekerjaan
  - [ ] Update_Notes
  - [ ] Updated_By
  - [ ] Up_1, Up_2, Up_3, Up_4, Up_5

- [ ] **Sheet "PIC_Mandor"** tetap ada (unchanged)

- [ ] **Sheet "PIC_Pengawas"** tetap ada (unchanged)

- [ ] **Sheet "Project"** tetap ada (unchanged)

### Notes:
```
_________________________________________________________________
_________________________________________________________________
```

---

## 🔄 TAHAP 2: N8N WORKFLOW VALIDATION

### Workflow Import

- [ ] **Workflow V2** sudah di-import ke n8n
  - Workflow name: TIM_submit_and_update_complaint

- [ ] **Workflow activated** (switch ON)

### Node Configuration Check

- [ ] **Node "Get Update History Count"**
  - Document ID correct: Yes / No
  - Sheet Name = "Update_History": Yes / No

- [ ] **Node "Append ke Update_History"**
  - Document ID correct: Yes / No
  - Sheet Name = "Update_History": Yes / No
  - Columns mapping correct: Yes / No

- [ ] **Node "Get Update History"** (in get-ticket-detail)
  - Document ID correct: Yes / No
  - Sheet Name = "Update_History": Yes / No
  - Filter by ID_Tiket configured: Yes / No

- [ ] **Node "Update Database Status"**
  - Document ID correct: Yes / No
  - Sheet Name = "Database": Yes / No
  - Matching column = "ID": Yes / No

### Webhook URLs

- [ ] **POST /salero-complaint** activated
  - Test URL: _______________________________

- [ ] **POST /update-ticket** activated
  - Test URL: _______________________________

- [ ] **GET /get-ticket-detail** activated (NEW!)
  - Test URL: _______________________________

- [ ] **POST /search-ticket** activated
  - Test URL: _______________________________

### Notes:
```
_________________________________________________________________
_________________________________________________________________
```

---

## 🌐 TAHAP 3: WEB APP VALIDATION

### Code Implementation Check

- [ ] **Webhook URL** GET_TICKET_DETAIL_URL added
  - Line ~1550: const GET_TICKET_DETAIL_URL = '...';

- [ ] **Modal CSS** added to stylesheet
  - Modal overlay styles present
  - Modal detail styles present
  - Timeline styles present
  - Attachment grid styles present

- [ ] **Modal HTML** added to body
  - Modal overlay element present
  - Modal detail element present
  - Modal header present
  - Modal content present
  - Modal footer present

- [ ] **JavaScript functions** added:
  - [ ] openTicketDetail()
  - [ ] renderDetailView()
  - [ ] closeDetailModal()
  - [ ] openUpdateFromDetail()

- [ ] **Function openUpdateForm()** modified
  - Now calls openTicketDetail() instead of direct form

### Visual Check

- [ ] **Load web app** in browser
  - URL: _______________________________
  - Browser: Chrome / Firefox / Safari / Other: _______________

- [ ] **No console errors** on page load
  - Check browser DevTools Console

- [ ] **Theme toggle** berfungsi (light/dark)
  - Light mode: OK / Issue
  - Dark mode: OK / Issue

- [ ] **Responsive** di mobile
  - Test on device or DevTools mobile view
  - Status: OK / Issue

### Notes:
```
_________________________________________________________________
_________________________________________________________________
```

---

## 🧪 TAHAP 4: FUNCTIONAL TESTING

### TEST 1: Submit Complaint Baru

- [ ] **Step 1**: Fill form submit complaint baru
  - Project: _______________
  - PIC: _______________
  - Description: "Test complaint untuk V2"
  - Priority: Tinggi
  - Upload 1 foto: Yes

- [ ] **Step 2**: Submit form
  - Success message shown: Yes / No
  - Ticket ID received: _______________________________

- [ ] **Step 3**: Check Google Sheets "Database"
  - New row added: Yes / No
  - All fields populated: Yes / No
  - ID matches ticket ID: Yes / No

- [ ] **Step 4**: Check Google Drive
  - Photo uploaded: Yes / No
  - URL in Database sheet: Yes / No

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 2: Search & Detail View

- [ ] **Step 1**: Go to "Update Status" tab

- [ ] **Step 2**: Search for ticket created in TEST 1
  - Search by ID: _______________________________
  - Ticket found: Yes / No

- [ ] **Step 3**: Click ticket card
  - Detail modal opened: Yes / No
  - Modal shows ticket ID: Yes / No

- [ ] **Step 4**: Check detail content displays:
  - [ ] Tanggal Komplain
  - [ ] Status badge
  - [ ] Project name
  - [ ] PIC Mandor
  - [ ] PIC Pengawas
  - [ ] Lokasi
  - [ ] Tipe Laporan
  - [ ] Prioritas badge (with color)
  - [ ] Kategori
  - [ ] Pengaju
  - [ ] Description (full text)
  - [ ] Lampiran Komplain (photo uploaded in TEST 1)

- [ ] **Step 5**: Check "Riwayat Update" section
  - Shows "Belum ada update" message: Yes / No
  - (This is correct for new ticket)

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 3: First Update (Sequence 1)

- [ ] **Step 1**: From detail modal, click "Tambah Update"
  - Form opened: Yes / No
  - Ticket ID shown: _______________________________

- [ ] **Step 2**: Fill update form
  - Status: Proses
  - Notes: "Update pertama - material dipesan"
  - Upload 1 foto: Yes

- [ ] **Step 3**: Submit update
  - Success message shown: Yes / No

- [ ] **Step 4**: Check Google Sheets "Update_History"
  - New row added: Yes / No
  - ID_Tiket: _______________________________
  - Update_Sequence: 1 (must be 1!)
  - Tanggal_Update: filled
  - Status_Pekerjaan: Proses
  - Update_Notes: "Update pertama..."
  - Updated_By: filled (or "System")
  - Up_1: photo URL filled
  - Up_2 to Up_5: "-"

- [ ] **Step 5**: Check Google Sheets "Database"
  - Status_Pekerjaan updated to "Proses": Yes / No
  - (Update_Notes NOT used anymore - this is correct)

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 4: Second Update (Sequence 2)

- [ ] **Step 1**: Search same ticket again
- [ ] **Step 2**: Open detail modal
- [ ] **Step 3**: Check "Riwayat Update" now shows:
  - Timeline visible: Yes / No
  - "Update #1" shown: Yes / No
  - Date/time correct: Yes / No
  - Status badge "Proses": Yes / No
  - Notes "Update pertama...": Yes / No
  - Photo attachment shown: Yes / No

- [ ] **Step 4**: Click "Tambah Update" again
- [ ] **Step 5**: Fill second update
  - Status: Proses
  - Notes: "Update kedua - tunggu vendor"
  - No photo this time

- [ ] **Step 6**: Submit update
- [ ] **Step 7**: Check Google Sheets "Update_History"
  - NEW row added: Yes / No
  - ID_Tiket: same as before
  - Update_Sequence: 2 (must be 2!)
  - Status_Pekerjaan: Proses
  - Update_Notes: "Update kedua..."
  - Up_1 to Up_5: all "-" (no photo)

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 5: Third Update (Change Status to Selesai)

- [ ] **Step 1**: Open detail modal again
- [ ] **Step 2**: Check timeline shows both updates:
  - Update #1 visible: Yes / No
  - Update #2 visible: Yes / No
  - Chronological order (1 then 2): Yes / No

- [ ] **Step 3**: Add third update
  - Status: Selesai
  - Notes: "Pekerjaan selesai 100%"
  - Upload 2 photos: Yes

- [ ] **Step 4**: Submit update
- [ ] **Step 5**: Check "Update_History"
  - NEW row added: Yes / No
  - Update_Sequence: 3 (must be 3!)
  - Status_Pekerjaan: Selesai
  - Up_1: photo 1 URL
  - Up_2: photo 2 URL
  - Up_3 to Up_5: "-"

- [ ] **Step 6**: Check "Database"
  - Status_Pekerjaan updated to "Selesai": Yes / No

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 6: Full Timeline Display

- [ ] **Step 1**: Open detail modal for same ticket
- [ ] **Step 2**: Scroll to "Riwayat Update" section
- [ ] **Step 3**: Verify timeline shows ALL 3 updates:
  - [ ] Update #1 - "material dipesan" - Proses - 1 photo
  - [ ] Update #2 - "tunggu vendor" - Proses - no photo
  - [ ] Update #3 - "selesai 100%" - Selesai - 2 photos

- [ ] **Step 4**: Check visual styling:
  - Timeline dots visible: Yes / No
  - Status badges colored correctly:
    - Proses = gold/yellow
    - Selesai = green
  - Dates formatted correctly: Yes / No
  - Photos clickable: Yes / No (open in new tab)

- [ ] **Step 5**: Check "Lampiran Komplain Awal" section
  - Shows initial photo from TEST 1: Yes / No
  - Separate from update photos: Yes / No

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 7: Different Ticket (New Complaint)

- [ ] **Step 1**: Submit another new complaint
  - ID received: _______________________________

- [ ] **Step 2**: Add update to this NEW ticket
  - Notes: "First update for ticket 2"

- [ ] **Step 3**: Check "Update_History"
  - New ticket has Update_Sequence = 1: Yes / No
  - (NOT 4 - sequence is per-ticket!)

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 8: Mobile Responsiveness

- [ ] **Step 1**: Open app on mobile device or DevTools mobile view
  - Device: _______________
  - Screen size: _______________

- [ ] **Step 2**: Test main functions:
  - Submit form: usable on mobile
  - Search: usable on mobile
  - Ticket cards: readable on mobile
  - Detail modal: displays correctly
  - Timeline: readable on mobile
  - Buttons: tappable/not overlapping

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 9: Dark Mode

- [ ] **Toggle to dark mode**
  - All text readable: Yes / No
  - Modal displays correctly: Yes / No
  - Timeline visible: Yes / No
  - Buttons styled correctly: Yes / No
  - No white/black contrast issues: Yes / No

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

### TEST 10: Error Handling

- [ ] **Test 1**: Try to get detail for non-existent ticket ID
  - Error message shown: Yes / No
  - App doesn't crash: Yes / No

- [ ] **Test 2**: Try to update without filling notes
  - Validation message shown: Yes / No

- [ ] **Test 3**: Try to update without selecting status
  - Validation message shown: Yes / No

**RESULT**: PASSED / FAILED

### Notes:
```
_________________________________________________________________
```

---

## 🎯 FINAL VALIDATION

### All Tests Summary

- [ ] TEST 1: Submit Complaint Baru - PASSED
- [ ] TEST 2: Search & Detail View - PASSED
- [ ] TEST 3: First Update (Seq 1) - PASSED
- [ ] TEST 4: Second Update (Seq 2) - PASSED
- [ ] TEST 5: Third Update (Selesai) - PASSED
- [ ] TEST 6: Full Timeline Display - PASSED
- [ ] TEST 7: Different Ticket - PASSED
- [ ] TEST 8: Mobile Responsive - PASSED
- [ ] TEST 9: Dark Mode - PASSED
- [ ] TEST 10: Error Handling - PASSED

### Go-Live Decision

**Total Tests**: 10  
**Passed**: _____ / 10  
**Failed**: _____ / 10

**Status**:
- [ ] All tests PASSED → **READY TO GO-LIVE** ✅
- [ ] Some tests FAILED → **NEED FIX** ⚠️

### Sign-Off

**Tester**: _______________________________  
**Date**: _______________  
**Time**: _______________  

**Final Notes**:
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

**CHECKLIST COMPLETE!**

If all tests PASSED → Congratulations! System ready untuk production.  
If some FAILED → Review IMPLEMENTATION_GUIDE.md troubleshooting section.

