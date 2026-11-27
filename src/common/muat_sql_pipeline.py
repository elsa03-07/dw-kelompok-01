from pathlib import Path
import sqlite3
import pandas as pd
from src.silver.muat_sql import muat_ke_sqlite

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / "data" / "capstone.sqlite"
GOLD_DIR = ROOT_DIR / "data" / "gold"
GOLD_DDL_PATH = ROOT_DIR / "src" / "gold" / "skema_gold.sql"


def _muat_parquet_ke_tabel(conn: sqlite3.Connection, parquet_path: Path, nama_tabel: str) -> int:
    if not parquet_path.exists():
        raise FileNotFoundError(f"Berkas tidak ditemukan: {parquet_path}")

    df = pd.read_parquet(parquet_path)
    if df.empty:
        return 0

    kolom = list(df.columns)
    placeholder = ", ".join(["?"] * len(kolom))
    kolom_sql = ", ".join(f'"{k}"' for k in kolom)
    sql = f'INSERT OR REPLACE INTO "{nama_tabel}" ({kolom_sql}) VALUES ({placeholder})'

    rows = [tuple(None if pd.isna(v) else v for v in row) for row in df.itertuples(index=False, name=None)]
    conn.executemany(sql, rows)
    return len(rows)


def muat_semua_ke_sqlite(db_path: Path = DB_PATH) -> dict[str, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    jumlah_silver = muat_ke_sqlite(db_path=db_path)

    if not GOLD_DDL_PATH.exists():
        raise FileNotFoundError(f"DDL Gold tidak ditemukan: {GOLD_DDL_PATH}")

    conn = sqlite3.connect(db_path)
    try:
        with open(GOLD_DDL_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        peta_gold = {
            "panel_gold": GOLD_DIR / "panel_provinsi.parquet",
            "tabel_nasional": GOLD_DIR / "tabel_nasional.parquet",
            "rekonsiliasi_nasional": GOLD_DIR / "rekonsiliasi_nasional.parquet",
        }

        ringkasan = {"silver": jumlah_silver}
        for nama_tabel, path_parquet in peta_gold.items():
            jumlah = _muat_parquet_ke_tabel(conn, path_parquet, nama_tabel)
            ringkasan[nama_tabel] = jumlah

        conn.commit()
    finally:
        conn.close()

    for tabel, total in ringkasan.items():
        print(f"[OK] {tabel}: {total} baris dimuat ke {db_path.name}")

    return ringkasan


if __name__ == "__main__":
    muat_semua_ke_sqlite()
