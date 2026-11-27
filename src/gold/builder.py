import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SILVER_FILE = ROOT / "data" / "silver" / "silver.parquet"

PANEL_SERI = ("var1473", "var1474")
KOLOM_PANEL = [
    "sumber", "seri_kode", "nama_indikator", "kode_sdg", "wilayah_kode",
    "nama_wilayah", "periode", "jenis_periode", "rincian", "nilai", "satuan",
    "_berkas_raw", "_sha256_raw",
]
KOLOM_NASIONAL = [
    "sumber", "seri_kode", "nama_indikator", "kode_sdg", "kelompok_indikator",
    "wilayah_kode", "nama_wilayah", "periode", "jenis_periode", "rincian",
    "nilai", "satuan", "dapat_dibandingkan_dengan", "catatan_perbandingan",
    "_berkas_raw", "_sha256_raw",
]
KUNCI_PANEL = ["seri_kode", "wilayah_kode", "periode"]
KUNCI_NASIONAL = ["sumber", "seri_kode", "periode"]
KUNCI_TRACE = [
    "sumber", "seri_kode", "wilayah_kode", "periode", "rincian",
    "_berkas_raw", "_sha256_raw",
]

SERI_META = {
    "var1473": {
        "nama_indikator": "Prevalensi Ketidakcukupan Konsumsi Pangan (PoU)",
        "kode_sdg": "2.1.1",
        "kelompok_indikator": "seri_utama_bps",
        "dapat_dibandingkan_dengan": "indikator utama BPS",
        "catatan_perbandingan": "Agregat nasional BPS untuk PoU; bukan indikator WHO.",
    },
    "var1474": {
        "nama_indikator": "Prevalensi Penduduk dengan Kerawanan Pangan Sedang atau Berat (FIES)",
        "kode_sdg": "2.1.2",
        "kelompok_indikator": "seri_utama_bps",
        "dapat_dibandingkan_dengan": "indikator utama BPS",
        "catatan_perbandingan": "Agregat nasional BPS untuk FIES; bukan indikator WHO.",
    },
    "SN.ITK.DEFC.ZS": {
        "nama_indikator": "Prevalence of undernourishment (% of population)",
        "kode_sdg": "2.1.1",
        "kelompok_indikator": "pembanding_wdi",
        "dapat_dibandingkan_dengan": "var1473 (pembanding, bukan pengganti)",
        "catatan_perbandingan": "PoU global dari WDI; definisi, metode estimasi, dan vintage berbeda dari BPS.",
    },
    "SN.ITK.MSFI.ZS": {
        "nama_indikator": "Prevalence of moderate or severe food insecurity in the population (%)",
        "kode_sdg": "2.1.2",
        "kelompok_indikator": "pembanding_wdi",
        "dapat_dibandingkan_dengan": "var1474 (pembanding, bukan pengganti)",
        "catatan_perbandingan": "FIES dari WDI; definisi, metode estimasi, dan vintage berbeda dari BPS.",
    },
    "NUTSTUNTINGPREV": {
        "nama_indikator": "Stunting in children (under 5)",
        "kode_sdg": "2.2.1",
        "kelompok_indikator": "pembanding_who",
        "dapat_dibandingkan_dengan": "tidak langsung",
        "catatan_perbandingan": "Stunting balita (SDG 2.2.1), bukan PoU/FIES; tidak setara dengan BPS.",
    },
    "NUTOVERWEIGHTPREV": {
        "nama_indikator": "Overweight in children (under 5)",
        "kode_sdg": "2.2.2",
        "kelompok_indikator": "pembanding_who",
        "dapat_dibandingkan_dengan": "tidak langsung",
        "catatan_perbandingan": "Overweight balita (SDG 2.2.2), bukan PoU/FIES; tidak setara dengan BPS.",
    },
    "NUTRITION_WH_2": {
        "nama_indikator": "Wasting in children (under 5)",
        "kode_sdg": "2.2.2",
        "kelompok_indikator": "pembanding_who",
        "dapat_dibandingkan_dengan": "tidak langsung",
        "catatan_perbandingan": "Wasting balita (SDG 2.2.2), bukan PoU/FIES; tidak setara dengan BPS.",
    },
}
RINCIAN_WHO = {
    "NUTSTUNTINGPREV": "SEX=TOTAL",
    "NUTOVERWEIGHTPREV": "SEX=TOTAL",
    "NUTRITION_WH_2": "SEX=TOTAL; AGE=TOTAL",
}
KOLOM_LEBAR = {
    "var1473": "bps_var1473",
    "var1474": "bps_var1474",
    "SN.ITK.DEFC.ZS": "wdi_defc",
    "SN.ITK.MSFI.ZS": "wdi_msfi",
    "NUTSTUNTINGPREV": "who_stunting",
    "NUTOVERWEIGHTPREV": "who_overweight",
    "NUTRITION_WH_2": "who_wasting",
}
JUMLAH_NASIONAL = {
    "var1473": 9,
    "var1474": 9,
    "SN.ITK.DEFC.ZS": 24,
    "SN.ITK.MSFI.ZS": 10,
    "NUTSTUNTINGPREV": 25,
    "NUTOVERWEIGHTPREV": 25,
    "NUTRITION_WH_2": 12,
}


