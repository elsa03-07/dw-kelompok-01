# Laporan Silver — Sprint 1

**NIM:** 124450005  
**Kasus:** 01 — Kerawanan pangan provinsi  
**Tanggal:** 20 November 2026  
**Komponen:** Penyusunan Silver

## Hasil

`python pipeline.py` berhasil menyelesaikan tahap Silver dan menulis
`data/silver/silver.parquet`; Gold dan Validasi belum tersedia sehingga pipeline
berhenti dengan status tertunda, bukan sebagai pipeline end-to-end yang selesai.

Hasil aktual:

| Ukuran | Nilai |
|---|---:|
| Baris Silver | 1.439 |
| Seri | 7 |
| Wilayah unik | 39 |
| Berkas sumber | 6 |
| Kunci kembar | 0 |
| Kategori `rincian` unik | 73 |
| Baris dengan rincian selain `Total` | 759 |

`python -m src.common.skema data/silver/silver.parquet` menghasilkan:

```text
LOLOS  1,439 baris, 7 seri, 39 wilayah, 6 berkas sumber
```

Seluruh periode Silver bertipe tahunan dan pengaman periode tetap dipertahankan.

## K-009 — Kunci kembar NUTRITION_WH_2 2008

Ditemukan dua baris pada
`who_gho/2026-10-20/datadot/FC5231F_NUTRITION_WH_2.csv`:

| Baris | `DIM_SEX` | `DIM_AGE` | `RATE_PER_100_N` |
|---:|---|---|---:|
| 87 | `MALE` | `MONTHS24-35` | 15,7 |
| 383 | `MALE` | `MONTHS24-35` | 16,3 |

Kedua baris identik pada seluruh kolom lain, termasuk `DIM_TIME=2008`,
`DIM_GEO_CODE_M49=360`, status `PUBLISHED`, dan seluruh dimensi lain yang kosong.
Keduanya menghasilkan kunci Silver yang sama.

Tidak ada bukti metadata eksplisit yang memungkinkan pengubahan label sumber
`15,7` menjadi agregat umur. Oleh karena itu:

- Data mentah tidak diubah; kedua baris tetap ada di raw.
- Label sumber tidak diubah.
- Untuk sementara, baris `15,7` tidak dimasukkan ke Silver agar kunci Silver unik.
- Baris `16,3` dipertahankan sebagai `SEX=MALE; AGE=MONTHS24-35`.
- Satu observasi masih menunggu klarifikasi koordinator.
- Dampak sementara: 1 baris.

Keputusan lengkap tercatat sebagai `K-009` di `log-keputusan.csv`.

## K-010 — Rincian WHO dipertahankan

Seluruh rincian sumber WHO GHO dipertahankan di Silver. Pemilihan rincian yang
sebanding untuk kebutuhan analisis dilakukan di Gold; Silver tidak melakukan
penyaringan rincian untuk kebutuhan Gold.

`K-004` milik anggota lain tidak diubah. Keputusan bahwa pemilihan rincian
sebanding merupakan tugas Gold dicatat sebagai `K-010`.

## Metrik

`results/124450005/metrics.json` diisi menggunakan hasil aktual:

```text
seri_silver=7
rincian_dienkode=73
baris_silver=1439
```

## Reproduksi

```bash
python pipeline.py
python -m src.common.skema data/silver/silver.parquet
python tests/test_periode.py
```

Catatan: pembaca BPS dan WHO di `src/ekstraksi/` masih belum lengkap dan
menghasilkan peringatan pada tahap ekstraksi. Modul tersebut bukan bagian dari
perubahan ini; Silver membaca raw langsung sesuai kontrak `src/silver/__init__.py`.
