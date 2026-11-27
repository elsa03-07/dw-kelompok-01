"""Tahap 4 dan 6 — Gold kanonis dan rekonsiliasi. Milik tim.

Gold kanonis (satu-satunya tabel Gold yang ditulis ke data/gold/ dan dimuat ke SQL, K-019):

    panel_provinsi        provinsi x periode x indikator (bentuk panjang) + penanda anomali (K-017)
    tabel_nasional        seri BPS, WDI, WHO nasional berdampingan (bentuk panjang, dengan lineage)
    tabel_nasional_lebar  tampilan lebar tabel_nasional per periode
    rekonsiliasi          BPS vs WDI per periode, selisih dan kategori penjelasannya (K-018)

Alur pemanggilan: pipeline.py -> gold.jalankan() -> builder.bangun_gold()
                                                -> aturan_pilih.pilih_baris_gold()  (#20)
                                                -> rekonsiliasi.bangun_rekonsiliasi() (#24)
"""
from pathlib import Path

import pandas as pd

from src.gold.aturan_pilih import (
    catat_dampak_ke_log, cocokkan_dengan_gold, pilih_baris_gold, tandai_anomali,
)
from src.gold.builder import SILVER_FILE, bangun_gold
from src.gold.rekonsiliasi import bangun_rekonsiliasi, validasi_rekonsiliasi

ROOT = Path(__file__).resolve().parents[2]
GOLD_DIR = ROOT / "data" / "gold"
TABEL_KANONIS = ("panel_provinsi", "tabel_nasional", "tabel_nasional_lebar", "rekonsiliasi")


def jalankan(silver=None):
    """Bangun, periksa, dan tulis Gold kanonis. Kembalikan {nama_tabel: DataFrame}."""
    if silver is None:
        silver = pd.read_parquet(SILVER_FILE)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    tabel = bangun_gold(silver)

    # Aturan satu nilai per sel (#20): dihitung, dicocokkan dengan Gold, dan dampaknya dicatat.
    provinsi, nasional, info = pilih_baris_gold(silver)
    cocokkan_dengan_gold(provinsi, nasional, tabel["panel_provinsi"], tabel["tabel_nasional"])
    catat_dampak_ke_log(info)
    print("  aturan #20 (dampak ditulis ke log-keputusan.csv):")
    for kode in ("K-014", "K-016", "K-015", "K-017"):
        print(f"    {kode} {info[kode]['nama']:<52} {info[kode]['dampak_baris']:>5} baris")
    print(f"    Silver {info['baris_silver']:,} -> terpilih {info['baris_terpilih']:,}, "
          f"tetap hanya di Silver {info['baris_tidak_terpilih']:,}")

    tabel["panel_provinsi"] = tandai_anomali(tabel["panel_provinsi"])

    rekon = bangun_rekonsiliasi(tabel["tabel_nasional"])
    validasi_rekonsiliasi(rekon)
    tabel["rekonsiliasi"] = rekon

    for nama in TABEL_KANONIS:
        df = tabel[nama]
        df.to_parquet(GOLD_DIR / f"{nama}.parquet", index=False)
        print(f"  data/gold/{nama}.parquet: {len(df):,} baris x {len(df.columns)} kolom")

    p = tabel["panel_provinsi"]
    print(f"  penanda anomali: {int(p['is_outlier'].sum())} outlier, {int(p['is_patahan'].sum())} patahan")
    print(f"  rekonsiliasi: {int((rekon['status_pasangan'] == 'berpasangan').sum())} berpasangan, "
          f"{int((rekon['kategori'] == 'tanpa pasangan').sum())} tanpa pasangan")

    tabel["_info_aturan"] = info
    return tabel


if __name__ == "__main__":
    jalankan()
