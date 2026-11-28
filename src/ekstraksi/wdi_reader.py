"""Pembaca berkas mentah World Bank WDI (JSON API [halaman, data] dan metadata). Milik tim — 124450112."""
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW
from src.ekstraksi._umum import baca_json_metadata, beri_lineage

SERI_KASUS = {"SN.ITK.DEFC.ZS", "SN.ITK.MSFI.ZS"}


def baca_wdi(path, raw=RAW):
    """Ratakan JSON data WDI. Semua indikator dalam berkas dipertahankan (penyaringan seri di Silver)."""
    with open(path, encoding="utf-8") as f:
        isi = json.load(f)
    if not (isinstance(isi, list) and len(isi) == 2 and isinstance(isi[1], list)):
        raise ValueError(f"{path}: bukan format API WDI [halaman, data]")
    baris = [{
        "indicator_id": (r.get("indicator") or {}).get("id"),
        "indicator_name": (r.get("indicator") or {}).get("value"),
        "country_id": (r.get("country") or {}).get("id"),
        "countryiso3code": r.get("countryiso3code"),
        "country_name": (r.get("country") or {}).get("value"),
        "date": r.get("date"),
        "value": r.get("value"),
        "unit": r.get("unit"),
        "obs_status": r.get("obs_status"),
        "decimal": r.get("decimal"),
    } for r in isi[1]]
    return beri_lineage(pd.DataFrame(baris), path, raw)


def baca_semua(raw=RAW):
    """{berkas relatif: DataFrame} untuk semua berkas WDI di data/raw/wdi/."""
    raw = Path(raw)
    hasil = {}
    for path in sorted((raw / "wdi").rglob("*.json")):
        df = baca_wdi(path, raw) if path.parent.name == "data" else baca_json_metadata(path, raw)
        hasil[df["_berkas_raw"].iat[0]] = df
    return hasil
