# 🚀 VIRA IMPROVEMENT ROADMAP & SHEET GUIDELINES
## Continuous Improvement + Operational Rules untuk Sam

**Date:** May 6, 2026  
**Version:** 1.0  

---

# PART 1: IMPROVEMENT ROADMAP
## Cara Tingkatkan Kualitas Respons Chat (Beyond FAQ)

Selain menambah FAQ, berikut improvement strategies yang bisa dilakukan secara bertahap:

---

## 🎯 PHASE 1: CONTENT OPTIMIZATION (BULAN 1-2)
### Quick Wins dengan Minimal Effort

### 1.1 **Conversation Examples Library** ⭐⭐⭐⭐⭐
**Apa:** Bikin database percakapan contoh untuk situasi umum

**Cara Implement:**
- Buat sheet baru: `CONVERSATION_EXAMPLES`
- Kolom: `Situation | User_Input | Ideal_Bot_Response | Notes`
- Isi 10-20 conversation examples untuk situasi seperti:
  - User ask harga → Best response style
  - User komplain mahal → Handling objection
  - User compare dengan kompetitor → Response strategy
  - User ragu-ragu → Confidence building

**System Prompt Update:**
```
Berikut adalah contoh-contoh percakapan ideal:
[Query conversation examples from sheet]

Gunakan style dan pendekatan yang sama dengan contoh di atas.
```

**Impact:**
- ✅ Bot learns Sam's preferred response style
- ✅ Consistent brand voice
- ✅ Better objection handling
- ✅ More conversational (less robotic)

**Effort:** Low (1-2 jam bikin examples)  
**Impact:** High (immediate improvement in tone)

---

### 1.2 **Persona Refinement dengan Real Feedback** ⭐⭐⭐⭐⭐
**Apa:** Update persona Sam di system prompt berdasarkan real conversation data

**Cara Implement:**
1. Setiap minggu, Sam review 10 conversations di STATS
2. Catat response yang "kurang Sam banget"
3. Update persona description di system prompt dengan specific examples:

**Before (generic):**
```
Kamu adalah Sam, mentor beasiswa yang ramah dan profesional.
```

**After (specific):**
```
Kamu adalah Sam, mentor beasiswa dengan style:
- Pakai emoji moderat (1-2 per response, terutama 😊 dan 👍)
- Friendly tapi nggak lebay
- Sering pakai phrase: "Yuk kita breakdown", "Gampang kok", "Jangan khawatir"
- Kalau user bilang "mahal" → always emphasize ROI dan success stories
- Never use: "Mohon maaf", "Terima kasih banyak" (too formal)
- Prefer: "Sorry ya", "Thanks!" (casual-professional)
```

**Impact:**
- ✅ Bot sounds MORE like real Sam
- ✅ User trust increases
- ✅ Natural conversation flow

**Effort:** Low (15 menit review per minggu)  
**Impact:** Very High (brand consistency)

---

### 1.3 **Context-Aware Responses** ⭐⭐⭐⭐
**Apa:** Tambahkan context dari chat history ke response logic

**Cara Implement:**
- Sistem memory sudah ada (6 messages window)
- Update system prompt untuk explicitly USE memory:

```
CONTEXT AWARENESS RULES:
1. Kalau user sudah tanya harga sebelumnya (dalam 6 messages terakhir):
   → Jangan repeat harga, langsung to the point
   → Example: "Seperti yang tadi aku share, untuk program Junior..."
   
2. Kalau user sudah mention nama sebelumnya:
   → Pakai nama mereka dalam response
   → Example: "Oke [Nama], jadi untuk situasi kamu..."
   
3. Kalau user return setelah >1 hari:
   → Welcome back message
   → Example: "Halo lagi! Ada yang mau ditanyain lebih lanjut?"
```

**Impact:**
- ✅ More personalized responses
- ✅ Less repetitive answers
- ✅ Better user experience

**Effort:** Low (update prompt)  
**Impact:** Medium-High

---

## 🎯 PHASE 2: DATA-DRIVEN OPTIMIZATION (BULAN 2-3)
### Pakai Analytics untuk Improve

### 2.1 **Unknown FAQ Mining** ⭐⭐⭐⭐⭐
**Apa:** Analisis sheet UNKNOWN untuk identify knowledge gaps

**Cara Implement:**
1. Setiap minggu, review sheet UNKNOWN
2. Identify patterns (ada 3+ user nanya hal yang sama?)
3. Tambahkan ke FAQ atau create dedicated sheet
4. Track: question → FAQ update → frequency drop

