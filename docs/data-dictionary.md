# Data Dictionary — Kelompok 01, Kasus 01

Dokumentasi struktur data pada setiap keluaran pipeline Data Wrangling. Tipe data, satuan, rentang, dan jumlah nilai kosong didasarkan pada hasil pengolahan data.

## Katalog Seri Terverifikasi

Satuan kanonis untuk tujuh seri Kasus 01 adalah `persen`. Kode SDG, periode, serta berkas dan field mentah yang menjadi sumber bukti tercatat di `reports/backlog/124450005/katalog_seri_terverifikasi.csv`.

| Sumber | Seri | Kode SDG | Satuan | Periode | Catatan |
|---|---|---|---|---|---|
| bps | var1473 | 2.1.1 | persen | tahun | katalog awal cocok |
| bps | var1474 | 2.1.2 | persen | tahun | katalog awal cocok |
| wdi | SN.ITK.DEFC.ZS | 2.1.1 | persen | tahun | satuan dan kode SDG dikoreksi |
| wdi | SN.ITK.MSFI.ZS | 2.1.2 | persen | tahun | satuan dan kode SDG dikoreksi |
| who_gho | NUTSTUNTINGPREV | 2.2.1 | persen | tahun | katalog awal cocok |
| who_gho | NUTOVERWEIGHTPREV | 2.2.2 | persen | tahun | katalog awal cocok |
| who_gho | NUTRITION_WH_2 | 2.2.2 | persen | tahun | katalog awal cocok |

Tidak ada seri dengan periode semesteran atau bulanan. Silver tidak merata-ratakan periode non-tahunan menjadi tahunan.

---

## 1. `data/silver/silver.parquet`

Tabel Silver menyimpan observasi tervalidasi dari seluruh sumber data dengan skema minimal 11 kolom wajib. Total baris: 1.439, mencakup 7 seri indikator dan 39 entitas wilayah (38 provinsi + 1 nasional).

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | bps, wdi, who_gho | nama folder di data/raw/ | Identitas produsen/lembaga penerbit data |
| seri_kode | string | — | tidak | var1473, var1474, SN.ITK.DEFC.ZS, SN.ITK.MSFI.ZS, NUTSTUNTINGPREV, NUTOVERWEIGHTPREV, NUTRITION_WH_2 | katalog data mentah | Kode unik seri indikator |
| wilayah_kode | integer | kode BPS x 100 | tidak | 9999 (Indonesia) atau 1100–9600 (38 provinsi) | Keputusan K-001 | Standar kodefikasi wilayah BPS 2025 |
| nama_wilayah | string | teks baku | tidak | Nama resmi 38 provinsi atau Indonesia | Keputusan K-001 | Nama wilayah terstandar |
| periode | string | YYYY (regex ^\d{4}$) | tidak | 1996 s.d. 2025 | Keputusan K-008 | Periode observasi tahunan |
| jenis_periode | string | kategori | tidak | tahun | Keputusan K-008 | Granularitas periode terverifikasi tahunan |
| rincian | string | teks dimensi | tidak | total atau gabungan dimensi DIM_* | Keputusan K-010 | Disagregasi rincian (gender, usia, wilayah) |
| nilai | float | numerik persen | tidak | 0.0 s.d. 100.0 | data mentah | Nilai observasi indikator kerawanan pangan dan gizi |
| satuan | string | teks | tidak | persen | Keputusan K-006 | Satuan kanonis terverifikasi |
| _berkas_raw | string | jalur relatif | tidak | jalur di bawah data/raw/ | fungsi ekstraksi | Jalur berkas mentah asal untuk audit lineage |
| _sha256_raw | string | 64-karakter hex | tidak | sha256 valid di MANIFEST.csv | src.common.manifest | Sidik hash integritas berkas mentah sumber |

---

## 2. `data/gold/panel_provinsi.parquet`

Panel long observasi BPS tingkat provinsi: 628 baris (314 `var1473` + 314 `var1474`).

