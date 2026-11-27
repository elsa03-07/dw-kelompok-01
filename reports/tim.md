# Laporan tim — Kelompok 1, kasus 01 Kerawanan pangan provinsi

Satu dokumen bersama, enam bagian. Angka harus dapat ditarik ulang dari `data/silver`, `data/gold`,
dan `log-keputusan.csv` yang sudah di-*commit*.

## Ringkasan
Proyek Capstone Data Wrangling Kelompok 1 berfokus pada **Kasus 01: Kerawanan Pangan Provinsi** (Klaster A: Pangan dan Kesehatan, Tujuan SDG 2: Tanpa Kelaparan). Kami mengolah 7 seri data indikator yang mencakup seri utama BPS tingkat provinsi (`var1473` Prevalensi Ketidakcukupan Konsumsi Pangan/PoU dan `var1474` Prevalensi Kerawanan Pangan Sedang/Berat berdasarkan FIES, 2017–2025) serta seri pembanding nasional dari World Bank WDI (`SN.ITK.DEFC.ZS` dan `SN.ITK.MSFI.ZS`, 2001–2024) dan WHO GHO (`NUTSTUNTINGPREV`, `NUTOVERWEIGHTPREV`, dan `NUTRITION_WH_2`, 1996–2024).

Temuan utama terkait kualitas data menunjukkan bahwa setelah standardisasi wilayah 38 provinsi dan koreksi katalog satuan kanonis `persen`, seluruh data mentah memiliki integritas lineage yang tinggi; panel provinsi terbukti lengkap 100% sejak tahun 2024, di mana 28 sel kosong pada periode 2017–2023 merupakan ketiadaan struktural pembentukan 4 Daerah Otonom Baru (DOB) Papua yang dipertahankan secara alami tanpa imputasi buatan, serta seluruh nilai ekstrem (outlier di Maluku dan Papua) mencerminkan kondisi riil kerentanan pangan wilayah kepulauan dan pedalaman yang dipertahankan utuh demi validitas evaluasi SDG nasional.

---

## Data dan lineage
* **Sumber dan Format Mentah:** Data mentah lapis *Bronze* berasal dari snapshot 17–20 Oktober 2026 yang tersusun atas **14 berkas mentah** yang terdaftar di `data/raw/MANIFEST.csv`, terdiri dari:
  * **BPS:** 4 berkas (2 file tabular CSV datar dan 2 file JSON respons WebAPI dinamis berstruktur *nested*).
  * **World Bank (WDI):** 4 berkas JSON larik dua elemen berstruktur metadata halaman dan daftar observasi indikator.
  * **WHO GHO:** 5 berkas (3 berkas CSV disagregasi indikator di folder `datadot` dan 2 berkas JSON kamus metadata di `odata` dan `datadot`).
* **Pembentukan Lineage (`_berkas_raw` dan `_sha256_raw`):**
  Penyematan lineage dilakukan di tahap ekstraksi (`src/ekstraksi/`) pada setiap skrip pembaca (`bps_reader.py`, `wdi_reader.py`, `who_reader.py`) sebelum masuk ke tahap pembersihan atau transformasi:
  * Atribut `_berkas_raw` mencatat jalur relatif berkas sumber terhadap folder `data/raw/` (misalnya: `bps/2026-10-20/sdg8_tpt.csv` atau `who_gho/datadot/NUTRITION_WH_2.csv`).
  * Atribut `_sha256_raw` diambil secara otomatis dan dinamis menggunakan pemanggil fungsi `src.common.manifest.sha256_raw(berkas)`. Nilai hash 64-karakter ini divalidasi langsung terhadap `MANIFEST.csv` tanpa pernah diketik manual, menjamin audit keterlacakan setiap baris observasi hingga ke fisik berkas mentahnya.
