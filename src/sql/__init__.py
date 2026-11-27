"""Tahap 5 — Penyimpanan SQL (Backlog #23). Milik tim.

Dipanggil dari pipeline.py setelah Gold. Membangun ulang data/capstone.sqlite dari nol setiap kali:

    silver                Silver (DDL: src/silver/skema_silver.sql, kunci primer 6 dimensi)
    panel_provinsi        Gold kanonis (DDL: src/gold/skema_gold.sql)
    tabel_nasional
    tabel_nasional_lebar
    rekonsiliasi

Setiap tabel dimuat dengan INSERT biasa (bukan INSERT OR REPLACE), jadi kunci ganda membuat
pemuatan gagal alih-alih menimpa baris diam-diam. Setelah dimuat, jumlah baris dan jumlah nilai
di SQL dibandingkan dengan Parquet; bila ada selisih, pipeline berhenti.

Alasan SQLite: tanpa server, satu berkas lokal yang dibangun ulang oleh pipeline, kunci primer dan
CHECK ditegakkan, cukup untuk ~2 ribu baris. Berkas .sqlite tidak di-commit (.gitignore).
"""
import math
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "capstone.sqlite"
SILVER_FILE = ROOT / "data" / "silver" / "silver.parquet"
GOLD_DIR = ROOT / "data" / "gold"
DDL_SILVER = ROOT / "src" / "silver" / "skema_silver.sql"
DDL_GOLD = ROOT / "src" / "gold" / "skema_gold.sql"
TABEL_GOLD = ("panel_provinsi", "tabel_nasional", "tabel_nasional_lebar", "rekonsiliasi")


def _ke_baris(df):
    """DataFrame -> tuple siap SQLite (NaN -> NULL, bool -> 0/1, numpy -> Python)."""
    hasil = []
    for baris in df.itertuples(index=False, name=None):
        hasil.append(tuple(
            None if (v is None or (isinstance(v, float) and math.isnan(v)) or v is pd.NA)
            else int(v) if isinstance(v, bool) or type(v).__name__ == "bool_"
            else v.item() if hasattr(v, "item")
            else v
            for v in baris
        ))
    return hasil


def _muat(conn, nama, df):
    kolom = ", ".join(f'"{k}"' for k in df.columns)
    tanda = ", ".join("?" * len(df.columns))
    conn.executemany(f'INSERT INTO "{nama}" ({kolom}) VALUES ({tanda})', _ke_baris(df))


def _cek(conn, nama, df):
    n_sql, jumlah_sql = conn.execute(
        f'SELECT COUNT(*), {"ROUND(SUM(nilai), 6)" if "nilai" in df.columns else "NULL"} FROM "{nama}"'
    ).fetchone()
    jumlah_parquet = round(float(df["nilai"].sum()), 6) if "nilai" in df.columns else None
    cocok = n_sql == len(df) and (jumlah_parquet is None or math.isclose(jumlah_sql, jumlah_parquet, abs_tol=1e-6))
    return {"tabel": nama, "baris_parquet": len(df), "baris_sql": n_sql,
            "jumlah_nilai_parquet": jumlah_parquet, "jumlah_nilai_sql": jumlah_sql, "cocok": cocok}


def jalankan(silver=None, gold=None, db_path=DB_PATH):
    """Bangun ulang basis data dari Parquet yang baru ditulis. Kembalikan daftar hasil pemeriksaan."""
    tabel = {"silver": pd.read_parquet(SILVER_FILE)}
    for nama in TABEL_GOLD:
        tabel[nama] = pd.read_parquet(GOLD_DIR / f"{nama}.parquet")

    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(DDL_SILVER.read_text(encoding="utf-8-sig"))
        conn.executescript(DDL_GOLD.read_text(encoding="utf-8-sig"))
        for nama, df in tabel.items():
            _muat(conn, nama, df)
        conn.commit()

        # Kunci primer benar-benar menolak duplikat (bukan menimpa).
        try:
            _muat(conn, "panel_provinsi", tabel["panel_provinsi"].head(1))
            raise AssertionError("panel_provinsi: kunci primer tidak menolak baris ganda")
        except sqlite3.IntegrityError:
            conn.rollback()

        hasil = [_cek(conn, nama, df) for nama, df in tabel.items()]
    finally:
        conn.close()

    for h in hasil:
        status = "cocok" if h["cocok"] else "TIDAK COCOK"
        print(f"  {h['tabel']:<22} Parquet {h['baris_parquet']:>5} | SQL {h['baris_sql']:>5} baris  [{status}]")
    gagal = [h["tabel"] for h in hasil if not h["cocok"]]
    if gagal:
        raise ValueError(f"Jumlah baris/nilai SQL tidak sama dengan Parquet: {gagal}")
    tampil = db_path.relative_to(ROOT).as_posix() if db_path.is_relative_to(ROOT) else db_path
    print(f"  {tampil}: {len(hasil)} tabel, kunci primer menolak duplikat")
    return hasil


if __name__ == "__main__":
    jalankan()
