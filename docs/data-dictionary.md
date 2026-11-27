# Kamus data: Silver dan Gold kanonis

Kelompok 1, Kasus 01: Kerawanan pangan provinsi. Semua tabel dihasilkan ulang oleh `python pipeline.py`
dan dimuat ke `data/capstone.sqlite` dengan nama tabel yang sama (DDL: `src/silver/skema_silver.sql`,
`src/gold/skema_gold.sql`). `tests/test_kamus.py` memeriksa bahwa setiap kolom di Parquet tercantum di sini.

Kolom **Asal**:
- **Silver**: disalin apa adanya dari Silver.
- **Metadata seri**: dari `SERI_META` di `src/gold/builder.py`.
- **Turunan**: dihitung di Gold. Keputusannya tercatat di `log-keputusan.csv`.

Penelusuran satu angka ke sumbernya: ambil `_berkas_raw`, buka `data/raw/<_berkas_raw>`, dan cocokkan
`_sha256_raw` dengan `data/raw/MANIFEST.csv`. Contoh: panel `var1473`, Aceh (1100), 2017, nilai 8.40,
berasal dari `bps/2026-10-20/sdg2_2_1_1_v1473.csv`, baris `1473,1100,ACEH,...,2017,...,8.4,Persen`.

## silver (`data/silver/silver.parquet`, 1.439 baris)

Kunci primer: `sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw`.

| Kolom | Tipe | Satuan | Arti | Asal |
|---|---|---|---|---|
| sumber | teks | - | Produsen data: `bps`, `wdi`, `who_gho` | Silver |
| seri_kode | teks | - | Kode seri di sumber (`var1473`, `SN.ITK.DEFC.ZS`, `NUTSTUNTINGPREV`, ...) | Silver |
| wilayah_kode | bilangan bulat | - | Kode provinsi BPS (dua digit × 100); `9999` = Indonesia (nasional) | Silver (K-001) |
| nama_wilayah | teks | - | Nama provinsi baku 38 provinsi, atau `INDONESIA` | Silver (K-001) |
| periode | teks | - | Tahun empat digit | Silver (K-008) |
| jenis_periode | teks | - | Selalu `tahun` pada kasus ini | Silver (K-008) |
| rincian | teks | - | Subkelompok: `Total` untuk BPS/WDI; `SEX=...`, `AGE=...` dan seterusnya untuk WHO | Silver (K-010) |
| nilai | desimal | persen | Nilai indikator | Silver |
| satuan | teks | - | Satuan kanonis, selalu `persen` | Silver (K-006) |
| _berkas_raw | teks | - | Jalur berkas mentah relatif `data/raw/` | Silver |
| _sha256_raw | teks | - | sha256 berkas mentah, sama dengan `MANIFEST.csv` | Silver |

## panel_provinsi (`data/gold/panel_provinsi.parquet`, 628 baris)

Satu baris = satu provinsi × satu tahun × satu indikator BPS (`var1473`, `var1474`), bentuk panjang.
Kunci primer: `seri_kode, wilayah_kode, periode`. Wilayah `9999` tidak masuk ke tabel ini.
Panel tidak seimbang: 4 DOB Papua baru ada mulai 2024, dan sel sebelum itu tidak dibuat (K-005, K-011).

| Kolom | Tipe | Satuan | Arti | Asal |
|---|---|---|---|---|
| sumber | teks | - | Selalu `bps` | Silver |
| seri_kode | teks | - | `var1473` (PoU) atau `var1474` (FIES) | Silver |
| nama_indikator | teks | - | Nama indikator dalam bahasa Indonesia | Metadata seri |
| kode_sdg | teks | - | `2.1.1` (PoU) atau `2.1.2` (FIES) | Metadata seri (K-007) |
| wilayah_kode | bilangan bulat | - | Kode provinsi | Silver |
| nama_wilayah | teks | - | Nama provinsi | Silver |
| periode | teks | - | Tahun 2017–2025 | Silver |
| jenis_periode | teks | - | `tahun` | Silver |
| rincian | teks | - | `Total` | Silver (K-015) |
| nilai | desimal | persen | Prevalensi provinsi | Silver |
| satuan | teks | - | `persen` | Silver |
| _berkas_raw | teks | - | Berkas mentah asal baris | Silver |
| _sha256_raw | teks | - | sha256 berkas mentah asal | Silver |
| status_anomali | teks | - | Kategori anomali Sprint 1 (`Outlier Asli ...`, `Patahan Seri ...`), atau `Normal` | Turunan (K-002, K-017) |
| is_outlier | boolean | - | Benar bila sel adalah outlier asli. Nilainya tidak diubah. | Turunan (K-017) |
| is_patahan | boolean | - | Benar bila sel adalah patahan seri, termasuk 4 DOB Papua sejak 2024 | Turunan (K-017) |

## tabel_nasional (`data/gold/tabel_nasional.parquet`, 114 baris)

