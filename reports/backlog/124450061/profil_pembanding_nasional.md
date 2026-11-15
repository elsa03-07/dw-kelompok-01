# Profil Seri Pembanding Nasional (5 Seri Pembanding)

**Penyusun:** Daffa Kharisma Adzana (124450061)  
**Komponen:** Profil dan Pembersihan Data (Tahap 2 & 3)  
**Tugas Backlog:** #6 (Prioritas: Sedang, Poin: 2)  
**Kasus:** Kasus 01 — Kerawanan Pangan Provinsi (SDG 2)  
**Tanggal:** 12 November 2026  

---

## 1. Pendahuluan

Sesuai ketentuan kasus tim, seri utama BPS di tingkat provinsi (`var1473` dan `var1474`) harus disandingkan dan direkonsiliasi dengan indikator pembanding nasional dari lembaga internasional pada lapis Bronze:
1. **World Bank (WDI)**: `SN.ITK.DEFC.ZS` dan `SN.ITK.MSFI.ZS`
2. **WHO GHO**: `NUTSTUNTINGPREV`, `NUTOVERWEIGHTPREV`, dan `NUTRITION_WH_2`

Laporan ini memetakan ketersediaan periode, rincian disagregasi (jenis kelamin, kelompok umur, wilayah, status ekonomi), satuan, serta tahun yang beririsan dengan seri utama BPS (2017–2025) guna menentukan rincian kandidat yang sebanding secara metodologis pada Tahap 6 (Integrasi & Rekonsiliasi).

---

## 2. Tabel Ketersediaan Seri Pembanding Nasional

Berkas CSV terstruktur tersimpan di [`reports/profiling/ketersediaan_pembanding_nasional.csv`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/profiling/ketersediaan_pembanding_nasional.csv) dan [`reports/profiling/matriks_ketersediaan_tahunan.csv`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/profiling/matriks_ketersediaan_tahunan.csv).

| Lembaga | Kode Seri | Nama Indikator | Satuan | Rentang Periode | Irisan Thn BPS (2017–2025) | Dimensi Rincian Tersedia | Rincian Kandidat Sebanding |
|---|---|---|---|:---:|:---:|---|---|
| **World Bank (WDI)** | `SN.ITK.DEFC.ZS` | *Prevalence of undernourishment (% of population)* | Persen (%) | 2001–2024 (24 thn) | **2017–2024 (8 tahun)** | Total Nasional | Total Populasi Nasional |
| **World Bank (WDI)** | `SN.ITK.MSFI.ZS` | *Prevalence of moderate or severe food insecurity in the population (%)* | Persen (%) | 2015–2024 (10 thn) | **2017–2024 (8 tahun)** | Total Nasional | Total Populasi Nasional |
| **WHO GHO** | `NUTSTUNTINGPREV` | *Stunting in children (under 5)* | Rate per 100 anak balita (%) | 2000–2024 (25 thn) | **2017–2024 (8 tahun)** | `DIM_SEX` (FEMALE, MALE, TOTAL) | `DIM_SEX = TOTAL` |
| **WHO GHO** | `NUTOVERWEIGHTPREV` | *Overweight in children (under 5)* | Rate per 100 anak balita (%) | 2000–2024 (25 thn) | **2017–2024 (8 tahun)** | `DIM_SEX` (FEMALE, MALE, TOTAL) | `DIM_SEX = TOTAL` |
| **WHO GHO** | `NUTRITION_WH_2` | *Wasting in children (under 5)* | Rate per 100 anak balita (%) | 1996–2023 (12 thn survei) | **2018–2023 (5 tahun)** | Multidimensi (`DIM_SEX`, `DIM_DEG_URB`, `DIM_AGE`, dll.) | `DIM_SEX = TOTAL`, `DIM_DEG_URB = TOTAL`, `DIM_AGE = TOTAL` |

---

## 3. Analisis Pemilihan Rincian yang Sebanding

### 3.1 Seri World Bank (WDI)
- **`SN.ITK.DEFC.ZS`**: Merupakan indikator PoU global yang dihitung oleh FAO/World Bank. Indikator ini langsung sebanding dengan BPS `var1473` (PoU) pada tingkat nasional. Keduanya mengukur persentase populasi yang asupan kalorinya di bawah kebutuhan energi minimum. Beririsan penuh dari 2017 hingga 2024.
- **`SN.ITK.MSFI.ZS`**: Mengukur prevalensi kerawanan pangan sedang atau berat menggunakan metodologi FIES. Indikator ini sebanding langsung dengan BPS `var1474` (FIES) tingkat nasional. Beririsan penuh dari 2017 hingga 2024.

### 3.2 Seri WHO GHO (Nutrisi Balita)
- **`NUTSTUNTINGPREV` & `NUTOVERWEIGHTPREV`**:
  - File mentah menyediakan 3 kategori pada dimensi `DIM_SEX`: `FEMALE` (perempuan), `MALE` (laki-laki), dan `TOTAL` (gabungan).
  - **Rincian Terpilih:** `DIM_SEX = TOTAL`.
  - **Alasan:** Seri utama BPS di tingkat provinsi (`var1473` dan `var1474`) tidak memiliki pemilahan gender balita, melainkan mengukur prevalensi agregat. Oleh karena itu, untuk menjaga konsistensi unit observasi makro, hanya data dengan rincian `TOTAL` yang digunakan sebagai pembanding nasional.
- **`NUTRITION_WH_2` (Wasting Balita)**:
  - Berkas ini memiliki 610 baris dengan 22 kolom yang mencakup kombinasi dimensi rumit (`DIM_POP_WEALTH_DECILE`, `DIM_DEG_URB`, `DIM_AGE`, `DIM_SEX`, dll.).
  - **Rincian Terpilih:** Baris di mana seluruh dimensi filter diset ke `TOTAL` (`DIM_SEX = TOTAL`, `DIM_DEG_URB = TOTAL`, `DIM_AGE = TOTAL`).
  - **Alasan:** Menghindari bias pemilihan sub-kelompok umur (misal hanya anak 0–5 bulan vs 48–59 bulan) atau pemilahan daerah perkotaan saja. Mengambil agregat total nasional memastikan angka prevalensi wasting mencakup seluruh balita Indonesia pada tahun survei terkait.

---

## 4. Rekomendasi untuk Tahap Integrasi (Tahap 6)

1. Pada pembuatan tabel Silver (`silver.parquet`), seluruh observasi yang valid dipertahankan dengan atribut `rincian` yang jelas (misal: `"Total"`, `"Laki-laki"`, `"Perempuan"`).
2. Pada tabel Gold (Tahap 4–6), filtering dilakukan hanya pada rincian terpilih (`TOTAL`) agar selisih angka antara BPS dan WDI/WHO dapat direkonsiliasikan secara adil dan transparan tanpa distorsi perbedaan cakupan populasi.
