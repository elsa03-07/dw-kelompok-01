"""Aturan pemilihan satu nilai per sel Gold (Tahap 4, Backlog #20). Penanggung jawab: 124450061.

Dipanggil dari pipeline:  pipeline.py -> src.gold.jalankan() -> pilih_baris_gold()

Aturan diterapkan berurutan pada Silver; dampak tiap aturan dihitung dari baris yang benar-benar
disisihkan oleh aturan itu sendiri, lalu ditulis otomatis ke kolom dampak_baris di
log-keputusan.csv (tidak diketik manual):

    K-014  Snapshot terbaru: bila sel (sumber, seri, wilayah, periode, rincian) muncul di lebih dari
           satu snapshot, pakai snapshot dengan tanggal folder terbaru.
    K-016  Periode tahunan: hanya jenis_periode == 'tahun'; tidak ada agregasi buatan.
    K-015  Rincian sebanding: BPS/WDI 'Total'; WHO memakai rincian total yang sama dengan
           src.gold.builder.RINCIAN_WHO. Subkelompok WHO tetap hanya di Silver.
    K-017  Penanda anomali: outlier dan patahan seri ditandai di panel Gold, tidak ada baris dibuang.

Hasil pemilihan dicocokkan dengan tabel Gold kanonis dari builder.py; bila berbeda, pipeline gagal.
"""
import re
from pathlib import Path

import pandas as pd

from src.gold.builder import PANEL_SERI, RINCIAN_WHO, SERI_META

ROOT = Path(__file__).resolve().parents[2]
ANOMALI_FILE = ROOT / "reports" / "backlog" / "124450061" / "daftar_anomali_terklasifikasi.csv"
LOG_KEPUTUSAN = ROOT / "log-keputusan.csv"

KUNCI_SEL = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian"]
DOB_PAPUA = {9200, 9500, 9600, 9700}
TAHUN_PEMEKARAN = 2024
POLA_TANGGAL = re.compile(r"(\d{4}-\d{2}-\d{2})")
POLA_DAMPAK = re.compile(r",(\d+)$")


def _tanggal_snapshot(berkas):
    cocok = POLA_TANGGAL.search(str(berkas))
    return cocok.group(1) if cocok else ""


def _rincian_sebanding(df):
    rincian_wajib = df["seri_kode"].map(RINCIAN_WHO).fillna("Total")
    return df["rincian"] == rincian_wajib


def pilih_baris_gold(silver):
    """Terapkan K-014, K-016, K-015 berurutan. Kembalikan (provinsi, nasional, info_dampak)."""
    awal = len(silver)

    # K-014: snapshot terbaru per sel
    df = silver.assign(_snapshot=silver["_berkas_raw"].map(_tanggal_snapshot))
    df = df.sort_values(KUNCI_SEL + ["_snapshot"]).drop_duplicates(KUNCI_SEL, keep="last")
    dampak_snapshot = awal - len(df)

    # K-016: periode tahunan murni
    sebelum = len(df)
    df = df[df["jenis_periode"] == "tahun"]
    dampak_periode = sebelum - len(df)

    # K-015: rincian sebanding (hanya seri kasus)
    sebelum = len(df)
    df = df[df["seri_kode"].isin(SERI_META) & _rincian_sebanding(df)]
    dampak_rincian = sebelum - len(df)

    df = df.drop(columns="_snapshot")
    provinsi = df[(df["sumber"] == "bps") & df["seri_kode"].isin(PANEL_SERI) & (df["wilayah_kode"] != 9999)]
    nasional = df[df["wilayah_kode"] == 9999]

    info = {
        "K-014": {"nama": "Snapshot terbaru per sel", "dampak_baris": int(dampak_snapshot)},
        "K-016": {"nama": "Periode tahunan murni", "dampak_baris": int(dampak_periode)},
        "K-015": {"nama": "Rincian sebanding (subkelompok WHO tetap di Silver)", "dampak_baris": int(dampak_rincian)},
        "K-017": {"nama": "Penanda outlier dan patahan (tanpa membuang baris)", "dampak_baris": 0},
        "baris_silver": int(awal),
        "baris_terpilih": int(len(provinsi) + len(nasional)),
    }
    info["baris_tidak_terpilih"] = info["baris_silver"] - info["baris_terpilih"]
    return provinsi, nasional, info


def cocokkan_dengan_gold(provinsi, nasional, panel, tabel_nasional):
    """Pastikan aturan #20 dan builder kanonis memilih sel yang sama persis."""
    for nama, pilihan, gold, kunci in [
        ("panel_provinsi", provinsi, panel, ["seri_kode", "wilayah_kode", "periode"]),
        ("tabel_nasional", nasional, tabel_nasional, ["sumber", "seri_kode", "periode"]),
    ]:
        a = set(map(tuple, pilihan[kunci].astype(str).to_numpy()))
        b = set(map(tuple, gold[kunci].astype(str).to_numpy()))
        if a != b:
            raise ValueError(
                f"{nama}: aturan pemilihan (#20) dan Gold kanonis berbeda "
                f"({len(a - b)} hanya di aturan, {len(b - a)} hanya di Gold)"
            )


def muat_peta_anomali(path=ANOMALI_FILE):
    """{(seri, wilayah, tahun): kategori} dari klasifikasi anomali Sprint 1 (K-002)."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Daftar anomali Sprint 1 tidak ditemukan: {path}")
    df = pd.read_csv(path)
    return {
        (str(r.seri_kode), int(r.wilayah_id), str(int(r.tahun))): str(r.kategori_anomali)
        for r in df.itertuples(index=False)
    }


def tandai_anomali(panel):
    """K-017: tambahkan status_anomali, is_outlier, is_patahan ke panel panjang. Baris tidak berubah."""
    peta = muat_peta_anomali()
    kunci = zip(panel["seri_kode"].astype(str), panel["wilayah_kode"].astype(int), panel["periode"].astype(str))
    status = pd.Series([peta.get(k, "Normal") for k in kunci], index=panel.index, dtype="string")
    tahun = panel["periode"].astype(int)
    pemekaran = panel["wilayah_kode"].isin(DOB_PAPUA) & (tahun >= TAHUN_PEMEKARAN)
    hasil = panel.copy()
    hasil["status_anomali"] = status
    hasil["is_outlier"] = status.str.contains("Outlier", regex=False).astype(bool)
    hasil["is_patahan"] = (status.str.contains("Patahan", regex=False) | pemekaran).astype(bool)
    return hasil


def catat_dampak_ke_log(info, path=LOG_KEPUTUSAN):
    """Tulis dampak_baris K-014..K-017 (kolom terakhir) ke log-keputusan.csv. Baris lain tidak disentuh."""
    path = Path(path)
    teks = path.read_bytes().decode("utf-8")
    akhir_baris = "\r\n" if "\r\n" in teks else "\n"
    kode_aturan = {k for k, v in info.items() if isinstance(v, dict)}
    baris_baru, ditemukan = [], set()
    for baris in teks.split(akhir_baris):
        kode = baris.split(",", 1)[0]
        if kode in kode_aturan and POLA_DAMPAK.search(baris):
            baris = POLA_DAMPAK.sub(f",{info[kode]['dampak_baris']}", baris)
            ditemukan.add(kode)
        baris_baru.append(baris)
    if kode_aturan - ditemukan:
        raise ValueError(f"log-keputusan.csv tidak memuat keputusan {sorted(kode_aturan - ditemukan)}")
    path.write_bytes(akhir_baris.join(baris_baru).encode("utf-8"))