def _tambah_meta(df):
    meta = pd.DataFrame.from_dict(SERI_META, orient="index")
    meta.index.name = "seri_kode"
    kolom = [
        "nama_indikator", "kode_sdg", "kelompok_indikator",
        "dapat_dibandingkan_dengan", "catatan_perbandingan",
    ]
    return df.merge(meta[kolom].reset_index(), on="seri_kode", how="left", validate="many_to_one")


def bangun_panel(silver):
    panel = silver[
        (silver["sumber"] == "bps")
        & (silver["seri_kode"].isin(PANEL_SERI))
        & (silver["wilayah_kode"] != 9999)
        & (silver["rincian"] == "Total")
    ].copy()
    # Aturan satu nilai per sel: kunci ganda adalah kesalahan, bukan untuk dirata-rata (K-014).
    ganda = panel.duplicated(KUNCI_PANEL, keep=False)
    if ganda.any():
        raise ValueError(
            f"panel_provinsi: {int(ganda.sum())} baris berkunci ganda (seri, wilayah, periode); "
            "selesaikan di aturan pemilihan, jangan dirata-rata"
        )
    panel = _tambah_meta(panel)
    panel = panel[KOLOM_PANEL].sort_values(
        ["seri_kode", "wilayah_kode", "periode"]
    ).reset_index(drop=True)
    return panel


def bangun_nasional(silver):
    nasional = silver[
        (silver["wilayah_kode"] == 9999)
        & (silver["seri_kode"].isin(SERI_META))
    ].copy()
    bagian = []
    for seri, grup in nasional.groupby("seri_kode", sort=False):
        rincian = RINCIAN_WHO.get(seri, "Total")
        terpilih = grup[grup["rincian"] == rincian]
        if terpilih.empty:
            raise ValueError(f"Rincian Gold {seri} tidak ditemukan: {rincian}")
        bagian.append(terpilih)
    nasional = pd.concat(bagian, ignore_index=True)
    nasional = _tambah_meta(nasional)
    nasional = nasional[KOLOM_NASIONAL].sort_values(
        ["sumber", "seri_kode", "periode"]
    ).reset_index(drop=True)
    return nasional


def bangun_nasional_lebar(nasional):
    nilai = nasional.pivot(
        index="periode", columns="seri_kode", values="nilai"
    ).reindex(columns=list(KOLOM_LEBAR))
    tahun_awal = int(nasional["periode"].min())
    tahun_akhir = int(nasional["periode"].max())
    tahun = [str(t) for t in range(tahun_awal, tahun_akhir + 1)]
    nilai = nilai.reindex(index=tahun)
    nilai = nilai.rename(columns=KOLOM_LEBAR).reset_index()
    nilai["periode"] = nilai["periode"].astype(str)
    return nilai


def _cek_kolom(df, kolom, nama):
    kurang = [k for k in kolom if k not in df.columns]
    if kurang:
        raise ValueError(f"{nama}: kolom wajib tidak ada: {kurang}")


def _cek_nilai_dan_satuan(df, nama):
    if df["nilai"].isna().any():
        raise ValueError(f"{nama}: ada {int(df['nilai'].isna().sum())} nilai kosong")
    if not ((df["nilai"] >= 0) & (df["nilai"] <= 100)).all():
        raise ValueError(f"{nama}: nilai di luar rentang 0-100")
    if set(df["satuan"]) != {"persen"}:
        raise ValueError(f"{nama}: satuan tidak konsisten: {sorted(set(df['satuan']))}")


def _cek_trace(silver, df, nama):
    sumber = silver[KUNCI_TRACE + ["nilai"]].copy()
    gabung = df.merge(
        sumber, on=KUNCI_TRACE, how="left", suffixes=("", "_silver"),
        indicator=True, validate="one_to_one",
    )
    if len(gabung) != len(df):
        raise ValueError(f"{nama}: penggabungan lineage mengubah jumlah baris")
    if not (gabung["_merge"] == "both").all():
        raise ValueError(f"{nama}: ada baris yang tidak ditemukan di Silver")
    selisih = (gabung["nilai"] - gabung["nilai_silver"]).abs()
    if (selisih > 1e-12).any():
        raise ValueError(f"{nama}: nilai berbeda dari Silver")


