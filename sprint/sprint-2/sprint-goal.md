# Sprint 2: Sprint Goal (draf untuk Backlog #27)

> Draf disiapkan dari keadaan cabang `perbaikan/sprint-2`. Koordinator (#27) menyesuaikan, lalu menyalinnya ke Workbench.

## Tujuan sprint

Dari Silver yang sudah tervalidasi, bangun Gold kanonis untuk Kasus 01 (panel provinsi × periode × indikator
dan tabel nasional), simpan Silver dan Gold di SQLite, dan rekonsiliasikan seri utama BPS dengan
pembanding WDI dengan setiap selisih dijelaskan. Semuanya dihasilkan ulang dengan satu perintah `python pipeline.py`.

## Definition of Done dan buktinya

| DoD | Bukti |
|---|---|
| Reshape ke panel Gold provinsi × periode × indikator (tahap 4) | `data/gold/panel_provinsi.parquet` 628 baris; aturan #20 (K-014 s.d. K-017) dengan dampak tertulis otomatis di `log-keputusan.csv` |
| Silver dan Gold tersimpan di SQL beserta alasan pilihannya (tahap 5) | Tahap `sql` di `pipeline.py` → `data/capstone.sqlite`, 5 tabel, jumlah baris = Parquet; alasan SQLite di `reports/tim.md` dan `src/sql/__init__.py` |
| Tabel rekonsiliasi seri utama vs pembanding nasional, selisih dijelaskan (tahap 6) | `data/gold/rekonsiliasi.parquet` 36 baris: 16 berpasangan dengan kategori dan penjelasan, 20 `tanpa pasangan`; K-018 |
| Demo wajib | Rekaman mengikuti `reports/reproduksi.md` |

## Pemeriksaan sebelum demo

- [x] `python pipeline.py` exit 0; validasi 19/19 lolos
- [x] Klon bersih: `git status --short` kosong setelah pipeline
- [x] `python -m unittest discover -s tests`: 25 tes lolos
- [x] `docs/data-dictionary.md` mencakup semua kolom (diperiksa tes)
- [ ] Setiap anggota menulis `sprint/sprint-2/<nim>.md` dan Log Sprint di Workbench
- [ ] Rekaman Demo Sprint 2 dikirim sebelum 30 Nov 2026, 23.59
