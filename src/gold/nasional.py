from __future__ import annotations

from pathlib import Path
import pandas as pd


SERI_UTAMA = ["var1473", "var1474"]
SERI_PEMBANDING = [
    "SN.ITK.DEFC.ZS",
    "SN.ITK.MSFI.ZS",
    "NUTSTUNTINGPREV",
    "NUTOVERWEIGHTPREV",
    "NUTRITION_WH_2",
]
SEMUA_SERI = SERI_UTAMA + SERI_PEMBANDING


def _format_raw(row: pd.Series) -> str:
    berkas = str(row.get("_berkas_raw", "") or "")
    sha = str(row.get("_sha256_raw", "") or "")
    if berkas and sha:
        return f"{berkas}#{sha[:12]}"
    return berkas or sha


def bangun_tabel_nasional(
    df_silver: pd.DataFrame,
    out_path: str | Path = "data/gold/tabel_nasional.parquet",
) -> pd.DataFrame:
    df = df_silver.copy()
    df["wilayah_kode_str"] = df["wilayah_kode"].astype(str).str.strip()
    df["periode_str"] = df["periode"].astype(str).str.strip()

    # Fokus ke rincian Total bila ada agar tidak duplikat per sub-kategori
    if "rincian" in df.columns:
        df_total = df[df["rincian"].astype(str).str.lower() == "total"]
        if not df_total.empty:
            df = df_total

    periodes = sorted(df["periode_str"].dropna().unique().tolist())
    rows: list[dict] = []

    for p in periodes:
        sub_p = df[df["periode_str"] == p]
        record: dict = {"periode": p}
        asal_items: list[str] = []

        for seri in SEMUA_SERI:
            sub_s = sub_p[sub_p["seri_kode"] == seri]
            nas = sub_s[sub_s["wilayah_kode_str"] == "9999"]

            if not nas.empty:
                r0 = nas.iloc[0]
                record[seri] = r0["nilai"]
                record[f"{seri}_raw"] = _format_raw(r0)
                asal_items.append(f"{seri}:baris_nasional_9999")
            else:
                # Fallback agregat provinsi jika tersedia (bobot setara/rata-rata provinsi)
                prov = sub_s[sub_s["wilayah_kode_str"] != "9999"]
                prov_valid = prov.dropna(subset=["nilai"])
                if not prov_valid.empty and seri in SERI_UTAMA:
                    n_prov = prov_valid["wilayah_kode_str"].nunique()
                    record[seri] = float(prov_valid["nilai"].mean())
                    record[f"{seri}_raw"] = _format_raw(prov_valid.iloc[0])
                    asal_items.append(
                        f"{seri}:agregat_provinsi(bobot_setara_1/{n_prov},alasan=tanpa_baris_9999)"
                    )
                elif not prov_valid.empty:
                    record[seri] = None
                    record[f"{seri}_raw"] = _format_raw(prov_valid.iloc[0])
                    asal_items.append(f"{seri}:tanpa_padanan_nasional_langsung")
                else:
                    record[seri] = None
                    record[f"{seri}_raw"] = None
                    asal_items.append(f"{seri}:tidak_tersedia")

        record["asal_angka_nasional"] = " | ".join(asal_items)
        rows.append(record)

    out_df = pd.DataFrame(rows)
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_parquet(out_file, index=False)
    return out_df

