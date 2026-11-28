"""Pembaca berkas mentah BPS (CSV datar dan JSON WebAPI). Milik tim — 124450112.

Keluaran setia pada sumber: kolom asli dipertahankan, tidak ada pembersihan. Setiap baris
diberi _berkas_raw (relatif data/raw/) dan _sha256_raw (dari MANIFEST.csv).
"""
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW
from src.ekstraksi._umum import baca_json_metadata, beri_lineage


def baca_bps_csv(path, raw=RAW):
    return beri_lineage(pd.read_csv(path, dtype=str), path, raw)


def baca_bps_json(path, raw=RAW):
    """Ratakan 'datacontent' WebAPI BPS. Kunci = wilayah + var + turvar + tahun + turtahun."""
    with open(path, encoding="utf-8") as f:
        halaman = json.load(f)
    if isinstance(halaman, dict):
        halaman = [halaman]
    baris = []
    for nomor, h in enumerate(halaman):
        wilayah = {str(v["val"]): v["label"] for v in h.get("vervar", [])}
        tahun = {str(v["val"]): v["label"] for v in h.get("tahun", [])}
        var = {str(v["val"]): v for v in h.get("var", [])}
        turvar = {str(v["val"]) for v in h.get("turvar", [])}
        turtahun = {str(v["val"]) for v in h.get("turtahun", [])}
        for kunci, nilai in (h.get("datacontent") or {}).items():
            cocok = _urai_kunci(kunci, wilayah, var, turvar, tahun, turtahun)
            if cocok is None:
                raise ValueError(f"{path}: kunci datacontent tidak dapat diurai: {kunci}")
            w, v, tv, t, tt = cocok
            baris.append({
                "halaman": nomor, "kunci_datacontent": kunci,
                "wilayah_id": w, "wilayah": wilayah[w], "var_id": v, "var": var[v]["label"],
                "satuan": var[v].get("unit"), "turvar_id": tv, "tahun_id": t, "tahun": tahun[t],
                "turtahun_id": tt, "nilai": nilai, "last_update": h.get("last_update"),
            })
    return beri_lineage(pd.DataFrame(baris), path, raw)


def _urai_kunci(kunci, wilayah, var, turvar, tahun, turtahun):
    for w in wilayah:
        if not kunci.startswith(w):
            continue
        sisa = kunci[len(w):]
        for v in var:
            if not sisa.startswith(v):
                continue
            sisa2 = sisa[len(v):]
            for tv in turvar:
                if not sisa2.startswith(tv):
                    continue
                sisa3 = sisa2[len(tv):]
                for t in tahun:
                    if sisa3.startswith(t) and sisa3[len(t):] in turtahun:
                        return w, v, tv, t, sisa3[len(t):]
    return None


def baca_semua(raw=RAW):
    """{berkas relatif: DataFrame} untuk semua berkas BPS di data/raw/bps/."""
    raw = Path(raw)
    hasil = {}
    for path in sorted((raw / "bps").rglob("*")):
        if path.suffix == ".csv":
            df = baca_bps_csv(path, raw)
        elif path.suffix == ".json" and path.parent.name == "json":
            df = baca_bps_json(path, raw)
        elif path.suffix == ".json":
            df = baca_json_metadata(path, raw)
        else:
            continue
        hasil[df["_berkas_raw"].iat[0]] = df
    return hasil
