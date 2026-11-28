"""Bantuan bersama pembaca ekstraksi: lineage dan pembacaan metadata JSON."""
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw


def relatif(path, raw=RAW):
    """Jalur berkas relatif data/raw/ dengan garis miring maju (sama dengan MANIFEST.csv)."""
    return Path(path).resolve().relative_to(Path(raw).resolve()).as_posix()


def beri_lineage(df, path, raw=RAW):
    berkas = relatif(path, raw)
    df = df.copy()
    df["_berkas_raw"] = berkas
    df["_sha256_raw"] = sha256_raw(berkas, raw)
    return df


def baca_json_metadata(path, raw=RAW):
    """JSON metadata -> DataFrame rata: ambil daftar rekaman utamanya, tanpa membersihkan isinya."""
    with open(path, encoding="utf-8") as f:
        isi = json.load(f)
    if isinstance(isi, dict) and isinstance(isi.get("value"), list):          # OData WHO GHO
        rekaman = isi["value"]
    elif isinstance(isi, list) and len(isi) == 2 and isinstance(isi[1], list):  # API WDI [halaman, data]
        rekaman = isi[1]
    elif isinstance(isi, list):
        rekaman = isi
    else:                                                                       # objek tunggal
        rekaman = [isi]
    return beri_lineage(pd.json_normalize(rekaman, max_level=1), path, raw)