def _cek_varian_total_wasting(silver):
    wasting = silver[
        (silver["sumber"] == "who_gho")
        & (silver["seri_kode"] == "NUTRITION_WH_2")
        & (silver["wilayah_kode"] == 9999)
    ]
    for periode, grup in wasting.groupby("periode"):
        total = grup[grup["rincian"].str.contains("TOTAL", regex=False)]
        if total.empty:
            raise ValueError(f"Wasting {periode}: tidak ada rincian total")
        nilai = set(round(float(v), 10) for v in total["nilai"])
        if len(nilai) != 1:
            raise ValueError(
                f"Wasting {periode}: varian rincian total tidak identik: {sorted(nilai)}"
            )


def validasi_gold(silver, panel, nasional, lebar):
    _cek_kolom(panel, KOLOM_PANEL, "panel_provinsi")
    _cek_kolom(nasional, KOLOM_NASIONAL, "tabel_nasional")
    _cek_kolom(
        lebar,
        ["periode"] + list(KOLOM_LEBAR.values()),
        "tabel_nasional_lebar",
    )

    if len(panel) != 628:
        raise ValueError(f"panel_provinsi: jumlah baris {len(panel)}, seharusnya 628")
    if len(nasional) != 114:
        raise ValueError(f"tabel_nasional: jumlah baris {len(nasional)}, seharusnya 114")
    if len(lebar) != 30:
        raise ValueError(f"tabel_nasional_lebar: jumlah baris {len(lebar)}, seharusnya 30")

    if panel.duplicated(KUNCI_PANEL).any():
        raise ValueError("panel_provinsi: kunci (seri, wilayah, periode) duplikat")
    if nasional.duplicated(KUNCI_NASIONAL).any():
        raise ValueError("tabel_nasional: kunci (sumber, seri, periode) duplikat")
    if lebar.duplicated(["periode"]).any():
        raise ValueError("tabel_nasional_lebar: periode duplikat")

    if set(panel["seri_kode"]) != set(PANEL_SERI):
        raise ValueError("panel_provinsi: seri tidak lengkap")
    if set(nasional["seri_kode"]) != set(SERI_META):
        raise ValueError("tabel_nasional: seri tidak lengkap")
    if set(panel["wilayah_kode"]) & {9999}:
        raise ValueError("panel_provinsi: agregat nasional 9999 tidak boleh masuk")
    if set(nasional["wilayah_kode"]) != {9999}:
        raise ValueError("tabel_nasional: harus hanya wilayah 9999")

    _cek_nilai_dan_satuan(panel, "panel_provinsi")
    _cek_nilai_dan_satuan(nasional, "tabel_nasional")

    for df, nama, kolom in [
        (panel, "panel_provinsi", KOLOM_PANEL),
        (nasional, "tabel_nasional", KOLOM_NASIONAL),
    ]:
        kosong = [k for k in kolom if df[k].isna().any()]
        if kosong:
            raise ValueError(f"{nama}: kolom kosong: {kosong}")

    hitung = panel.groupby("seri_kode").size().to_dict()
    if hitung != {"var1473": 314, "var1474": 314}:
        raise ValueError(f"panel_provinsi: jumlah per seri salah: {hitung}")

    hitung_nasional = nasional.groupby("seri_kode").size().to_dict()
    if hitung_nasional != JUMLAH_NASIONAL:
        raise ValueError(f"tabel_nasional: jumlah per seri salah: {hitung_nasional}")

    for seri, rincian in RINCIAN_WHO.items():
        dipilih = set(nasional.loc[nasional["seri_kode"] == seri, "rincian"])
        if dipilih != {rincian}:
            raise ValueError(f"tabel_nasional: rincian {seri} salah: {dipilih}")

    _cek_varian_total_wasting(silver)
    _cek_trace(silver, panel, "panel_provinsi")
    _cek_trace(silver, nasional, "tabel_nasional")

    panjang = nasional.set_index(["periode", "seri_kode"])["nilai"].to_dict()
    non_kosong = 0
    for _, baris in lebar.iterrows():
        for seri, kolom in KOLOM_LEBAR.items():
            nilai = baris[kolom]
            asli = panjang.get((baris["periode"], seri))
            if pd.isna(nilai):
                if asli is not None:
                    raise ValueError(f"tabel_nasional_lebar: {baris['periode']} {seri} kosong")
            else:
                non_kosong += 1
                if asli is None or not math.isclose(float(nilai), float(asli), rel_tol=0, abs_tol=1e-12):
                    raise ValueError(
                        f"tabel_nasional_lebar: nilai {baris['periode']} {seri} tidak cocok"
                    )
    if non_kosong != len(nasional):
        raise ValueError(
            f"tabel_nasional_lebar: {non_kosong} sel terisi, seharusnya {len(nasional)}"
        )


def bangun_gold(silver):
    panel = bangun_panel(silver)
    nasional = bangun_nasional(silver)
    lebar = bangun_nasional_lebar(nasional)
    validasi_gold(silver, panel, nasional, lebar)
    return {
        "panel_provinsi": panel,
        "tabel_nasional": nasional,
        "tabel_nasional_lebar": lebar,
    }
