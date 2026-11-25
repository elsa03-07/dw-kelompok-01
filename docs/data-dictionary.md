# Data dictionary — Kelompok 1 (Kerawanan Pangan Provinsi)

Satu tabel per keluaran (Silver dan setiap tabel Gold). Isi dari data nyata, bukan dari ingatan:
tipe, satuan, rentang, dan jumlah kosong dihitung ulang setiap kali pipeline berjalan.

## Katalog seri terverifikasi (Tahap 4 persiapan)

Satuan kanonis untuk tujuh seri Kasus 01 adalah `persen`. Kode SDG, periode, serta berkas dan
field mentah yang menjadi sumber bukti tercatat di
`reports/backlog/124450005/katalog_seri_terverifikasi.csv`.

| Sumber | Seri | Kode SDG | Satuan | Periode | Catatan |
|---|---|---|---|---|---|
| bps | var1473 | 2.1.1 | persen | tahun | katalog awal cocok |
| bps | var1474 | 2.1.2 | persen | tahun | katalog awal cocok |
| wdi | SN.ITK.DEFC.ZS | 2.1.1 | persen | tahun | satuan dan kode SDG dikoreksi |
| wdi | SN.ITK.MSFI.ZS | 2.1.2 | persen | tahun | satuan dan kode SDG dikoreksi |
| who_gho | NUTSTUNTINGPREV | 2.2.1 | persen | tahun | katalog awal cocok |
| who_gho | NUTOVERWEIGHTPREV | 2.2.2 | persen | tahun | katalog awal cocok |
| who_gho | NUTRITION_WH_2 | 2.2.2 | persen | tahun | katalog awal cocok |

Tidak ada seri dengan periode semesteran atau bulanan; Silver tidak merata-ratakan periode
non-tahunan menjadi tahunan.

---

## data/silver/silver.parquet

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
| nilai | float | numerik persen | tidak | 0.0 s.d. 100.0 | data mentah | Nilai observasi indikator kerawanan pangan & gizi |
| satuan | string | teks | tidak | persen | Keputusan K-006 | Satuan kanonis terverifikasi |
| _berkas_raw | string | jalur relatif | tidak | jalur di bawah data/raw/ | fungsi ekstraksi | Jalur berkas mentah asal untuk audit lineage |
| _sha256_raw | string | 64-karakter hex | tidak | sha256 valid di MANIFEST.csv | src.common.manifest | Sidik hash integritas berkas mentah sumber |

## data/gold/panel_provinsi.parquet

Tabel panel Gold tingkat provinsi (format wide) yang menyandingkan kedua seri utama BPS per provinsi per tahun, dilengkapi penanda diagnostik anomali dan patahan seri Sprint 1. Dimensi: 314 baris × 9 kolom.

| Kolom | Tipe Data | Satuan/Format | Boleh Kosong? | Rentang atau Nilai Sah | Asal (Berkas/Keputusan Log) | Keterangan & Definisi |
|---|:---:|:---:|:---:|---|---|---|
| `wilayah_kode` | int | 4-digit numerik | Tidak | 1100 s.d. 9700 (38 Provinsi BPS) | Keputusan K-001 | Kode provinsi BPS (kode 2-digit × 100). |
| `nama_wilayah` | string | Teks Huruf Kapital | Tidak | Nama resmi 38 provinsi | Keputusan K-001 | Nama baku provinsi di Indonesia. |
| `periode` | string | YYYY (regex `^\d{4}$`) | Tidak | 2017 s.d. 2025 | Keputusan K-008 | Tahun kalender pengamatan SUSENAS. |
| `var1473` | float | Persentase | Tidak | 1.43 s.d. 38.35 | `data/silver/silver.parquet` (bps, var1473) | Prevalensi Ketidakcukupan Konsumsi Pangan (PoU). |
| `var1474` | float | Persentase | Tidak | 0.38 s.d. 35.67 | `data/silver/silver.parquet` (bps, var1474) | Prevalensi Kerawanan Pangan Sedang atau Berat (FIES). |
| `status_anomali_var1473` | string | Teks kategori | Tidak | `NORMAL`, `OUTLIER_ASLI`, `PATAHAN_SERI` | Keputusan K-002 & `daftar_anomali_terklasifikasi.csv` | Klasifikasi anomali indikator PoU. |
| `status_anomali_var1474` | string | Teks kategori | Tidak | `NORMAL`, `OUTLIER_ASLI`, `PATAHAN_SERI` | Keputusan K-002 & `daftar_anomali_terklasifikasi.csv` | Klasifikasi anomali indikator FIES. |
| `is_outlier` | bool | Boolean | Tidak | `True`, `False` | Keputusan K-002 & K-011 | True jika observasi merupakan outlier geografis asli (Maluku/Papua). |
| `is_patahan` | bool | Boolean | Tidak | `True`, `False` | Keputusan K-002 & K-011 | True jika observasi merupakan patahan struktural (pemekaran DOB 2024-2025). |

---

## data/gold/rekonsiliasi_nasional.parquet

Tabel Gold tingkat nasional yang menyandingkan angka agregat BPS dengan pembanding internasional WDI dan WHO GHO per tahun untuk evaluasi selisih metodologi. Dimensi: 27 baris × 10 kolom.

| Kolom | Tipe Data | Satuan/Format | Boleh Kosong? | Rentang atau Nilai Sah | Asal (Berkas/Keputusan Log) | Keterangan & Definisi |
|---|:---:|:---:|:---:|---|---|---|
| `periode` | string | YYYY | Tidak | 1996 s.d. 2025 | Keputusan K-008 | Tahun pengamatan indikator nasional. |
| `wilayah_kode` | int | 9999 | Tidak | 9999 | Keputusan K-001 | Kode agregat nasional Indonesia. |
| `nama_wilayah` | string | INDONESIA | Tidak | `INDONESIA` | Keputusan K-001 | Entitas nasional Indonesia. |
| `bps_var1473` | float | Persentase | Ya (hanya 2017-2025) | 7.63 s.d. 10.21 | BPS SUSENAS var1473 | Prevalensi PoU nasional menurut BPS. |
| `bps_var1474` | float | Persentase | Ya (hanya 2017-2025) | 4.00 s.d. 8.66 | BPS SUSENAS var1474 | Prevalensi FIES nasional menurut BPS. |
| `wdi_SN.ITK.DEFC.ZS` | float | Persentase | Ya (2001-2024) | 5.20 s.d. 19.30 | World Bank / FAO | Prevalensi PoU pembanding dari WDI. |
| `wdi_SN.ITK.MSFI.ZS` | float | Persentase | Ya (2015-2024) | 4.30 s.d. 9.10 | World Bank / FAO | Prevalensi FIES pembanding dari WDI. |
| `who_NUTSTUNTINGPREV` | float | Persentase | Ya (2000-2024) | 21.50 s.d. 42.40 | WHO GHO (SEX=TOTAL) | Prevalensi Stunting balita nasional (agregat total). |
| `who_NUTOVERWEIGHTPREV` | float | Persentase | Ya (2000-2024) | 2.80 s.d. 11.50 | WHO GHO (SEX=TOTAL) | Prevalensi Overweight balita nasional (agregat total). |
| `who_NUTRITION_WH_2` | float | Persentase | Ya (1996-2023) | 7.10 s.d. 15.70 | WHO GHO (TOTAL) | Prevalensi Wasting balita nasional (agregat total). |
