import importlib.util
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "periode",
    ROOT / "src" / "silver" / "periode.py",
)
assert SPEC is not None and SPEC.loader is not None
periode = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(periode)


class ValidasiPeriodeTest(unittest.TestCase):
    def test_bps_tahunan_lolos(self):
        periode.validasi_periode_bps(["Tahun", "tahun", "TAHUN"], "var1473")

    def test_bps_semester_ditolak(self):
        with self.assertRaises(periode.PeriodeTidakTahunan) as context:
            periode.validasi_periode_bps(["Tahun", "Semester 1"], "var1473")

        pesan = str(context.exception)
        self.assertIn("var1473", pesan)
        self.assertIn("Semester 1", pesan)

    def test_wdi_tahun_empat_digit_lolos(self):
        periode.validasi_periode_wdi(["2017", "2024", 2025], "SN.ITK.DEFC.ZS")

    def test_wdi_bulanan_ditolak(self):
        with self.assertRaises(periode.PeriodeTidakTahunan) as context:
            periode.validasi_periode_wdi(["2024-06"], "SN.ITK.DEFC.ZS")

        self.assertIn("2024-06", str(context.exception))

    def test_who_year_lolos(self):
        periode.validasi_periode_who(["YEAR", "year"], "NUTSTUNTINGPREV")

    def test_who_bulanan_ditolak(self):
        with self.assertRaises(periode.PeriodeTidakTahunan) as context:
            periode.validasi_periode_who(["MONTH"], "NUTSTUNTINGPREV")

        self.assertIn("MONTH", str(context.exception))

    def test_nilai_kosong_ditolak(self):
        with self.assertRaises(periode.PeriodeTidakTahunan):
            periode.validasi_periode_bps(["Tahun", math.nan], "var1473")


if __name__ == "__main__":
    unittest.main()
