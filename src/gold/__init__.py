"""Pembentukan Gold utama dan keluaran analisis anomali."""

from pathlib import Path
import pandas as pd

from src.gold.builder import SILVER_FILE, bangun_gold, rekonsiliasi_golongan
from src.gold.aturan_pilih import proses_gold

ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "data" / "gold"


def jalankan(silver=None):
    """Membangun Gold kanonis Sprint 2 dan analisis anomali Backlog #20."""
    if silver is None:
        silver = pd.read_parquet(SILVER_FILE)

    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Bangun Gold kanonis tim (panel long 628 baris, tabel nasional, tabel nasional lebar, rekonsiliasi)
    tabel = bangun_gold(silver)
    rekon = rekonsiliasi_golongan(tabel["panel_provinsi"], tabel["tabel_nasional"])
    tabel["rekonsiliasi"] = rekon

    for nama, df in tabel.items():
        tujuan = GOLD_DIR / f"{nama}.parquet"
        df.to_parquet(tujuan, index=False)
        print(f"{tujuan.relative_to(ROOT)} berhasil dibuat: {len(df):,} baris.")

    # 2. Jalankan aturan pemilihan satu nilai per sel & analisis anomali (Backlog #20)
    print("\n" + "=" * 70)
    print("[GOLD] Menjalankan Tahap 4 (Persiapan Gold) - Backlog #20")
    print("Alur Pemanggilan: pipeline.py -> src.gold.jalankan() -> src.gold.aturan_pilih.pilih_baris_gold()")
    print("-" * 70)

    hasil_anomali = proses_gold(silver)
    info_dampak = hasil_anomali["info_dampak"]

    print("Pencatatan Dampak Baris per Aturan (tercatat di log-keputusan.csv):")
    for k, v in info_dampak.items():
        if k.startswith("K-"):
            print(f"  - [{k}] {v['nama']:<38}: {v['dampak_baris']} baris")
    print(f"Total baris Silver yang tidak terpilih (sub-rincian tetap di Silver): {hasil_anomali['baris_tidak_terpilih']:,} baris.")
    print("-" * 70)

    keluaran_anomali = {
        "panel_provinsi_anomali": hasil_anomali["panel_provinsi"],
        "rekonsiliasi_nasional": hasil_anomali["rekonsiliasi_nasional"],
    }
    for nama, df in keluaran_anomali.items():
        tujuan = GOLD_DIR / f"{nama}.parquet"
        df.to_parquet(tujuan, index=False)
        print(f"  {tujuan.relative_to(ROOT)}: {len(df):,} baris x {len(df.columns)} kolom")
        tabel[nama] = df
    print("=" * 70 + "\n")

    print("Gold selesai: panel provinsi, tabel nasional, dan anomali tervalidasi.")
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