Kunci unik: `(seri_kode, wilayah_kode, periode)`. Wilayah `9999` tidak ada karena agregat nasional dipisahkan ke tabel nasional.

Tidak ada nilai kosong pada observasi yang tersedia. Rentang nilai: `var1473` 1,43–38,35 dan `var1474` 0,76–27,54.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | bps | Silver | sumber seri utama |
| seri_kode | string | — | tidak | var1473, var1474 | Silver | indikator panel |
| nama_indikator | string | — | tidak | PoU, FIES | katalog terverifikasi | nama indikator |
| kode_sdg | string | — | tidak | 2.1.1, 2.1.2 | katalog terverifikasi | kode SDG |
| wilayah_kode | int64 | kode BPS × 100 | tidak | 1100–9700 | Silver | 38 provinsi; 9999 tidak termasuk |
| nama_wilayah | string | — | tidak | nama provinsi | Silver | nama wilayah |
| periode | string | tahun | tidak | 2017–2025 | Silver | periode tahunan |
| jenis_periode | string | — | tidak | tahun | Silver | seluruh periode tahunan |
| rincian | string | — | tidak | Total | Silver | rincian observasi BPS |
| nilai | float64 | persen | tidak | 0–100 | Silver | nilai asli; tidak dinormalisasi |
| satuan | string | — | tidak | persen | katalog K-006 | satuan kanonis |
| _berkas_raw | string | jalur relatif | tidak | bps/... | Silver | lineage berkas mentah |
| _sha256_raw | string | sha256 | tidak | 64 heksadesimal | MANIFEST.csv | lineage berkas mentah |

Grid teoritis 38 provinsi × 9 periode = 342 sel per seri. Terisi 314 dan kosong 28 per seri. Sebanyak 56 sel kosong berasal dari 4 DOB Papua periode 2017–2023 dan **tidak diimputasi** (K-005, K-011).

Oleh karena itu, tabel ini merupakan panel tidak seimbang alami, bukan grid lengkap berisi NaN.

---

## 3. `data/gold/tabel_nasional.parquet`

Tabel nasional kanonis long: 114 baris dari 7 seri, dengan lineage dan metadata perbandingan.

Kunci unik: `(sumber, seri_kode, periode)`. Seluruh nilai memakai satuan persen dan tidak ada nilai kosong. Tabel ini merupakan sumber kebenaran untuk tabel nasional; view lebar diturunkan darinya.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | bps, wdi, who_gho | Silver | sumber seri |
| seri_kode | string | — | tidak | 7 seri Kasus 01 | Silver | kode seri |
| nama_indikator | string | — | tidak | nama resmi | katalog terverifikasi | definisi ringkas |
| kode_sdg | string | — | tidak | 2.1.1, 2.1.2, 2.2.1, 2.2.2 | katalog terverifikasi | kode SDG |
| kelompok_indikator | string | — | tidak | seri_utama_bps, pembanding_wdi, pembanding_who | Gold | pengelompokan peran |
| wilayah_kode | int64 | kode BPS × 100 | tidak | 9999 | Silver | agregat Indonesia |
| nama_wilayah | string | — | tidak | INDONESIA | Silver | nama wilayah |
| periode | string | tahun | tidak | 1996–2025 | Silver | tahun observasi |
| jenis_periode | string | — | tidak | tahun | Silver | seluruh periode tahunan |
| rincian | string | — | tidak | Total, SEX=TOTAL, SEX=TOTAL; AGE=TOTAL | Silver | rincian terpilih |
| nilai | float64 | persen | tidak | 0–100 | Silver | nilai asli; tidak dinormalisasi |
| satuan | string | — | tidak | persen | katalog K-006 | satuan kanonis |
| dapat_dibandingkan_dengan | string | — | tidak | teks | Gold | hubungan indikator, bukan penyetaraan |
| catatan_perbandingan | string | — | tidak | teks | Gold | alasan perbedaan definisi/metode |
| _berkas_raw | string | jalur relatif | tidak | bps/..., wdi/..., who_gho/... | Silver | lineage berkas mentah |
| _sha256_raw | string | sha256 | tidak | 64 heksadesimal | MANIFEST.csv | lineage berkas mentah |

