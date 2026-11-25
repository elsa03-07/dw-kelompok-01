# Laporan Profil dan Deteksi Calon Anomali Seri Utama (var1473 & var1474)

**Penyusun:** Daffa Kharisma Adzana (124450061)  
**Komponen:** Profil dan Pembersihan Data (Tahap 2 & 3)  
**Tugas Backlog:** #5 (Prioritas: Tinggi, Poin: 3)  
**Kasus:** Kasus 01 — Kerawanan Pangan Provinsi (SDG 2)  
**Tanggal:** 12 November 2026  

---

## 1. Pendahuluan dan Tujuan

Tujuan dari analisis ini adalah melakukan perhitungan statistik deskriptif menyeluruh per seri dan per provinsi untuk seri utama BPS:
1. **`var1473`**: Prevalensi Ketidakcukupan Konsumsi Pangan (*Prevalence of Undernourishment* / PoU), SDG 2.1.1 (2017–2025).
2. **`var1474`**: Prevalensi Kerawanan Pangan Sedang atau Berat Berdasarkan Skala Pengalaman (*Food Insecurity Experience Scale* / FIES), SDG 2.1.2 (2017–2025).

Analisis ini bertujuan **menemukan dan memetakan calon anomali**, bukan langsung memperbaikinya/menghapusnya, menggunakan metode statistika formal (*Interquartile Range* / IQR dan *Z-score*), serta memvisualisasikan sebaran nilai dan deret waktunya.

---

## 2. Statistik Deskriptif Global dan Tahunan

Data mentah BPS mencakup 323 baris untuk masing-masing seri, yang terdiri dari 34 provinsi (2017–2023), 38 provinsi (2024–2025 setelah pemekaran 4 Daerah Otonom Baru di Papua), dan 1 baris agregat nasional (`wilayah_kode` = 9999 / `INDONESIA`).

### 2.1 Ringkasan Statistik Global Tingkat Provinsi (N = 314 observasi)

| Metrik Statistik | var1473 (PoU) | var1474 (FIES) |
|---|---:|---:|
| **Mean** | 11.58% | 6.54% |
| **Standar Deviasi (Std)** | 8.42% | 3.65% |
| **Minimum** | 1.43% (DKI Jakarta, 2019) | 0.76% (Kep. Bangka Belitung, 2024) |
| **Kuartil 1 (Q1)** | 6.76% | 3.85% |
| **Median (Q2)** | 9.23% | 5.57% |
| **Kuartil 3 (Q3)** | 12.70% | 8.53% |
| **Maksimum** | 38.35% (Papua, 2018) | 27.54% (NTT, 2017) |
| **Rentang Interkuartil (IQR)** | 5.94% | 4.68% |
| **Batas Atas Pencilan Global ($Q3 + 1.5 \times IQR$)** | 21.61% | 15.55% |

### 2.2 Tabel Statistik Deskriptif Per Tahun

Berkas lengkap tersimpan di [`reports/profiling/statistik_deskriptif_tahunan.csv`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/profiling/statistik_deskriptif_tahunan.csv).

| Seri | Tahun | N Prov | Mean (%) | Std (%) | Median (%) | Min (%) | Max (%) | Batas Atas IQR (%) |
|---|:---:|:---:|---:|---:|---:|---:|---:|---:|
| **var1473** | 2017 | 34 | 10.78 | 8.31 | 8.78 | 1.80 | 34.27 | 20.62 |
| **var1473** | 2018 | 34 | 10.72 | 8.65 | 8.71 | 1.46 | 38.35 | 19.24 |
| **var1473** | 2019 | 34 | 10.23 | 9.13 | 7.82 | 1.43 | 38.21 | 17.57 |
| **var1473** | 2020 | 34 | 11.02 | 8.55 | 9.16 | 1.94 | 35.55 | 19.23 |
| **var1473** | 2021 | 34 | 11.32 | 8.03 | 9.72 | 1.78 | 37.37 | 20.18 |
| **var1473** | 2022 | 34 | 13.68 | 8.32 | 12.03 | 2.24 | 36.18 | 27.90 |
| **var1473** | 2023 | 34 | 11.49 | 7.81 | 9.40 | 2.17 | 35.63 | 21.53 |
| **var1473** | 2024 | 38 | 12.56 | 8.87 | 9.70 | 2.55 | 37.69 | 25.23 |
| **var1473** | 2025 | 38 | 12.20 | 8.41 | 9.30 | 2.67 | 32.30 | 25.02 |
| **var1474** | 2017 | 34 | 10.02 | 4.56 | 9.10 | 3.97 | 27.54 | 17.95 |
| **var1474** | 2018 | 34 | 8.45 | 3.96 | 7.40 | 3.14 | 21.32 | 15.69 |
| **var1474** | 2019 | 34 | 6.88 | 3.05 | 6.36 | 2.68 | 14.99 | 14.48 |
| **var1474** | 2020 | 34 | 6.15 | 3.07 | 5.62 | 1.84 | 15.46 | 12.03 |
| **var1474** | 2021 | 34 | 6.04 | 2.73 | 5.26 | 2.87 | 15.31 | 12.74 |
| **var1474** | 2022 | 34 | 5.61 | 2.68 | 5.11 | 2.16 | 14.48 | 10.74 |
| **var1474** | 2023 | 34 | 5.43 | 2.88 | 4.64 | 2.17 | 14.68 | 9.93 |
| **var1474** | 2024 | 38 | 5.35 | 3.78 | 4.14 | 0.76 | 18.13 | 12.85 |
| **var1474** | 2025 | 38 | 5.21 | 2.97 | 4.52 | 1.28 | 13.69 | 11.51 |