**Metrics to Track:**
| Week | Unknown Questions | Common Patterns | FAQ Added | Repeat Rate |
|------|-------------------|-----------------|-----------|-------------|
| W1 | 15 | Scholarship deadlines | 2 | N/A |
| W2 | 12 | Scholarship deadlines | 0 | -80% ✅ |

**Impact:**
- ✅ Proactive knowledge base growth
- ✅ Reduce UNKNOWN queries over time
- ✅ Data-driven FAQ expansion

**Effort:** Medium (30 menit per minggu)  
**Impact:** Very High (continuous improvement)

---

### 2.2 **Response Time Optimization** ⭐⭐⭐⭐
**Apa:** Track berapa lama user tunggu sebelum dapat response yang memuaskan

**Cara Implement:**
1. Add kolom di STATS: `resolved_in_messages`
2. Manual tracking: Berapa messages user perlu kirim sebelum "puas"?
3. Target: <3 messages untuk 80% queries

**Analysis:**
```
User: "Mau tanya harga" 
Bot: "Harga program mana nih?" ← Message 1
User: "Junior"
Bot: "Program Junior..." ← Message 2 (RESOLVED) ✅

VS

User: "Mau daftar"
Bot: "Mau daftar program apa?" ← Message 1
User: "Yang buat SMP"
Bot: "Ada Junior dan Intermediate..." ← Message 2
User: "Yang murah"
Bot: "Keduanya sama harganya..." ← Message 3 (RESOLVED) ❌ Too long
```

**Improvement Action:**
- Update FAQ untuk anticipate follow-up questions
- Make initial response more comprehensive

**Impact:**
- ✅ Faster resolution
- ✅ Less back-and-forth
- ✅ Better user satisfaction

**Effort:** Medium (tracking + analysis)  
**Impact:** High

---

### 2.3 **Chat Intensity-Based Personalization** ⭐⭐⭐⭐⭐
**Apa:** Pakai Chat Intensity metric untuk personalize response style

**Cara Implement:**
Update system prompt dengan intensity-aware logic:

```javascript
// Di Process Counter & Merge Data node, ada Chat Intensity calculation
// Gunakan ini di system prompt:

PERSONALIZATION RULES:
- Chat Intensity >100: HOT LEAD
  → Be more direct, action-oriented
  → "Yuk langsung aja kita discuss detail programnya!"
  → Push for GForm / booking faster
  
- Chat Intensity 50-100: INTERESTED
  → Balance info + engagement
  → "Oke, aku jelasin detail ya..."
  
- Chat Intensity <50: CASUAL BROWSER
  → More informational, less pushy
  → "Boleh kok tanya-tanya dulu, no pressure!"
```

**Impact:**
- ✅ Match user's energy level
- ✅ Higher conversion for hot leads
- ✅ Don't scare casual browsers

**Effort:** Low (add to prompt)  
**Impact:** Very High (conversion optimization)

---

## 🎯 PHASE 3: ADVANCED AI FEATURES (BULAN 3-6)
### Technical Improvements

### 3.1 **Multi-Turn Conversation Planning** ⭐⭐⭐⭐
**Apa:** AI plans conversation flow untuk achieve specific goals

**Cara Implement:**
Add conversation state tracking:

```
CONVERSATION GOALS:
1. Get to know user's situation (class, target country)
2. Understand their concerns/objections
3. Match them to right program
4. Get GForm submission

CONVERSATION STATE TRACKING:
- known_about_user: [class, target, budget, concerns]
- goal_progress: [discovery, matching, closing]
- next_recommended_action: [ask_class, explain_ROI, send_gform]

Before responding, check:
"What do I still need to know? What's the next logical step?"
```

**Impact:**
- ✅ More structured conversations
- ✅ Higher conversion (guided flow)
- ✅ Less random tangents

**Effort:** Medium-High (prompt engineering)  
**Impact:** Very High

---

### 3.2 **Sentiment Analysis & Objection Detection** ⭐⭐⭐⭐⭐
**Apa:** Detect user sentiment dan objections untuk appropriate response

**Cara Implement:**
Update system prompt:

```
SENTIMENT DETECTION:
Before responding, analyze user's message:
- EXCITED: "Wah keren!", "Pengen banget!"
  → Match their energy, move to action fast
  
- DOUBTFUL: "Mahal ya", "Ga yakin...", "Bisa ga ya"
  → Address concerns first, provide social proof
  
- FRUSTRATED: "Udah coba tapi gagal", "Susah banget"
  → Empathy first, then solution
  
- CONFUSED: "Maksudnya?", "Ga ngerti"
  → Simplify, use examples

OBJECTION HANDLING:
Common objections + responses:
- "Terlalu mahal" → ROI focus, payment options, success stories
- "Ga ada waktu" → Flexible schedule, online format
- "Ga yakin lolos" → Success rate stats, mock interview option
```

