-- Skema DDL Tabel Silver (SQLite / DuckDB / PostgreSQL)
-- Repositori: Kelompok 1 — Capstone Data Wrangling
-- Penyusun: 124450061 (Persiapan Tahap 5 - Penyimpanan SQL)

CREATE TABLE IF NOT EXISTS silver (
    sumber VARCHAR(20) NOT NULL,
    seri_kode VARCHAR(50) NOT NULL,
    wilayah_kode INTEGER NOT NULL,
    nama_wilayah VARCHAR(100) NOT NULL,
    periode VARCHAR(20) NOT NULL,
    jenis_periode VARCHAR(20) NOT NULL,
    rincian VARCHAR(255) NOT NULL,
    nilai REAL NOT NULL,
    satuan VARCHAR(50) NOT NULL,
    _berkas_raw VARCHAR(255) NOT NULL,
    _sha256_raw VARCHAR(64) NOT NULL,
    -- Kunci primer komposit 6 dimensi menjamin keunikan observasi ber-provenans
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)
);

-- Indeks sekunder untuk percepatan kueri analitis
CREATE INDEX IF NOT EXISTS idx_silver_seri_wilayah ON silver (seri_kode, wilayah_kode);
CREATE INDEX IF NOT EXISTS idx_silver_periode ON silver (periode);
CREATE INDEX IF NOT EXISTS idx_silver_sumber ON silver (sumber);
