"""Pembaca WHO GHO (3 CSV, 2 JSON). Tahap 1: tidak membersihkan apa pun.

DIM_* kosong = dimensi tidak berlaku untuk baris itu (bukan data hilang),
jadi semua kolom dibaca sebagai string dan kosong tidak diubah jadi NaN.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def _tempel_asal(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    df["_berkas_raw"] = path.name
    df["_sha256_raw"] = _sha256(path)
    return df


def baca_csv(path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[])
    return _tempel_asal(df, path)


def baca_json(path) -> pd.DataFrame:
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        isi = json.load(f)
    if isinstance(isi, dict) and isinstance(isi.get("value"), list):
        isi = isi["value"]
    elif isinstance(isi, dict):
        isi = [isi]
    df = pd.json_normalize(isi, sep=".")
    df = df.astype(object).where(df.notna(), "")
    return _tempel_asal(df, path)


def baca_berkas(path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return baca_csv(path)
    if path.suffix.lower() == ".json":
        return baca_json(path)
    raise ValueError(f"Ekstensi tidak didukung: {path}")


def baca_semua(folder) -> dict[str, pd.DataFrame]:
    hasil = {}
    for p in sorted(Path(folder).rglob("*")):
        if p.suffix.lower() in {".csv", ".json"}:
            hasil[p.name] = baca_berkas(p)
    return hasil

if __name__ == "__main__":
    import sys

    for nama, df in baca_semua(sys.argv[1]).items():
        print(f"{nama}: {len(df)} baris, {df.shape[1]} kolom")