**Impact:**
- ✅ More empathetic responses
- ✅ Better objection handling
- ✅ Higher user satisfaction

**Effort:** Medium (prompt update)  
**Impact:** Very High

---

### 3.3 **Dynamic System Prompt Based on User Type** ⭐⭐⭐⭐
**Apa:** Different prompt for different user segments

**Cara Implement:**
1. Identify user type from first message
2. Load appropriate prompt variation

**User Types:**
```
FIRST_TIMER (belum pernah chat):
→ More welcoming, more explanatory
→ "Halo! Aku Sam, mentor di The Scholars..."

RETURNING_USER (ada di STATS):
→ Pick up where left off
→ "Hi again! Masih mau lanjutin diskusi tentang program Junior?"

HOT_LEAD (high intensity):
→ More action-focused
→ "Yuk kita bahas detail dan langkah selanjutnya!"

MOCK_INTERVIEW_BOOKER:
→ Interview prep focused
→ "Great! Let's prepare kamu untuk mock interview..."
```

**Impact:**
- ✅ Relevant responses for each user type
- ✅ Better personalization
- ✅ Higher engagement

**Effort:** High (dynamic prompt logic)  
**Impact:** Very High

---

## 🎯 PHASE 4: EXTERNAL INTEGRATIONS (BULAN 6+)
### Connect More Data Sources

### 4.1 **Success Stories Database** ⭐⭐⭐⭐⭐
**Apa:** AI bisa share relevant success stories based on user situation

**Cara Implement:**
1. Create sheet: `SUCCESS_STORIES`
2. Columns: `Student_Name | Program | Target_School | Got_Scholarship | Story | Similar_To_User_Profile`

```
Example:
Name: "Budi"
Program: "Junior"
Target: "ACS(I) Singapore"
Scholarship: "ASEAN Scholarship"
Story: "Budi awalnya ragu karena nilai math-nya B. Tapi setelah ikut program Junior, dia belajar strategi khusus dan akhirnya lolos!"
Similar_To: "students with average math grades"
```

**AI Usage:**
```
User: "Nilai gw biasa aja nih, takut ga lolos"
Bot: [Query SUCCESS_STORIES where Similar_To contains "average grades"]
Bot: "Tenang! Ada Budi yang awalnya juga nilai math-nya B. Setelah ikut program Junior, dia lolos ASEAN Scholarship ke ACS(I). Kuncinya ada di strategi belajar yang tepat!"
```

**Impact:**
- ✅ Social proof yang relevan
- ✅ Overcome objections with real examples
- ✅ Build trust

**Effort:** Medium (create database)  
**Impact:** Very High (conversion boost)

---

### 4.2 **Live Calendar Integration** ⭐⭐⭐⭐
**Apa:** Bot tahu real-time availability Sam untuk mock interview

**Cara Implement:**
1. Integrate dengan Google Calendar API
2. Bot bisa check: "Slot tersedia kapan?"
3. Langsung offer specific dates

**Before:**
```
User: "Mau book mock interview"
Bot: "Oke! Nanti Sam akan confirm jadwal ya"
```

**After:**
```
User: "Mau book mock interview"
Bot: [Check calendar real-time]
Bot: "Ada slot available:
- Senin, 10 Mei jam 15:00
- Rabu, 12 Mei jam 10:00
Mana yang cocok?"
```

**Impact:**
- ✅ Instant booking confirmation
- ✅ Less back-and-forth
- ✅ Professional experience

**Effort:** High (API integration)  
**Impact:** High

---

### 4.3 **WhatsApp Rich Media** ⭐⭐⭐⭐
**Apa:** Kirim images, PDFs, buttons via WhatsApp

**Cara Implement:**
- Kirimi API supports rich media
- Bot bisa send:
  - Program brochure (PDF)
  - Sample questions (image)
  - Success stories (carousel)
  - Interactive buttons ("Lihat Harga", "Book Now")

**Example:**
```
User: "Mau liat materi yang diajarkan"
Bot: "Ini sample materi program Junior ya!" 
     [Kirim PDF: Junior_Curriculum.pdf]
     [Button: "Mau Daftar?" → Direct to GForm]
```

**Impact:**
- ✅ Richer user experience
- ✅ Visual content more engaging
- ✅ Easier navigation

**Effort:** Medium (implement rich media API)  
**Impact:** High

---

## 🎯 PHASE 5: INTELLIGENCE & LEARNING (BULAN 6+)
### Self-Improving System

