# Laporan perorangan — Zannuba Arifah Ilman (124450112), komponen Ekstraksi dan lineage

Salin berkas ini menjadi `reports/individu/<nim>.md`. Paling banyak 1200 kata di luar tabel
dan kode. Setiap klaim angka harus dapat ditelusuri ke kode atau keluaran yang sudah di-*commit*.

## 1. Komponen saya
Sebagai Integrator dengan fokus pada komponen Ekstraksi dan lineage, saya bertanggung jawab menyiapkan infrastruktur awal pipeline, melakukan ingestion, dan menjamin keterlacakan data mentah hingga tahap siap olah. Peran ini memastikan seluruh 15 berkas data Kasus 07 (BPS dan WDI) terunduh dan terverifikasi sesuai checksum MANIFEST.csv. Komponen ini menjadi landasan integritas data awal agar tahap pembersihan dan transformasi anggota tim lain dapat berjalan secara konsisten.

## 2. Keputusan wrangling
Keputusan wrangling utama pada tahap ini adalah penetapan skema pengkodean wilayah_kode berbasis susunan 38 provinsi BPS tahun 2025 (kode 2 digit BPS $\times 100$) serta penentuan kode $9999$ untuk tingkat agregat nasional Indonesia. Alternatif yang ditolak adalah pencocokan berbasis string nama provinsi serta pembobotan jumlah penduduk untuk provinsi hasil pemekaran. Alternatif tersebut ditolak karena variasi ejaan nama provinsi antarberkas tidak seragam dan opsi pembobotan memerlukan data populasi tambahan. Keputusan ini menjaga konsistensi key antarberkas tanpa mengubah jumlah baris data utama (dampak baris: 0). Rujukan keputusan: K-001.

## 3. Kegagalan dan pelajaran
Kegagalan nyata yang dialami pada awal eksekusi adalah terblokirnya skrip aktivasi virtual environment (.venv\Scripts\Activate.ps1) oleh kebijakan keamanan PowerShell (PSSecurityException), yang sempat menghambat pengujian dependensi pipeline. Perubahan yang diambil adalah menerapkan penyesuaian hak eksekusi sesi terminal melalui Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass serta memverifikasi kembali konfigurasi identitas Git dan Personal Access Token (PAT). Pelajaran utamanya adalah pentingnya isolasi environment dan validasi otorisasi akses sebelum menjalankan pengujian otomatisasi pipeline.

## 4. Bukti
Sebelum vs sesudah: jumlah baris, sel kosong, atau statistik yang relevan, beserta perintah untuk
menghasilkannya ulang.

| Ukuran | Sebelum | Sesudah | Perintah |
|---|---|---|---|
| Berkas data mentah tervalidasi | 0 berkas | 15 berkas cocok `MANIFEST.csv` | `python unduh_data.py --kasus 07` |
| Verifikasi pipeline ekstraksi | Belum teruji | Validasi sukses (`NotImplementedError` Tahap 1) | `python pipeline.py` |
| Catatan lineage Sprint 0 | Belum ada | 1 file terbuat (`sprint/sprint-0/124450112.md`) | `git push origin 124450112/kerja` |

## 5. Yang akan saya ubah jika ada satu sprint lagi
Jika ada satu sprint tambahan, saya akan menambahkan skema validasi otomatis untuk memeriksa skema header dan tipe kolom pada 15 berkas mentah sebelum data masuk ke tahap penguraian (parsing). Saya juga akan mengintegrasikan pengujian unit (unit test) berbasis pytest untuk memverifikasi kecocokan checksum SHA-256 secara langsung dalam pipeline CI/CD. Selain itu, saya ingin membangun modul visualisasi data lineage graph berbasis skrip agar alur perubahan data dari berkas mentah hingga format silver dapat dipantau oleh seluruh anggota tim secara terbuka.
