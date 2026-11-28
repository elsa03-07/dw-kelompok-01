"""Uji perbaikan Sprint 2: aturan #20, rekonsiliasi #24, SQL #23, ekstraksi, dan kamus data #26.

Jalankan setelah `python unduh_data.py --kasus 1`:  python -m unittest discover -s tests
"""
import re
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gold.aturan_pilih import cocokkan_dengan_gold, pilih_baris_gold, tandai_anomali  # noqa: E402
from src.gold.builder import SILVER_FILE, bangun_gold  # noqa: E402
from src.gold.rekonsiliasi import bangun_rekonsiliasi, validasi_rekonsiliasi  # noqa: E402

GOLD_DIR = ROOT / "data" / "gold"
TABEL_KANONIS = ("panel_provinsi", "tabel_nasional", "tabel_nasional_lebar", "rekonsiliasi")


class Sprint2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.silver = pd.read_parquet(SILVER_FILE)
        cls.gold = bangun_gold(cls.silver)
        cls.rekon = bangun_rekonsiliasi(cls.gold["tabel_nasional"])

    # --- #20 aturan satu nilai per sel -------------------------------------------------------
    def test_aturan_pilih_sama_dengan_gold(self):
        provinsi, nasional, info = pilih_baris_gold(self.silver)
        cocokkan_dengan_gold(provinsi, nasional, self.gold["panel_provinsi"], self.gold["tabel_nasional"])
        self.assertEqual(info["baris_terpilih"], 742)
        self.assertEqual(info["K-015"]["dampak_baris"], 697)
        self.assertEqual(
            sum(info[k]["dampak_baris"] for k in ("K-014", "K-015", "K-016")),
            info["baris_tidak_terpilih"],
        )

    def test_wasting_who_ikut_terpilih(self):
        _, nasional, _ = pilih_baris_gold(self.silver)
        self.assertEqual(int((nasional["seri_kode"] == "NUTRITION_WH_2").sum()), 12)

    def test_kunci_ganda_gagal_bukan_dirata_rata(self):
        from src.gold.builder import bangun_panel
        ganda = pd.concat([self.silver, self.silver[self.silver["seri_kode"] == "var1473"].head(1)])
        with self.assertRaises(ValueError):
            bangun_panel(ganda)

    def test_penanda_anomali_tidak_mengubah_baris(self):
        panel = self.gold["panel_provinsi"]
        bertanda = tandai_anomali(panel)
        self.assertEqual(len(bertanda), len(panel))
        pd.testing.assert_series_equal(bertanda["nilai"], panel["nilai"])
        self.assertEqual(int(bertanda["is_outlier"].sum()), 45)
        dob_2024 = bertanda[bertanda["wilayah_kode"].isin([9200, 9500, 9600, 9700])]
        self.assertTrue(dob_2024["is_patahan"].all())

    # --- #24 rekonsiliasi ---------------------------------------------------------------------
    def test_rekonsiliasi_pasangan_bps_wdi(self):
        validasi_rekonsiliasi(self.rekon)
        pasangan = set(zip(self.rekon["seri_utama"], self.rekon["seri_pembanding"]))
        self.assertEqual(pasangan, {("var1473", "SN.ITK.DEFC.ZS"), ("var1474", "SN.ITK.MSFI.ZS")})
        berpasangan = self.rekon[self.rekon["status_pasangan"] == "berpasangan"]
        self.assertEqual(len(berpasangan), 16)
        self.assertEqual(sorted(berpasangan["periode"].unique()), [str(t) for t in range(2017, 2025)])

    def test_rekonsiliasi_tanpa_belum_terjelaskan(self):
        self.assertNotIn("belum terjelaskan", set(self.rekon["kategori"]))
        tanpa = self.rekon[self.rekon["status_pasangan"] != "berpasangan"]
        self.assertTrue((tanpa["kategori"] == "tanpa pasangan").all())
        self.assertTrue(tanpa["selisih"].isna().all())

    def test_selisih_sama_dengan_nilai_nasional(self):
        nas = self.gold["tabel_nasional"].set_index(["seri_kode", "periode"])["nilai"]
        for r in self.rekon[self.rekon["status_pasangan"] == "berpasangan"].itertuples():
            self.assertAlmostEqual(r.nilai_utama, nas[(r.seri_utama, r.periode)])
            self.assertAlmostEqual(r.nilai_pembanding, nas[(r.seri_pembanding, r.periode)])
            self.assertAlmostEqual(r.selisih, r.nilai_utama - r.nilai_pembanding, places=4)

    # --- #23 SQL ------------------------------------------------------------------------------
    def test_sql_jumlah_baris_sama_dan_kunci_primer(self):
        from src import sql
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "uji.sqlite"
            hasil = sql.jalankan(db_path=db)
            self.assertTrue(all(h["cocok"] for h in hasil))
            self.assertEqual({h["tabel"] for h in hasil}, {"silver", *TABEL_KANONIS})
            conn = sqlite3.connect(db)
            try:
                pk = [r[1] for r in conn.execute("PRAGMA table_info(panel_provinsi)") if r[5]]
                self.assertEqual(set(pk), {"seri_kode", "wilayah_kode", "periode"})
            finally:
                conn.close()

    # --- ekstraksi ----------------------------------------------------------------------------
    def test_ekstraksi_membaca_semua_berkas_manifest(self):
        from src import ekstraksi
        from src.common.manifest import baca
        hasil = ekstraksi.jalankan()
        self.assertEqual(set(hasil), set(baca()))
        for berkas, df in hasil.items():
            self.assertTrue((df["_berkas_raw"] == berkas).all())

    # --- #26 kamus data -----------------------------------------------------------------------
    def test_kamus_data_mencakup_semua_kolom(self):
        teks = (ROOT / "docs" / "data-dictionary.md").read_text(encoding="utf-8")
        bagian = dict(re.findall(r"^## (\w+) \(.*?\n(.*?)(?=^## |\Z)", teks, flags=re.M | re.S))
        sumber = {"silver": ROOT / "data" / "silver" / "silver.parquet",
                  **{n: GOLD_DIR / f"{n}.parquet" for n in TABEL_KANONIS}}
        for nama, path in sumber.items():
            self.assertIn(nama, bagian, f"kamus data tidak punya bagian {nama}")
            terdokumentasi = set(re.findall(r"^\| (\w+) \|", bagian[nama], flags=re.M)) - {"Kolom"}
            self.assertEqual(set(pd.read_parquet(path).columns), terdokumentasi, nama)


if __name__ == "__main__":
    unittest.main()
