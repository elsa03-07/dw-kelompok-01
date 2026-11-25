# Rancangan Skema SQL Silver: Kunci Primer, Tipe Kolom, dan Pilihan Basis Data

**Penyusun:** DAFFA KHARISMA ADZANA (124450061)  
**Komponen:** Profil dan Pembersihan / Penyimpanan SQL (Tahap 5)  
**Tugas Sampingan:** Penjaga Data & Evaluasi  
**Repositori:** Kelompok 1 — Capstone Data Wrangling  
**Tanggal:** 21 November 2026  

---

## 1. Pendahuluan dan Tujuan
Sebagai bagian dari persiapan Tahap 5 (Penyimpanan SQL), dokumen ini merancang skema relasional tabel *Silver*, mendefinisikan kunci primer (*Primary Key*) komposit, memetakan tipe data kolom yang ketat, serta mengevaluasi pilihan arsitektur basis data.

Pipeline pemuatan telah diimplementasikan dalam skrip [src/silver/muat_sql.py](file:///C:/Users/daffascript_/workbench-workspace/capstone-data-wrangling/src/silver/muat_sql.py) dan skema DDL di [src/silver/skema_silver.sql](file:///C:/Users/daffascript_/workbench-workspace/capstone-data-wrangling/src/silver/skema_silver.sql). Skrip telah berhasil memuat seluruh 1.439 baris dari `data/silver/silver.parquet` ke dalam basis data `data/silver/silver.sqlite`.

---

## 2. Rancangan Skema DDL dan Definisi Kunci

### 2.1. Skema DDL SQL
```sql
CREATE TABLE IF NOT EXISTS silver (
    sumber VARCHAR(20) NOT NULL,
    seri_kode VARCHAR(50) NOT NULL,
    wilayah_kode INTEGER NOT NULL,
    nama_wilayah VARCHAR(100) NOT NULL,
    periode VARCHAR(20) NOT NULL,
    jenis_periode VARCHAR(20) NOT NULL,
    rincian VARCHAR(255) NOT NULL,
    nilai REAL NOT NULL,
    satuan VARCHAR(50) NOT NULL,
    _berkas_raw VARCHAR(255) NOT NULL,
    _sha256_raw VARCHAR(64) NOT NULL,
    -- Kunci Primer Komposit 6 Dimensi
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)
);

CREATE INDEX IF NOT EXISTS idx_silver_seri_wilayah ON silver (seri_kode, wilayah_kode);
CREATE INDEX IF NOT EXISTS idx_silver_periode ON silver (periode);
CREATE INDEX IF NOT EXISTS idx_silver_sumber ON silver (sumber);
```

### 2.2. Definisi Kunci Primer Komposit (*Composite Primary Key*)
Kunci primer tabel *Silver* terdiri atas 6 atribut gabungan:
$$\text{PK} = \{\text{sumber}, \text{seri\_kode}, \text{wilayah\_kode}, \text{periode}, \text{rincian}, \text{\_berkas\_raw}\}$$

**Justifikasi:**
1. **Pemisahan Sumber Multi-Snapshot:** Pada layer Silver, data dari sumber berbeda (misal BPS vs WDI vs WHO) sengaja tidak digabungkan. Atribut `sumber` dan `_berkas_raw` memastikan observasi dari dua berkas snapshot yang berbeda tetap dapat diidentifikasi secara unik.
2. **Granularitas Observasi:** Kombinasi `seri_kode` + `wilayah_kode` + `periode` + `rincian` memastikan bahwa untuk indikator yang sama, setiap kombinasi wilayah (kode BPS / 9999), tahun, dan rincian (misal disagregasi gender balita pada WHO GHO) hanya memiliki satu nilai tunggal.
3. **Penegakan Integritas Otomatis:** Mesin SQL menolak secara otomatis bila terjadi duplikasi baris atau data korup (*duplicate key constraint violation*), terbukti pada hasil uji coba di `muat_sql.py`.

---

## 3. Alasan Pemilihan Basis Data (SQLite & DuckDB)

Dalam memenuhi parameter capstone (komputasi $\le$ 15 menit di laptop standar CPU 8 GB RAM, tanpa dependensi berbayar/server luar), tim memilih **SQLite** (didukung oleh **DuckDB** untuk analitik kolumnar):

1. **Embedded & Zero-Configuration:**
   - Tidak memerlukan instalasi *database daemon* atau server terpisah (seperti PostgreSQL/MySQL).
   - Seluruh basis data disimpan dalam satu berkas portabel (`data/silver/silver.sqlite`), sehingga seluruh anggota tim dan dosen pembimbing dapat menjalankan ulang pipeline secara instan di lingkungan kerja mana pun.
2. **Kepatuhan ACID dan Integritas Relasional:**
   - SQLite mendukung penuh standar SQL, transaksi ACID, dan penegakan *Primary Key* serta batasan `NOT NULL`.
3. **Efisiensi Memori & Kecepatan Baca:**
   - Ukuran basis data SQLite untuk 1.439 baris sangat ringkas ($< 200$ KB), jauh di bawah batas commit GitHub (20 MB).
   - Bersama Parquet dan DuckDB, SQLite menyediakan ekosistem terpadu antara penyimpanan transaksional dan kueri analitik OLAP berkecepatan tinggi.

---

## 4. Perbandingan: Tabel Relasional SQL vs Dokumen Mentah JSON

| Dimensi Evaluasi | Penyimpanan Respons Mentah JSON (Document Store) | Tabel Terstruktur SQL (Silver SQLite) |
|---|---|---|
| **Paradigma Skema** | *Schema-on-read* (struktur fleksibel, tanpa penegakan skema awal). | *Schema-on-write* (tipe data, kolom, dan kunci ditegakkan saat data dimuat). |
| **Integritas & Tipe Data** | Lemah. Tipe data rentan bercampur (angka terbaca string, null ambigu). | Sangat kuat. Tipe `INTEGER`, `REAL`, `VARCHAR`, dan `NOT NULL` terjamin. |
| **Pencegahan Duplikasi** | Rentan ganda karena tidak ada mekanisme *Primary Key* bawaan. | Dijamin oleh *Composite Primary Key* 6 dimensi. |
| **Efisiensi Kueri Analitis** | Lambat. Membutuhkan *full JSON parsing* dan penelusuran hierarki setiap kali difilter. | Sangat cepat. Menggunakan indeks B-Tree (`idx_silver_...`) dan kueri relasional teroptimasi. |
| **Ukuran Penyimpanan** | Boros. Kunci JSON (*keys*) diulang di setiap rekaman dokumen. | Hemat dan terkompresi. Struktur tabel hanya mendefinisikan skema sekali di katalog. |
| **Kesesuaian Tahapan** | Cocok untuk lapis *Bronze* (arsip respons asli API BPS/WDI). | Sangat ideal untuk lapis *Silver* dan persiapan *Gold* (siap analisis panel). |

**Kesimpulan:**  
Format dokumen mentah JSON dipertahankan pada lapis *Bronze* sebagai bukti otentik *lineage*, sedangkan tabel relasional SQL adalah standar mutlak pada lapis *Silver* untuk menjamin akurasi analisis numerik, kepatuhan skema, dan performa pemrosesan data SDG antarprovinsi.
