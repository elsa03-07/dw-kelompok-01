# Laporan tim — Kelompok 1, kasus 01 Kerawanan pangan provinsi

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan
Kasus, seri yang ditangani, dan satu kalimat temuan utama tentang kualitas datanya.

## Data dan lineage
Sumber dan format mentah, jumlah berkas, cara `_berkas_raw`/`_sha256_raw` dibentuk, dan hasil tarik
ulang API (bila dilakukan): apa yang berubah sejak snapshot 17–20 Oktober 2026.

## Masalah data dan penanganannya

Berdasarkan proses audit data mentah, profiling statistik deskriptif, dan penyusunan tabel Silver (`1.439` baris), berikut adalah ringkasan masalah data yang teridentifikasi beserta keputusan penanganannya yang telah disahkan di `log-keputusan.csv` (K-001 s.d. K-010).

### 1. Tabel Rekapitulasi Masalah Data

| No | Tipe Masalah | Seri Terdampak | Baris Terdampak | ID Log | Keputusan Wrangling | Alternatif yang Ditolak |
|---|---|---|:---:|:---:|---|---|
| 1 | Standardisasi Wilayah | `var1473`, `var1474` | 38 | K-001 | Memetakan nama wilayah BPS ke kode numerik dua digit $\times 100$ (susunan 38 provinsi tahun 2025). | Mempertahankan penulisan nama lama BPS yang variatif. |
| 2 | Outlier & Patahan Seri | `var1473`, `var1474` | 0 | K-002 | Mempertahankan nilai ekstrem Maluku & Papua sebagai outlier asli; menandai patahan pemekaran DOB 2024 tanpa menghapus baris. | Menghapus baris outlier atau melakukan winsorizing/imputasi nilai ekstrem. |
| 3 | Multi-snapshot Vintage | Semua seri (BPS, WDI, WHO) | 0 | K-003 | Deduplikasi multi-snapshot: pasangan identik disimpan sekali; angka berbeda pada snapshot 20 Oktober ditetapkan sebagai revisi resmi produsen. | Menyimpan data snapshot ganda sebagai baris duplikat di Silver. |
| 4 | Granularitas Rincian | Seri WHO GHO (`NUTSTUNTINGPREV`, `NUTOVERWEIGHTPREV`, `NUTRITION_WH_2`) | 574 (di Gold) | K-004 & K-010 | Mempertahankan seluruh 73 rincian WHO di Silver; penyaringan 574 baris ke agregat total balita (`DIM_SEX/AGE/DEG_URB=TOTAL`) diterapkan pada Gold. | Memotong/memfilter rincian langsung di Silver. |
| 5 | Celah Panel & Missing | `var1473`, `var1474` | 0 | K-005 | Mempertahankan panel tidak seimbang alami tanpa imputasi angka buatan pada 28 sel kosong 4 DOB Papua (2017–2023); memisahkan 18 baris agregat nasional (`9999`). | Melakukan imputasi buatan (backcasting/interpolasi) atau memotong panel menjadi 34 provinsi. |
| 6 | Anomali Satuan Katalog | WDI (`SN.ITK.DEFC.ZS`, `SN.ITK.MSFI.ZS`) | 0 | K-006 | Menetapkan satuan kanonis `persen` untuk 7 seri; satuan WDI yang kosong diisi dari judul indikator (*Percentage of population*). | Membiarkan satuan kosong (`tidak_ada`) atau menebak dari besaran angka. |
| 7 | Kode SDG Tidak Lengkap | WDI (`SN.ITK.DEFC.ZS`, `SN.ITK.MSFI.ZS`) | 0 | K-007 | Melengkapi kode SDG WDI: `SN.ITK.DEFC.ZS` = 2.1.1 (PoU) dan `SN.ITK.MSFI.ZS` = 2.1.2 (FIES). | Membiarkan kode SDG kosong (`—`). |
| 8 | Granularitas Periode | Seluruh 7 seri | 0 | K-008 | Mempertahankan granularitas periode mentah tahunan; menolak agregasi rata-rata buatan non-tahunan. | Merata-ratakan periode non-tahunan menjadi tahunan. |
| 9 | Duplikasi Kunci Nilai Beda | `NUTRITION_WH_2` (2008) | 1 | K-009 | Menahan sementara baris 15,7 dan mempertahankan baris 16,3 pada dimensi kunci kembar WHO 2008 agar kunci primer Silver unik. | Mengubah label secara inferensi atau melakukan `keep='last'` tanpa audit. |

---

### 2. Temuan Terpenting dan Analisis Penanganan

#### A. Celah Panel: Ketiadaan Struktural vs Missing Murni (K-005)
* **Kerangka Grid:** Pembentukan grid teoritis 38 provinsi $\times$ 9 periode (2017–2025) menghasilkan ukuran 342 sel observasi per seri utama BPS (total 684 sel untuk `var1473` dan `var1474`).
* **Keterisian Panel:**
  * Periode **2017–2023** memiliki tingkat kelengkapan **89,47%** (34 dari 38 provinsi terisi penuh 100% tanpa ada satu pun nilai kosong pada provinsi lama).
  * Periode **2024–2025** memiliki tingkat kelengkapan **100,00%** (*balanced panel* penuh 38 provinsi).