### 5.1 **Conversation Quality Scoring** ⭐⭐⭐⭐⭐
**Apa:** Track quality metrics untuk each conversation

**Cara Implement:**
Add to STATS:
- `conversation_quality_score` (1-10)
- `user_satisfaction` (thumbs up/down)
- `resolved` (yes/no)
- `escalated_to_human` (yes/no)

**Metrics:**
```
Quality Score Calculation:
- Resolved in <3 messages: +3 points
- No escalation to human: +2 points
- High chat intensity: +2 points
- User sent "thanks" or positive sentiment: +3 points
- Total: /10
```

**Analysis:**
- Conversations with score <6 → Review & learn
- Conversations with score >8 → Extract best practices

**Impact:**
- ✅ Quantify improvement over time
- ✅ Identify what works vs. doesn't
- ✅ Data-driven optimization

**Effort:** Medium (implement scoring)  
**Impact:** Very High (continuous learning)

---

### 5.2 **A/B Testing System Prompts** ⭐⭐⭐⭐
**Apa:** Test different prompt variations untuk find best performance

**Cara Implement:**
1. Create 2 versions of system prompt (A vs B)
2. 50% users get version A, 50% get version B
3. Track: conversion rate, satisfaction, resolution time
4. Winner becomes default

**Example Test:**
```
Version A (Friendly):
"Halo! Aku Sam, mentor beasiswa yang siap bantu kamu..."

Version B (Professional):
"Selamat datang di The Scholars. Saya Sam, mentor dengan pengalaman..."

Test for 2 weeks → Check:
- Which gets higher GForm submission?
- Which gets better user feedback?
- Which resolves faster?
```

**Impact:**
- ✅ Scientific improvement
- ✅ Remove guesswork
- ✅ Continuous optimization

**Effort:** Medium-High  
**Impact:** Very High

---

### 5.3 **Predictive User Intent** ⭐⭐⭐⭐⭐
**Apa:** AI predicts what user wants before they finish asking

**Cara Implement:**
Analyze patterns:

```
Pattern Detection:
- User mentions "SMP 3" → 80% likely asking about Intermediate program
- User asks "harga" first → 60% likely have budget concerns
- User asks multiple detail questions → 90% likely serious (hot lead)

PROACTIVE RESPONSES:
User: "Anak gw SMP 3"
AI: [Detects: likely interested in Intermediate]
AI: "Oh untuk SMP 3 pas banget program Intermediate! Mau aku jelasin detail programnya?"
```

**Impact:**
- ✅ Faster to the point
- ✅ Feels more intelligent
- ✅ Better user experience

**Effort:** High (pattern analysis + ML)  
**Impact:** Very High

---

# SUMMARY: IMPROVEMENT PRIORITY MATRIX

| Feature | Effort | Impact | Priority | Timeline |
|---------|--------|--------|----------|----------|
| **Conversation Examples** | Low | High | 🔥 P0 | Week 1-2 |
| **Persona Refinement** | Low | Very High | 🔥 P0 | Ongoing |
| **Unknown FAQ Mining** | Medium | Very High | 🔥 P0 | Week 1+ |
| **Chat Intensity Personalization** | Low | Very High | 🔥 P0 | Week 2 |
| **Context-Aware Responses** | Low | Medium | ⭐ P1 | Week 3 |
| **Sentiment Analysis** | Medium | Very High | ⭐ P1 | Month 2 |
| **Response Time Optimization** | Medium | High | ⭐ P1 | Month 2 |
| **Multi-Turn Planning** | High | Very High | ⭐⭐ P2 | Month 3 |
| **Success Stories DB** | Medium | Very High | ⭐⭐ P2 | Month 3 |
| **Dynamic Prompts** | High | Very High | ⭐⭐ P2 | Month 4 |
| **Conversation Quality Score** | Medium | Very High | ⭐⭐⭐ P3 | Month 4 |
| **Calendar Integration** | High | High | ⭐⭐⭐ P3 | Month 5 |
| **Rich Media** | Medium | High | ⭐⭐⭐ P3 | Month 5 |
| **A/B Testing** | High | Very High | ⭐⭐⭐⭐ P4 | Month 6 |
| **Predictive Intent** | Very High | Very High | ⭐⭐⭐⭐ P4 | Month 6+ |

**Recommended First 3 Months:**
1. ✅ Week 1-2: Conversation Examples + Persona Refinement
2. ✅ Week 3-4: Unknown FAQ Mining + Chat Intensity Personalization
3. ✅ Month 2: Sentiment Analysis + Response Time Optimization
4. ✅ Month 3: Multi-Turn Planning + Success Stories DB

