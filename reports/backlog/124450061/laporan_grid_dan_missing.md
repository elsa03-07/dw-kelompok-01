# Laporan Backlog #7: Grid 38 Provinsi × Periode, Kelengkapan Panel, dan Strategi Missing

**Penyusun:** DAFFA KHARISMA ADZANA (124450061)  
**Komponen:** Profil dan Pembersihan (Tahap 3)  
**Tugas Sampingan:** Penjaga Data & Evaluasi  
**Repositori:** Kelompok 1 — Capstone Data Wrangling  
**Tanggal:** 17 November 2026  

---

## 1. Latar Belakang dan Tujuan
Pada data mentah (*Bronze*) maupun tabel *Silver*, data disimpan dalam format *sparse* yang hanya memuat observasi yang memiliki nilai (tidak menyimpan baris kosong atau `NaN`). Akibatnya, ketiadaan data (*data gaps*) tidak tampak sebelum dibentuk kerangka matriks lengkap (*grid*) wilayah $\times$ periode.

Tujuan dari analisis ini adalah:
1. Membentuk grid teoritis lengkap 38 provinsi $\times$ 9 periode (2017 s.d. 2025) untuk seri utama BPS (`var1473` dan `var1474`).
2. Memisahkan baris agregat nasional Indonesia (`wilayah_kode = 9999`) dari panel observasi antarprovinsi.
3. Menghitung dan melaporkan persentase kelengkapan panel per seri per tahun.
4. Menentukan sejak tahun berapa panel dapat dinyatakan lengkap.
5. Membedakan secara metodologis antara *missing value* murni vs *ketiadaan struktural* (*structural absence* akibat pemekaran wilayah).
6. Merumuskan keputusan strategi penanganan *missing value* serta mencatatnya di `log-keputusan.csv`.

---

## 2. Pemisahan Baris Indonesia (`wilayah_kode = 9999`)
Sesuai arahan kasus, agregat nasional Indonesia (`9999`) dipisahkan sejak awal dari panel provinsi:
- **Jumlah baris Indonesia:** 18 baris (9 periode untuk `var1473` dan 9 periode untuk `var1474`).
- **Tingkat kelengkapan nasional:** 100% (tersedia kontinu 2017–2025).
- **Justifikasi pemisahan:** Memasukkan agregat nasional ke dalam panel provinsi akan menimbulkan *double-counting* (karena angka nasional adalah agregasi dari seluruh provinsi) dan mendistorsi perhitungan statistik sebaran (rata-rata, variansi, kuartil, dan deteksi anomali antarwilayah). Baris Indonesia disimpan terpisah sebagai seri pembanding makro.

---

## 3. Pembentukan Grid 38 Provinsi × 9 Periode

### 3.1. Parameter Grid
- **Jumlah Wilayah Standar:** 38 Provinsi (mengikuti susunan resmi wilayah Indonesia pasca pemekaran 2022/2024).
- **Rentang Periode:** 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 (9 tahun).
- **Ukuran Grid Teoritis:** $38 \times 9 = 342$ sel observasi per seri ($684$ sel untuk 2 seri utama).

### 3.2. Tabel Kelengkapan Tahunan per Seri

Berikut adalah matriks hasil evaluasi keterisian grid per tahun untuk seri `var1473` (PoU) dan `var1474` (FIES):

| Seri Kode | Tahun | Total Grid Provinsi | Provinsi Terisi | Sel Kosong | Kelengkapan (%) | Status Kelengkapan |
|---|:---:|:---:|:---:|:---:|:---:|:---|
| `var1473` | 2017 | 38 | 34 | 4 | 89.47% | 34 Provinsi Lama Terisi Penuh |
| `var1473` | 2018 | 38 | 34 | 4 | 89.47% | 34 Provinsi Lama Terisi Penuh |
| `var1473` | 2019 | 38 | 34 | 4 | 89.47% | 34 Provinsi Lama Terisi Penuh |
| `var1473` | 2020 | 38 | 34 | 4 | 89.47% | 34 Provinsi Lama Terisi Penuh |
| `var1473` | 2021 | 38 | 34 | 4 | 89.47% | 34 Provinsi Lama Terisi Penuh |
| `var1473` | 2022 | 38 | 34 | 4 | 89.47% | 34 Provinsi Lama Terisi Penuh |
| `var1473` | 2023 | 38 | 34 | 4 | 89.47% | 34 Provinsi Lama Terisi Penuh |
| `var1473` | 2024 | 38 | 38 | 0 | 100.00% | **Lengkap Penuh (38 Provinsi)** |
| `var1473` | 2025 | 38 | 38 | 0 | 100.00% | **Lengkap Penuh (38 Provinsi)** |
| **Total** | **2017–2025** | **342** | **314** | **28** | **91.81%** | — |

