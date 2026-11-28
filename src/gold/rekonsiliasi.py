"""Tabel rekonsiliasi Gold: seri utama BPS nasional vs pembanding WDI (Tahap 6, Backlog #24).

Satu baris = satu pasangan seri x satu periode. Pasangan ditetapkan dari definisi SDG yang sama:

    var1473 (BPS, PoU, SDG 2.1.1)   <->  SN.ITK.DEFC.ZS (WDI, PoU, SDG 2.1.1)
    var1474 (BPS, FIES, SDG 2.1.2)  <->  SN.ITK.MSFI.ZS (WDI, FIES, SDG 2.1.2)

Seri WHO GHO (stunting, overweight, wasting balita) tidak direkonsiliasi karena mengukur hal lain
(status gizi anak, SDG 2.2); ketiganya tetap tersaji berdampingan di tabel_nasional (K-018).

Periode yang hanya ada di salah satu sisi tetap ditulis dengan kategori "tanpa pasangan" dan
selisih kosong: selisih dijelaskan, tidak dihapus.
"""
import pandas as pd

PASANGAN = {
    "var1473": {
        "seri_pembanding": "SN.ITK.DEFC.ZS",
        "kategori": "metode berbeda",
        "penjelasan": (
            "Definisi sama (PoU, SDG 2.1.1). BPS menghitung langsung dari konsumsi kalori "
            "SUSENAS; WDI/FAO memakai model distribusi parametrik dengan parameter DEC global, "
            "sehingga tingkat BPS konsisten lebih tinggi."
        ),
    },
    "var1474": {
        "seri_pembanding": "SN.ITK.MSFI.ZS",
        "kategori": "metode berbeda",
        "penjelasan": (
            "Definisi sama (FIES sedang/berat, SDG 2.1.2). BPS memakai modul FIES SUSENAS dengan "
            "kalibrasi nasional; WDI/FAO memakai data FAO dan kalibrasi skala global, sehingga "
            "angka berdekatan tetapi tidak identik."
        ),
    },
}

KATEGORI_TANPA_PASANGAN = "tanpa pasangan"
KATEGORI_SAH = [
    "definisi berbeda",
    "metode berbeda",
    "vintage berbeda",
    "cakupan berbeda",
    "belum terjelaskan",
    KATEGORI_TANPA_PASANGAN,
]
KOLOM_REKONSILIASI = [
    "periode", "seri_utama", "seri_pembanding", "nilai_utama", "nilai_pembanding",
    "selisih", "status_pasangan", "kategori", "penjelasan",
    "_berkas_raw_utama", "_berkas_raw_pembanding",
]
KUNCI_REKONSILIASI = ["seri_utama", "periode"]


def _ambil(nasional, seri, awalan):
    bagian = nasional.loc[nasional["seri_kode"] == seri, ["periode", "nilai", "_berkas_raw"]]
    if bagian["periode"].duplicated().any():
        raise ValueError(f"rekonsiliasi: periode ganda pada seri {seri}")
    return bagian.rename(columns={"nilai": f"nilai_{awalan}", "_berkas_raw": f"_berkas_raw_{awalan}"})


def bangun_rekonsiliasi(nasional):
    """Bangun tabel rekonsiliasi dari tabel_nasional Gold (bentuk panjang, wilayah 9999)."""
    bagian = []
    for seri_utama, aturan in PASANGAN.items():
        seri_pembanding = aturan["seri_pembanding"]
        utama = _ambil(nasional, seri_utama, "utama")
        pembanding = _ambil(nasional, seri_pembanding, "pembanding")
        if utama.empty or pembanding.empty:
            raise ValueError(f"rekonsiliasi: seri {seri_utama} atau {seri_pembanding} tidak ada di Gold")

        gabung = utama.merge(pembanding, on="periode", how="outer", indicator=True)
        gabung["seri_utama"] = seri_utama
        gabung["seri_pembanding"] = seri_pembanding
        gabung["status_pasangan"] = gabung["_merge"].map(
            {"both": "berpasangan", "left_only": "hanya_utama", "right_only": "hanya_pembanding"}
        ).astype(str)
        berpasangan = gabung["_merge"] == "both"
        gabung["selisih"] = (gabung["nilai_utama"] - gabung["nilai_pembanding"]).where(berpasangan).round(4)
        gabung["kategori"] = KATEGORI_TANPA_PASANGAN
        gabung.loc[berpasangan, "kategori"] = aturan["kategori"]
        gabung["penjelasan"] = aturan["penjelasan"]
        gabung.loc[gabung["status_pasangan"] == "hanya_utama", "penjelasan"] = (
            f"{seri_pembanding} belum merilis angka untuk periode ini."
        )
        gabung.loc[gabung["status_pasangan"] == "hanya_pembanding", "penjelasan"] = (
            f"{seri_utama} (BPS) tidak tersedia untuk periode ini; seri BPS dimulai 2017."
        )
        bagian.append(gabung.drop(columns="_merge"))

    rekon = pd.concat(bagian, ignore_index=True)[KOLOM_REKONSILIASI]
    rekon["periode"] = rekon["periode"].astype(str)
    return rekon.sort_values(KUNCI_REKONSILIASI).reset_index(drop=True)


def validasi_rekonsiliasi(rekon):
    """Pemeriksaan keras: dipanggil sebelum tabel ditulis."""
    if rekon.duplicated(KUNCI_REKONSILIASI).any():
        raise ValueError("rekonsiliasi: kunci (seri_utama, periode) duplikat")
    if not set(rekon["kategori"]) <= set(KATEGORI_SAH):
        raise ValueError(f"rekonsiliasi: kategori tidak sah: {set(rekon['kategori']) - set(KATEGORI_SAH)}")
    pasangan = rekon["status_pasangan"] == "berpasangan"
    if rekon.loc[pasangan, "selisih"].isna().any():
        raise ValueError("rekonsiliasi: baris berpasangan tanpa selisih")
    if (rekon.loc[pasangan, "kategori"] == KATEGORI_TANPA_PASANGAN).any():
        raise ValueError("rekonsiliasi: baris berpasangan berlabel 'tanpa pasangan'")
    if (rekon.loc[~pasangan, "kategori"] != KATEGORI_TANPA_PASANGAN).any():
        raise ValueError("rekonsiliasi: baris tanpa pasangan harus berlabel 'tanpa pasangan'")
    if rekon["penjelasan"].isna().any() or (rekon["penjelasan"].str.strip() == "").any():
        raise ValueError("rekonsiliasi: ada baris tanpa penjelasan")
