"""Tahap 2–4 — Profil, pembersihan, dan penyeragaman ke Silver (pertemuan II–VII). Milik tim.

Keluaran: data/silver/silver.parquet dengan skema minimal di src/common/skema.py.
Satu baris = satu seri x wilayah x periode x rincian x berkas sumber. Nilai dari sumber berbeda
TIDAK digabung di sini. Setiap keputusan pembersihan dicatat di log-keputusan.csv.
"""
from pathlib import Path
from src.silver.builder import bangun_silver

ROOT = Path(__file__).resolve().parents[2]
SILVER_DIR = ROOT / "data" / "silver"
SILVER_FILE = SILVER_DIR / "silver.parquet"


def jalankan(mentah=None):
    """Terima keluaran tahap 1 (atau baca langsung), tulis dan kembalikan DataFrame Silver."""
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    
    # Bangun tabel silver bersih berstandar skema
    df_silver = bangun_silver()
    
    # Simpan ke data/silver/silver.parquet
    df_silver.to_parquet(SILVER_FILE, index=False)
    print(f"data/silver/silver.parquet berhasil dibuat: {len(df_silver):,} baris.")
    
    return df_silver


if __name__ == "__main__":
    jalankan()
