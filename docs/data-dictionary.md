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

## data/gold/<tabel>.parquet

*(Bagian ini akan ditambahkan pada Sprint 2 dan Sprint 3 setelah transformasi panel Gold dan tabel rekonsiliasi dibentuk).*
