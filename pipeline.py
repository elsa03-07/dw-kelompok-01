"""Satu perintah reproduksi tim: data mentah -> ekstraksi -> Silver -> Gold -> SQL -> validasi.

    python unduh_data.py --kasus <N>     # sekali, isi data/raw/
    python pipeline.py                   # hasilkan ulang semuanya
    python pipeline.py --nim 124450032   # sama, lalu tulis results/<nim>/metrics.json dari hasil run ini

Urutan tahap tidak diubah; isi tiap tahap di src/<tahap>/. Tahap 7 (skala, arsip WDI) ditulis
sebagai skrip terpisah di src/skala/ karena memakai unduhan tambahan.

Setiap run menulis reports/ringkasan_pipeline.md: jumlah baris tiap keluaran, sidik sha256-nya,
hasil pemeriksaan SQL, dan hasil validasi. Isinya deterministik, jadi dua klon bersih yang
menjalankan pipeline atas data mentah yang sama harus menghasilkan berkas yang identik.
"""
import argparse
import json
import sys
import time
from pathlib import Path

from src import ekstraksi, gold, silver, sql, validasi
from src.common.manifest import periksa, sha256

ROOT = Path(__file__).resolve().parent
RINGKASAN = ROOT / "reports" / "ringkasan_pipeline.md"


def tulis_ringkasan(n_raw, hasil):
    keluaran = [ROOT / "data" / "silver" / "silver.parquet"] + [
        ROOT / "data" / "gold" / f"{nama}.parquet" for nama in gold.TABEL_KANONIS
    ]
    tabel = {"silver": hasil["silver"], **{k: v for k, v in hasil["gold"].items() if not k.startswith("_")}}
    info = hasil["gold"]["_info_aturan"]
    rekon = hasil["gold"]["rekonsiliasi"]
    baris = [
        "# Ringkasan run pipeline.py",
        "",
        "Ditulis otomatis oleh `python pipeline.py`. Jangan disunting manual.",
        "",
        f"- Berkas mentah cocok dengan MANIFEST.csv: **{n_raw}**",
        f"- Berkas mentah terbaca di tahap ekstraksi: **{len(hasil['ekstraksi'])}**",
        f"- Validasi: **{hasil['validasi']['aturan_lolos']}/{hasil['validasi']['aturan_validasi']} aturan lolos** "
        "(rincian di `reports/validasi.md`)",
        "",
        "## Keluaran",
        "",
        "| Berkas | Baris | Kolom | sha256 (12 awal) |",
        "|---|---:|---:|---|",
    ]
    for path in keluaran:
        df = tabel[path.stem]
        baris.append(f"| `{path.relative_to(ROOT).as_posix()}` | {len(df):,} | {len(df.columns)} | `{sha256(path)[:12]}` |")
    baris += [
        "",
        "## Aturan satu nilai per sel (#20), juga tertulis di log-keputusan.csv",
        "",
        "| Keputusan | Aturan | Baris disisihkan |",
        "|---|---|---:|",
    ]
    for kode in ("K-014", "K-016", "K-015", "K-017"):
        baris.append(f"| {kode} | {info[kode]['nama']} | {info[kode]['dampak_baris']:,} |")
    baris += [
        "",
        f"Silver {info['baris_silver']:,} baris → terpilih ke Gold {info['baris_terpilih']:,}; "
        f"{info['baris_tidak_terpilih']:,} baris subkelompok tetap hanya di Silver.",
        "",
        "## Rekonsiliasi (#24)",
        "",
        "| Seri utama | Pembanding | Berpasangan | Tanpa pasangan | Rata-rata selisih |",
        "|---|---|---:|---:|---:|",
    ]
    for seri, grup in rekon.groupby("seri_utama"):
        pas = grup[grup["status_pasangan"] == "berpasangan"]
        baris.append(f"| {seri} | {grup['seri_pembanding'].iat[0]} | {len(pas)} | {len(grup) - len(pas)} | "
                     f"{pas['selisih'].mean():+.2f} poin persen |")
    baris += [
        "",
        "## SQL (#23): data/capstone.sqlite",
        "",
        "| Tabel | Baris Parquet | Baris SQL | Cocok |",
        "|---|---:|---:|:---:|",
    ]
    for h in hasil["sql"]:
        baris.append(f"| {h['tabel']} | {h['baris_parquet']:,} | {h['baris_sql']:,} | {'ya' if h['cocok'] else 'TIDAK'} |")
    RINGKASAN.write_text("\n".join(baris) + "\n", encoding="utf-8")
    print(f"Ringkasan ditulis: {RINGKASAN.relative_to(ROOT).as_posix()}")


def tulis_metrik(nim, n_raw, hasil, durasi):
    from src.common.hasil import tulis_hasil

    lama = ROOT / "results" / str(nim) / "metrics.json"
    metrik = json.loads(lama.read_text(encoding="utf-8"))["metrik"] if lama.exists() else {}
    rekon = hasil["gold"]["rekonsiliasi"]
    metrik.update({
        "berkas_raw_terverifikasi": n_raw,
        "baris_silver": len(hasil["silver"]),
        "baris_gold_panel": len(hasil["gold"]["panel_provinsi"]),
        "baris_gold_nasional": len(hasil["gold"]["tabel_nasional"]),
        "baris_rekonsiliasi": len(rekon),
        "rekonsiliasi_berpasangan": int((rekon["status_pasangan"] == "berpasangan").sum()),
        "tabel_sql_cocok": sum(h["cocok"] for h in hasil["sql"]),
        "aturan_validasi": hasil["validasi"]["aturan_validasi"],
        "aturan_lolos": hasil["validasi"]["aturan_lolos"],
    })
    print(f"Metrik ditulis: {tulis_hasil(nim, metrik, seed=0, durasi_detik=durasi).relative_to(ROOT).as_posix()}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pipeline tim: data mentah sampai Gold, SQL, dan validasi")
    ap.add_argument("--nim", help="tulis results/<nim>/metrics.json dari hasil run ini")
    args = ap.parse_args(argv)

    n, salah = periksa()
    if salah:
        sys.exit(f"data/raw tidak cocok dengan MANIFEST.csv ({len(salah)} berkas). Jalankan ulang unduh_data.py.")
    print(f"data/raw: {n} berkas cocok dengan MANIFEST.csv")

    hasil = {}
    mulai_total = time.time()
    for nama, langkah in [("ekstraksi", lambda h: ekstraksi.jalankan()),
                          ("silver", lambda h: silver.jalankan(h["ekstraksi"])),
                          ("gold", lambda h: gold.jalankan(h["silver"])),
                          ("sql", lambda h: sql.jalankan(h["silver"], h["gold"])),
                          ("validasi", lambda h: validasi.jalankan(h["silver"], h["gold"], h["sql"]))]:
        print(f"[{nama}]")
        mulai = time.time()
        hasil[nama] = langkah(hasil)
        print(f"{nama:<10} selesai dalam {time.time() - mulai:.1f} s")
    durasi = time.time() - mulai_total

    tulis_ringkasan(n, hasil)
    if args.nim:
        tulis_metrik(args.nim, n, hasil, durasi)
    print(f"Pipeline selesai dalam {durasi:.1f} s.")
    print("Periksa skema minimal: python -m src.common.skema data/silver/silver.parquet")


if __name__ == "__main__":
    main()
