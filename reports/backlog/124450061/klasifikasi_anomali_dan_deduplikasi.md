# Klasifikasi Anomali, Patahan Seri, Galat Input, dan Aturan Deduplikasi

**Penyusun:** Daffa Kharisma Adzana (124450061)  
**Komponen:** Profil dan Pembersihan Data (Tahap 2 & 3)  
**Tugas Backlog:** #8 (Prioritas: Mendesak, Poin: 3)  
**Kasus:** Kasus 01 — Kerawanan Pangan Provinsi (SDG 2)  
**Tanggal:** 12 November 2026  

---

## 1. Landasan Prinsip Wrangling

Dalam proses penanganan kualitas data lapis Bronze ke Silver, terdapat tiga fenomena data ekstrem yang sering kali tertukar dan diperlakukan keliru:
1. **Outlier Asli (*True Extreme Values*)**
2. **Patahan Seri (*Structural Break*) akibat Perubahan Metodologi atau Batas Wilayah**
3. **Galat Input (*Data Entry Error*)**

**Prinsip Emas Capstone:**
> *Hanya galat input yang boleh diperbaiki atau dikoreksi. Outlier asli dan patahan seri TIDAK BOLEH dihapus atau diubah angkanya, melainkan wajib ditandai, diklasifikasikan, dan dijelaskan latar belakang penyebabnya secara tertulis.*

---

## 2. Pemisahan Tiga Kategori Anomali pada Seri Utama BPS

Dari hasil deteksi statistika (metode IQR tahunan dan Z-Score $|z| \ge 2.0$), teridentifikasi sebanyak 61 observasi pencilan. Seluruhnya telah diklasifikasikan secara rinci pada berkas [`reports/profiling/daftar_anomali_terklasifikasi.csv`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/reports/profiling/daftar_anomali_terklasifikasi.csv).

### Ringkasan Distribusi Klasifikasi:

| Kategori Anomali | Jumlah Baris | Wilayah & Periode Terdampak | Perlakuan Wrangling |
|---|:---:|---|---|
| **Outlier Asli (Sosio-Geografis)** | 45 | Maluku (8100), Maluku Utara (8200), Papua lama (9400 thn 2017–2023), Kalimantan Utara (6500 thn 2022) | **Dipertahankan utuh**. Angka mencerminkan disparitas struktural nyata rantai pasok kepulauan dan pedalaman. |
| **Patahan Seri (Pemekaran DOB Papua)** | 10 | 4 DOB baru: Papua Barat Daya (9200), Papua Selatan (9500), Papua Tengah (9600), Papua Pegunungan (9700), serta penurunan drastis induk Papua (9400) pada 2024–2025 | **Dipertahankan & Ditandai**. Tercatat sebagai dampak pemekaran administratif 2024, bukan penurunan kerawanan riil secara tiba-tiba. |
| **Patahan Seri (Metodologi FIES Awal)** | 3 | NTT (5300) dan Gorontalo (7500) pada 2017–2018 | **Dipertahankan & Ditandai**. Merupakan fase inisiasi survei instrumen FIES pada Susenas sebelum stabilisasi tren. |
| **Patahan Seri (Kejutan Makro Pandemi/Pangan)** | 3 | Pergeseran mean serentak nasional pada 2020 (COVID-19) dan 2022 (Krisis Pangan Global) | **Dipertahankan & Ditandai**. Fenomena sistemik yang terjadi serentak antardaerah. |
| **Galat Input** | **0** | Tidak ditemukan nilai negatif, nilai $> 100\%$, atau kesalahan ketik desimal | **Tidak ada baris yang perlu diperbaiki/dihapus**. |

---

## 3. Penjelasan Mendalam Patahan Seri Pemekaran Papua (2024)

Bukti konkret patahan seri akibat perubahan batas wilayah:
- Pada periode 2017–2023, induk Provinsi Papua (9400) mencatat PoU sebesar $34.27\% - 38.35\%$.
- Pada tahun 2024, angka PoU induk Papua turun tajam menjadi $26.03\%$.
- Di saat yang sama, provinsi baru hasil pemekaran wilayah pegunungan, yaitu Papua Tengah (9600), mencatat PoU sebesar $37.69\%$, dan Papua Pegunungan (9700) sebesar $27.26\%$.
- **Kesimpulan:** Penurunan angka di Provinsi Papua pada 2024 adalah **patahan seri (*structural break*)**, bukan anomali kesalahan data atau lonjakan keberhasilan intervensi pangan. Wilayah dengan kerawanan pangan paling rawan telah terpisah secara administratif menjadi provinsi tersendiri.

---

## 4. Aturan Deduplikasi Multi-Snapshot

Data mentah diunduh dalam bentuk snapshot bertanggal (misalnya `2026-10-17` dan `2026-10-20`). Untuk menjamin reproduksibilitas lineage tanpa menimbulkan duplikasi baris ganda, ditetapkan aturan tertulis berikut:

### Aturan Baku Deduplikasi:
1. **Kunci Observasi Identik & Nilai Sama**:
   - Jika satu baris data memiliki kombinasi kunci identik (`sumber + seri_kode + wilayah_kode + periode + rincian`) dan memiliki nilai angka yang sama pada kedua snapshot, observasi tersebut **bukan duplikat yang salah**, melainkan konfirmasi kestabilan data. Hanya 1 baris yang disimpan di tabel Silver, dengan mencatat lineage berkas snapshot terkait.
2. **Kunci Observasi Identik & Nilai Berbeda**:
   - Jika terdapat perbedaan angka pada periode dan wilayah yang sama antara snapshot lama dan snapshot baru, baris tersebut **diklasifikasikan sebagai Revisi Resmi Produsen Data**.
   - **Perlakuan:** Nilai dari snapshot terbaru yang dipertahankan sebagai data final di Silver/Gold, sementara perbedaan angka dicatat ke dalam log keputusan sebagai jejak revisi produsen data.

---

## 5. Bukti Pencatatan di `log-keputusan.csv`

Keputusan-keputusan ini telah didokumentasikan secara formal pada file [`log-keputusan.csv`](file:///C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling/log-keputusan.csv) dengan rujukan ID:
- **`K-002`**: Klasifikasi dan perlakuan anomali seri utama (pemisahan outlier asli sosio-geografis vs patahan seri pemekaran wilayah Papua tanpa penghapusan baris).
- **`K-003`**: Aturan deduplikasi multi-snapshot dan resolusi revisi angka produsen data.
- **`K-004`**: Penyaringan rincian seri pembanding WHO GHO pada agregat total balita.