* **Hasil Tarik Ulang dan Pembandingan Snapshot:**
  Perbandingan data BPS antara snapshot 17 Oktober dan 20 Oktober 2026 menunjukkan kestabilan angka observasi pada deret waktu historis. Nilai pada snapshot 20 Oktober ditetapkan sebagai angka rilis mutakhir resmi BPS (`K-003`), dan pasangan observasi identik dari dua snapshot di-deduplikasi menjadi satu observasi kanonik di lapisan Silver.
* **Pemilihan Basis Data (SQLite) dan Perbandingan dengan JSON Mentah:**
  * **Alasan memilih SQLite:** Bersifat serverless (berbasis berkas lokal data/capstone.sqlite) tanpa perlu menjalankan server basis data terpisah, mudah direplikasi lewat pipeline Python, dan menjaga repositori tetap ringan karena berkas .sqlite diabaikan di .gitignore
  * **Perbandingan dengan penyimpanan JSON mentah:** Menyimpan respons JSON mentah sebagai dokumen cocok untuk arsip mentah, tetapi kurang efisien untuk menegakkan primary key, tipe data eksplisit, agregasi lintas wilayah/periode, dan kueri rekonsiliasi berulang dibandingkan tabel relasional SQLite.
  * **Kesesuaian kasus:** Dataset Silver dan Gold bersifat tabular dan panel (`silver`, `panel_provinsi`, `tabel_nasional`, `tabel_nasional_lebar`, `rekonsiliasi`) yang sering di-kueri berdasarkan kunci utama dan dimensi waktu/wilayah, sehingga skema relasional lebih sesuai.
  * **Pemuatan dari pipeline (K-019):** tahap `sql` di `pipeline.py` (`src/sql/`) membangun ulang `data/capstone.sqlite` dari Parquet setiap kali pipeline dijalankan, memakai DDL `src/silver/skema_silver.sql` dan `src/gold/skema_gold.sql` (kunci primer dan `CHECK` rentang nilai). Baris dimuat dengan `INSERT` biasa sehingga kunci ganda menggagalkan pemuatan, bukan menimpa baris. Setelah pemuatan, jumlah baris dan jumlah kolom `nilai` setiap tabel dibandingkan dengan Parquet; kelima tabel cocok (1.439 / 628 / 114 / 30 / 36 baris, lihat `reports/ringkasan_pipeline.md`).

---

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

---

## Integrasi dan rekonsiliasi
Integrasi mempertemukan seri utama BPS (provinsi dan nasional) dengan pembanding nasional WDI dan WHO GHO. Semua angka di bagian ini dapat ditarik ulang dari `data/gold/` setelah `python pipeline.py`.

### Pemilihan satu nilai per sel (K-014 s.d. K-017)
Silver menyimpan 1.439 baris, termasuk seluruh subkelompok WHO. `src/gold/aturan_pilih.py` menerapkan aturan secara berurutan, dan dampaknya ditulis otomatis ke `log-keputusan.csv`:

| Keputusan | Aturan | Baris disisihkan |
|---|---|---:|
| K-014 | Snapshot terbaru per sel | 0 |
| K-016 | Periode tahunan murni | 0 |
| K-015 | Rincian sebanding: BPS/WDI `Total`, stunting/overweight `SEX=TOTAL`, wasting `SEX=TOTAL; AGE=TOTAL` | 697 |
| K-017 | Penanda outlier/patahan, tanpa membuang baris | 0 |

Hasilnya 742 baris terpilih (628 panel provinsi + 114 nasional), dan 697 baris subkelompok WHO tetap hanya di Silver. Hasil aturan ini dicocokkan dengan Gold kanonis di `src/gold/builder.py`; bila berbeda, pipeline berhenti.

### Gold kanonis (K-019)
| Tabel | Baris | Isi |
|---|---:|---|
| `panel_provinsi` | 628 | 38 provinsi × 2017–2025 × `var1473`/`var1474`, bentuk panjang, dengan `status_anomali`, `is_outlier` (45), `is_patahan` (24) |
| `tabel_nasional` | 114 | 7 seri nasional berdampingan (BPS 9+9, WDI 24+10, WHO 25+25+12), dengan lineage |
| `tabel_nasional_lebar` | 30 | Tampilan lebar 1996–2025, satu kolom per seri |
| `rekonsiliasi` | 36 | BPS vs WDI per tahun, beserta selisih, kategori, dan penjelasan |

