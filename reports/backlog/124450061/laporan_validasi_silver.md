# Laporan Validasi Data Silver

**Penyusun:** Tim Kelompok 1 (Pelaksana Komponen Validasi: 124450061)  
**Total Baris Silver:** 1,439  
**Jumlah Aturan Diuji:** 12  
**Jumlah Aturan Lolos:** 12  
**Status Evaluasi:** SELURUH ATURAN LOLOS

---

## Tabel Hasil Pengujian Aturan Dasar

| No | Aturan Validasi | Status | Catatan / Hasil Pemeriksaan |
|:---:|---|:---:|---|
| 1 | Skema Kolom & Tipe Data Pandera | ✅ **LOLOS** | Seluruh 11 kolom memenuhi tipe data dan batasan Pandera |
| 2 | Rentang Nilai Prevalensi Wajar (0 - 100%) | ✅ **LOLOS** | Semua nilai berada dalam rentang [0.0, 100.0] |
| 3 | Konsistensi Satuan Kanonis ('persen') | ✅ **LOLOS** | Satuan terdeteksi: {'persen'} |
| 4 | Keunikan Kunci Primer Komposit 6 Dimensi | ✅ **LOLOS** | 0 duplikasi (100% unik) |
| 5 | Keunikan Kombinasi Provinsi x Periode (Panel BPS) | ✅ **LOLOS** | Tepat satu nilai per provinsi x tahun |
| 6 | Format Periode (4 Digit Tahun Kalender) | ✅ **LOLOS** | Seluruh periode terformat YYYY (2000-2025) |
| 7 | Validitas Kode Wilayah (9999 / 38 Provinsi) | ✅ **LOLOS** | Semua kode wilayah sah sesuai standar 38 provinsi & 9999 |
| 8 | Integritas Format SHA-256 Provenans | ✅ **LOLOS** | Seluruh hash terdiri dari 64 karakter heksadesimal valid |
| 9 | Kelengkapan Data (Non-Null Constraints) | ✅ **LOLOS** | 0 nilai null/NaN di seluruh 11 kolom |
| 10 | Validitas Sumber Data (Whitelist) | ✅ **LOLOS** | Semua sumber data resmi (bps, wdi, who_gho) |
| 11 | Kesesuaian Kode Seri Kasus 01 | ✅ **LOLOS** | Seluruh 7 seri sesuai kasus kerawanan pangan |
| 12 | Ketersediaan Rincian Agregat Pembanding WHO (K-004) | ✅ **LOLOS** | Tersedia observasi tingkat agregat TOTAL untuk disandingkan dengan BPS di tahap Gold |

---

## Keterangan Pengujian Lapis Gold

- **Status Gold:** Tersedia (5 tabel)
- Rincian pembanding nasional WHO yang sebanding (DIM_SEX=TOTAL, DIM_AGE=TOTAL) telah diverifikasi tersedia di layer Silver sesuai aturan keputusan **K-004**.
