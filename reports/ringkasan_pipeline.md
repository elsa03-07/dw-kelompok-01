# Ringkasan run pipeline.py

Ditulis otomatis oleh `python pipeline.py`. Jangan disunting manual.

- Berkas mentah cocok dengan MANIFEST.csv: **14**
- Berkas mentah terbaca di tahap ekstraksi: **14**
- Validasi: **19/19 aturan lolos** (rincian di `reports/validasi.md`)

## Keluaran

| Berkas | Baris | Kolom | sha256 (12 awal) |
|---|---:|---:|---|
| `data/silver/silver.parquet` | 1,439 | 11 | `9a57a26c239e` |
| `data/gold/panel_provinsi.parquet` | 628 | 16 | `f325aff629b8` |
| `data/gold/tabel_nasional.parquet` | 114 | 16 | `1227aa5634bb` |
| `data/gold/tabel_nasional_lebar.parquet` | 30 | 8 | `0dfbee8c337d` |
| `data/gold/rekonsiliasi.parquet` | 36 | 11 | `72d544478d4a` |

## Aturan satu nilai per sel (#20), juga tertulis di log-keputusan.csv

| Keputusan | Aturan | Baris disisihkan |
|---|---|---:|
| K-014 | Snapshot terbaru per sel | 0 |
| K-016 | Periode tahunan murni | 0 |
| K-015 | Rincian sebanding (subkelompok WHO tetap di Silver) | 697 |
| K-017 | Penanda outlier dan patahan (tanpa membuang baris) | 0 |

Silver 1,439 baris → terpilih ke Gold 742; 697 baris subkelompok tetap hanya di Silver.

## Rekonsiliasi (#24)

| Seri utama | Pembanding | Berpasangan | Tanpa pasangan | Rata-rata selisih |
|---|---|---:|---:|---:|
| var1473 | SN.ITK.DEFC.ZS | 8 | 17 | +2.06 poin persen |
| var1474 | SN.ITK.MSFI.ZS | 8 | 3 | +0.05 poin persen |

## SQL (#23): data/capstone.sqlite

| Tabel | Baris Parquet | Baris SQL | Cocok |
|---|---:|---:|:---:|
| silver | 1,439 | 1,439 | ya |
| panel_provinsi | 628 | 628 | ya |
| tabel_nasional | 114 | 114 | ya |
| tabel_nasional_lebar | 30 | 30 | ya |
| rekonsiliasi | 36 | 36 | ya |
