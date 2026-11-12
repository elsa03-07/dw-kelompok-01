"""Tahap 1 – Ekstraksi. Milik tim.

Baca setiap berkas di data/raw/ menjadi DataFrame mentah 
serta catat atribut lineage (_berkas_raw dan _sha256_raw).
"""

from pathlib import Path
from src.ekstraksi import bps_reader, wdi_reader, who_reader

def jalankan():
    """Kembalikan {nama_sumber: DataFrame mentah}."""
    hasil = {}
    
    # 1. Membaca data BPS
    try:
        bps_hasil = bps_reader.baca_semua("data/raw")
        if isinstance(bps_hasil, dict):
            hasil.update(bps_hasil)
    except Exception as e:
        print(f"Catatan BPS reader: {e}")

    # 2. Membaca data WDI
    try:
        wdi_dir = Path("data/raw/wdi")
        if wdi_dir.exists():
            for file_json in wdi_dir.rglob("*.json"):
                df_wdi = wdi_reader.baca_wdi(file_json)
                if df_wdi is not None and not df_wdi.empty:
                    hasil[file_json.name] = df_wdi
    except Exception as e:
        print(f"Catatan WDI reader: {e}")

    # 3. Membaca data WHO GHO
    try:
        who_hasil = who_reader.baca_semua("data/raw")
        if isinstance(who_hasil, dict):
            hasil.update(who_hasil)
    except Exception as e:
        print(f"Catatan WHO reader: {e}")

    if not hasil:
        raise NotImplementedError("Tahap 1: Belum ada data mentah yang berhasil dimuat.")
        
    return hasil