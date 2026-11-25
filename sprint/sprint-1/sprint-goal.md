# Sprint 1 – Goal (Case 01)

## Tujuan Utama
Menyelesaikan alur **End‑to‑End** data pipeline mulai dari data mentah hingga data *silver* yang tervalidasi, serta menyediakan dokumentasi dan artefak yang dapat direproduksi.

## Kriteria Keberhasilan (Definition of Done)
1. **Unduh data mentah** dengan verifikasi SHA‑256 yang lolos.
2. **Pipeline** (`python pipeline.py`) menghasilkan file `data/silver/silver.parquet` dalam ≤ 2 detik.
3. **Pemeriksaan skema** (`python -m src.common.skema …`) menampilkan **1.414 baris** dan lolos tanpa error.
4. **Laporan ekstraksi** (`reports/ekstraksi.md`) berisi jumlah baris per berkas sumber.
5. **Deteksi duplikat WHO** menghasilkan `reports/kembar-who.csv` dengan tiga metode penulisan “total” dan satu catatan yang bertentangan.
6. **Analisis grid** menghasilkan laporan `reports/kelengkapan-panel.md` & `reports/anomali.md` yang membandingkan *belum_ada* vs *batas_lama* (Papua).
7. **Validasi** dan **unit‑test** (`pytest -q`) harus lulus semua test.
8. **Penelusuran** satu baris silver ke file mentah berhasil, didokumentasikan di `docs/data-dictionary.md` sebagai contoh.
9. **Reproduksi**: klon repo ke folder baru, jalankan tiga perintah utama, dan pastikan `silver.parquet` identik (checksum SHA‑256 = `9A57A26C239EC189632E1141A317334ABEDB94E30601F2A91AA0AEE79F951428`).

## Checklist Sprint
- [ ] `unduh_data.py --kasus 1` berhasil dan SHA‑256 terverifikasi.
- [ ] `pipeline.py` selesai dalam < 2 detik dan menghasilkan `silver.parquet`.
- [ ] Skema parquet lolos (`src.common.skema`).
- [ ] Ekstraksi baris per berkas selesai (`reports/ekstraksi.md`).
- [ ] Duplikat WHO terdeteksi (`reports/kembar-who.csv`).
- [ ] Analisis grid selesai (`reports/kelengkapan-panel.md`, `reports/anomali.md`).
- [ ] Semua tes `pytest` lulus.
- [ ] Contoh penelusuran baris silver tercatat (`docs/data-dictionary.md`).
- [ ] Reproduksi berhasil; log mencatat waktu eksekusi.

## Catatan Tambahan
- Semua perintah dijalankan dalam **virtual‑env** `.venv`.
- Log lengkap disimpan di `run_demo.log`.
- Rekaman demo akan dilakukan secara **manual** (OBS/Game Bar); tidak ada rekaman otomatis.

---
*Dokumen ini disiapkan pada 2026‑11‑21 untuk Sprint 1 – Case 01.*