---

---

# PART 2: GOOGLE SHEETS GUIDELINES
## Aturan Main: Sheet Mana yang Boleh Sam Edit

---

## 🟢 **SAFE TO EDIT** - Sam Boleh & Harus Edit Bebas

### 📋 **Sheet: FAQ**
**Purpose:** Knowledge base untuk pertanyaan umum

**Kolom Structure:**
| Column | Required | Sam Boleh Edit | Notes |
|--------|----------|----------------|-------|
| Question | ✅ Yes | ✅ YES | Pertanyaan dari user |
| Answer | ✅ Yes | ✅ YES | Jawaban yang ideal |
| Category | ⚪ Optional | ✅ YES | Ex: "Harga", "Program", "Scholarship" |
| Keywords | ⚪ Optional | ✅ YES | Kata kunci untuk better matching |

**Guidelines:**
- ✅ **BOLEH:** Add FAQ baru kapan saja
- ✅ **BOLEH:** Update answer kalau ada perubahan policy/info
- ✅ **BOLEH:** Delete FAQ yang sudah tidak relevan
- ⚠️ **HATI-HATI:** Jangan duplicate questions (check dulu)
- ⚠️ **BEST PRACTICE:** Gunakan bahasa yang sama dengan Sam chat

**Example Entry:**
```
Question: "Berapa harga program Junior?"
Answer: "Program Junior harganya Rp 2.250.000/bulan untuk 4 bulan. Jadi total investment Rp 9.000.000. Ini include semua materi, live session, dan akses ke komunitas alumni!"
Category: "Harga"
Keywords: "harga, biaya, junior, cost"
```

---

### 📋 **Sheet: HARGA**
**Purpose:** Pricing information untuk semua program

**Kolom Structure:**
| Column | Required | Sam Boleh Edit | Notes |
|--------|----------|----------------|-------|
| Program | ✅ Yes | ✅ YES | Nama program |
| Harga Per Bulan | ✅ Yes | ✅ YES | Monthly price |
| Total Harga | ✅ Yes | ✅ YES | Total 4 months |
| Cicilan Tersedia | ⚪ Optional | ✅ YES | Yes/No |
| Diskon Special | ⚪ Optional | ✅ YES | Promo info |

**Guidelines:**
- ✅ **BOLEH:** Update harga kapan saja (langsung live di bot!)
- ✅ **BOLEH:** Add program baru
- ✅ **BOLEH:** Update cicilan options
- ⚠️ **IMPORTANT:** Bot akan quote harga ini VERBATIM, jadi pastikan akurat!

---

### 📋 **Sheet: PROGRAM**
**Purpose:** Detail semua program yang available

**Kolom Structure:**
| Column | Required | Sam Boleh Edit | Notes |
|--------|----------|----------------|-------|
| Nama Program | ✅ Yes | ✅ YES | Ex: "Junior", "Intermediate", "Senior" |
| Deskripsi | ✅ Yes | ✅ YES | Short description |
| Target Peserta | ✅ Yes | ✅ YES | Ex: "SD 6 / SMP 1" |
| Durasi | ✅ Yes | ✅ YES | Ex: "4 bulan (16 sesi)" |
| Mata Pelajaran | ⚪ Optional | ✅ YES | Ex: "Math, English, GAT, Interview" |
| Status | ✅ Yes | ✅ YES | "Open" / "Closed" / "Coming Soon" |

**Guidelines:**
- ✅ **BOLEH:** Update program details
- ✅ **BOLEH:** Change status (Open → Closed)
- ✅ **BOLEH:** Add new programs
- ⚠️ **IMPORTANT:** Status "Closed" → bot will say "batch sudah penuh"

---

### 📋 **Sheet: BATCH**
**Purpose:** Jadwal batch yang akan datang

**Kolom Structure:**
| Column | Required | Sam Boleh Edit | Notes |
|--------|----------|----------------|-------|
| Nama Batch | ✅ Yes | ✅ YES | Ex: "Batch 5" |
| Program | ✅ Yes | ✅ YES | Link to PROGRAM sheet |
| Tanggal Mulai | ✅ Yes | ✅ YES | Start date |
| Tanggal Selesai | ✅ Yes | ✅ YES | End date |
| Deadline Daftar | ✅ Yes | ✅ YES | Registration deadline |
| Kuota | ✅ Yes | ✅ YES | Max students |
| Status | ✅ Yes | ✅ YES | "Open" / "Full" / "Coming Soon" |

**Guidelines:**
- ✅ **BOLEH:** Update batch info
- ✅ **BOLEH:** Add new batch
- ✅ **BOLEH:** Change status based on registrations
- ⚠️ **IMPORTANT:** Update status ASAP kalau batch penuh!

