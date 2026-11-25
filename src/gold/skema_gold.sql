CREATE TABLE IF NOT EXISTS panel_gold (
    wilayah_kode INTEGER NOT NULL,
    periode TEXT NOT NULL,
    nama_wilayah TEXT,
    var1473 REAL,
    var1474 REAL,
    status_anomali_var1473 TEXT,
    status_anomali_var1474 TEXT,
    is_outlier INTEGER,
    is_patahan INTEGER,
    PRIMARY KEY (wilayah_kode, periode)
);

CREATE INDEX IF NOT EXISTS idx_panel_gold_periode ON panel_gold (periode);
CREATE INDEX IF NOT EXISTS idx_panel_gold_wilayah ON panel_gold (wilayah_kode);

CREATE TABLE IF NOT EXISTS tabel_nasional (
    periode TEXT PRIMARY KEY,
    var1473 REAL,
    var1474 REAL,
    status_anomali_var1473 TEXT,
    status_anomali_var1474 TEXT
);

CREATE TABLE IF NOT EXISTS rekonsiliasi_nasional (
    periode TEXT PRIMARY KEY,
    var1473_nasional REAL,
    var1473_agregat REAL,
    selisih_var1473 REAL,
    var1474_nasional REAL,
    var1474_agregat REAL,
    selisih_var1474 REAL
);

