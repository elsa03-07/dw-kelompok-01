# Laporan Profiling dan Pemeriksaan Data
## Capstone Sprint 0: Kerawanan Pangan Provinsi

**Kelompok:** 01  
**Nama:** Daffa Kharisma Adzana  
**NIM:** 124450061  
**Komponen:** Profil dan Pembersihan Data  
**Kasus:** Case 01 - Kerawanan Pangan Provinsi  
**SDG:** 2 - Zero Hunger

### 1. Tujuan

Melakukan pemeriksaan awal terhadap data mentah untuk mengetahui struktur data, jumlah baris dan kolom, nilai kosong, duplikasi, tipe data, serta potensi anomali sebelum proses pembersihan dan transformasi.

### 2. Hasil Profiling Umum

Proses profiling dilakukan menggunakan Python dan Pandas terhadap file dalam folder `data/raw/`.

Hasil pembacaan:
- Total tabel atau struktur yang berhasil dibaca: 18.
- File manifest dikecualikan dari profiling.
- Tidak ditemukan kesalahan pembacaan file.

Catatan: Angka 18 menunjukkan jumlah tabel atau struktur yang diprofilkan, bukan jumlah file mentah.

### 3. Hasil Pemeriksaan Data BPS

Dua indikator utama yang diperiksa:

| Pemeriksaan | var1473 | var1474 |
|---|---:|---:|
| Jumlah baris | 323 | 323 |
| Jumlah kolom | 11 | 11 |
| Rentang tahun | 2017–2025 | 2017–2025 |
| Jumlah wilayah unik | 39 | 39 |
| Baris duplikat | 0 | 0 |
| Nilai kosong | 0 | 0 |
| Nilai minimum | 1,43 | 0,76 |
| Nilai maksimum | 38,35 | 27,54 |
| Nilai di bawah 0 | 0 | 0 |
| Nilai di atas 100 | 0 | 0 |

Kedua indikator memiliki struktur kolom yang sama, yaitu:
`var_id`, `wilayah_id`, `wilayah`, `turvar_id`, `turvar`, `tahun_id`, `tahun`, `periode_id`, `periode`, `nilai`, dan `satuan`.

### 4. Perubahan Jumlah Wilayah

Ditemukan perubahan jumlah wilayah dalam data BPS:

| Periode | Jumlah wilayah | Keterangan |
|---|---:|---|
| 2017–2023 | 35 | 34 provinsi dan 1 agregat nasional |
| 2024–2025 | 39 | 38 provinsi dan 1 agregat nasional |

Perubahan berkaitan dengan pemekaran wilayah Papua. Empat provinsi baru yang muncul dalam data adalah:
1. Papua Barat Daya
2. Papua Selatan
3. Papua Tengah
4. Papua Pegunungan

Kode wilayah `9999` dengan nama `INDONESIA` merupakan agregat nasional, bukan provinsi.

### 5. Temuan Data WHO dan WDI

**WHO:**
- Beberapa kolom dimensi memiliki nilai kosong dalam jumlah besar.
- Nilai kosong dapat menunjukkan dimensi yang tidak berlaku untuk observasi tertentu.
- Nilai kosong tidak langsung dihapus sebelum maknanya diperiksa.
- Salah satu file nutrisi WHO memiliki 610 baris dan 22 kolom.

**WDI:**
- File observasi memiliki 2.112 record.
- Kolom `value` memiliki 849 nilai tersedia dan 1.263 nilai kosong.
- File memuat berbagai indikator, sehingga nilai kosong perlu diperiksa berdasarkan kode indikator dan relevansinya terhadap kasus kerawanan pangan.

### 6. Keputusan Awal Pembersihan

1. Data mentah tidak diubah secara langsung.
2. Kolom nilai indikator dipastikan bertipe numerik.
3. Kode wilayah dipertahankan sebagai identitas wilayah.
4. Kode `9999` dipisahkan dari kelompok provinsi.
5. Data provinsi hasil pemekaran tetap dipertahankan.
6. Nilai kosong WHO dan WDI tidak langsung dihapus.
7. Data duplikat diperiksa berdasarkan seluruh kolom sebelum penghapusan.
8. Satuan dan periode observasi dipertahankan agar interpretasi data tidak berubah.

### 7. Kesimpulan

Profiling awal berhasil dilakukan terhadap 18 tabel atau struktur data. Dua indikator utama BPS tidak menunjukkan nilai kosong, baris duplikat, maupun nilai di luar rentang 0–100.

Perubahan jumlah provinsi dari 34 menjadi 38 mulai terlihat pada tahun 2024. Hal ini perlu diperhatikan dalam proses integrasi dan perbandingan antarwilayah.

Data WHO dan WDI memerlukan pemeriksaan lanjutan karena memiliki nilai kosong dan struktur data yang lebih kompleks.

Laporan ini menjadi dasar untuk proses pembersihan, transformasi, dan penyusunan data Silver pada tahap berikutnya.

......