---

## 3. Visualisasi Sebaran dan Deret Waktu

Semua gambar visualisasi beresolusi tinggi telah dihasilkan dan disimpan di folder [`reports/gambar/`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/gambar/):

### 3.1 Boxplot Sebaran Tahunan
- [`boxplot_var1473_tahunan.png`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/gambar/boxplot_var1473_tahunan.png): Menunjukkan bahwa nilai pencilan atas (*outlier*) pada `var1473` bersifat persisten di setiap tahun pengamatan ($> 20\%$), yang terkonsentrasi pada wilayah Indonesia Timur.
- [`boxplot_var1474_tahunan.png`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/gambar/boxplot_var1474_tahunan.png): Memperlihatkan kecenderungan median yang terus menurun secara bertahap dari tahun 2017 ($9.10\%$) hingga 2025 ($4.52\%$), dengan dispersi antardaerah yang semakin menyempit.

### 3.2 Tren Deret Waktu Agregat Nasional vs Rerata Provinsi
- [`deret_waktu_tren_nasional_vs_provinsi.png`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/gambar/deret_waktu_tren_nasional_vs_provinsi.png): Menunjukkan bahwa garis nasional `INDONESIA` (9999) selalu berada di bawah garis rerata provinsi sederhana. Hal ini logis secara demografi karena angka nasional BPS adalah rata-rata tertimbang (*weighted average*) berbasis jumlah penduduk, di mana provinsi-provinsi padat penduduk di Pulau Jawa memiliki tingkat kerawanan pangan yang relatif rendah.

### 3.3 Deret Waktu Wilayah Ekstrem vs Terendah
- [`deret_waktu_provinsi_ekstrem_var1473.png`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/gambar/deret_waktu_provinsi_ekstrem_var1473.png): Menggambarkan disparitas yang mencolok antara Papua, Maluku, dan Maluku Utara ($> 30\%$) dibandingkan DKI Jakarta dan Bali ($< 3\%$).
- [`deret_waktu_provinsi_ekstrem_var1474.png`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/gambar/deret_waktu_provinsi_ekstrem_var1474.png): Menggambarkan lonjakan NTT ($27.54\%$) dan Gorontalo ($19.36\%$) pada tahun awal 2017 sebelum mengalami normalisasi.

---

## 4. Daftar Calon Anomali dan Alasan Penandaan

Dari kriteria deteksi ($Nilai > Q3 + 1.5 \times IQR$ tahunan atau $|Z| \ge 2.0$), ditemukan total **61 observasi calon anomali** (tersimpan di [`reports/profiling/daftar_calon_anomali_seri_utama.csv`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/profiling/daftar_calon_anomali_seri_utama.csv)).

Beberapa temuan paling signifikan:
1. **Papua (9400) pada var1473**:
   - 2017–2023: Konsisten menjadi pencilan tertinggi nasional ($34.27\% - 38.35\%$, $z > 2.7$).
   - 2024–2025: Mengalami penurunan drastis ke $26.03\%$ (2024) dan $26.11\%$ (2025). Penurunan ini bukan perbaikan mendadak kondisi pangan, melainkan pelepasan 4 provinsi pemekaran baru (DOB) yang memisahkan wilayah dataran tinggi dengan kerawanan ekstrem.
2. **Provinsi Pemekaran Baru Papua (2024–2025)**:
   - Papua Tengah (9600): $37.69\%$ (2024) dan $32.30\%$ (2025) — langsung menjadi pencilan tertinggi baru.
   - Papua Pegunungan (9700): $27.26\%$ (2024) dan $28.72\%$ (2025).
   - Papua Selatan (9500): $29.26\%$ (2024) pada var1473 dan $18.13\%$ pada var1474.
3. **Maluku (8100) dan Maluku Utara (8200)**:
   - Konsisten berada di atas batas $30\%$ sepanjang 9 tahun pengamatan pada var1473.
4. **Nusa Tenggara Timur (5300) pada var1474**:
   - Nilai $27.54\%$ (2017) dan $21.32\%$ (2018) dengan $z = 3.84$.

---

## 5. Kesimpulan Tahap Profiling (DoD Terpenuhi)

1. Ringkasan statistik deskriptif telah tersimpan di repository.
2. Seluruh calon anomali terdaftar lengkap beserta alasan penandaannya.
3. Visualisasi boxplot dan deret waktu telah tersedia di [`reports/gambar/`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/gambar/).
4. Temuan ini menjadi dasar perlakuan pada Tahap 3 (pembersihan dan pemisahan outlier vs patahan seri).
