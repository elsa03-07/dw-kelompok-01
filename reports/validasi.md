# Laporan Validasi Data Silver dan Gold

**Penyusun:** Tim Kelompok 1 (Pelaksana Komponen Validasi: 124450061 - Backlog #25)  
**Total Baris Silver:** 1,439  
**Status Lapis Gold:** Tersedia (6 tabel)  
**Jumlah Aturan Diuji:** 18  
**Jumlah Aturan Lolos:** 18  
**Status Evaluasi:** SELURUH ATURAN LOLOS (100%)  

---

## Tabel Hasil Pengujian Aturan Silver dan Gold

| No | Aturan Validasi | Lingkup | Status | Catatan / Hasil Pemeriksaan |
|:---:|---|:---:|:---:|---|
| 1 | Skema Kolom & Tipe Data Pandera | Silver | ✅ **LOLOS** | Seluruh 11 kolom memenuhi tipe data dan batasan Pandera |
| 2 | Rentang Nilai Prevalensi Wajar (0 - 100%) | Silver | ✅ **LOLOS** | Semua nilai berada dalam rentang [0.0, 100.0] |
| 3 | Konsistensi Satuan Kanonis ('persen') | Silver | ✅ **LOLOS** | Satuan terdeteksi: {'persen'} |
| 4 | Keunikan Kunci Primer Komposit 6 Dimensi | Silver | ✅ **LOLOS** | 0 duplikasi (100% unik) |
| 5 | Keunikan Kombinasi Provinsi x Periode (Panel BPS) | Silver | ✅ **LOLOS** | Tepat satu nilai per provinsi x tahun |
| 6 | Format Periode (4 Digit Tahun Kalender) | Silver | ✅ **LOLOS** | Seluruh periode terformat YYYY (2000-2025) |
| 7 | Validitas Kode Wilayah (9999 / 38 Provinsi) | Silver | ✅ **LOLOS** | Semua kode wilayah sah sesuai standar 38 provinsi & 9999 |
| 8 | Integritas Format SHA-256 Provenans | Silver | ✅ **LOLOS** | Seluruh hash terdiri dari 64 karakter heksadesimal valid |
| 9 | Kelengkapan Data (Non-Null Constraints) | Silver | ✅ **LOLOS** | 0 nilai null/NaN di seluruh 11 kolom |
| 10 | Validitas Sumber Data (Whitelist) | Silver | ✅ **LOLOS** | Semua sumber data resmi (bps, wdi, who_gho) |
| 11 | Kesesuaian Kode Seri Kasus 01 | Silver | ✅ **LOLOS** | Seluruh 7 seri sesuai kasus kerawanan pangan |
| 12 | Ketersediaan Rincian Agregat Pembanding WHO (K-004) | Silver | ✅ **LOLOS** | Tersedia observasi tingkat agregat TOTAL untuk disandingkan dengan BPS di tahap Gold |
| 13 | Keunikan Kunci Panel Provinsi Gold (seri x wilayah x periode) | Gold & Rekon | ✅ **LOLOS** | 0 duplikasi dari 628 baris panel provinsi |
| 14 | Keunikan Kunci Tabel Nasional Gold (sumber x seri x periode) | Gold & Rekon | ✅ **LOLOS** | 0 duplikasi dari 114 baris tabel nasional |
| 15 | Konsistensi Satuan Tunggal per Indikator Gold ('persen') | Gold & Rekon | ✅ **LOLOS** | Seluruh indikator di Gold memiliki tepat 1 satuan terstandarisasi kanonis ('persen') |
| 16 | Keterlacakan Seluruh Sel Gold ke Silver (Traceability Pasangan) | Gold & Rekon | ✅ **LOLOS** | 100% sel panel provinsi dan tabel nasional memiliki pasangan identik di layer Silver |
| 17 | Kategori Sah pada Setiap Baris Rekonsiliasi Berpasangan | Gold & Rekon | ✅ **LOLOS** | Seluruh 18 pasangan rekonsiliasi memiliki kategori definitif valid ({'definisi berbeda', 'metode berbeda'}) |
| 18 | Rentang Nilai Prevalensi Wajar Gold (0 - 100%) | Gold & Rekon | ✅ **LOLOS** | Seluruh nilai numerik pada panel provinsi dan tabel nasional berada dalam rentang [0.0, 100.0] |

---

## Keterangan Pengujian Lapis Gold & Rekonsiliasi (Backlog #25)
1. **Keunikan Kunci Panel:** Panel provinsi (`seri_kode`, `wilayah_kode`, `periode`) dan tabel nasional (`sumber`, `seri_kode`, `periode`) terbukti 100% unik tanpa duplikasi.
2. **Konsistensi Satuan:** Setiap indikator Gold memiliki tepat satu satuan kanonis (`persen`).
3. **Keterlacakan Pasangan (Traceability):** 100% sel data Gold terbukti dapat dilacak secara deterministik ke sel asalnya di lapisan Silver dengan nilai numerik identik.
4. **Kategori Rekonsiliasi:** Seluruh baris berpasangan pada tabel rekonsiliasi memiliki kategori penyebab selisih yang definitif (`definisi berbeda` dan `metode berbeda`) tanpa ada nilai yang kosong atau belum terjelaskan.
