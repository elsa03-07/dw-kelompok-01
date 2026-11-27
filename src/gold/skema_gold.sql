-- Skema DDL Gold kanonis (SQLite). Kelompok 1 — Kasus 01 Kerawanan pangan provinsi.
-- Kolom dan kunci mengikuti data/gold/*.parquet yang ditulis src/gold (K-019).
-- Dimuat oleh src/sql (tahap "sql" di pipeline.py) setelah Silver.

DROP TABLE IF EXISTS panel_provinsi;
CREATE TABLE panel_provinsi (
    sumber          TEXT    NOT NULL,
    seri_kode       TEXT    NOT NULL,
    nama_indikator  TEXT    NOT NULL,
    kode_sdg        TEXT    NOT NULL,
    wilayah_kode    INTEGER NOT NULL,
    nama_wilayah    TEXT    NOT NULL,
    periode         TEXT    NOT NULL CHECK (length(periode) = 4),
    jenis_periode   TEXT    NOT NULL,
    rincian         TEXT    NOT NULL,
    nilai           REAL    NOT NULL CHECK (nilai BETWEEN 0 AND 100),
    satuan          TEXT    NOT NULL,
    _berkas_raw     TEXT    NOT NULL,
    _sha256_raw     TEXT    NOT NULL,
    status_anomali  TEXT    NOT NULL,
    is_outlier      INTEGER NOT NULL CHECK (is_outlier IN (0, 1)),
    is_patahan      INTEGER NOT NULL CHECK (is_patahan IN (0, 1)),
    PRIMARY KEY (seri_kode, wilayah_kode, periode)
);
CREATE INDEX idx_panel_provinsi_periode ON panel_provinsi (periode);

DROP TABLE IF EXISTS tabel_nasional;
CREATE TABLE tabel_nasional (
    sumber                     TEXT    NOT NULL,
    seri_kode                  TEXT    NOT NULL,
    nama_indikator             TEXT    NOT NULL,
    kode_sdg                   TEXT    NOT NULL,
    kelompok_indikator         TEXT    NOT NULL,
    wilayah_kode               INTEGER NOT NULL CHECK (wilayah_kode = 9999),
    nama_wilayah               TEXT    NOT NULL,
    periode                    TEXT    NOT NULL CHECK (length(periode) = 4),
    jenis_periode              TEXT    NOT NULL,
    rincian                    TEXT    NOT NULL,
    nilai                      REAL    NOT NULL CHECK (nilai BETWEEN 0 AND 100),
    satuan                     TEXT    NOT NULL,
    dapat_dibandingkan_dengan  TEXT    NOT NULL,
    catatan_perbandingan       TEXT    NOT NULL,
    _berkas_raw                TEXT    NOT NULL,
    _sha256_raw                TEXT    NOT NULL,
    PRIMARY KEY (sumber, seri_kode, periode)
);

DROP TABLE IF EXISTS tabel_nasional_lebar;
CREATE TABLE tabel_nasional_lebar (
    periode         TEXT PRIMARY KEY CHECK (length(periode) = 4),
    bps_var1473     REAL,
    bps_var1474     REAL,
    wdi_defc        REAL,
    wdi_msfi        REAL,
    who_stunting    REAL,
    who_overweight  REAL,
    who_wasting     REAL
);

DROP TABLE IF EXISTS rekonsiliasi;
CREATE TABLE rekonsiliasi (
    periode                 TEXT NOT NULL CHECK (length(periode) = 4),
    seri_utama              TEXT NOT NULL,
    seri_pembanding         TEXT NOT NULL,
    nilai_utama             REAL,
    nilai_pembanding        REAL,
    selisih                 REAL,
    status_pasangan         TEXT NOT NULL CHECK (status_pasangan IN ('berpasangan', 'hanya_utama', 'hanya_pembanding')),
    kategori                TEXT NOT NULL CHECK (kategori IN ('definisi berbeda', 'metode berbeda', 'vintage berbeda',
                                                              'cakupan berbeda', 'belum terjelaskan', 'tanpa pasangan')),
    penjelasan              TEXT NOT NULL,
    _berkas_raw_utama       TEXT,
    _berkas_raw_pembanding  TEXT,
    PRIMARY KEY (seri_utama, periode)
);
