"""Tahap 4–6 — Reshape, integrasi, dan penyimpanan ke Gold (pertemuan VII, IX, XI, XII). Milik tim.

Keluaran: data/gold/*.parquet (panel provinsi x tahun x indikator siap analisis, plus tabel
rekonsiliasi dengan pembanding nasional) dan basis data SQL (mis. data/gold/gold.sqlite).
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.gold.aturan_pilih import proses_gold
GOLD_DIR = ROOT / "data" / "gold"
PANEL_PROV_FILE = GOLD_DIR / "panel_provinsi.parquet"
REKON_NAS_FILE = GOLD_DIR / "rekonsiliasi_nasional.parquet"


def jalankan(silver=None):
    """Terima Silver, tulis tabel Gold, kembalikan {nama_tabel: DataFrame}."""
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    
    if silver is None:
        silver_file = ROOT / "data" / "silver" / "silver.parquet"
        if not silver_file.exists():
            raise FileNotFoundError(f"Berkas Silver Parquet tidak ditemukan di: {silver_file}")
        silver = pd.read_parquet(silver_file)
        
    print("\n" + "=" * 70)
    print("[GOLD] Menjalankan Tahap 4 (Persiapan Gold) - Backlog #20")
    print("Alur Pemanggilan: pipeline.py -> src.gold.jalankan() -> src.gold.aturan_pilih.pilih_baris_gold()")
    print("-" * 70)
    
    hasil = proses_gold(silver)
    df_panel = hasil["panel_provinsi"]
    df_rekon = hasil["rekonsiliasi_nasional"]
    info_dampak = hasil["info_dampak"]
    
    print("Pencatatan Dampak Baris per Aturan (tercatat di log-keputusan.csv):")
    for k, v in info_dampak.items():
        if k.startswith("K-"):
            print(f"  - [{k}] {v['nama']:<38}: {v['dampak_baris']} baris")
    print(f"Total baris Silver yang tidak terpilih (sub-rincian tetap di Silver): {hasil['baris_tidak_terpilih']:,} baris.")
    print("-" * 70)
    
    df_panel.to_parquet(PANEL_PROV_FILE, index=False)
    df_rekon.to_parquet(REKON_NAS_FILE, index=False)
    
    print(f"Keluaran Gold berhasil disimpan:")
    print(f"  1. data/gold/panel_provinsi.parquet       : {len(df_panel):,} baris x {len(df_panel.columns)} kolom")
    print(f"  2. data/gold/rekonsiliasi_nasional.parquet : {len(df_rekon):,} baris x {len(df_rekon.columns)} kolom")
    print("=" * 70 + "\n")
    
    return {
        "panel_provinsi": df_panel,
        "rekonsiliasi_nasional": df_rekon
    }


if __name__ == "__main__":
    jalankan()
