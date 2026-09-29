/* ============================================================================
 * tenants.js — REGISTRY TENANT (server-side only, JANGAN pernah dikirim ke browser)
 *
 * Satu-satunya tempat yang memetakan tenant -> spreadsheet + skema kolom.
 * Frontend TIDAK PERNAH mengirim/menerima spreadsheet ID. Client hanya kirim
 * token bertanda tangan; server yang menentukan sheet mana yang boleh dibaca.
 *
 * Menambah tenant ke-3 = tambah 1 entri di sini. Nol perubahan di frontend.
 *
 * Dipakai oleh:
 *   - n8n Code node "Tenant Profile"  (di-inline oleh build_workflow.py)
 *   - qa/selftest.html                (di-load langsung sebagai <script>)
 * ========================================================================== */
'use strict';

/* --- Kamus tipe kolom yang dipahami frontend ------------------------------
 * text | int | date | wa | toggle | badge | datetime
 * ----------------------------------------------------------------------- */

var VIRA_TENANTS = {

  /* ======================================================================
   * THE SCHOLARS — konsultan pendidikan, VIRA = "Sam versi AI"
   * ==================================================================== */
  thescholars: {
    id: 'thescholars',
    name: 'The Scholars',
    product: 'VIRA — Asisten WhatsApp',
    accent: 'blue',
    // Satu kalimat bidang usaha, HANYA dipakai sebagai konteks prompt
    // rekomendasi AI. Tidak pernah dikirim ke frontend.
    //
    // Letaknya SESUDAH accent, bukan di tengah id/name/product/accent:
    // qa/serve.py membaca blok itu dengan regex yang mengharuskan keempatnya
    // berurutan, dan menyisipkan apa pun di tengahnya membuat harness QA mati
    // dengan pesan "gagal membaca akun/tenant".
    aiContext: 'konsultan pendidikan dan beasiswa untuk pelajar Indonesia — program persiapan, kelas, dan mock interview',

    /*
     * Berkas logo, relatif terhadap index.html dashboard. Dikirim ke klien
     * lewat deskriptor tenant supaya frontend tidak perlu tahu tenant mana
     * yang punya logo — dulu peta ini hidup di app/js/config.js, yang berarti
     * menambah klien ketiga menuntut perubahan kode frontend.
     * Kosongkan (atau hilangkan) untuk memakai emblem huruf awal.
     * Hanya path relatif se-origin yang diterima; render.js menolak URL absolut.
     */
    logo: 'icons/thescholars.jpg',
    sheetId: '1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE',

    // Tab yang dibaca dashboard. CONFIG SENGAJA TIDAK DIBACA.
    tabs: ['STATS', 'UNKNOWN', 'MOCK_INTERVIEW_BOOKING', 'MOCK_SLOTS', 'MONTHLY_SUMMARY'],

    // Tab tempat state per-user hidup (dipakai toggle bot_mode).
    statsTab: 'STATS',

    // Pemetaan kolom sheet -> kunci generik yang dirender frontend.
    // Nilai array = ambil kolom pertama yang terisi (prioritas kiri ke kanan).
    map: {
      wa:         'No WA',
      lid:        'lid',
      nama:       'Nama',
      segment:    'program_interest',
      stage:      'kelas_anak',
      counter:    'Counter',
      first_chat: 'Tanggal Chat Pertama',
      last_chat:  'Tanggal Chat Terakhir',
      last_hour:  'Jam Chat Terakhir',
      bot_mode:   'bot_mode'
    },

    // Label kolom di tabel Direktori Lead (urutan = urutan tampil).
    leadColumns: [
      { key: 'wa',       label: 'No WA',          type: 'wa'     },
      { key: 'nama',     label: 'Nama',           type: 'text'   },
      { key: 'segment',  label: 'Minat Program',  type: 'badge'  },
      { key: 'stage',    label: 'Kelas Anak',     type: 'text'   },
      { key: 'counter',  label: 'Chat',           type: 'int'    },
      { key: 'last_chat',label: 'Chat Terakhir',  type: 'date'   },
      { key: 'bot_mode', label: 'Bot',            type: 'toggle' }
    ],

    // Isi drawer detail lead: kolom mentah -> label.
    detailFields: [
      { col: 'Nama',                  label: 'Nama'                },
      { col: 'lid',                   label: 'LID'                 },
      { col: 'program_interest',      label: 'Minat Program'       },
      { col: 'kelas_anak',            label: 'Kelas Anak'          },
      { col: 'Counter',               label: 'Total Chat'          },
      { col: 'Intensitas Chat',       label: 'Intensitas Chat'     },
      { col: 'Tanggal Chat Pertama',  label: 'Chat Pertama'        },
      { col: 'Tanggal Chat Terakhir', label: 'Chat Terakhir'       },
      { col: 'Jam Chat Terakhir',     label: 'Jam Chat Terakhir'   },
      { col: 'greeting_sent',         label: 'Sudah Disapa'        },
      { col: 'gform_sent_ts',         label: 'GForm Dikirim (ts)'  },
      { col: 'follow_up_count',       label: 'Jumlah Follow-up'    },
      { col: 'Pesan Pertama',         label: 'Pesan Pertama'       }
    ],

    // KPI tambahan di luar 4 KPI universal.
    extraKpis: [
      { id: 'gform_sent', label: 'GForm Terkirim', tone: 'teal',
        agg: 'count_nonempty', tab: 'STATS', col: 'gform_sent_ts',
        hint: 'Baris STATS dengan gform_sent_ts terisi' },
      { id: 'mock_booking', label: 'Booking Mock Interview', tone: 'purple',
        agg: 'count_rows', tab: 'MOCK_INTERVIEW_BOOKING',
        hint: 'Total baris MOCK_INTERVIEW_BOOKING' }
    ],

    // Doughnut tambahan (di luar chart universal).
    // Ringkasan bulanan topik (diisi WF-B "VIRA Monthly Rollup").
    // Menampilkan bulan TERAKHIR yang sudah direkap = bulan lalu.
    // Chart-nya sengaja tanpa rangeAware: granularitasnya bulan, bukan hari.
    monthlySummary: {
      id: 'topik',
      tab: 'MONTHLY_SUMMARY',
      monthCol: 'bulan',
      topCol: 'top_json',
      // Diisi WF-B (Monthly Rollup). Dashboard hanya membacanya.
      insightCol: 'ai_insight_json',
      insightTitle: 'AI Insight dari Topik',
      noteCol: 'coverage_note',
      labelKey: 'topic',
      valueKey: 'users',
      chartTop: 5,
      chartTitle: 'Komposisi Topik (5 terbesar)',
      tableTitle: 'Peringkat Topik',
      kpis: [
        { id: 'bulan_user',  label: 'User Chat Bulan Lalu', tone: 'blue',
          col: 'total_user_unik', hint: 'User unik yang chat VIRA' },
        { id: 'bulan_pesan', label: 'Pesan Bulan Lalu',     tone: 'teal',
          col: 'total_pesan',     hint: 'Total pesan masuk' }
      ]
    },

    // id topik -> label yang enak dibaca Sam. Tanpa entri di sini, id
    // snake_case otomatis dirapikan (underscore jadi spasi + huruf besar).
    topicLabels: {
      minat_asean_scholarship:             'ASEAN Scholarship',
      syarat_usia_kelas:                   'Syarat usia / kelas anak',
      program_senior_admisi_uni:           'Program Senior & admisi universitas',
      minat_program_batch_generik:         'Minat program (belum spesifik)',
      beasiswa_umum_luar_negeri:           'Beasiswa luar negeri (umum)',
      tanya_tanpa_topik_spesifik:          'Mau tanya, topik belum disebut',
      status_pendaftaran_dan_ketersediaan: 'Status pendaftaran & kuota',
      akses_webinar_zoom:                  'Akses webinar / Zoom',
      uob_cli_scholarship:                 'UOB / CLI Scholarship',
      biaya_program:                       'Biaya program',
      lokasi_cabang:                       'Lokasi & cabang',
      info_program_general:                'Info program (umum)',
      konsultasi_langsung:                 'Minta bicara langsung',
      jadwal_kelas_waktu:                  'Jadwal & waktu kelas',
      les_privat_lain:                     'Les privat mapel lain',
      ielts_english_test:                  'IELTS / tes bahasa Inggris',
      lainnya:                             'Lainnya'
    },

    distributions: [
      { id: 'program', title: 'Minat Program', key: 'segment',
        hint: 'Sebaran kolom Minat Program dari SELURUH lead di tab STATS ' +
              '(6 nilai terbanyak, sisanya digabung). Tidak mengikuti filter rentang.' },
      { id: 'kelas',   title: 'Distribusi Kelas', key: 'stage',
        hint: 'Sebaran kolom Kelas Anak dari SELURUH lead di tab STATS ' +
              '(6 nilai terbanyak). Lead yang kelasnya belum ditanyakan tidak ikut terhitung.' }
    ],

    // Tabel tambahan di tab "Operasional".
    tables: [
      {
        id: 'mock', title: 'Booking Mock Interview', tab: 'MOCK_INTERVIEW_BOOKING',
        hint: 'Dari tab MOCK_INTERVIEW_BOOKING — satu baris per booking mock ' +
              'interview yang berhasil masuk. Ini hasilnya; daftar slot yang ' +
              'tersedia ada di kartu "Slot Mock Interview".',
        empty: 'Belum ada booking mock interview.',
        sort: { col: 'Tanggal', dir: 'desc' }, limit: 200,
        columns: [
          { col: 'ID Booking',        label: 'ID',        type: 'text' },
          { col: 'Tanggal',           label: 'Tanggal',   type: 'text' },
          { col: 'Sesi',              label: 'Sesi',      type: 'text' },
          { col: 'Nama Anak',         label: 'Nama Anak', type: 'text' },
          { col: 'Nama Orang Tua',    label: 'Orang Tua', type: 'text' },
          { col: 'Sekolah',           label: 'Sekolah',   type: 'text' },
          { col: 'Kelas',             label: 'Kelas',     type: 'text' },
          { col: 'Target Uni Jurusan',label: 'Target',    type: 'text' },
          { col: 'Status',            label: 'Status',    type: 'badge' }
        ]
      },
      {
        id: 'slots', title: 'Slot Mock Interview', tab: 'MOCK_SLOTS',
        hint: 'Dari tab MOCK_SLOTS — inventori jadwal yang dibuka, beserta ' +
              'status terisinya. Sifatnya data admin: berguna untuk melihat slot ' +
              'mana yang masih kosong, bukan untuk mengukur performa.',
        empty: 'Belum ada slot terdaftar.',
        sort: { col: 'Tanggal', dir: 'asc' }, limit: 200,
        columns: [
          { col: 'ID',          label: 'ID',       type: 'text' },
          { col: 'Tanggal',     label: 'Tanggal',  type: 'text' },
          { col: 'JamMulai',    label: 'Mulai',    type: 'text' },
          { col: 'JamSelesai',  label: 'Selesai',  type: 'text' },
          { col: 'Booked',      label: 'Terisi',   type: 'badge' },
          { col: 'NamaPemesan', label: 'Pemesan',  type: 'text' }
        ]
      }
    ],

    // Tabel "pertanyaan tak terjawab" (sama di semua tenant, tab UNKNOWN).
    unknownTable: {
      id: 'unknown', title: 'Pertanyaan Belum Terjawab Bot', tab: 'UNKNOWN',
      hint: 'Dari tab UNKNOWN. Bot menulis satu baris ke situ setiap kali ada ' +
            'pertanyaan yang tidak bisa ia jawab. Ini daftar kerja, bukan metrik: ' +
            'tiap baris adalah kandidat tambahan FAQ atau perbaikan prompt. ' +
            'Kalau isinya kosong, artinya bot menjawab semuanya.',
      empty: 'Tidak ada pertanyaan yang gagal dijawab. Bagus.',
      sort: { col: 'Tanggal', dir: 'desc' }, limit: 300,
      columns: [
        { col: 'Tanggal',    label: 'Tanggal',    type: 'text' },
        { col: 'User',       label: 'User',       type: 'wa'   },
        { col: 'Pertanyaan', label: 'Pertanyaan', type: 'text' }
      ]
    }
  },

  /* ======================================================================
   * PERSADA CISOKA RESIDENCE — developer perumahan, VIRA = telemarketer
   * ==================================================================== */
  persada: {
    id: 'persada',
    name: 'Persada Cisoka Residence',
    product: 'VIRA-PCR — Telemarketer WhatsApp',
    accent: 'blue',
    aiContext: 'pengembang perumahan yang menjual unit rumah lewat survei dan kunjungan lokasi',
    logo: '',                      /* belum punya berkas logo -> emblem huruf */
    sheetId: '1pzGuRZbDXCFSZrHHbiEpTbF8F-_yMY0yex80_NmjB4o',

    // CONFIG SENGAJA TIDAK DIBACA — tab itu memuat private key service account
    // Google dalam bentuk plaintext (lihat docs/2026-07-28-konsultasi-rekomendasi.md T1).
    tabs: ['STATS', 'UNKNOWN', 'SURVEY', 'EVENTS'],
    statsTab: 'STATS',

    map: {
      wa:         'No WA',
      lid:        'lid',
      nama:       ['nama_lengkap', 'Nama'],
      segment:    'unit_interest',
      stage:      'survey_status',
      counter:    'Counter',
      first_chat: 'Tanggal Chat Pertama',
      last_chat:  'Tanggal Chat Terakhir',
      last_hour:  'Jam Chat Terakhir',
      bot_mode:   'bot_mode'
    },

    leadColumns: [
      { key: 'wa',        label: 'No WA',         type: 'wa'     },
      { key: 'nama',      label: 'Nama',          type: 'text'   },
      { key: 'segment',   label: 'Unit Diminati', type: 'badge'  },
      { key: 'stage',     label: 'Status Survey', type: 'badge'  },
      { key: 'counter',   label: 'Chat',          type: 'int'    },
      { key: 'last_chat', label: 'Chat Terakhir', type: 'date'   },
      { key: 'bot_mode',  label: 'Bot',           type: 'toggle' }
    ],

    detailFields: [
      { col: 'nama_lengkap',          label: 'Nama Lengkap'      },
      { col: 'Nama',                  label: 'Nama WhatsApp'     },
      { col: 'lid',                   label: 'LID'               },
      { col: 'lead_source',           label: 'Sumber Traffic'    },
      { col: 'unit_interest',         label: 'Unit Diminati'     },
      { col: 'budget_range',          label: 'Range Budget'      },
      { col: 'lokasi_kerja',          label: 'Lokasi Kerja'      },
      { col: 'survey_date',           label: 'Tanggal Survey'    },
      { col: 'survey_time',           label: 'Jam Survey'        },
      { col: 'survey_status',         label: 'Status Survey'     },
      { col: 'flag_survey',           label: 'Flag Survey'       },
      { col: 'Counter',               label: 'Total Chat'        },
      { col: 'Intensitas Chat',       label: 'Intensitas Chat'   },
      { col: 'Tanggal Chat Pertama',  label: 'Chat Pertama'      },
      { col: 'Tanggal Chat Terakhir', label: 'Chat Terakhir'     },
      { col: 'follow_up_count',       label: 'Jumlah Follow-up'  },
      { col: 'Pesan Pertama',         label: 'Pesan Pertama'     }
    ],

    extraKpis: [
      { id: 'survey_scheduled', label: 'Survey Terjadwal', tone: 'teal',
        agg: 'count_nonempty', tab: 'STATS', col: 'survey_date',
        hint: 'Baris STATS dengan survey_date terisi' },
      { id: 'survey_logged', label: 'Survey Tercatat', tone: 'purple',
        agg: 'count_rows', tab: 'SURVEY',
        hint: 'Total baris tab SURVEY' }
    ],

    distributions: [
      { id: 'unit',   title: 'Unit Diminati',  key: 'segment',
        hint: 'Sebaran kolom Unit Diminati dari SELURUH lead di tab STATS ' +
              '(6 nilai terbanyak). Tidak mengikuti filter rentang.' },
      { id: 'source', title: 'Sumber Traffic', col: 'lead_source',
        hint: 'Sebaran kolom lead_source dari SELURUH lead di tab STATS ' +
              '(6 nilai terbanyak). Lead yang sumbernya belum terdeteksi tidak ikut terhitung.' }
    ],

    tables: [
      {
        id: 'survey', title: 'Jadwal Survey', tab: 'SURVEY',
        hint: 'Dari tab SURVEY — satu baris per jadwal survey unit yang sudah ' +
              'tercatat, beserta status dan sumber traffic-nya.',
        empty: 'Belum ada survey terjadwal.',
        sort: { col: 'created_ts', dir: 'desc' }, limit: 200,
        columns: [
          { col: 'tanggal',        label: 'Tanggal',  type: 'text' },
          { col: 'jam',            label: 'Jam',      type: 'text' },
          { col: 'nama',           label: 'Nama',     type: 'text' },
          { col: 'no_wa',          label: 'No WA',    type: 'wa'   },
          { col: 'unit_diminati',  label: 'Unit',     type: 'text' },
          { col: 'sumber_traffic', label: 'Sumber',   type: 'badge'},
          { col: 'status',         label: 'Status',   type: 'badge'},
          { col: 'catatan',        label: 'Catatan',  type: 'text' }
        ]
      },
      {
        id: 'events', title: 'Log Aktivitas', tab: 'EVENTS',
        hint: 'Dari tab EVENTS — jejak kejadian yang dicatat bot, termasuk saat ' +
              'percakapan dialihkan ke manusia. Dipakai untuk menelusuri kembali ' +
              'apa yang terjadi pada satu lead.',
        empty: 'Belum ada aktivitas tercatat.',
        sort: { col: 'ts', dir: 'desc' }, limit: 200,
        columns: [
          { col: 'ts',     label: 'Waktu',  type: 'epoch_auto' },
          { col: 'nama',   label: 'Nama',   type: 'text'  },
          { col: 'no_wa',  label: 'No WA',  type: 'wa'    },
          { col: 'event',  label: 'Event',  type: 'badge' },
          { col: 'detail', label: 'Detail', type: 'text'  }
        ]
      }
    ],

    unknownTable: {
      id: 'unknown', title: 'Pertanyaan Belum Terjawab Bot', tab: 'UNKNOWN',
      hint: 'Dari tab UNKNOWN. Bot menulis satu baris ke situ setiap kali ada ' +
            'pertanyaan yang tidak bisa ia jawab. Ini daftar kerja, bukan metrik: ' +
            'tiap baris adalah kandidat tambahan FAQ atau perbaikan prompt. ' +
            'Kalau isinya kosong, artinya bot menjawab semuanya.',
      empty: 'Tidak ada pertanyaan yang gagal dijawab. Bagus.',
      sort: { col: 'Tanggal', dir: 'desc' }, limit: 300,
      columns: [
        { col: 'Tanggal',    label: 'Tanggal',    type: 'text' },
        { col: 'User',       label: 'User',       type: 'wa'   },
        { col: 'Pertanyaan', label: 'Pertanyaan', type: 'text' }
      ]
    }
  },

  /* ---------------------------------------------------------------------
   * VIRA Personal — bot pribadi Steven (klien ke-3, ditambahkan 2026-08-28).
   * Berbeda dari dua tenant lain: ini bukan klien berbayar, melainkan corong
   * lead untuk jasa Steven sendiri. Karena itu KPI-nya berputar di sekitar
   * "berapa brief deck yang masuk", bukan booking/survey.
   * ------------------------------------------------------------------- */
  personal: {
    id: 'personal',
    name: 'VIRA Personal',
    product: 'VIRA — Asisten WhatsApp Pribadi',
    accent: 'blue',
    aiContext: 'layanan otomasi dan konsultasi teknis untuk klien perorangan',
    logo: '',                      /* belum punya berkas logo -> emblem huruf */
    sheetId: '1C5gF1TTJFAHCrfVESiaIhAts6iByRH9BRjLqBCO_Yxk',

    // CONFIG SENGAJA TIDAK DIBACA — sama alasannya dengan dua tenant lain:
    // tab itu memuat kredensial Kirimi dalam bentuk plaintext.
    // REQUESTS ikut dibaca karena jadi sumber KPI "Brief Masuk".
    tabs: ['STATS', 'UNKNOWN', 'REQUESTS', 'EVENTS'],
    statsTab: 'STATS',

    map: {
      wa: 'No WA', lid: 'lid', nama: ['nama_lengkap', 'Nama'],
      segment: 'minat_paket', stage: 'industri', counter: 'Counter',
      first_chat: 'Tanggal Chat Pertama', last_chat: 'Tanggal Chat Terakhir',
      last_hour: 'Jam Chat Terakhir', bot_mode: 'bot_mode'
    },

    leadColumns: [
      { key: 'wa',        label: 'No WA',         type: 'wa'     },
      { key: 'nama',      label: 'Nama',          type: 'text'   },
      { key: 'segment',   label: 'Paket Diminati',type: 'badge'  },
      { key: 'stage',     label: 'Industri',      type: 'text'   },
      { key: 'counter',   label: 'Chat',          type: 'int'    },
      { key: 'last_chat', label: 'Chat Terakhir', type: 'date'   },
      { key: 'bot_mode',  label: 'Bot',           type: 'toggle' }
    ],

    detailFields: [
      { col: 'Nama',                  label: 'Nama'               },
      { col: 'nama_lengkap',          label: 'Nama Lengkap'       },
      { col: 'lid',                   label: 'LID'                },
      { col: 'nama_bisnis',           label: 'Nama Bisnis'        },
      { col: 'industri',              label: 'Industri'           },
      { col: 'minat_paket',           label: 'Paket Diminati'     },
      { col: 'budget_range',          label: 'Kisaran Budget'     },
      { col: 'masalah_utama',         label: 'Masalah Utama'      },
      { col: 'volume_chat',           label: 'Volume Chat Harian' },
      { col: 'deck_requested',        label: 'Minta Deck'         },
      { col: 'brief_terisi',          label: 'Kelengkapan Brief'  },
      { col: 'lead_source',           label: 'Sumber Lead'        },
      { col: 'Counter',               label: 'Total Chat'         },
      { col: 'Tanggal Chat Pertama',  label: 'Chat Pertama'       },
      { col: 'Tanggal Chat Terakhir', label: 'Chat Terakhir'      },
      { col: 'Jam Chat Terakhir',     label: 'Jam Chat Terakhir'  },
      { col: 'follow_up_count',       label: 'Jumlah Follow-up'   },
      { col: 'Pesan Pertama',         label: 'Pesan Pertama'      }
    ],

    extraKpis: [
      { id: 'deck_diminta', label: 'Deck Diminta', tone: 'teal',
        agg: 'count_nonempty', tab: 'STATS', col: 'deck_requested',
        hint: 'Baris STATS dengan deck_requested terisi' },
      { id: 'brief_masuk', label: 'Brief Masuk', tone: 'purple',
        agg: 'count_rows', tab: 'REQUESTS',
        hint: 'Total baris tab REQUESTS' }
    ],

    distributions: [
      { id: 'paket',  title: 'Paket Diminati', key: 'segment',
        hint: 'Sebaran kolom minat_paket dari SELURUH lead di tab STATS ' +
              '(6 nilai terbanyak). Tidak mengikuti filter rentang.' },
      { id: 'source', title: 'Sumber Traffic', col: 'lead_source',
        hint: 'Sebaran kolom lead_source dari SELURUH lead di tab STATS ' +
              '(6 nilai terbanyak). Lead yang sumbernya belum terdeteksi tidak ikut terhitung.' }
    ],

    tables: [
      {
        id: 'requests', title: 'Brief Deck Masuk', tab: 'REQUESTS',
        hint: 'Dari tab REQUESTS — satu baris per prospek yang mengisi brief ' +
              'lewat alur [DECK_REQUEST]. Kolom kelengkapan menunjukkan seberapa ' +
              'lengkap brief itu sebelum deck dibuatkan.',
        empty: 'Belum ada brief deck yang masuk.',
        sort: { col: 'update_terakhir', dir: 'desc' }, limit: 200,
        columns: [
          { col: 'update_terakhir', label: 'Update',    type: 'text'  },
          { col: 'nama',            label: 'Nama',      type: 'text'  },
          { col: 'no_wa',           label: 'No WA',     type: 'wa'    },
          { col: 'nama_bisnis',     label: 'Bisnis',    type: 'text'  },
          { col: 'industri',        label: 'Industri',  type: 'badge' },
          { col: 'minat_paket',     label: 'Paket',     type: 'badge' },
          { col: 'budget_range',    label: 'Budget',    type: 'text'  },
          { col: 'urgensi',         label: 'Urgensi',   type: 'badge' },
          { col: 'kelengkapan',     label: 'Lengkap',   type: 'text'  },
          { col: 'status_followup', label: 'Follow-up', type: 'badge' }
        ]
      },
      {
        id: 'events', title: 'Log Aktivitas', tab: 'EVENTS',
        hint: 'Dari tab EVENTS — jejak kejadian yang dicatat bot, termasuk saat ' +
              'percakapan dialihkan ke Steven. Dipakai untuk menelusuri kembali ' +
              'apa yang terjadi pada satu lead.',
        empty: 'Belum ada aktivitas tercatat.',
        sort: { col: 'ts', dir: 'desc' }, limit: 200,
        columns: [
          { col: 'ts',     label: 'Waktu',  type: 'epoch_auto' },
          { col: 'nama',   label: 'Nama',   type: 'text'  },
          { col: 'no_wa',  label: 'No WA',  type: 'wa'    },
          { col: 'event',  label: 'Event',  type: 'badge' },
          { col: 'detail', label: 'Detail', type: 'text'  }
        ]
      }
    ],

    unknownTable: {
      id: 'unknown', title: 'Pertanyaan Belum Terjawab Bot', tab: 'UNKNOWN',
      hint: 'Dari tab UNKNOWN. Bot menulis satu baris ke situ setiap kali ada ' +
            'pertanyaan yang tidak bisa ia jawab. Ini daftar kerja, bukan metrik: ' +
            'tiap baris adalah kandidat tambahan FAQ atau perbaikan prompt. ' +
            'Kalau isinya kosong, artinya bot menjawab semuanya.',
      empty: 'Tidak ada pertanyaan yang gagal dijawab. Bagus.',
      sort: { col: 'Tanggal', dir: 'desc' }, limit: 300,
      columns: [
        { col: 'Tanggal',    label: 'Tanggal',    type: 'text' },
        { col: 'User',       label: 'User',       type: 'wa'   },
        { col: 'Pertanyaan', label: 'Pertanyaan', type: 'text' }
      ]
    }
  }
};

