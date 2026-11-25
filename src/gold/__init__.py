"""Tahap 4–6 — Pembentukan panel Gold dan tabel pembanding nasional.

Keluaran:
- data/gold/panel_provinsi.parquet
- data/gold/tabel_nasional.parquet
- data/gold/tabel_nasional_lebar.parquet
"""
from pathlib import Path

import pandas as pd

from src.gold.builder import SILVER_FILE, bangun_gold

ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "data" / "gold"


def jalankan(silver=None):
    """Terima Silver, validasi, tulis tabel Gold, kembalikan {nama_tabel: DataFrame}."""
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


if __name__ == "__main__":
    jalankan()
