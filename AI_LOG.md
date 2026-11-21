# AI_LOG — <Nama tim>

Satu baris per pemakaian AI yang bermakna (ChatGPT, Claude, Copilot, Bravais, dan sejenisnya).
Ringkas dan jujur; transkrip penuh tidak diminta. Yang dinilai bukan "pakai AI atau tidak",
melainkan "mengerti atau tidak" — isi kolom terakhir dengan apa yang Anda ubah dari keluarannya.

| Tanggal | Siapa (NIM) | Alat | Untuk apa | Apa yang diubah dari keluarannya |
|---|---|---|---|---|
| 2026-11-08 | 124450061 | Antigravity AI | Skrip profiling awal JSON & CSV BPS | Menyesuaikan fungsi serialisasi `json.dumps` untuk kolom nested dict/list |
| 2026-11-12 | 124450061 | Antigravity AI | Otomasi deteksi anomali IQR/z-score & visualisasi deret waktu | Menyesuaikan parameter batas IQR 1.5, menambahkan klasifikasi patahan seri pemekaran DOB Papua 2024, dan menyesuaikan API boxplot tick_labels |
| 2026-11-17 | 124450061 | Antigravity AI | Evaluasi grid 38 provinsi x periode, matriks kelengkapan panel, dan perumusan strategi missing value | Menyesuaikan logika pemisahan wilayah_kode 9999 (Indonesia), menetapkan klasifikasi sel kosong 4 DOB Papua 2017-2023 sebagai ketiadaan struktural, dan mencatat keputusan K-005 |
| 2026-11-18 | 124450005 | opencode | Memeriksa satuan, kode SDG, dan jenis periode tujuh seri dari metadata mentah; menyusun katalog dan skrip verifikasi | Menetapkan persen untuk WDI dari judul indikator, mengisi SDG 2.1.1/2.1.2, menolak agregasi periode non-tahunan, dan menyesuaikan rentang nilai dengan hasil hitung ulang |
| 2026-11-21 | 124450061 | Antigravity AI | Penyusunan skema SQL Silver (DDL & loader), implementasi 12 aturan validasi Pandera di pipeline, dan dokumentasi kamus data | Merancang DDL primary key komposit 6 dimensi, mengintegrasikan validasi ke pipeline.py, dan menyusun penelusuran lineage baris riil |
| 2026-11-21 | 124450088 | Antigravity AI | Perumusan Sprint Goal, pemutakhiran data dictionary 11 kolom Silver, penyusunan enam bagian laporan tim reports/tim.md, dan sinkronisasi metrik | Mengintegrasikan seluruh aturan keputusan K-001 s.d. K-010 ke kamus data, menyusun rekapitulasi numerik terverifikasi dan pembagian kerja pada laporan tim, serta menyelaraskan dengan skema starter |