---

### 📋 **Sheet: SYARAT**
**Purpose:** Requirements untuk masuk setiap program

**Kolom Structure:**
| Column | Required | Sam Boleh Edit | Notes |
|--------|----------|----------------|-------|
| Program | ✅ Yes | ✅ YES | Link to PROGRAM |
| Syarat | ✅ Yes | ✅ YES | Requirements list |
| Rekomendasi | ⚪ Optional | ✅ YES | Nice to have |

**Guidelines:**
- ✅ **BOLEH:** Update requirements
- ✅ **BOLEH:** Add new programs
- ⚠️ **TIP:** Be specific! "SMP 2-3" clearer than "SMP"

---

### 📋 **Sheet: MOCK_INTERVIEW**
**Purpose:** Mock interview session info

**Kolom Structure:**
| Column | Required | Sam Boleh Edit | Notes |
|--------|----------|----------------|-------|
| Sesi | ✅ Yes | ✅ YES | Session name |
| Deskripsi | ✅ Yes | ✅ YES | What's included |
| Durasi | ✅ Yes | ✅ YES | Session length |
| Harga | ✅ Yes | ✅ YES | Price per session |
| Format | ✅ Yes | ✅ YES | "1-on-1 online" |

**Guidelines:**
- ✅ **BOLEH:** Update pricing
- ✅ **BOLEH:** Update format/description
- ✅ **BOLEH:** Add new session types

---

### 📋 **Sheet: LINKS**
**Purpose:** Important URLs (GForm, social media, etc.)

**Kolom Structure:**
| Column | Required | Sam Boleh Edit | Notes |
|--------|----------|----------------|-------|
| Link Name | ✅ Yes | ✅ YES | Ex: "GForm Pendaftaran" |
| URL | ✅ Yes | ✅ YES | The actual link |
| Description | ⚪ Optional | ✅ YES | What's this link for |

**Guidelines:**
- ✅ **BOLEH:** Update links
- ✅ **BOLEH:** Add new links
- ⚠️ **CRITICAL:** GForm link harus akurat! Bot kirim link ini ke user

**Important Links to Maintain:**
```
Link Name: "GForm Pendaftaran"
URL: [Your actual Google Form URL]
Description: "Form pendaftaran untuk semua program"
```

---

### 📋 **Sheet: ABOUT_SAM**
**Purpose:** Sam's background untuk bot share ke user

**Kolom Structure:**
| Column | Required | Sam Boleh Edit | Notes |
|--------|----------|----------------|-------|
| Topic | ✅ Yes | ✅ YES | Ex: "Education", "Experience" |
| Details | ✅ Yes | ✅ YES | The info |

**Guidelines:**
- ✅ **BOLEH:** Update bio anytime
- ✅ **BOLEH:** Add achievements
- ⚠️ **TIP:** Keep it relevant to target audience (students)

**Example:**
```
Topic: "Education"
Details: "Alumni SMU BPK Penabur, ACS(I) Singapore dengan School-Based Scholarship, ACJC, dan SMU Finance (Magna Cum Laude) dengan Mochtar Riady Scholarship."

Topic: "Experience"
Details: "Investment Analyst di Family Office Singapore. Sudah membimbing 100+ murid lolos ASEAN Scholarship."
```

---

## 🟡 **EDIT WITH CAUTION** - Boleh Edit, Tapi Hati-Hati

### 📋 **Sheet: STATS**
**Purpose:** Track semua user yang pernah chat

**Kolom Structure:**
| Column | Auto-Generated | Sam Boleh Edit | Notes |
|--------|----------------|----------------|-------|
| No WA | ✅ AUTO | ❌ JANGAN | Sistem auto-fill |
| Nama | ✅ AUTO | ⚠️ BOLEH | Nama dari user message |
| Tanggal | ✅ AUTO | ❌ JANGAN | First chat date |
| Jam | ✅ AUTO | ❌ JANGAN | First chat time |
| Pesan Pertama | ✅ AUTO | ❌ JANGAN | User's first message |
| Counter | ✅ AUTO | ❌ JANGAN | Message count |
| Intensitas Chat | ✅ AUTO | ❌ JANGAN | Calculated metric |
| Tanggal Chat Terakhir | ✅ AUTO | ❌ JANGAN | Last activity |
| **bot_mode** | ⚪ Manual | ✅ EDIT INI | "OFF" = manual mode |
| **gform_sent_ts** | ✅ AUTO | ⚠️ LIHAT | Timestamp GForm sent |
| **gform_filled** | ⚪ Manual | ✅ EDIT INI | "Y" kalau user isi form |
| follow_up_count | ✅ AUTO | ❌ JANGAN | Follow-up counter |