Satu baris = satu seri nasional (wilayah `9999`) × satu tahun. Seri BPS, WDI, dan WHO disimpan
berdampingan dalam bentuk panjang. Kunci primer: `sumber, seri_kode, periode`.

| Kolom | Tipe | Satuan | Arti | Asal |
|---|---|---|---|---|
| sumber | teks | - | `bps`, `wdi`, `who_gho` | Silver |
| seri_kode | teks | - | Salah satu dari 7 seri kasus | Silver |
| nama_indikator | teks | - | Nama indikator | Metadata seri |
| kode_sdg | teks | - | Kode SDG indikator | Metadata seri |
| kelompok_indikator | teks | - | `seri_utama_bps`, `pembanding_wdi`, `pembanding_who` | Metadata seri |
| wilayah_kode | bilangan bulat | - | Selalu `9999` | Silver |
| nama_wilayah | teks | - | `INDONESIA` | Silver |
| periode | teks | - | Tahun | Silver |
| jenis_periode | teks | - | `tahun` | Silver |
| rincian | teks | - | `Total` (BPS/WDI), `SEX=TOTAL` (stunting, overweight), `SEX=TOTAL; AGE=TOTAL` (wasting) | Silver (K-012, K-015) |
| nilai | desimal | persen | Nilai nasional | Silver |
| satuan | teks | - | `persen` | Silver |
| dapat_dibandingkan_dengan | teks | - | Seri yang sebanding, atau `tidak langsung` | Metadata seri |
| catatan_perbandingan | teks | - | Alasan keterbandingan atau ketidaksetaraan | Metadata seri |
| _berkas_raw | teks | - | Berkas mentah asal baris | Silver |
| _sha256_raw | teks | - | sha256 berkas mentah asal | Silver |

## tabel_nasional_lebar (`data/gold/tabel_nasional_lebar.parquet`, 30 baris)

Tampilan lebar dari `tabel_nasional`: satu baris per tahun (1996–2025), satu kolom per seri. Sel kosong
berarti seri itu tidak terbit untuk tahun tersebut. Tabel ini tidak menambah angka baru, jadi lineage
setiap angka ada di `tabel_nasional`. Kunci primer: `periode`.

| Kolom | Tipe | Satuan | Arti | Asal |
|---|---|---|---|---|
| periode | teks | - | Tahun | Turunan |
| bps_var1473 | desimal | persen | BPS PoU nasional | Turunan dari tabel_nasional |
| bps_var1474 | desimal | persen | BPS FIES sedang/berat nasional | Turunan dari tabel_nasional |
| wdi_defc | desimal | persen | WDI `SN.ITK.DEFC.ZS` (PoU) | Turunan dari tabel_nasional |
| wdi_msfi | desimal | persen | WDI `SN.ITK.MSFI.ZS` (FIES) | Turunan dari tabel_nasional |
| who_stunting | desimal | persen | WHO stunting balita, total jenis kelamin | Turunan dari tabel_nasional |
| who_overweight | desimal | persen | WHO overweight balita, total jenis kelamin | Turunan dari tabel_nasional |
| who_wasting | desimal | persen | WHO wasting balita, total jenis kelamin dan umur | Turunan dari tabel_nasional |

## rekonsiliasi (`data/gold/rekonsiliasi.parquet`, 36 baris)

Satu baris = satu pasangan seri (BPS nasional vs WDI dengan definisi SDG yang sama) × satu tahun.
Pasangannya `var1473` ↔ `SN.ITK.DEFC.ZS` dan `var1474` ↔ `SN.ITK.MSFI.ZS`. Seri WHO tidak
direkonsiliasi karena mengukur status gizi anak, bukan PoU/FIES (K-018). Kunci primer: `seri_utama, periode`.

| Kolom | Tipe | Satuan | Arti | Asal |
|---|---|---|---|---|
| periode | teks | - | Tahun | Turunan |
| seri_utama | teks | - | Seri BPS | Turunan (K-018) |
| seri_pembanding | teks | - | Seri WDI pasangannya | Turunan (K-018) |
| nilai_utama | desimal | persen | Nilai BPS nasional. Kosong bila BPS tidak terbit tahun itu. | tabel_nasional |
| nilai_pembanding | desimal | persen | Nilai WDI. Kosong bila WDI belum terbit tahun itu. | tabel_nasional |
| selisih | desimal | poin persen | `nilai_utama - nilai_pembanding`. Hanya terisi untuk baris berpasangan. | Turunan |
| status_pasangan | teks | - | `berpasangan`, `hanya_utama`, atau `hanya_pembanding` | Turunan |
| kategori | teks | - | Penyebab selisih: `metode berbeda` dan lainnya, atau `tanpa pasangan` | Turunan (K-018) |
| penjelasan | teks | - | Penjelasan kalimat untuk kategori pada baris ini | Turunan (K-018) |
| _berkas_raw_utama | teks | - | Berkas mentah asal `nilai_utama` | tabel_nasional |
| _berkas_raw_pembanding | teks | - | Berkas mentah asal `nilai_pembanding` | tabel_nasional |