### Rekonsiliasi BPS vs WDI (K-018)
Pasangan ditetapkan dari definisi SDG yang sama: **PoU** `var1473` ↔ `SN.ITK.DEFC.ZS` (2.1.1) dan **FIES** `var1474` ↔ `SN.ITK.MSFI.ZS` (2.1.2). Tahun 2017–2024 berpasangan (16 baris). Tahun yang hanya ada di satu sisi (WDI 2001–2016, dan BPS 2025 yang belum dirilis WDI) tetap ditulis dengan kategori `tanpa pasangan` (20 baris). Selisihnya dijelaskan, tidak dihapus.

| Tahun | BPS PoU | WDI PoU | Selisih | BPS FIES | WDI FIES | Selisih |
|---|---:|---:|---:|---:|---:|---:|
| 2017 | 8,23 | 6,0 | +2,23 | 8,66 | 7,6 | +1,06 |
| 2018 | 7,92 | 6,0 | +1,92 | 6,86 | 7,0 | −0,14 |
| 2019 | 7,63 | 6,4 | +1,23 | 5,42 | 5,8 | −0,38 |
| 2020 | 8,34 | 6,6 | +1,74 | 5,12 | 5,1 | +0,02 |
| 2021 | 8,49 | 6,7 | +1,79 | 4,79 | 4,9 | −0,11 |
| 2022 | 10,21 | 6,6 | +3,61 | 4,85 | 4,7 | +0,15 |
| 2023 | 8,53 | 6,5 | +2,03 | 4,50 | 4,5 | 0,00 |
| 2024 | 8,27 | 6,3 | +1,97 | 4,02 | 4,2 | −0,18 |

* **PoU: metode berbeda.** Angka BPS konsisten lebih tinggi daripada WDI, dengan selisih rata-rata +2,07 poin persen. BPS menghitung langsung dari konsumsi kalori SUSENAS, sedangkan WDI/FAO memakai model distribusi parametrik dengan parameter DEC global yang menghaluskan fluktuasi tahunan. Selisih terbesar terjadi pada 2022 (+3,61), saat angka BPS melonjak ke 10,21 sementara WDI tetap 6,6. Lonjakan ini perlu dicek terhadap catatan rilis SUSENAS 2022 sebelum disimpulkan.
* **FIES: metode berbeda.** Kedua seri berimpit; sejak 2018 selisihnya tidak lebih dari 0,4 poin persen. Satu-satunya selisih besar ada pada 2017 (+1,06). BPS memakai modul FIES SUSENAS dengan kalibrasi nasional, sedangkan WDI/FAO memakai data dan kalibrasi skala global.
* **WHO tidak direkonsiliasi.** Stunting, overweight, dan wasting balita (SDG 2.2) mengukur status gizi anak, bukan akses pangan rumah tangga. Ketiganya disandingkan di `tabel_nasional` sebagai konteks, tetapi selisihnya terhadap PoU/FIES tidak bermakna.
* **Agenda Sprint 3:** dinamika revisi vintage WDI memakai arsip 142 rilis (`python unduh_data.py --arsip-wdi`), untuk menguji apakah sebagian selisih termasuk kategori `vintage berbeda`.

---