**Guidelines:**

#### ✅ **Sam BOLEH Edit:**
1. **bot_mode:**
   - Set ke "OFF" kalau Sam mau takeover conversation
   - Kosongkan atau set "ON" untuk kembalikan ke bot
   
2. **gform_filled:**
   - Set ke "Y" kalau user sudah isi form
   - Bot akan stop kirim reminder

#### ❌ **Sam JANGAN Edit:**
- Semua kolom lain (auto-generated by system)
- Counter, Intensitas, Timestamps
- No WA, Tanggal, Jam

#### ⚠️ **CRITICAL WARNING:**
- JANGAN delete rows! (akan break follow-up logic)
- JANGAN sort/filter lalu save! (akan mess up order)
- Kalau mau analyze → Export copy dulu, analyze di file terpisah

---

### 📋 **Sheet: UNKNOWN**
**Purpose:** Log pertanyaan yang bot tidak bisa jawab

**Kolom Structure:**
| Column | Auto-Generated | Sam Boleh Edit | Notes |
|--------|----------------|----------------|-------|
| Pertanyaan | ✅ AUTO | ❌ JANGAN | User query |
| User | ✅ AUTO | ❌ JANGAN | WA number |
| Tanggal | ✅ AUTO | ❌ JANGAN | Timestamp |
| Takeover_Status | ⚪ Manual | ✅ EDIT | "Pending" / "Resolved" |
| Notes | ⚪ Manual | ✅ EDIT | Sam's notes |

**Guidelines:**
- ✅ **Sam BOLEH:** Add notes, update status
- ✅ **Sam BOLEH:** Review untuk add to FAQ
- ❌ **Sam JANGAN:** Delete entries (archive instead)

**Best Practice:**
```
Weekly Review Process:
1. Check UNKNOWN sheet every Monday
2. Identify common patterns (3+ sama)
3. Add to FAQ
4. Update Takeover_Status = "Resolved via FAQ"
5. Add Notes = "Added to FAQ on [date]"
```

---

### 📋 **Sheet: MOCK_INTERVIEW_BOOKING**
**Purpose:** Track mock interview bookings

**Kolom Structure:**
| Column | Auto-Generated | Sam Boleh Edit | Notes |
|--------|----------------|----------------|-------|
| No WA | ✅ AUTO | ❌ JANGAN | User number |
| Nama | ✅ AUTO | ⚠️ BOLEH | User name |
| Sesi | ✅ AUTO | ⚠️ BOLEH | Session type |
| Status | ✅ AUTO | ✅ EDIT | "Pending" / "Confirmed" / "Done" |
| Tanggal | ✅ AUTO | ❌ JANGAN | Booking date |
| ID Booking | ✅ AUTO | ❌ JANGAN | Unique ID |
| **Confirmed Date/Time** | ⚪ Manual | ✅ EDIT | Sam confirms actual slot |

**Guidelines:**
- ✅ **Sam EDIT:** Status + Confirmed Date/Time
- ❌ **Sam JANGAN:** Auto-generated fields

**Workflow:**
```
1. User books via bot → Creates row with Status="Pending"
2. Sam checks availability
3. Sam edits:
   - Status = "Confirmed"
   - Confirmed Date/Time = "10 Mei 2026, 15:00"
4. Sam contacts user via WA untuk confirm
5. After interview → Status = "Done"
```

---

## 🔴 **READ-ONLY** - Sam JANGAN Edit

### 📋 **Sheet: FASE_ROADMAP** (If exists)
**Purpose:** Technical documentation untuk future development

**Guidelines:**
- ❌ **JANGAN EDIT:** This is technical documentation
- ✅ **BOLEH BACA:** Untuk tahu roadmap development

---

## 📊 SHEET EDITING SUMMARY

| Sheet | Sam Boleh Edit | Update Frequency | Impact on Bot |
|-------|----------------|------------------|---------------|
| **FAQ** | ✅ YES | Weekly | IMMEDIATE |
| **HARGA** | ✅ YES | As needed | IMMEDIATE |
| **PROGRAM** | ✅ YES | Monthly | IMMEDIATE |
| **BATCH** | ✅ YES | Monthly | IMMEDIATE |
| **SYARAT** | ✅ YES | As needed | IMMEDIATE |
| **MOCK_INTERVIEW** | ✅ YES | As needed | IMMEDIATE |
| **LINKS** | ✅ YES | Rarely | IMMEDIATE |
| **ABOUT_SAM** | ✅ YES | Quarterly | IMMEDIATE |
| **STATS** | ⚠️ PARTIAL | Daily (bot_mode only) | Critical |
| **UNKNOWN** | ⚠️ PARTIAL | Weekly review | None |
| **MOCK_INTERVIEW_BOOKING** | ⚠️ PARTIAL | Daily (status/confirm) | Follow-up logic |
| **FASE_ROADMAP** | ❌ NO | Never | None |

