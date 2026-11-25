# Data dictionary — Kelompok 01, Kasus 01

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

## data/silver/silver.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | bps, bnpb, wdi, who_gho, ilostat | nama folder data/raw | |
| wilayah_kode | int | kode BPS x 100 | tidak | 9999 atau 1100–9600 | log K-… | |

## data/gold/panel_provinsi.parquet

Panel long observasi BPS tingkat provinsi: 628 baris (314 `var1473` + 314 `var1474`).
Kunci unik: `(seri_kode, wilayah_kode, periode)`. Wilayah `9999` tidak ada karena agregat
nasional dipisahkan ke tabel nasional. Tidak ada nilai kosong. Rentang nilai: `var1473`
1,43–38,35 dan `var1474` 0,76–27,54.

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
| sumber | string | — | tidak | bps | nama folder data/raw | sumber seri utama |
| seri_kode | string | — | tidak | var1473, var1474 | Silver | indikator panel |
| nama_indikator | string | — | tidak | PoU, FIES | katalog terverifikasi | nama indikator |
| kode_sdg | string | — | tidak | 2.1.1, 2.1.2 | katalog terverifikasi | kode SDG |
| wilayah_kode | int64 | kode BPS × 100 | tidak | 1100–9700 | Silver | 38 provinsi; 9999 tidak termasuk |
| nama_wilayah | string | — | tidak | nama provinsi | Silver | nama wilayah |
| periode | string | tahun | tidak | 2017–2025 | Silver | periode tahunan |
| jenis_periode | string | — | tidak | tahun | Silver | seluruh periode tahunan |
| rincian | string | — | tidak | Total | Silver | BPS tidak memiliki disagregasi gender |
| nilai | float64 | persen | tidak | 0–100 | Silver | nilai asli; tidak dinormalisasi |
| satuan | string | — | tidak | persen | katalog K-006 | satuan kanonis |
| _berkas_raw | string | jalur relatif | tidak | bps/2026-10-20/... | Silver | lineage berkas mentah |
| _sha256_raw | string | sha256 | tidak | 64 heksadesimal | MANIFEST.csv | lineage berkas mentah |

Grid teoritis 38 provinsi × 9 periode = 342 sel per seri. Terisi 314 dan kosong 28 per seri;
56 sel kosong total berasal dari 4 DOB Papua 2017–2023 dan **tidak diimputasi** (K-005, K-011).
Oleh karena itu tabel ini adalah panel tidak seimbang alami, bukan grid lengkap berisi NaN.

## data/gold/tabel_nasional.parquet

Tabel nasional kanonis long: 114 baris dari 7 seri, dengan lineage dan metadata perbandingan.
Kunci unik: `(sumber, seri_kode, periode)`. Seluruh nilai memakai satuan persen dan tidak ada
nilai kosong. Tabel ini adalah sumber kebenaran untuk tabel nasional; view lebar diturunkan
darinya.

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

Jumlah per seri: `var1473` 9, `var1474` 9, `SN.ITK.DEFC.ZS` 24, `SN.ITK.MSFI.ZS` 10,
`NUTSTUNTINGPREV` 25, `NUTOVERWEIGHTPREV` 25, `NUTRITION_WH_2` 12. Rincian WHO yang dipilih
adalah `SEX=TOTAL` untuk stunting/overweight dan `SEX=TOTAL; AGE=TOTAL` untuk wasting (K-012).
BPS PoU/FIES tidak dianggap setara dengan indikator WHO; WDI diposisikan sebagai pembanding,
bukan pengganti BPS.

## data/gold/tabel_nasional_lebar.parquet

View lebar untuk menampilkan seri nasional secara berdampingan: 30 baris tahun 1996–2025.
Tabel ini **diturunkan** dari `tabel_nasional.parquet`; lineage per sel dilacak melalui join
`(periode, seri_kode)` ke tabel long. Tahun 1997–1999 tidak memiliki observasi pada ketujuh
seri sehingga ketiga baris tersebut kosong (tidak diimputasi). Total sel terisi = 114.

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

Nilai kosong pada view lebar berarti seri tidak menerbitkan observasi pada tahun tersebut,
bukan nol dan bukan hasil imputasi. Untuk analisis, gunakan tabel long agar metadata dan
lineage tetap tersedia.
