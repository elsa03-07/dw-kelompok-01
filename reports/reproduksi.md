# Uji reproduksi dari klon bersih: Sprint 2 (Backlog #30)

Penanggung jawab: Raihan Azwar Faqih Wijaya (124450032), peran Reproduksi & Demo.

## Prosedur

Setiap langkah dijalankan di folder baru, di luar folder kerja, dengan lingkungan Python baru:

```bash
git clone <repo tim> klon && cd klon
python -m venv ../venv
../venv/Scripts/python -m pip install -r requirements.txt
../venv/Scripts/python unduh_data.py --kasus 1          # unduh ulang data mentah
../venv/Scripts/python pipeline.py                       # mentah -> Silver -> Gold -> SQL -> validasi
git status --short                                       # harus kosong
../venv/Scripts/python -m src.common.skema data/silver/silver.parquet
../venv/Scripts/python -m unittest discover -s tests
```

`git status --short` adalah pemeriksaan utamanya. Pipeline menimpa semua keluaran yang di-*commit*
(`data/silver`, `data/gold`, `log-keputusan.csv`, `reports/validasi.md`, `reports/ringkasan_pipeline.md`).
Bila hasilnya kosong, setiap berkas yang dihasilkan ulang identik byte demi byte dengan versi di repo.

## Hasil (27 Nov 2026)

Lingkungan: Windows AMD64, Python 3.13.9, pandas 3.1.1, pyarrow 26.0.1, pandera 0.36.0.

| Pemeriksaan | Hasil |
|---|---|
| `unduh_data.py --kasus 1` | 14 berkas cocok dengan MANIFEST.csv |
| `pipeline.py` | exit 0, sekitar 4 detik termasuk impor |
| Validasi | 19/19 aturan lolos (12 Silver, 6 Gold/rekonsiliasi, 1 SQL) |
| SQL vs Parquet | 5 tabel cocok: silver 1.439, panel_provinsi 628, tabel_nasional 114, tabel_nasional_lebar 30, rekonsiliasi 36 |
| `git status --short` setelah run | kosong: semua keluaran identik dengan repo |
| `src.common.skema` | LOLOS: 1.439 baris, 7 seri, 39 wilayah, 6 berkas sumber |
| Unit test | 25 tes lolos |

Sidik keluaran tercatat di `reports/ringkasan_pipeline.md` (contoh: `silver.parquet` `9a57a26c239e…`,
sama dengan sidik Sprint 1).

## Temuan sebelum perbaikan (klon bersih `main` @ 2d96a3b)

Uji yang sama pada `main` sebelum perbaikan menemukan:

1. Tidak ada basis data yang dibuat atau diperbarui oleh pipeline. `data/silver/silver.sqlite` di repo adalah sisa run manual (#23).
2. Rekonsiliasi: 96 dari 114 baris berlabel `belum terjelaskan`, karena WDI/WHO tidak pernah berpasangan (#24).
3. `data/gold/panel_provinsi.parquet` di repo tidak sinkron dengan kode: kolom `nilai_normal` belum ada (#21).
4. Tahap ekstraksi kosong (`baca_semua` tidak ada; error ditelan).

Keempatnya diperbaiki di cabang `perbaikan/sprint-2`. Rinciannya ada di pesan commit dan di `log-keputusan.csv` (K-018, K-019).

## Demo Sprint 2

Rekaman demo mengikuti urutan prosedur di atas: klon, unduh, `pipeline.py`, `git status` kosong,
lalu buka `reports/ringkasan_pipeline.md` dan tunjukkan satu kueri ke `data/capstone.sqlite`, misalnya:

```sql
SELECT periode, seri_utama, nilai_utama, nilai_pembanding, selisih, kategori
FROM rekonsiliasi WHERE status_pasangan = 'berpasangan' ORDER BY seri_utama, periode;
```
