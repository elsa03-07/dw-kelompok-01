# Data dictionary — <Nama tim>

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

## data/gold/<tabel>.parquet

| Kolom | Tipe | Satuan/format | Boleh kosong | Rentang atau nilai sah | Asal (berkas/aturan) | Keterangan |
|---|---|---|---|---|---|---|