* **Identifikasi 28 Sel Kosong:** Seluruh 28 sel kosong per seri (total 56 sel) terlokalisasi secara eksklusif pada 4 Daerah Otonom Baru (DOB) di Papua: Papua Barat Daya (`9200`), Papua Selatan (`9500`), Papua Tengah (`9600`), dan Papua Pegunungan (`9700`) selama periode 2017–2023 (7 tahun).
* **Penetapan Status:** Ketiadaan data ini diklasifikasikan sebagai **ketiadaan struktural (*structural absence*)**, bukan *missing value* akibat kelalaian survei, karena entitas administratif 4 DOB baru dibentuk secara legal pada akhir 2022 (UU No. 14, 15, 16, 29 Tahun 2022) dan data statistiknya baru diterbitkan resmi oleh BPS pada publikasi tahun 2024. Panel resmi dinyatakan lengkap sejak tahun **2024**.
* **Strategi Penanganan:** Sesuai K-005, tim menolak imputasi buatan (interpolasi/KNN/backcasting) karena karakteristik geografis pegunungan Papua yang sangat spesifik akan menghasilkan halusinasi data yang menyesatkan. Data dibiarkan berstatus panel tidak seimbang alami. Baris agregat nasional Indonesia (`9999`, 18 baris) dipisahkan agar tidak menimbulkan bias pembobotan atau *double-counting*.

#### B. Klasifikasi Anomali: Outlier Asli vs Patahan Seri (K-002)
* Dari deteksi statistik (metode IQR dengan ambang $1.5 \times \text{IQR}$ dan *z-score*), ditemukan **61 calon anomali** pada seri utama. Melalui penelusuran kontekstual, anomali tersebut dipisahkan menjadi dua kategori:
  1. **Outlier Asli (45 observasi):** Terkonsentrasi pada provinsi kepulauan (Maluku) dan wilayah pedalaman Papua dengan angka prevalensi ketidakcukupan konsumsi pangan jauh melampaui rata-rata nasional. Data ini dipertahankan utuh karena mencerminkan realitas kerentanan pangan dan beban logistik riil wilayah terluar.
  2. **Patahan Seri (16 observasi):** Terjadi loncatan nilai serentak pada tahun 2024 pada provinsi induk Papua (`9100` Papua Barat dan `9400` Papua). Penurunan/loncatan drastis ini bukan perubahan performa program pangan, melainkan akibat pemisahan 4 DOB baru dari wilayah induk. Nilai ditandai (*flagged*) sebagai patahan pemekaran administratif tanpa mengubah angka aslinya.

#### C. Deduplikasi Multi-Snapshot dan Vintage Data (K-003, K-009)
* Data mentah BPS menyertakan snapshot 17 Oktober dan 20 Oktober 2026. Pemeriksaan sidik hash dan kesamaan nilai menunjukkan bahwa observasi identik dipertahankan satu kali. Apabila terdapat revisi angka resmi antar-snapshot, angka pada snapshot 20 Oktober diperlakukan sebagai angka rilis termutakhir.
* Pada seri `NUTRITION_WH_2` (WHO GHO 2008), ditemukan kasus khusus dua baris mentah dengan kunci identik (`DIM_SEX=MALE`, `DIM_AGE=MONTHS24-35`) namun memiliki nilai berbeda (15,7 vs 16,3). Untuk menjamin integritas keunikan kunci Silver, baris 15,7 ditahan sementara (dampak 1 baris) dengan catatan transparan, menunggu konfirmasi metadata lebih lanjut.

#### D. Harmonisasi Katalog, Satuan, dan Metadata (K-006, K-007, K-008, K-010)
* **Koreksi Satuan (K-006):** Seluruh 7 seri indikator Kasus 01 diseragamkan ke satuan kanonis **`persen`**. Indikator WDI (`SN.ITK.DEFC.ZS` dan `SN.ITK.MSFI.ZS`) yang berstatus satuan kosong di katalog awal berhasil dikoreksi menjadi persen berdasarkan teks judul indikator (*Percentage of population*), dengan seluruh observasi berada pada rentang valid $0.0 \le \text{nilai} \le 100.0$.
* **Pelengkapan Kode SDG (K-007):** Melengkapi kode SDG WDI yang awalnya kosong (`—`) menjadi **2.1.1** untuk PoU (`SN.ITK.DEFC.ZS`) dan **2.1.2** untuk FIES (`SN.ITK.MSFI.ZS`).
* **Granularitas Periode (K-008):** Terverifikasi bahwa ketujuh seri merupakan data tahunan murni (regex `^\d{4}$`), sehingga tidak dilakukan agregasi atau perataan buatan dari data bulanan/semesteran.
* **Preservasi Rincian Silver (K-010):** Lapisan Silver mempertahankan seluruh **73 rincian** dimensi WHO GHO untuk menjaga keterlacakan data mentah secara maksimal; penyaringan ke agregat total balita (K-004, dampak 574 baris) didelegasikan sepenuhnya ke lapisan Gold.

## Integrasi dan rekonsiliasi
Seri utama vs pembanding nasional: selisih, penjelasannya (definisi, metode, vintage, granularitas),
dan hasil analisis revisi dari arsip WDI.

## Validasi dan reproduksibilitas
Skema validasi (aturan, hasil lolos/gagal), waktu `python pipeline.py` dari nol, perbandingan pandas
vs DuckDB/Dask, dan keterbatasan yang tersisa.

## Pembagian kerja
| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