## Validasi dan reproduksibilitas
* **Skema Validasi Otomatis (Pandera & Starter):**
  * Seluruh data Silver diverifikasi menggunakan **12 aturan validasi skema otomatis** berbasis Pandera (`src/validasi/`): keunikan kunci komposit 6 dimensi, kelengkapan 11 kolom wajib, validitas numerik dan rentang nilai persentase ($0.0 \le \text{nilai} \le 100.0$), integritas format periode (`^\d{4}$`), konsistensi satuan `persen`, dan kesesuaian sidik SHA-256 terhadap `MANIFEST.csv`. Hasil: **12/12 aturan LOLOS (100%)**.
  * Pemeriksaan skema minimal starter dosen dijalankan dan lolos tanpa catatan:
    ```bash
    python -m src.common.skema data/silver/silver.parquet
    # Output: LOLOS 1,439 baris, 7 seri, 39 wilayah, 6 berkas sumber
    ```
* **Validasi Gold, rekonsiliasi, dan SQL (Sprint 2):** 6 aturan Gold/rekonsiliasi (kunci unik panel dan nasional, satuan tunggal, keterlacakan setiap sel Gold ke Silver, setiap baris rekonsiliasi dijelaskan, rentang 0–100) ditambah 1 aturan SQL (jumlah baris SQL = Parquet). Total **19/19 aturan lolos** (`reports/validasi.md`). Pipeline berhenti bila ada aturan yang gagal.
* **Keterulangan (Reproducibility):**
  * Satu perintah `python pipeline.py` menjalankan ekstraksi → Silver → Gold → SQL → validasi dari data mentah dan menulis `reports/ringkasan_pipeline.md`, yang berisi jumlah baris dan sidik sha256 setiap keluaran. Isinya deterministik.
  * Uji klon bersih (`reports/reproduksi.md`): klon baru, lingkungan Python baru, `unduh_data.py --kasus 1`, lalu `pipeline.py`. Semua keluaran identik dengan yang di-*commit*, dengan waktu jalan sekitar 1 detik.
  * `python -m unittest discover -s tests`: 25 tes lolos.
* **Keterbatasan yang Tersisa:**
  * Pengujian skalabilitas terhadap arsip 142 rilis WDI (tahap 7) dikerjakan pada Sprint 3.
  * Silver dibangun langsung dari berkas data mentah oleh `src/silver/builder.py`; keluaran tahap ekstraksi saat ini menjadi inventaris lineage (semua 14 berkas MANIFEST terbaca), belum menjadi masukan Silver.

---

## Pembagian kerja
Sesuai Kontrak Tim dan pembagian peran di DSWorkbench, berikut adalah kontribusi spesifik setiap anggota kelompok:

| Anggota | NIM | Komponen | Tugas sampingan | Bagian laporan yang ditulis |
|---|---|---|---|---|
| NI MADE OKTA VIOLA DARMA PUTRI | 124450005 | Transformasi dan panel | Penjaga Data & Evaluasi | Verifikasi katalog seri terverifikasi, harmonisasi satuan & periode (K-006 s.d. K-008), dan builder lapisan Silver |
| GH. MIKAEL NIKO ANTONI SETIADI | 124450025 | Integrasi, penyimpanan, dan skala | Analis Utama | Integrasi dan rekonsiliasi awal seri utama BPS vs WDI/WHO, perumusan klasifikasi kategori selisih |
| Raihan Azwar Faqih Wijaya | 124450032 | Reproduksi & Demo | Reproduksi & Demo | Pengujian reproduksibilitas pipeline di lingkungan bersih dan penyiapan skenario demo sprint |
| DAFFA KHARISMA ADZANA | 124450061 | Profil dan pembersihan | Penjaga Data & Evaluasi | Profiling data mentah, deteksi anomali/outlier vs patahan seri (K-002), evaluasi grid kelengkapan & strategi missing (K-005) |
| Elsa Sitorus | 124450088 | Validasi dan dokumentasi | Koordinator | Ringkasan eksekutif, koordinasi sprint & DoD, validasi skema Silver, dan penyusunan kamus data 11 kolom |
| Zannuba Arifah Ilman | 124450112 | Ekstraksi dan lineage | Integrator | Data dan lineage, implementasi pembaca berkas mentah BPS, WDI, WHO GHO, dan orkestrasi fungsi ekstraksi |

