
"""Pembentukan Gold utama dan keluaran analisis anomali."""

from pathlib import Path

import pandas as pd

from src.gold.builder import SILVER_FILE, bangun_gold
from src.gold.aturan_pilih import proses_gold

ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "data" / "gold"

def jalankan(silver=None):
    """Membangun Gold kanonis Sprint 2."""
    if silver is None:
        silver = pd.read_parquet(SILVER_FILE)

    tabel = bangun_gold(silver)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    for nama, df in tabel.items():
        tujuan = GOLD_DIR / f"{nama}.parquet"
        df.to_parquet(tujuan, index=False)
        print(f"{tujuan.relative_to(ROOT)} berhasil dibuat: {len(df):,} baris.")

    print("Gold selesai: panel provinsi dan tabel nasional tervalidasi.")
    return tabel

def jalankan_analisis_anomali(silver=None):
    """Menjalankan keluaran analisis anomali tanpa menimpa Gold kanonis."""
    if silver is None:
        silver = pd.read_parquet(SILVER_FILE)

    hasil = proses_gold(silver)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    keluaran = {
        "panel_provinsi_anomali": hasil["panel_provinsi"],
        "rekonsiliasi_nasional": hasil["rekonsiliasi_nasional"],
    }

    for nama, df in keluaran.items():
        tujuan = GOLD_DIR / f"{nama}.parquet"
        df.to_parquet(tujuan, index=False)
        print(f"{tujuan.relative_to(ROOT)} berhasil dibuat: {len(df):,} baris.")

    print("Analisis anomali Gold selesai.")
    return keluaran

if __name__ == "__main__":
    jalankan()