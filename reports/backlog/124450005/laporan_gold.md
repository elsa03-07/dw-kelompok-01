# Laporan Gold — Sprint 2

**NIM:** 124450005
**Kasus:** 01 — Kerawanan pangan provinsi
**Tanggal:** 25 November 2026
**Komponen:** Pembentukan Gold Layer

## 1. Tujuan

Membentuk tabel Gold yang siap dianalisis dari Silver tanpa mengubah data mentah atau
menghapus informasi sumber. Gold terdiri atas panel provinsi untuk dua seri utama BPS dan
tabel nasional yang membandingkan BPS dengan WDI serta WHO secara transparan.

## 2. Sumber data

Seluruh nilai Gold berasal dari `data/silver/silver.parquet`:

- Seri utama BPS: `var1473` (PoU, SDG 2.1.1) dan `var1474` (FIES, SDG 2.1.2).
- Pembanding WDI: `SN.ITK.DEFC.ZS` (PoU, SDG 2.1.1) dan `SN.ITK.MSFI.ZS` (FIES, SDG 2.1.2).
- Pembanding WHO GHO: `NUTSTUNTINGPREV` (SDG 2.2.1), `NUTOVERWEIGHTPREV` (SDG 2.2.2),
  dan `NUTRITION_WH_2` (SDG 2.2.2).

Setiap baris Gold membawa `_berkas_raw` dan `_sha256_raw` dari Silver. Tidak ada nilai yang
diambil langsung dari berkas mentah pada tahap ini.

## 3. Panel provinsi

Panel dibentuk dari observasi BPS provinsi (selain `wilayah_kode=9999`) dan disimpan dalam
format long dengan kunci `(seri_kode, wilayah_kode, periode)`.

| Ukuran | var1473 | var1474 |
|---|---:|---:|
| Baris observasi | 314 | 314 |
| Provinsi unik | 38 | 38 |
| Periode | 2017–2025 | 2017–2025 |
| Nilai minimum–maksimum | 1,43–38,35 | 0,76–27,54 |

Total panel 628 baris. Grid teoritis 38 provinsi × 9 periode = 342 sel per seri; 28 sel per
seri (56 sel total) tidak tersedia untuk 4 DOB Papua pada 2017–2023. Sel tersebut adalah
ketiadaan struktural, bukan missing acak. Sesuai K-005 dan K-011:

- Tidak ada imputasi angka buatan.
- Tidak ada baris NaN buatan di Gold.
- Seluruh observasi asli dipertahankan; outlier dan patahan seri tidak dihapus (K-002).
- Agregat nasional `9999` dipisahkan agar tidak terjadi double counting.

## 4. Tabel nasional

Tabel nasional kanonis berisi 114 baris dari tujuh seri:

| Sumber | Seri | Baris | Periode | Rincian Gold |
|---|---|---:|---|---|
| BPS | var1473 | 9 | 2017–2025 | Total |
| BPS | var1474 | 9 | 2017–2025 | Total |
| WDI | SN.ITK.DEFC.ZS | 24 | 2001–2024 | Total |
| WDI | SN.ITK.MSFI.ZS | 10 | 2015–2024 | Total |
| WHO | NUTSTUNTINGPREV | 25 | 2000–2024 | `SEX=TOTAL` |
| WHO | NUTOVERWEIGHTPREV | 25 | 2000–2024 | `SEX=TOTAL` |
| WHO | NUTRITION_WH_2 | 12 | 1996–2023 | `SEX=TOTAL; AGE=TOTAL` |

Kunci unik tabel nasional adalah `(sumber, seri_kode, periode)`. Rincian WHO dipilih di Gold,
bukan di Silver, sesuai K-004, K-010, dan K-012. Untuk wasting, tiga varian baris total di
Silver (`TOTAL`, `SEX=TOTAL; AGE=TOTAL`, dan baris semua-dimensi-TOTAL) memiliki nilai yang
identik pada seluruh 12 tahun; validator memeriksa kesamaan ini sebelum Gold ditulis.

## 5. Satuan dan transformasi

Seluruh tujuh seri menggunakan satuan kanonis `persen` (K-006). Tidak ada pencampuran satuan
dalam satu kolom nilai dan tidak ada normalisasi/standardisasi yang mengubah nilai. Kolom
`nilai` pada Gold adalah salinan nilai Silver asli. Dengan demikian nilai asli tetap tersedia
dan dapat ditelusuri.

## 6. Perbandingan dan keterbandingan

BPS PoU/FIES dan WDI sama-sama indikator SDG 2.1.1/2.1.2, tetapi definisi, metode estimasi,
dan vintage dapat berbeda. WDI diposisikan sebagai pembanding, bukan pengganti. Pada irisan
2017–2024:

- Selisih BPS PoU terhadap WDI PoU berkisar +1,23 sampai +3,61 poin persentase.
- Selisih BPS FIES terhadap WDI FIES berkisar −0,38 sampai +1,06 poin persentase.

Selisih tersebut dijelaskan, bukan dihapus. WHO stunting/overweight/wasting mengukur kondisi
balita (SDG 2.2.x) dan **tidak setara** dengan PoU/FIES; kolom
`dapat_dibandingkan_dengan` dan `catatan_perbandingan` menandai hal ini. WHO wasting tidak
menerbitkan observasi tahunan penuh; tahun yang tidak ada dibiarkan kosong.

## 7. Struktur output

| Berkas | Format | Baris | Fungsi |
|---|---|---:|---|
| `data/gold/panel_provinsi.parquet` | long | 628 | panel provinsi × periode × indikator |
| `data/gold/tabel_nasional.parquet` | long | 114 | tabel nasional kanonis + lineage |
| `data/gold/tabel_nasional_lebar.parquet` | wide | 30 | view nasional berdampingan |

`baris_gold` yang dilaporkan = 628 + 114 = **742**, yaitu baris tabel Gold kanonis.
`tabel_nasional_lebar` adalah view turunan 30 baris; nilainya tidak dihitung ulang dalam
`baris_gold` agar tidak terjadi double counting. View lebar memuat tahun 1996–2025; 1997–1999
kosong karena tidak ada observasi pada seri mana pun dan tidak diimputasi.

Definisi kolom lengkap ada di `docs/data-dictionary.md`.

## 8. Traceability dan validasi

Setiap baris panel dan tabel nasional dapat ditelusuri ke Silver melalui kunci lengkap
`sumber + seri_kode + wilayah_kode + periode + rincian + _berkas_raw + _sha256_raw`.
Validator memastikan:

- 628 baris panel; 314 per seri; 38 provinsi; 9 periode; 0 duplikat; 0 nilai/lineage kosong.
- 114 baris nasional; 7 seri; 0 duplikat; 0 nilai/lineage kosong.
- Semua satuan `persen`; semua nilai berada di 0–100.
- Rincian WHO yang dipilih tepat dan varian total wasting identik.
- View lebar 30 baris, 114 sel terisi, dan setiap nilai sama dengan tabel long.
- Build dijalankan ulang menghasilkan tabel yang sama (idempoten).

Hasil pengujian:

```text
python pipeline.py                              exit 0, Gold tertulis
tests/test_gold.py                              8 tests OK
tests/test_periode.py                           7 tests OK
python -m unittest discover -s tests -v         15 tests OK
python -m src.common.skema data/silver/silver.parquet
                                                LOLOS 1.439 baris, 7 seri,
                                                39 wilayah, 6 berkas
```

## 9. Metrik

Metrik Sprint 1 dipertahankan dan metrik Sprint 2 ditambahkan dalam satu pembaruan:

- Sprint 1 katalog: `berkas_dibaca=14`, `seri_diperiksa=7`, `satuan_terverifikasi=7`,
  `kode_sdg_terverifikasi=7`, `koreksi_satuan=2`, `koreksi_kode_sdg=2`,
  `periode_non_tahunan=0`, `nilai_di_luar_0_100=0`, `keputusan_dicatat=3`.
- Sprint 1 Silver: `seri_silver=7`, `rincian_dienkode=73`, `baris_silver=1439`.
- Sprint 2: `seri_panel=2`, `baris_panel=628`, `baris_nasional=114`, `baris_gold=742`,
  `baris_nasional_lebar=30`, `keputusan_gold=3`.

## 10. Keputusan teknis

- **K-011:** panel Gold long, hanya observasi provinsi, 9999 dipisahkan, 56 sel struktural
  tidak diimputasi.
- **K-012:** pemilihan rincian WHO Gold; semua varian total wasting diverifikasi identik.
- **K-013:** tabel nasional kanonis long + view lebar; indikator berbeda definisi tidak
  digabung.

## 11. Batasan

- Tahap Validasi (`src/validasi/`) masih milik komponen lain dan belum tersedia; pipeline
  berhenti dengan status “Gold selesai; Validasi tertunda”.
- Pembaca BPS/WHO di `src/ekstraksi/` masih menghasilkan peringatan, tetapi Gold membaca
  Silver langsung sesuai kontrak proyek.
- K-009 masih menunggu klarifikasi koordinator; baris `15,7` tetap tidak masuk Silver dan
  tidak memengaruhi rincian total WHO yang dipakai Gold.

## 12. Reproduksi

```bash
python pipeline.py
python tests/test_gold.py
python tests/test_periode.py
python -m unittest discover -s tests -v
python -m src.common.skema data/silver/silver.parquet
```