/* --- Akun dashboard --------------------------------------------------------
 * password = sha256(salt + ":" + plaintext), hex lowercase.
 * role 'super'  -> boleh berpindah antar tenant (Steven).
 * role 'owner'  -> terkunci ke tenant di `tenants` (hanya 1 entri).
 *
 * Ganti password: jalankan  python qa/hash_password.py "password-baru"
 * lalu tempel salt+hash di sini dan re-import workflow.
 * ------------------------------------------------------------------------ */
var VIRA_USERS = {
  steven: {
    username: 'steven',
    display: 'Steven',
    role: 'super',
    tenants: ['thescholars', 'persada', 'personal'],
    salt: 'f416f0d2775c5439',
    hash: '44cb6fdb048ee14f15da014b6d0eb7a5198c50bfa469c2044aad99c052fded26'
  },
  sam: {
    username: 'sam',
    display: 'Sam — The Scholars',
    role: 'owner',
    tenants: ['thescholars'],
    salt: '8f6d41013227cdbe',
    hash: 'c11b445aad7cdc8eefa860762424dacd86ffe145593323b3b0137388951a2771'
  },
  sulianto: {
    username: 'sulianto',
    display: 'Om Sulianto — Persada',
    role: 'owner',
    tenants: ['persada'],
    salt: '46c22d4c454f68a0',
    hash: '8e311975b300b8c6f01417c63d73b34450a5d502c9b94af476f17685e25a79fd'
  }
};

