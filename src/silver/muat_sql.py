"""Skrip pemuat tabel Silver ke basis data SQL (SQLite dan DuckDB).
Milik tim — Tahap 5: Penyimpanan SQL.
"""
import sqlite3
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SILVER_PARQUET = ROOT / "data" / "silver" / "silver.parquet"
SQLITE_DB = ROOT / "data" / "silver" / "silver.sqlite"
DDL_FILE = Path(__file__).resolve().parent / "skema_silver.sql"

def muat_ke_sqlite(parquet_path=SILVER_PARQUET, db_path=SQLITE_DB, ddl_path=DDL_FILE):
    if not parquet_path.exists():
        raise FileNotFoundError(f"Berkas Silver Parquet tidak ditemukan: {parquet_path}")

    print(f"1. Membaca Silver Parquet dari: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    total_baris = len(df)
    print(f"   Total baris dibaca: {total_baris:,}")

    print(f"2. Menghubungkan ke SQLite DB: {db_path}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"3. Menjalankan DDL dari: {ddl_path}")
    ddl_sql = ddl_path.read_text(encoding="utf-8")
    cursor.executescript(ddl_sql)

    # Bersihkan isi tabel sebelum memuat ulang
    cursor.execute("DELETE FROM silver")

    print(f"4. Memuat {total_baris:,} baris ke tabel 'silver'...")
    cols = [
        "sumber", "seri_kode", "wilayah_kode", "nama_wilayah",
        "periode", "jenis_periode", "rincian", "nilai",
        "satuan", "_berkas_raw", "_sha256_raw"
    ]
    placeholders = ", ".join(["?"] * len(cols))
    insert_sql = f"INSERT INTO silver ({', '.join(cols)}) VALUES ({placeholders})"

    data_tuples = [tuple(x) for x in df[cols].to_numpy()]
    cursor.executemany(insert_sql, data_tuples)
    conn.commit()

    # Verifikasi pemuatan
    cursor.execute("SELECT COUNT(*) FROM silver")
    count_sql = cursor.fetchone()[0]
    print(f"5. Verifikasi: Jumlah baris di SQLite = {count_sql:,}")
    if count_sql != total_baris:
        raise ValueError(f"Jumlah baris tidak cocok: Parquet={total_baris}, SQLite={count_sql}")

    # Uji coba Primary Key Constraint (mencegah duplikat kunci)
    try:
        sample_row = data_tuples[0]
        cursor.execute(insert_sql, sample_row)
        conn.commit()
        raise AssertionError("Gagal: Primary key constraint tidak menolak duplikasi!")
    except sqlite3.IntegrityError:
        print("6. Uji Integritas: Primary key komposit 6 dimensi BERHASIL menolak duplikasi baris.")

    # Contoh kueri analitis singkat
    print("7. Contoh Kueri: Rata-rata nilai per seri:")
    cursor.execute("""
        SELECT seri_kode, COUNT(*) as jumlah_baris, ROUND(AVG(nilai), 2) as rata_rata_nilai, satuan
        FROM silver
        GROUP BY seri_kode, satuan
        ORDER BY seri_kode
    """)
    for row in cursor.fetchall():
        print(f"   - {row[0]:<20} : {row[1]:>4} baris | Rata-rata = {row[2]:>6.2f} {row[3]}")

    conn.close()
    print(f"Pemuatan Silver ke SQLite BERHASIL disimpan di: {db_path}\n")
    return count_sql

if __name__ == "__main__":
    muat_ke_sqlite()