*(Catatan: Seri `var1474` menunjukkan profil distribusi dan persentase kelengkapan yang identik persis).*

---

## 4. Analisis Ketiadaan Data: Mengapa Bukan Missing Value?

Sebanyak **28 sel kosong** per seri (total 56 sel untuk dua seri) berasal secara eksklusif dari 4 provinsi baru hasil pemekaran di wilayah Papua:
1. `9200` — **PAPUA BARAT DAYA** (kosong 2017–2023 = 7 tahun)
2. `9500` — **PAPUA SELATAN** (kosong 2017–2023 = 7 tahun)
3. `9600` — **PAPUA TENGAH** (kosong 2017–2023 = 7 tahun)
4. `9700` — **PAPUA PEGUNUNGAN** (kosong 2017–2023 = 7 tahun)

### Dasar Metodologis:
- Keempat Daerah Otonom Baru (DOB) tersebut secara yuridis dibentuk melalui UU No. 14, 15, 16, dan 29 Tahun 2022 pada akhir semester II tahun 2022.
- Badan Pusat Statistik (BPS) baru pertama kali merilis indikator kerawanan pangan tingkat provinsi untuk 4 DOB ini pada SUSENAS/publikasi tahun **2024**.
- Sebelum tahun 2024, entitas administratif tersebut belum ada dan data populasinya masih terintegrasi di dalam data provinsi induk (`9100` Papua Barat dan `9400` Papua).
- Berdasarkan prinsip panduan capstone: *"Seri yang belum terbit pada tahun awal bukan missing"*. Kondisi ini dikategorikan sebagai **Ketiadaan Struktural (*Structural Absence / Unborn Entity*)**, bukan data hilang karena kelalaian survei (*missing completely at random* / non-respons).

### Penentuan Tahun Panel Lengkap:
- **Tingkat 34 Provinsi Historis:** Panel telah **lengkap 100% sejak tahun 2017** (2017–2023 terisi 34/34 provinsi tanpa ada satu pun nilai bolong).
- **Tingkat 38 Provinsi Standar 2025:** Panel baru dinyatakan **lengkap 100% (*balanced panel*) sejak tahun 2024** (2024 dan 2025 terisi penuh 38/38 provinsi).

---

## 5. Keputusan Strategi Missing dan Alternatif yang Ditolak

Keputusan dicatat secara resmi pada log keputusan proyek (`log-keputusan.csv` ID `K-005`):

1. **Keputusan yang Ditetapkan:**
   - Mempertahankan panel tidak seimbang (*unbalanced panel*) alami.
   - **TIDAK melakukan imputasi angka buatan** pada 28 sel kosong 4 DOB untuk periode 2017–2023.
   - Tabel *Silver* tetap berpegang pada prinsip kebersihan data provenans (tidak menyisipkan baris kosong atau nilai buatan).
   
2. **Alternatif yang Ditolak & Alasannya:**
   - *Alternatif A (Imputasi Statistik: Backcasting / Interpolasi / KNN):*  
     **Ditolak.** Memperkirakan angka kerawanan pangan (PoU/FIES) untuk entitas yang secara administratif belum berdiri adalah halusinasi data (*fabricated data*). Karakteristik geografis pegunungan Papua sangat ekstrem sehingga imputasi berbasis regresi/rata-rata nasional akan menghasilkan estimasi bias yang menyesatkan.
   - *Alternatif B (Menyalin Angka Provinsi Induk Papua/Papua Barat):*  
     **Ditolak.** Kerawanan pangan di Papua Pegunungan atau Papua Tengah secara faktual jauh lebih tinggi daripada kota pelabuhan seperti Jayapura atau Sorong. Memasukkan angka induk ke DOB sebelum 2024 akan mengaburkan disparitas riil.
   - *Alternatif C (Memotong Analisis Menjadi Hanya 34 Provinsi):*  
     **Ditolak.** Menghilangkan 4 DOB pada tahun 2024–2025 berarti membuang informasi berharga mengenai kantong kerawanan pangan tertinggi di Indonesia.

---

## 6. Sinkronisasi Metrik Komponen
Sesuai instruksi deliverable, metrik hasil komponen diperbarui menggunakan modul `src.common.hasil`:
- `baris_silver`: 1,439
- `sel_kosong_grid`: 28 (per seri utama pada grid 38 provinsi)
- `outlier_ditandai`: 45
- `calon_anomali_terdeteksi`: 61
- `patahan_seri`: 16
- `keputusan_dicatat`: 5

Berkas artefak tersimpan di `results/124450061/metrics.json` dan siap dikirim melalui Workbench.