Jumlah per seri:

- `var1473`: 9
- `var1474`: 9
- `SN.ITK.DEFC.ZS`: 24
- `SN.ITK.MSFI.ZS`: 10
- `NUTSTUNTINGPREV`: 25
- `NUTOVERWEIGHTPREV`: 25
- `NUTRITION_WH_2`: 12

Rincian WHO yang dipilih adalah `SEX=TOTAL` untuk stunting/overweight dan `SEX=TOTAL; AGE=TOTAL` untuk wasting (K-012).

BPS PoU/FIES tidak dianggap setara dengan indikator WHO. WDI diposisikan sebagai pembanding, bukan pengganti BPS.

---

## 4. `data/gold/tabel_nasional_lebar.parquet`

View lebar untuk menampilkan seri nasional secara berdampingan: 30 baris tahun 1996–2025.

Tabel ini **diturunkan** dari `tabel_nasional.parquet`; lineage per sel dilacak melalui join `(periode, seri_kode)` ke tabel long.

Tahun 1997–1999 tidak memiliki observasi pada ketujuh seri sehingga ketiga baris tersebut kosong (tidak diimputasi). Total sel terisi = 114.

| Kolom | Tipe | Satuan | Boleh kosong | Rentang | Seri asal |
|---|---|---|---|---|---|
| periode | string | tahun | tidak | 1996–2025 | — |
| bps_var1473 | float64 | persen | ya | 7,63–10,21 | var1473 |
| bps_var1474 | float64 | persen | ya | 4,00–8,66 | var1474 |
| wdi_defc | float64 | persen | ya | 6,00–18,40 | SN.ITK.DEFC.ZS |
| wdi_msfi | float64 | persen | ya | 4,20–7,60 | SN.ITK.MSFI.ZS |
| who_stunting | float64 | persen | ya | 22,60–39,80 | NUTSTUNTINGPREV |
| who_overweight | float64 | persen | ya | 2,60–8,50 | NUTOVERWEIGHTPREV |
| who_wasting | float64 | persen | ya | 5,40–14,90 | NUTRITION_WH_2 |

Nilai kosong pada view lebar berarti seri tidak menerbitkan observasi pada tahun tersebut, bukan nol dan bukan hasil imputasi. Untuk analisis, gunakan tabel long agar metadata dan lineage tetap tersedia.

---

## 5. `data/gold/panel_provinsi_anomali.parquet`

Keluaran analisis anomali tingkat provinsi dari proses Gold Sprint 1. Tabel ini menggunakan format wide dan menyandingkan kedua seri utama BPS per provinsi per tahun, dilengkapi penanda diagnostik anomali dan patahan seri.

Dimensi: 314 baris × 9 kolom.

**Catatan:** Keluaran ini merupakan panel analisis anomali terpisah dan bukan pengganti `panel_provinsi.parquet` kanonis Sprint 2.

| Kolom | Tipe data | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/keputusan log) | Keterangan |
|---|---|---|---|---|---|---|
| wilayah_kode | int | 4-digit numerik | tidak | 1100 s.d. 9700 (38 provinsi BPS) | Keputusan K-001 | Kode provinsi BPS (kode 2-digit × 100) |
| nama_wilayah | string | teks huruf kapital | tidak | Nama resmi 38 provinsi | Keputusan K-001 | Nama baku provinsi di Indonesia |
| periode | string | YYYY (regex ^\d{4}$) | tidak | 2017 s.d. 2025 | Keputusan K-008 | Tahun kalender pengamatan SUSENAS |
| var1473 | float | persentase | tidak | 1.43 s.d. 38.35 | Silver (bps, var1473) | Prevalensi Ketidakcukupan Konsumsi Pangan (PoU) |
| var1474 | float | persentase | tidak | 0.38 s.d. 35.67 | Silver (bps, var1474) | Prevalensi Kerawanan Pangan Sedang atau Berat (FIES) |
| status_anomali_var1473 | string | teks kategori | tidak | NORMAL, OUTLIER_ASLI, PATAHAN_SERI | Keputusan K-002 dan daftar_anomali_terklasifikasi.csv | Klasifikasi anomali indikator PoU |
| status_anomali_var1474 | string | teks kategori | tidak | NORMAL, OUTLIER_ASLI, PATAHAN_SERI | Keputusan K-002 dan daftar_anomali_terklasifikasi.csv | Klasifikasi anomali indikator FIES |
| is_outlier | bool | Boolean | tidak | True, False | Keputusan K-002 dan K-011 | True jika observasi merupakan outlier geografis asli |
| is_patahan | bool | Boolean | tidak | True, False | Keputusan K-002 dan K-011 | True jika observasi merupakan patahan struktural akibat pemekaran DOB 2024–2025 |

