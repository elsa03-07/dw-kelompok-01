"""Tahap 1 – Ekstraksi. Milik tim.

Baca setiap berkas di data/raw/ (CSV dan JSON WebAPI BPS, JSON WDI, CSV/JSON WHO GHO) menjadi
DataFrame mentah yang setia pada sumbernya: tidak dibersihkan, hanya diratakan, dan setiap baris
diberi _berkas_raw (relatif data/raw/) serta _sha256_raw (dari MANIFEST.csv).

Tahap ini gagal keras bila ada berkas di MANIFEST.csv yang tidak terbaca, sehingga inventaris
ekstraksi selalu lengkap. Silver (src/silver/builder.py) membaca berkas data langsung dengan
lineage yang sama; ringkasan baris per berkas dari tahap ini menjadi bukti inventarisnya.
"""
from src.common.manifest import RAW, baca
from src.ekstraksi import bps_reader, wdi_reader, who_reader


def jalankan(raw=RAW):
    """Kembalikan {berkas relatif data/raw/: DataFrame mentah}."""
    hasil = {}
    for pembaca in (bps_reader, wdi_reader, who_reader):
        hasil.update(pembaca.baca_semua(raw))

    manifest = set(baca(raw))
    tidak_terbaca = sorted(manifest - set(hasil))
    if tidak_terbaca:
        raise ValueError(f"Ekstraksi: berkas MANIFEST tidak terbaca: {tidak_terbaca}")
    tambahan = sorted(set(hasil) - manifest)
    if tambahan:
        raise ValueError(f"Ekstraksi: berkas di luar MANIFEST ikut terbaca: {tambahan}")

    for berkas in sorted(hasil):
        print(f"  {berkas:<55} {len(hasil[berkas]):>6} baris")
    return hasil