/* --- Pengaturan runtime -------------------------------------------------- */
var VIRA_SETTINGS = {
  // Umur token sesi (detik). 30 hari — sengaja panjang supaya owner cukup
  // masuk sekali lalu pakai ikon PWA di layar depan tanpa login ulang.
  // Mencabut akses tetap seketika: hapus entri user di VIRA_USERS lalu
  // rebuild+import, karena setiap request memeriksa ulang akun ke registry
  // dan tidak hanya percaya isi token.
  tokenTtlSec: 30 * 24 * 60 * 60,

  // TTL cache statistik (detik). Melindungi kuota Google Sheets bot.
  // Naikkan kalau kuota terasa ketat; turunkan kalau butuh data lebih segar.
  statsCacheSec: 60,

  // Lockout login: N gagal dalam windowSec -> tolak sampai window habis.
  loginMaxFail: 5,
  loginWindowSec: 15 * 60,

  // Origin yang boleh memanggil API. Isi domain hasil deploy Cloudflare/Netlify.
  // '*' TIDAK dipakai supaya token tidak bisa dipanggil dari halaman asing.
  corsOrigins: [
    // Domain produksi SENGAJA di urutan pertama. vaCorsOrigin() jatuh ke
    // entry [0] kalau origin tidak dikenal, jadi urutan ini membuat header
    // yang keluar langsung memberi tahu versi kode mana yang sedang jalan.
    'https://vira-dashboard.chatminagent.workers.dev',
    'http://localhost:8080',
    'http://127.0.0.1:8080'
  ],

  // Rentang default grafik tren (hari).
  defaultRangeDays: 30,

  // Tab audit: setiap perubahan bot_mode dari dashboard dicatat di sini.
  // Buat tab ini di SETIAP spreadsheet tenant dengan header persis:
  //   ts | actor | role | no_wa | from | to
  // Kalau tabnya belum ada, node append gagal diam-diam dan toggle TETAP jalan
  // (onError: continueRegularOutput) — jadi ini aman dipasang bertahap.
  auditTab: 'DASH_AUDIT'
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { VIRA_TENANTS: VIRA_TENANTS, VIRA_USERS: VIRA_USERS, VIRA_SETTINGS: VIRA_SETTINGS };
}
