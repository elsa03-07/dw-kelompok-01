# Verifikasi Satuan dan Kode SDG Tujuh Seri

**Penyusun:** Ni Made Okta Viola Darma Putri (124450005)  
**Komponen:** Validasi dan dokumentasi  
**Tugas:** Tahap 4 (persiapan) — verifikasi katalog seri  
**Kasus:** Kasus 01 — Kerawanan Pangan Provinsi (SDG 2)  
**Tanggal:** 18 November 2026

---

## 1. Tujuan

Memeriksa ulang satuan, kode SDG, dan nama seri pada katalog awal terhadap judul tabel
serta metadata di berkas mentah. Satuan yang kosong atau tidak cocok dengan besaran nilai
ditetapkan ulang, lalu setiap koreksi dicatat di `log-keputusan.csv`.

Berkas hasil mesin: [`katalog_seri_terverifikasi.csv`](katalog_seri_terverifikasi.csv).

## 2. Metode

1. Membaca metadata mentah tiap sumber:
   - BPS: kolom `satuan`, `periode`, dan `var[0].unit`/`var[0].label` pada JSON.
   - WDI: `indicator.value`, field `unit`, `date`, dan metadata indikator `source46`.
   - WHO GHO: `UnitOfMeasure`, `ValueDisplayLabel`, `IndicatorName`, `FullName`, dan `DIM_TIME_TYPE`.
2. Menghitung ulang jumlah observasi, nilai minimum, dan nilai maksimum dari nilai mentah.
3. Menetapkan satu satuan kanonis per seri. Semua seri menggunakan `persen`; nilai berada
   pada rentang 0–100 sehingga konsisten dengan satuan tersebut.
4. Memeriksa jenis periode. BPS memakai `periode=Tahun`, WHO memakai `DIM_TIME_TYPE=YEAR`,
   dan WDI memakai `date` empat digit. Tidak ada periode semesteran atau bulanan pada tujuh seri.
5. Menjalankan `verifikasi_katalog.py` untuk mengulang pemeriksaan secara otomatis dari `data/raw/`.

## 3. Hasil per Seri

| Sumber | Seri | Satuan final | Kode SDG | Periode | Nilai (min–maks; n) | Status katalog awal |
|---|---|---|---|---|---|---|
| BPS | `var1473` | persen | 2.1.1 | tahun | 1,43–38,35; 323 | cocok |
| BPS | `var1474` | persen | 2.1.2 | tahun | 0,76–27,54; 323 | cocok |
| WDI | `SN.ITK.DEFC.ZS` | persen | 2.1.1 | tahun | 6,0–18,4; 24 | dikoreksi |
| WDI | `SN.ITK.MSFI.ZS` | persen | 2.1.2 | tahun | 4,2–7,6; 10 | dikoreksi |
| WHO GHO | `NUTSTUNTINGPREV` | persen | 2.2.1 | tahun | 21,2–41,3; 75 | cocok |
| WHO GHO | `NUTOVERWEIGHTPREV` | persen | 2.2.2 | tahun | 2,4–9,1; 75 | cocok |
| WHO GHO | `NUTRITION_WH_2` | persen | 2.2.2 | tahun | 3,4–22,2; 610 | cocok |

Sumber bukti per baris (berkas dan field mentah) tercatat lengkap di
`katalog_seri_terverifikasi.csv`.

## 4. Koreksi yang Ditetapkan

1. **Satuan WDI.** Field `unit` pada data WDI kosong dan katalog awal menulis `tidak_ada`.
   Judul kedua indikator memuat `(%)`/`(% of population)`, dan seluruh nilai berada di 0–100.
   Satuan kanonis ditetapkan `persen` (K-006).
2. **Kode SDG WDI.** Katalog awal menulis `—` untuk kedua seri. Judul indikator sepadan dengan
   definisi SDG 2.1.1 (PoU) dan 2.1.2 (FIES), sehingga kode diisi `2.1.1` dan `2.1.2` (K-007).
3. **Granularitas periode.** Tujuh seri terverifikasi tahunan. Tidak ada perataan semesteran
   atau bulanan ke tahunan; nilai tahunan dipertahankan sebagaimana dipublikasikan (K-008).

Catatan: berkas mentah WDI/WHO tidak memuat field kode SDG eksplisit. Pemetaan kode dilakukan
dari judul/nama indikator ke indikator SDG resmi; sumber judul dan metadata pencocoknya dicatat
pada kolom `sumber_kode_sdg`.

## 5. Verifikasi Ulang

```bash
python reports/backlog/124450005/verifikasi_katalog.py
```

Skrip hanya memakai pustaka standar Python, membaca `data/raw/`, dan akan gagal bila:

- ada seri yang hilang/duplikat atau satuan/kode SDG kosong;
- satuan atau kode SDG tidak sama dengan hasil pemeriksaan metadata;
- nilai berada di luar 0–100;
- ditemukan periode non-tahunan.

## 6. Checklist Selesai

- [x] Tujuh seri memiliki satu satuan kanonis.
- [x] Tujuh seri memiliki kode SDG.
- [x] Berkas dan field sumber satuan/kode SDG tercatat.
- [x] Setiap koreksi katalog tercatat di `log-keputusan.csv` (K-006, K-007).
- [x] Aturan tidak merata-ratakan periode non-tahunan dicatat (K-008).