---

## 🎯 **BEST PRACTICES for Sam**

### 1. **Before Editing ANY Sheet:**
- [ ] Buka file
- [ ] Check current data structure
- [ ] JANGAN sort/filter lalu save (mess up order)
- [ ] Edit only di cell yang needed
- [ ] Double-check typos
- [ ] Save

### 2. **Content Update Process:**
```
Example: Update Harga Program Junior

1. Buka sheet HARGA
2. Find row dengan Program = "Junior"
3. Update kolom "Harga Per Bulan" dan "Total Harga"
4. JANGAN delete/insert rows
5. Save
6. Test: Chat bot → Tanya harga Junior → Verify updated
```

### 3. **HITL (Manual Takeover) Process:**
```
1. User butuh personal attention
2. Buka STATS sheet
3. Find row dengan No WA user
4. Set bot_mode = "OFF"
5. Chat with user manually di WhatsApp
6. Setelah selesai:
   - Set bot_mode = kosong atau "ON"
   - Bot auto-resume
```

### 4. **Weekly Maintenance Checklist:**
```
Monday Morning (15 minutes):
[ ] Check UNKNOWN sheet → Add to FAQ if needed
[ ] Review STATS → Any users stuck? Need follow-up?
[ ] Update BATCH status if any changes
[ ] Check MOCK_INTERVIEW_BOOKING → Confirm pending bookings

Monthly (30 minutes):
[ ] Review FAQ → Remove outdated Q&A
[ ] Update PROGRAM → Any new programs?
[ ] Refresh ABOUT_SAM → Any new achievements?
[ ] Check HARGA → Any price changes?
```

---

## ⚠️ **COMMON MISTAKES to AVOID**

### ❌ **MISTAKE 1: Sorting Sheet then Saving**
```
Sam sorts STATS by "Intensitas Chat" → Highest first
Sam saves
→ Follow-up workflow BREAKS (expect original order)
```

**Fix:** Export to separate file for analysis, DON'T sort original.

---

### ❌ **MISTAKE 2: Deleting Rows in STATS**
```
Sam thinks: "User ini spam, delete aja"
Sam deletes row
→ Follow-up logic might error (looking for missing user)
```

**Fix:** DON'T delete. Instead, set bot_mode = "OFF" permanently.

---

### ❌ **MISTAKE 3: Duplicate FAQ Questions**
```
Already exists:
Q: "Berapa harga program Junior?"
A: "Rp 2.250.000/bulan..."

Sam adds:
Q: "Harga Junior berapa?"
A: "Rp 2.250.000/bulan..."

→ AI might get confused, give inconsistent answers
```

**Fix:** Search before adding. Update existing instead of duplicate.

---

### ❌ **MISTAKE 4: Typo in Critical Fields**
```
LINKS sheet:
Link Name: "GForm Pendaftaran"
URL: "https://forms.gle/TYPO123" ← WRONG URL

→ Bot sends broken link to users!
```

**Fix:** Triple-check URLs, test them before saving.

---

### ❌ **MISTAKE 5: Forgetting to Update Status**
```
BATCH sheet:
Batch 5 is FULL (60/60 students)
Status still says: "Open"

→ Bot keeps telling users "Batch 5 masih open!"
```

**Fix:** Update status IMMEDIATELY when batch full.

---

## 🎯 **FINAL CHECKLIST: Sam's Editing Rights**

✅ **Sam CAN Freely Edit (Content Sheets):**
- FAQ
- HARGA
- PROGRAM
- BATCH
- SYARAT
- MOCK_INTERVIEW
- LINKS
- ABOUT_SAM

⚠️ **Sam CAN Edit SPECIFIC FIELDS ONLY (System Sheets):**
- STATS: bot_mode, gform_filled
- UNKNOWN: Takeover_Status, Notes
- MOCK_INTERVIEW_BOOKING: Status, Confirmed Date/Time

❌ **Sam CANNOT Edit (System-Generated):**
- Auto-calculated fields (Counter, Intensitas, Timestamps)
- Auto-generated IDs
- Technical configuration sheets

---

**Remember:** Kalau ragu, JANGAN edit. Ask developer first! 😊