---

## 6. `data/gold/rekonsiliasi_nasional.parquet`

Tabel Gold tingkat nasional yang menyandingkan angka agregat BPS dengan pembanding internasional WDI dan WHO GHO per tahun untuk evaluasi selisih metodologi.

Dimensi: 27 baris × 10 kolom.

| Kolom | Tipe data | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/keputusan log) | Keterangan |
|---|---|---|---|---|---|---|
| periode | string | YYYY | tidak | 1996 s.d. 2025 | Keputusan K-008 | Tahun pengamatan indikator nasional |
| wilayah_kode | int | 9999 | tidak | 9999 | Keputusan K-001 | Kode agregat nasional Indonesia |
| nama_wilayah | string | INDONESIA | tidak | INDONESIA | Keputusan K-001 | Entitas nasional Indonesia |
| bps_var1473 | float | persentase | ya (hanya 2017–2025) | 7.63 s.d. 10.21 | BPS SUSENAS var1473 | Prevalensi PoU nasional menurut BPS |
| bps_var1474 | float | persentase | ya (hanya 2017–2025) | 4.00 s.d. 8.66 | BPS SUSENAS var1474 | Prevalensi FIES nasional menurut BPS |
| wdi_SN.ITK.DEFC.ZS | float | persentase | ya (2001–2024) | 5.20 s.d. 19.30 | World Bank / FAO | Prevalensi PoU pembanding dari WDI |
| wdi_SN.ITK.MSFI.ZS | float | persentase | ya (2015–2024) | 4.30 s.d. 9.10 | World Bank / FAO | Prevalensi FIES pembanding dari WDI |
| who_NUTSTUNTINGPREV | float | persentase | ya (2000–2024) | 21.50 s.d. 42.40 | WHO GHO (SEX=TOTAL) | Prevalensi stunting balita nasional |
| who_NUTOVERWEIGHTPREV | float | persentase | ya (2000–2024) | 2.80 s.d. 11.50 | WHO GHO (SEX=TOTAL) | Prevalensi overweight balita nasional |
| who_NUTRITION_WH_2 | float | persentase | ya (1996–2023) | 7.10 s.d. 15.70 | WHO GHO (TOTAL) | Prevalensi wasting balita nasional |

---

## Catatan Penggunaan Data

1. `panel_provinsi.parquet` merupakan panel kanonis Sprint 2 dengan format long.
2. `panel_provinsi_anomali.parquet` merupakan keluaran analisis anomali dengan format wide.
3. `tabel_nasional.parquet` merupakan tabel nasional kanonis dengan format long.
4. `tabel_nasional_lebar.parquet` merupakan view lebar yang diturunkan dari tabel nasional long.
5. `rekonsiliasi_nasional.parquet` merupakan keluaran rekonsiliasi nasional dari proses analisis sebelumnya.
6. Nilai indikator menggunakan satuan persen dan tidak dinormalisasi.
7. Nilai kosong akibat tidak tersedianya observasi tidak dianggap sebagai nol dan tidak diimputasi.
8. BPS PoU/FIES, WDI, dan WHO GHO memiliki definisi serta metodologi masing-masing sehingga tidak boleh dianggap identik.
