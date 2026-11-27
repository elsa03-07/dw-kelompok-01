"""Pembaca berkas mentah WHO GHO (CSV datadot dan JSON metadata OData). Milik tim — 124450112.

CSV datadot dibaca apa adanya (semua kolom DIM_* dan RATE_*); rincian tidak disaring di sini.
"""
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW
from src.ekstraksi._umum import baca_json_metadata, beri_lineage


def baca_who_csv(path, raw=RAW):
    return beri_lineage(pd.read_csv(path, dtype=str), path, raw)


def baca_semua(raw=RAW):
    """{berkas relatif: DataFrame} untuk semua berkas WHO GHO di data/raw/who_gho/."""
    raw = Path(raw)
    hasil = {}
    for path in sorted((raw / "who_gho").rglob("*")):
        if path.suffix == ".csv":
            df = baca_who_csv(path, raw)
        elif path.suffix == ".json":
            df = baca_json_metadata(path, raw)
        else:
            continue
        hasil[df["_berkas_raw"].iat[0]] = df
    return hasil
