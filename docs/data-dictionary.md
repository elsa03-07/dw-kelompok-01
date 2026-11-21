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

Tabel terstandarisasi lapis Silver memuat 1.439 baris observasi ber-provenans dari 7 seri indikator kerawanan pangan dan gizi (BPS, WDI, dan WHO GHO).

| Kolom | Tipe Data | Satuan / Format | Boleh Kosong? | Rentang atau Nilai Sah | Asal (Berkas / Aturan Log) | Keterangan & Definisi |
|---|:---:|:---:|:---:|---|---|---|
| `sumber` | string | — | Tidak (0 null) | `bps`, `wdi`, `who_gho` (whitelist: bps, bnpb, wdi, who_gho, ilostat) | Nama folder `data/raw/<sumber>/...` | Lembaga/organisasi resmi penyedia data mentah. |
| `seri_kode` | string | — | Tidak (0 null) | `var1473`, `var1474`, `SN.ITK.DEFC.ZS`, `SN.ITK.MSFI.ZS`, `NUTSTUNTINGPREV`, `NUTOVERWEIGHTPREV`, `NUTRITION_WH_2` | Kode berkas CSV BPS atau atribut indikator JSON WDI / CSV WHO | Pengenal unik seri indikator SDG 2 (Prevalensi Ketidakcukupan Pangan, Kerawanan Sedang/Berat, Stunting, Wasting, Overweight). |
| `wilayah_kode` | int | Kode numerik | Tidak (0 null) | `9999` (Indonesia) atau `1100`–`9700` (38 Provinsi Indonesia 2025) | Keputusan `log-keputusan.csv` K-001 (pemetaan standar 38 provinsi) & `wilayah_id` BPS | Kode identifikasi wilayah administratif resmi standar BPS (kode provinsi 2-digit $\times$ 100) atau 9999 untuk nasional. |
| `nama_wilayah` | string | Teks Huruf Kapital | Tidak (0 null) | `INDONESIA`, `ACEH`, `SUMATERA UTARA`, ..., `PAPUA PEGUNUNGAN` (39 nama unik) | Kolom `wilayah` pada CSV BPS; nama negara pada WDI & WHO | Nama baku entitas wilayah geografis tempat pengukuran dilakukan. |
| `periode` | string | `YYYY` | Tidak (0 null) | `1996` s.d. `2025` (rentang 4 digit tahun kalender) | Kolom `tahun` (BPS), `date` (WDI), `DIM_TIME` (WHO GHO) | Tahun kalender pelaksanaan pengukuran/estimasi survei. |
| `jenis_periode` | string | — | Tidak (0 null) | `tahun` | Standarisasi frekuensi observasi | Granularitas temporal data; seluruh seri pada Kasus 01 memiliki periode tahunan. |
| `rincian` | string | — | Tidak (0 null) | `Total` (BPS & WDI), atau rincian disagregasi WHO seperti `SEX=BTSX`, `SEX=FMLE`, `SEX=MLE`, atau atribut `DIM_` | Atribut dimensi WHO GHO atau default `Total` | Keterangan rincian sub-kelompok populasi (gender balita, kelompok usia, atau total populasi). |
| `nilai` | float | Desimal | Tidak (0 null) | $0.00$ s.d. $100.00$ (rentang aktual: $0.38$ s.d. $53.30$) | Kolom `nilai` (BPS), `value` (WDI), `RATE_PER_100_N` (WHO GHO) | Angka prevalensi terukur dalam skala persentase. |
| `satuan` | string | — | Tidak (0 null) | `persen` | Katalog seri terverifikasi | Satuan pengukuran resmi data (seluruh seri diseragamkan ke satuan kanonis `persen`). |
| `_berkas_raw` | string | Path relatif | Tidak (0 null) | Path relatif valid terhadap `data/raw/` (mis. `bps/2026-10-20/sdg2_2_1_1_v1473.csv`) | Jejak pembacaan berkas saat tahap ekstraksi | Tautan silsilah data (*provenance lineage*) ke berkas mentah asal observasi. |
| `_sha256_raw` | string | Hex 64 karakter | Tidak (0 null) | Hash SHA-256 terdaftar di `data/raw/MANIFEST.csv` | Fungsi `src.common.manifest.sha256_raw` | Sidik kriptografis berkas mentah untuk audit integritas dan replikabilitas. |

---

## Contoh Penelusuran Baris Silver ke Berkas Mentah (Data Lineage Trace)

Sebagai bukti bahwa seluruh data pada lapis *Silver* dapat ditelusuri (*fully traceable and reproducible*), berikut adalah contoh penelusuran satu baris observasi riil:

### 1. Baris Observasi pada `data/silver/silver.parquet`
```json
{
  "sumber": "bps",
  "seri_kode": "var1473",
  "wilayah_kode": 1100,
  "nama_wilayah": "ACEH",
  "periode": "2024",
  "jenis_periode": "tahun",
  "rincian": "Total",
  "nilai": 9.1,
  "satuan": "persen",
  "_berkas_raw": "bps/2026-10-20/sdg2_2_1_1_v1473.csv",
  "_sha256_raw": "bef21c5a1dd5f724058aa745830f0d8444f506b1029fecf8cb48a75d68b31b0d"
}
```

### 2. Verifikasi Integritas Berkas di `data/raw/MANIFEST.csv`
Atribut `_sha256_raw` dicocokkan dengan entri manifes:
```csv
bps/2026-10-20/sdg2_2_1_1_v1473.csv,20837,bef21c5a1dd5f724058aa745830f0d8444f506b1029fecf8cb48a75d68b31b0d
```
- Ukuran berkas mentah: **20.837 byte**.
- Nilai hash SHA-256: **`bef21c5a1dd5f724058aa745830f0d8444f506b1029fecf8cb48a75d68b31b0d`** (cocok 100%).

### 3. Penelusuran ke Berkas Mentah Asal
Membuka berkas fisik `data/raw/bps/2026-10-20/sdg2_2_1_1_v1473.csv`:
- **Baris CSV:** Indeks ke-7 (baris ke-9 pada berkas teks).
- **Nilai mentah:**
  ```text
  var_id: 1473
  wilayah_id: 1100
  wilayah: ACEH
  tahun: 2024
  periode: Tahun
  nilai: 9.1
  satuan: Persen
  ```

### 4. Transformasi yang Diterapkan oleh Pipeline
1. `var_id` $\rightarrow$ dipetakan ke kode kanonis `var1473` (Prevalensi Ketidakcukupan Konsumsi Pangan / PoU).
2. `wilayah_id` $\rightarrow$ diverifikasi bernilai `1100` (Aceh) sesuai standar 38 provinsi di `log-keputusan.csv` K-001.
3. `tahun` & `periode` $\rightarrow$ dinormalisasi menjadi `periode: "2024"` dan `jenis_periode: "tahun"`.
4. `satuan` $\rightarrow$ dinormalisasi dari teks `"Persen"` menjadi `"persen"`.
5. `rincian` $\rightarrow$ diset menjadi `"Total"` karena indikator BPS merupakan agregat seluruh populasi provinsi.
6. `_berkas_raw` & `_sha256_raw` $\rightarrow$ disematkan otomatis dari manifes pembacaan data.

---

## data/gold/<tabel>.parquet

*(Bagian ini akan ditambahkan pada Sprint 2 dan Sprint 3 setelah transformasi panel Gold dan tabel rekonsiliasi dibentuk).*
