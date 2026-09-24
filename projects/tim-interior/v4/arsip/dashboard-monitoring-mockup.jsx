import React, { useState } from 'react';
import { ClipboardList, AlertTriangle, Wallet, Clock3, MapPin } from 'lucide-react';

const C = {
  cream: '#F7F4ED',
  paper: '#FFFFFF',
  ink: '#2C2824',
  inkSoft: '#A39A90',
  gold: '#B49157',
  goldSoft: '#EFE6D5',
  sage: '#6E7F5C',
  sageSoft: '#E3E9DC',
  terracotta: '#AD5640',
  terracottaSoft: '#F4DCD4',
  slate: '#5C6E78',
  slateSoft: '#DEE5E8',
  line: '#E6DFD3',
};

const FONTS = `
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
.tim-mono { font-family: 'IBM Plex Mono', monospace; }
.tim-sans { font-family: 'Plus Jakarta Sans', sans-serif; }
`;

const formatRp = (n) => 'Rp ' + n.toLocaleString('id-ID');

/* ── Signature element: tape-measure / ruler progress bar ── */
function RulerBar({ segments, total }) {
  return (
    <div>
      <div
        style={{
          position: 'relative',
          height: 22,
          borderRadius: 5,
          background: C.cream,
          border: `1px solid ${C.line}`,
          overflow: 'hidden',
          display: 'flex',
        }}
      >
        {segments.map((s, i) => (
          <div
            key={i}
            style={{
              width: `${Math.max(0, Math.min(100, (s.value / total) * 100))}%`,
              background: s.color,
            }}
          />
        ))}
        {[10, 20, 30, 40, 50, 60, 70, 80, 90].map((t) => (
          <div
            key={t}
            style={{
              position: 'absolute',
              left: `${t}%`,
              top: 0,
              bottom: 0,
              width: 1,
              background: t === 50 ? 'rgba(44,40,36,0.22)' : 'rgba(44,40,36,0.09)',
            }}
          />
        ))}
      </div>
      <div
        className="tim-mono"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: 4,
          fontSize: 10,
          color: C.inkSoft,
          letterSpacing: 0.5,
        }}
      >
        <span>0</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100</span>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, eyebrow, value, sub, accent, ruler }) {
  return (
    <div
      style={{
        background: C.paper,
        border: `1px solid ${C.line}`,
        borderRadius: 10,
        padding: '16px 16px 14px',
        display: 'flex',
        flexDirection: 'column',
        gap: 10,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div
          style={{
            width: 30,
            height: 30,
            borderRadius: 7,
            background: accent.soft,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <Icon size={15} color={accent.main} strokeWidth={2.2} />
        </div>
        <span
          className="tim-mono"
          style={{ fontSize: 10, letterSpacing: 1, textTransform: 'uppercase', color: C.inkSoft }}
        >
          {eyebrow}
        </span>
      </div>
      <div className="tim-sans" style={{ fontSize: 26, fontWeight: 800, color: C.ink, lineHeight: 1 }}>
        {value}
      </div>
      {sub && (
        <div className="tim-sans" style={{ fontSize: 12, color: C.inkSoft }}>
          {sub}
        </div>
      )}
      {ruler && <RulerBar segments={ruler.segments} total={ruler.total} />}
    </div>
  );
}

function StatusBadge({ status }) {
  const map = {
    Proses: { bg: C.slateSoft, fg: C.slate },
    Selesai: { bg: C.sageSoft, fg: C.sage },
    Reject: { bg: C.terracottaSoft, fg: C.terracotta },
  };
  const s = map[status] || map.Proses;
  return (
    <span
      className="tim-mono"
      style={{
        background: s.bg,
        color: s.fg,
        fontSize: 10,
        fontWeight: 600,
        padding: '3px 8px',
        borderRadius: 5,
        letterSpacing: 0.5,
        whiteSpace: 'nowrap',
      }}
    >
      {status.toUpperCase()}
    </span>
  );
}

function PriorityDot({ prioritas }) {
  const map = { Kritis: C.terracotta, Tinggi: C.gold, Normal: C.inkSoft };
  return (
    <span
      style={{
        display: 'inline-block',
        width: 7,
        height: 7,
        borderRadius: '50%',
        background: map[prioritas] || C.inkSoft,
        marginRight: 6,
      }}
    />
  );
}

function SectionCard({ title, eyebrow, children }) {
  return (
    <div
      style={{
        background: C.paper,
        border: `1px solid ${C.line}`,
        borderRadius: 10,
        padding: 18,
      }}
    >
      <div className="tim-mono" style={{ fontSize: 10, letterSpacing: 1.5, color: C.gold, marginBottom: 4 }}>
        {eyebrow}
      </div>
      <div className="tim-sans" style={{ fontSize: 16, fontWeight: 700, color: C.ink, marginBottom: 14 }}>
        {title}
      </div>
      {children}
    </div>
  );
}

/* ── Mock data per proyek ── */
const PROJECTS = {
  ronald: {
    name: 'Ko Ronald — Renovasi Kantor & Gudang',
    lokasi: 'Jakarta Utara',
    statusCounts: { Proses: 5, Selesai: 12, Reject: 1 },
    kritisAktif: 2,
    updateCompliance: 87,
    budget: 85_000_000,
    realisasi: 62_300_000,
    rabCategories: [
      { name: 'Persiapan', budget: 6_000_000, realisasi: 6_000_000 },
      { name: 'Sipil & Partisi', budget: 28_000_000, realisasi: 24_500_000 },
      { name: 'Finishing', budget: 22_000_000, realisasi: 14_200_000 },
      { name: 'MEP (Elektrikal/Plumbing)', budget: 17_000_000, realisasi: 11_100_000 },
      { name: 'Furniture & Custom', budget: 12_000_000, realisasi: 6_500_000 },
    ],
    recentTickets: [
      { id: 'TIM-0142', kategori: 'Komplain', deskripsi: 'AC ruang meeting bocor', pic: 'Hendi', status: 'Proses', prioritas: 'Kritis', tanggal: '13 Jun' },
      { id: 'TIM-0141', kategori: 'Pembelian', deskripsi: 'Beli bracket TV lt. 2', pic: 'Mita', status: 'Selesai', prioritas: 'Normal', tanggal: '12 Jun' },
      { id: 'TIM-0140', kategori: 'Koordinasi', deskripsi: 'Follow up vendor parket', pic: 'Niki (Tantan)', status: 'Proses', prioritas: 'Tinggi', tanggal: '12 Jun' },
      { id: 'TIM-0139', kategori: 'Tambahan', deskripsi: 'Tambah rak gantung pantry', pic: 'Hendi', status: 'Selesai', prioritas: 'Normal', tanggal: '11 Jun' },
      { id: 'TIM-0138', kategori: 'Komplain', deskripsi: 'Pintu geser macet lt. 1', pic: 'Mita', status: 'Reject', prioritas: 'Normal', tanggal: '11 Jun' },
    ],
    picWorkload: [
      { nama: 'Hendi', aktif: 3, selesai: 8 },
      { nama: 'Mita', aktif: 1, selesai: 5 },
      { nama: 'Niki (Tantan)', aktif: 1, selesai: 3 },
    ],
  },
  vila: {
    name: 'Vila Cengkareng — Tahap 2',
    lokasi: 'Tangerang',
    statusCounts: { Proses: 2, Selesai: 20, Reject: 0 },
    kritisAktif: 0,
    updateCompliance: 95,
    budget: 140_000_000,
    realisasi: 138_200_000,
    rabCategories: [
      { name: 'Persiapan', budget: 8_000_000, realisasi: 8_000_000 },
      { name: 'Sipil & Partisi', budget: 45_000_000, realisasi: 45_000_000 },
      { name: 'Finishing', budget: 38_000_000, realisasi: 37_400_000 },
      { name: 'MEP (Elektrikal/Plumbing)', budget: 24_000_000, realisasi: 23_800_000 },
      { name: 'Furniture & Custom', budget: 25_000_000, realisasi: 24_000_000 },
    ],
    recentTickets: [
      { id: 'TIM-0214', kategori: 'Koordinasi', deskripsi: 'Jadwal serah terima lt. 3', pic: 'Hendi', status: 'Proses', prioritas: 'Tinggi', tanggal: '13 Jun' },
      { id: 'TIM-0213', kategori: 'Tambahan', deskripsi: 'Finishing cat ulang pagar', pic: 'Niki (Tantan)', status: 'Selesai', prioritas: 'Normal', tanggal: '12 Jun' },
      { id: 'TIM-0212', kategori: 'Komplain', deskripsi: 'Keramik teras retak', pic: 'Mita', status: 'Proses', prioritas: 'Normal', tanggal: '11 Jun' },
      { id: 'TIM-0211', kategori: 'Pembelian', deskripsi: 'Lampu taman tambahan', pic: 'Hendi', status: 'Selesai', prioritas: 'Normal', tanggal: '10 Jun' },
    ],
    picWorkload: [
      { nama: 'Hendi', aktif: 1, selesai: 11 },
      { nama: 'Mita', aktif: 0, selesai: 6 },
      { nama: 'Niki (Tantan)', aktif: 1, selesai: 3 },
    ],
  },
};

export default function Dashboard() {
  const [active, setActive] = useState('ronald');
  const p = PROJECTS[active];
  const totalTiket = p.statusCounts.Proses + p.statusCounts.Selesai + p.statusCounts.Reject;
  const realisasiPct = Math.round((p.realisasi / p.budget) * 100);

  return (
    <div className="tim-sans" style={{ minHeight: '100vh', background: C.cream, color: C.ink, padding: '20px 16px 40px' }}>
      <style>{FONTS}</style>

      <div style={{ maxWidth: 880, margin: '0 auto' }}>
        {/* Header */}
        <div className="tim-mono" style={{ fontSize: 11, letterSpacing: 2, color: C.gold, marginBottom: 6 }}>
          DASHBOARD MONITORING · TIM INTERIOR
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', justifyContent: 'space-between', gap: 8, marginBottom: 14 }}>
          <h1 style={{ fontSize: 22, fontWeight: 800, margin: 0 }}>{p.name}</h1>
          <div className="tim-mono" style={{ fontSize: 11, color: C.inkSoft }}>
            Update terakhir: 13 Jun 2026, 14:30 WIB
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
          <MapPin size={13} color={C.inkSoft} />
          <span style={{ fontSize: 12, color: C.inkSoft }}>{p.lokasi}</span>
        </div>

        {/* Project switcher */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          {Object.entries(PROJECTS).map(([key, proj]) => (
            <button
              key={key}
              onClick={() => setActive(key)}
              className="tim-sans"
              style={{
                padding: '7px 14px',
                borderRadius: 999,
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                border: `1px solid ${active === key ? C.gold : C.line}`,
                background: active === key ? C.gold : 'transparent',
                color: active === key ? C.paper : C.inkSoft,
              }}
            >
              {proj.name.split('—')[0].trim()}
            </button>
          ))}
        </div>

        {/* KPI row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: 12,
            marginBottom: 16,
          }}
        >
          <KpiCard
            icon={ClipboardList}
            eyebrow="Tiket Aktif"
            value={p.statusCounts.Proses}
            sub={`dari ${totalTiket} total tiket`}
            accent={{ main: C.slate, soft: C.slateSoft }}
          />
          <KpiCard
            icon={AlertTriangle}
            eyebrow="Perlu Perhatian"
            value={p.kritisAktif}
            sub="prioritas kritis, belum selesai"
            accent={{ main: C.terracotta, soft: C.terracottaSoft }}
          />
          <KpiCard
            icon={Wallet}
            eyebrow="Realisasi RAB"
            value={`${realisasiPct}%`}
            sub={`${formatRp(p.realisasi)} / ${formatRp(p.budget)}`}
            accent={{ main: C.gold, soft: C.goldSoft }}
            ruler={{ segments: [{ value: p.realisasi, color: C.gold }], total: p.budget }}
          />
          <KpiCard
            icon={Clock3}
            eyebrow="Update Tepat Waktu"
            value={`${p.updateCompliance}%`}
            sub="tiket diupdate sebelum 19:00"
            accent={{ main: C.sage, soft: C.sageSoft }}
            ruler={{ segments: [{ value: p.updateCompliance, color: C.sage }], total: 100 }}
          />
        </div>

        {/* Main grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
          {/* Status tiket */}
          <SectionCard eyebrow="STATUS TIKET" title="Distribusi Status">
            <RulerBar
              segments={[
                { value: p.statusCounts.Proses, color: C.slate },
                { value: p.statusCounts.Selesai, color: C.sage },
                { value: p.statusCounts.Reject, color: C.terracotta },
              ]}
              total={totalTiket}
            />
            <div style={{ display: 'flex', gap: 16, marginTop: 12, flexWrap: 'wrap' }}>
              {[
                ['Proses', p.statusCounts.Proses, C.slate],
                ['Selesai', p.statusCounts.Selesai, C.sage],
                ['Reject', p.statusCounts.Reject, C.terracotta],
              ].map(([label, val, color]) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
                  <span style={{ color: C.inkSoft }}>{label}</span>
                  <span className="tim-mono" style={{ fontWeight: 600 }}>{val}</span>
                </div>
              ))}
            </div>
          </SectionCard>

          {/* Recent tickets */}
          <SectionCard eyebrow="AKTIVITAS" title="Tiket Terbaru">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {p.recentTickets.map((t) => (
                <div
                  key={t.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 10,
                    paddingBottom: 10,
                    borderBottom: `1px solid ${C.line}`,
                  }}
                >
                  <div style={{ minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', fontSize: 13, fontWeight: 600 }}>
                      <PriorityDot prioritas={t.prioritas} />
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {t.deskripsi}
                      </span>
                    </div>
                    <div className="tim-mono" style={{ fontSize: 11, color: C.inkSoft, marginTop: 2 }}>
                      {t.id} · {t.kategori} · {t.pic} · {t.tanggal}
                    </div>
                  </div>
                  <StatusBadge status={t.status} />
                </div>
              ))}
            </div>
          </SectionCard>

          {/* RAB per kategori */}
          <SectionCard eyebrow="REALISASI RAB" title="Per Kategori Pekerjaan">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {p.rabCategories.map((c) => {
                const pct = Math.round((c.realisasi / c.budget) * 100);
                return (
                  <div key={c.name}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: 12 }}>
                      <span style={{ fontWeight: 600 }}>{c.name}</span>
                      <span className="tim-mono" style={{ color: C.inkSoft }}>
                        {formatRp(c.realisasi)} / {formatRp(c.budget)} · {pct}%
                      </span>
                    </div>
                    <RulerBar segments={[{ value: c.realisasi, color: C.gold }]} total={c.budget} />
                  </div>
                );
              })}
            </div>
          </SectionCard>

          {/* PIC workload */}
          <SectionCard eyebrow="BEBAN KERJA" title="Tiket per PIC Mandor">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {p.picWorkload.map((pic) => {
                const total = pic.aktif + pic.selesai;
                return (
                  <div key={pic.nama}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: 12 }}>
                      <span style={{ fontWeight: 600 }}>{pic.nama}</span>
                      <span className="tim-mono" style={{ color: C.inkSoft }}>
                        {pic.aktif} aktif · {pic.selesai} selesai
                      </span>
                    </div>
                    <RulerBar
                      segments={[
                        { value: pic.aktif, color: C.slate },
                        { value: pic.selesai, color: C.sage },
                      ]}
                      total={total}
                    />
                  </div>
                );
              })}
            </div>
          </SectionCard>
        </div>

        <div className="tim-mono" style={{ fontSize: 10, color: C.inkSoft, marginTop: 20, textAlign: 'center' }}>
          Data di atas adalah ilustrasi · akan terhubung langsung ke sheet Database &amp; Update_History
        </div>
      </div>
    </div>
  );
}
