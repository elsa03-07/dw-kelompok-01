"""Verifikasi katalog satuan dan kode SDG Kasus 01 terhadap data mentah.

Jalankan dari akar repositori:

    python reports/backlog/124450005/verifikasi_katalog.py

Skrip hanya memakai pustaka standar agar dapat dijalankan tanpa pandas/pyarrow.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
KATALOG = ROOT / "reports" / "backlog" / "124450005" / "katalog_seri_terverifikasi.csv"

BPS_FILES = {
    "var1473": "bps/2026-10-20/sdg2_2_1_1_v1473.csv",
    "var1474": "bps/2026-10-20/sdg2_2_1_2_v1474.csv",
}
WDI_FILE = "wdi/2026-10-20/data/kelompok-07-hal-01.json"
WDI_METADATA = "wdi/2026-10-20/metadata/sumber46_indikator.json"
WHO_FILES = {
    "NUTSTUNTINGPREV": {
        "csv": "who_gho/2026-10-20/datadot/5F8A486_NUTSTUNTINGPREV.csv",
        "uuid": "5F8A486",
    },
    "NUTOVERWEIGHTPREV": {
        "csv": "who_gho/2026-10-20/datadot/64E2430_NUTOVERWEIGHTPREV.csv",
        "uuid": "64E2430",
    },
    "NUTRITION_WH_2": {
        "csv": "who_gho/2026-10-20/datadot/FC5231F_NUTRITION_WH_2.csv",
        "uuid": "FC5231F",
    },
}
WHO_DDI = "who_gho/2026-10-20/datadot/ddiindicators_skip0000.json"
WHO_INDICATOR = "who_gho/2026-10-20/odata/Indicator.json"

EXPECTED = {
    ("bps", "var1473"): ("2.1.1", "persen", "tahun"),
    ("bps", "var1474"): ("2.1.2", "persen", "tahun"),
    ("wdi", "SN.ITK.DEFC.ZS"): ("2.1.1", "persen", "tahun"),
    ("wdi", "SN.ITK.MSFI.ZS"): ("2.1.2", "persen", "tahun"),
    ("who_gho", "NUTSTUNTINGPREV"): ("2.2.1", "persen", "tahun"),
    ("who_gho", "NUTOVERWEIGHTPREV"): ("2.2.2", "persen", "tahun"),
    ("who_gho", "NUTRITION_WH_2"): ("2.2.2", "persen", "tahun"),
}


def baca_katalog():
    with KATALOG.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def baca_csv_raw(relatif):
    with (RAW / relatif).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def baca_json(relatif):
    return json.loads((RAW / relatif).read_text(encoding="utf-8-sig"))


def iter_dicts(obj):
    if isinstance(obj, dict):
        yield obj
        for nilai in obj.values():
            yield from iter_dicts(nilai)
    elif isinstance(obj, list):
        for nilai in obj:
            yield from iter_dicts(nilai)


def nilai_numerik(baris, kolom):
    return [float(r[kolom]) for r in baris if str(r.get(kolom, "")).strip()]


def statistik(nilai):
    if not nilai:
        return 0, None, None
    return len(nilai), min(nilai), max(nilai)


def cek_rentang(cat, n, minimum, maksimum, salah):
    if int(float(cat["nilai_n"])) != n:
        salah.append(f"jumlah observasi {n} != katalog {cat['nilai_n']}")
    if minimum is not None and abs(float(cat["nilai_min"]) - minimum) > 0.01:
        salah.append(f"nilai_min {minimum} != katalog {cat['nilai_min']}")
    if maksimum is not None and abs(float(cat["nilai_max"]) - maksimum) > 0.01:
        salah.append(f"nilai_max {maksimum} != katalog {cat['nilai_max']}")
    if minimum is not None and minimum < 0:
        salah.append(f"nilai minimum {minimum} < 0")
    if maksimum is not None and maksimum > 100:
        salah.append(f"nilai maksimum {maksimum} > 100")


def cek_bps(cat, salah):
    baris = baca_csv_raw(BPS_FILES[cat["seri_kode"]])
    satuan = {str(r["satuan"]).strip().casefold() for r in baris}
    periode = {str(r["periode"]).strip().casefold() for r in baris}
    if satuan != {"persen"}:
        salah.append(f"satuan BPS tidak konsisten: {sorted(satuan)}")
    if periode != {"tahun"}:
        salah.append(f"periode BPS bukan tahunan: {sorted(periode)}")
    n, minimum, maksimum = statistik(nilai_numerik(baris, "nilai"))
    cek_rentang(cat, n, minimum, maksimum, salah)


def cek_wdi(cat, salah):
    data = baca_json(WDI_FILE)
    if not (isinstance(data, list) and len(data) > 1 and isinstance(data[1], list)):
        salah.append("struktur data WDI tidak dikenali")
        return
    seri = cat["seri_kode"]
    baris = [
        r for r in data[1]
        if isinstance(r, dict)
        and r.get("indicator", {}).get("id") == seri
        and r.get("value") is not None
    ]
    nama = {r.get("indicator", {}).get("value", "") for r in baris}
    if not nama or not all("%" in n for n in nama):
        salah.append(f"judul WDI tidak memuat tanda persen: {sorted(nama)}")
    tanggal = [str(r.get("date", "")) for r in baris]
    if not all(re.fullmatch(r"\d{4}", t) for t in tanggal):
        salah.append("tanggal WDI tidak semuanya tahunan empat digit")
    n, minimum, maksimum = statistik([r["value"] for r in baris])
    cek_rentang(cat, n, minimum, maksimum, salah)
    metadata = baca_json(WDI_METADATA)
    item = next(
        (
            x for x in iter_dicts(metadata)
            if x.get("id") == seri and isinstance(x.get("source"), dict)
        ),
        None,
    )
    if item is None:
        salah.append(f"metadata WDI untuk {seri} tidak ditemukan")
    elif str(item.get("source", {}).get("value", "")).strip() != "Sustainable Development Goals":
        salah.append(f"sumber metadata WDI {seri} bukan Sustainable Development Goals")


def cek_who(cat, salah):
    seri = cat["seri_kode"]
    info = WHO_FILES[seri]
    baris = baca_csv_raw(info["csv"])
    tipe_waktu = {str(r["DIM_TIME_TYPE"]).strip().casefold() for r in baris}
    if tipe_waktu != {"year"}:
        salah.append(f"periode WHO bukan tahunan: {sorted(tipe_waktu)}")
    kode = {str(r.get("IND_CODE", "")).strip() for r in baris}
    if kode != {seri}:
        salah.append(f"IND_CODE WHO tidak cocok: {sorted(kode)}")
    n, minimum, maksimum = statistik(nilai_numerik(baris, "RATE_PER_100_N"))
    cek_rentang(cat, n, minimum, maksimum, salah)

    ddi = baca_json(WHO_DDI).get("value", [])
    item = next(
        (
            x for x in ddi
            if isinstance(x, dict)
            and x.get("AlternativeCodes") == seri
        ),
        None,
    )
    if item is None:
        salah.append(f"metadata ddi WHO untuk {seri} tidak ditemukan")
    else:
        unit = str(item.get("UnitOfMeasure", ""))
        if "percentage" not in unit.casefold():
            salah.append(f"UnitOfMeasure WHO {seri} bukan percentage: {unit!r}")
        if "%" not in str(item.get("FullName", "")):
            salah.append(f"FullName WHO {seri} tidak memuat persen")

    indikator = baca_json(WHO_INDICATOR)
    if isinstance(indikator, dict):
        indikator = indikator.get("value", [])
    kode_indikator = {
        x.get("IndicatorCode")
        for x in indikator
        if isinstance(x, dict)
    }
    if seri not in kode_indikator:
        salah.append(f"IndicatorCode WHO {seri} tidak ditemukan di Indicator.json")


def main():
    katalog = baca_katalog()
    salah = []
    kunci = [(r["sumber"], r["seri_kode"]) for r in katalog]
    if len(katalog) != len(EXPECTED):
        salah.append(f"jumlah baris katalog {len(katalog)} != {len(EXPECTED)}")
    if len(kunci) != len(set(kunci)):
        salah.append("ada pasangan sumber+seri_kode duplikat")
    if set(kunci) != set(EXPECTED):
        salah.append(f"seri katalog tidak sesuai: {sorted(set(kunci) ^ set(EXPECTED))}")

    for cat in katalog:
        key = (cat["sumber"], cat["seri_kode"])
        if key not in EXPECTED:
            continue
        kode_sdg, satuan, periode = EXPECTED[key]
        if cat.get("kode_sdg") != kode_sdg:
            salah.append(f"{key}: kode_sdg {cat.get('kode_sdg')!r} != {kode_sdg!r}")
        if cat.get("satuan") != satuan:
            salah.append(f"{key}: satuan {cat.get('satuan')!r} != {satuan!r}")
        if cat.get("jenis_periode") != periode:
            salah.append(f"{key}: jenis_periode {cat.get('jenis_periode')!r} != {periode!r}")
        for kolom in ("sumber_satuan", "sumber_kode_sdg", "periode_bukti"):
            if not str(cat.get(kolom, "")).strip():
                salah.append(f"{key}: kolom {kolom} kosong")

        sebelum = len(salah)
        if cat["sumber"] == "bps":
            cek_bps(cat, salah)
        elif cat["sumber"] == "wdi":
            cek_wdi(cat, salah)
        elif cat["sumber"] == "who_gho":
            cek_who(cat, salah)
        else:
            salah.append(f"{key}: sumber tidak dikenal")
        if len(salah) == sebelum:
            print(f"OK   {cat['sumber']:<8} {cat['seri_kode']:<20} {satuan} {kode_sdg} {periode}")
        else:
            print(f"GAGAL {cat['sumber']:<8} {cat['seri_kode']:<20}")

    if salah:
        print("\nVerifikasi gagal:")
        for pesan in salah:
            print(f"- {pesan}")
        return 1

    print(
        f"\nLolos: {len(katalog)} seri, "
        f"{sum(1 for r in katalog if r['satuan'] == 'persen')} satuan persen, "
        f"{sum(1 for r in katalog if r['kode_sdg'])} kode SDG, "
        "0 periode non-tahunan"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
