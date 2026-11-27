import sys
import unittest
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gold.builder import (  # noqa: E402
    KOLOM_LEBAR,
    KUNCI_NASIONAL,
    KUNCI_PANEL,
    KUNCI_TRACE,
    SERI_META,
    SILVER_FILE,
    bangun_gold,
)


class GoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.silver = pd.read_parquet(SILVER_FILE)
        cls.tabel = bangun_gold(cls.silver)
        cls.panel = cls.tabel["panel_provinsi"]
        cls.nasional = cls.tabel["tabel_nasional"]
        cls.lebar = cls.tabel["tabel_nasional_lebar"]

    def test_panel_bentuk_dan_kunci(self):
        self.assertEqual(len(self.panel), 628)
        self.assertEqual(set(self.panel["seri_kode"]), {"var1473", "var1474"})
        self.assertEqual(self.panel["wilayah_kode"].nunique(), 38)
        self.assertEqual(self.panel["periode"].nunique(), 9)
        self.assertFalse(self.panel.duplicated(KUNCI_PANEL).any())
        self.assertNotIn(9999, set(self.panel["wilayah_kode"]))
        self.assertFalse(self.panel["nilai"].isna().any())
        self.assertEqual(self.panel.groupby("seri_kode").size().to_dict(),
                         {"var1473": 314, "var1474": 314})

    def test_panel_trace_ke_silver(self):
        sumber = self.silver[KUNCI_TRACE + ["nilai"]].copy()
        gabung = self.panel.merge(
            sumber, on=KUNCI_TRACE, how="left", suffixes=("", "_silver"),
            indicator=True, validate="one_to_one",
        )
        self.assertEqual(len(gabung), len(self.panel))
        self.assertTrue((gabung["_merge"] == "both").all())
        self.assertTrue(((gabung["nilai"] - gabung["nilai_silver"]).abs() < 1e-12).all())

    def test_panel_tidak_mengimputasi_sel_struktural(self):
        provinsi = set(self.silver.loc[
            (self.silver["sumber"] == "bps")
            & (self.silver["wilayah_kode"] != 9999),
            "wilayah_kode",
        ])
        tahun = set(self.silver.loc[
            (self.silver["sumber"] == "bps")
            & (self.silver["wilayah_kode"] != 9999),
            "periode",
        ])
        grid = {(w, t) for w in provinsi for t in tahun}
        for seri in ("var1473", "var1474"):
            teramati = set(
                self.panel.loc[self.panel["seri_kode"] == seri]
                .set_index(["wilayah_kode", "periode"])
                .index
            )
            self.assertEqual(len(grid - teramati), 28)
            self.assertTrue(teramati.issubset(grid))

    def test_nasional_bentuk_dan_kunci(self):
        self.assertEqual(len(self.nasional), 114)
        self.assertEqual(set(self.nasional["seri_kode"]), set(SERI_META))
        self.assertFalse(self.nasional.duplicated(KUNCI_NASIONAL).any())
        self.assertEqual(set(self.nasional["wilayah_kode"]), {9999})
        self.assertFalse(self.nasional["nilai"].isna().any())
        self.assertEqual(set(self.nasional["satuan"]), {"persen"})
        self.assertTrue(((self.nasional["nilai"] >= 0) & (self.nasional["nilai"] <= 100)).all())

    def test_nasional_trace_ke_silver(self):
        sumber = self.silver[KUNCI_TRACE + ["nilai"]].copy()
        gabung = self.nasional.merge(
            sumber, on=KUNCI_TRACE, how="left", suffixes=("", "_silver"),
            indicator=True, validate="one_to_one",
        )
        self.assertEqual(len(gabung), len(self.nasional))
        self.assertTrue((gabung["_merge"] == "both").all())
        self.assertTrue(((gabung["nilai"] - gabung["nilai_silver"]).abs() < 1e-12).all())

    def test_pemilihan_rincian_who(self):
        hitung = self.nasional.groupby("seri_kode").size().to_dict()
        self.assertEqual(hitung["NUTSTUNTINGPREV"], 25)
        self.assertEqual(hitung["NUTOVERWEIGHTPREV"], 25)
        self.assertEqual(hitung["NUTRITION_WH_2"], 12)
        self.assertEqual(
            set(self.nasional.loc[self.nasional["seri_kode"] == "NUTSTUNTINGPREV", "rincian"]),
            {"SEX=TOTAL"},
        )
        self.assertEqual(
            set(self.nasional.loc[self.nasional["seri_kode"] == "NUTOVERWEIGHTPREV", "rincian"]),
            {"SEX=TOTAL"},
        )
        self.assertEqual(
            set(self.nasional.loc[self.nasional["seri_kode"] == "NUTRITION_WH_2", "rincian"]),
            {"SEX=TOTAL; AGE=TOTAL"},
        )

    def test_tabel_lebar_berdampingan(self):
        self.assertEqual(len(self.lebar), 30)
        self.assertFalse(self.lebar.duplicated(["periode"]).any())
        self.assertEqual(
            list(self.lebar.columns),
            ["periode"] + list(KOLOM_LEBAR.values()),
        )
        jumlah_sel = int(self.lebar[list(KOLOM_LEBAR.values())].notna().sum().sum())
        self.assertEqual(jumlah_sel, len(self.nasional))
        panjang = self.nasional.set_index(["periode", "seri_kode"])["nilai"].to_dict()
        for _, baris in self.lebar.iterrows():
            for seri, kolom in KOLOM_LEBAR.items():
                nilai = baris[kolom]
                asli = panjang.get((baris["periode"], seri))
                if pd.isna(nilai):
                    self.assertIsNone(asli)
                else:
                    self.assertIsNotNone(asli)
                    self.assertAlmostEqual(float(nilai), float(asli), places=12)

    def test_idempoten(self):
        ulang = bangun_gold(self.silver)
        for nama in self.tabel:
            assert_frame_equal(self.tabel[nama], ulang[nama], check_like=False)


if __name__ == "__main__":
    unittest.main()
