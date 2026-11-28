"""Dipertahankan untuk kompatibilitas: pemuatan SQL kini menjadi tahap "sql" di pipeline.py.

Implementasinya ada di src/sql/__init__.py. Versi lama memuat Gold ke DDL yang tidak cocok dengan
kolom Parquet dan memakai INSERT OR REPLACE (baris berkunci ganda tertimpa tanpa ketahuan).
"""
from src.sql import DB_PATH, jalankan


def muat_semua_ke_sqlite(db_path=DB_PATH):
    return {h["tabel"]: h["baris_sql"] for h in jalankan(db_path=db_path)}


if __name__ == "__main__":
    muat_semua_ke_sqlite()
