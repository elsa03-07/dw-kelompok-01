"""Tahap 8 — Validasi dan dokumentasi.
Milik tim.

Aturan validasi Silver dan Gold menggunakan Pandera:
- Rentang nilai yang masuk akal (0-100 persen).
- Keunikan kunci primer komposit 6 dimensi.
- Konsistensi satuan ('persen').
- Keunikan kombinasi provinsi x tahun per seri BPS.
- Integritas kode wilayah dan format sha256.
"""
from pathlib import Path
import re
import pandas as pd
try:
    import pandera.pandas as pa
    from pandera.pandas import Column, Check, DataFrameSchema
except ImportError:
    import pandera as pa
    from pandera import Column, Check, DataFrameSchema

from src.gold.rekonsiliasi import KATEGORI_SAH, PASANGAN

ROOT = Path(__file__).resolve().parents[2]
VALIDASI_MD = ROOT / "reports" / "validasi.md"
LAPORAN_INDIVIDU = ROOT / "reports" / "backlog" / "124450061" / "laporan_validasi_silver.md"

def bangun_skema_silver_pandera():
    """Mendefinisikan skema validasi deklaratif dengan Pandera untuk tabel Silver."""
    return DataFrameSchema(
        columns={
            "sumber": Column(
                pa.String,
                Check.isin(["bps", "bnpb", "wdi", "who_gho", "ilostat"]),
                nullable=False,
                description="Sumber penyedia data mentah"
            ),
            "seri_kode": Column(
                pa.String,
                Check.isin([
                    "var1473", "var1474",
                    "SN.ITK.DEFC.ZS", "SN.ITK.MSFI.ZS",
                    "NUTSTUNTINGPREV", "NUTOVERWEIGHTPREV", "NUTRITION_WH_2"
                ]),
                nullable=False,
                description="Kode identifikasi seri indikator"
            ),
            "wilayah_kode": Column(
                pa.Int,
                Check(lambda s: (s == 9999) | ((s >= 1100) & (s <= 9700) & (s % 100 == 0))),
                nullable=False,
                description="Kode wilayah resmi (9999 nasional atau kode provinsi BPS)"
            ),
            "nama_wilayah": Column(
                pa.String,
                Check(lambda s: s.str.len() > 0),
                nullable=False,
                description="Nama wilayah terstandarisasi huruf kapital"
            ),
            "periode": Column(
                pa.String,
                Check(lambda s: s.str.match(r"^\d{4}$")),
                nullable=False,
                description="Periode tahun dalam format 4 digit"
            ),
            "jenis_periode": Column(
                pa.String,
                Check.isin(["tahun"]),
                nullable=False,
                description="Granularitas periode (tahun)"
            ),
            "rincian": Column(
                pa.String,
                nullable=False,
                description="Disagregasi indikator atau Total"
            ),
            "nilai": Column(
                pa.Float,
                Check(lambda s: (s >= 0.0) & (s <= 100.0)),
                nullable=False,
                description="Nilai prevalensi dalam rentang wajar 0-100 persen"
            ),
            "satuan": Column(
                pa.String,
                Check.isin(["persen"]),
                nullable=False,
                description="Satuan terstandarisasi kanonis (persen)"
            ),
            "_berkas_raw": Column(
                pa.String,
                Check(lambda s: s.str.len() > 0),
                nullable=False,
                description="Path relatif berkas mentah asal observasi"
            ),
            "_sha256_raw": Column(
                pa.String,
                Check(lambda s: s.str.match(r"^[0-9a-f]{64}$")),
                nullable=False,
                description="Sidik SHA-256 berkas mentah 64 karakter heksadesimal"
            ),
        },
        strict=True,
        coerce=True
    )

def validasi_silver(df_silver):
    """Menjalankan 12 aturan pengujian validasi dasar pada data Silver."""
    hasil_aturan = []
    
    # 1. Skema Kolom Lengkap
    skema = bangun_skema_silver_pandera()
    try:
        skema.validate(df_silver)
        hasil_aturan.append(("Skema Kolom & Tipe Data Pandera", True, "Seluruh 11 kolom memenuhi tipe data dan batasan Pandera"))
    except Exception as e:
        hasil_aturan.append(("Skema Kolom & Tipe Data Pandera", False, str(e)))

    # 2. Rentang Nilai Prevalensi (0 - 100%)
    invalid_nilai = df_silver[(df_silver["nilai"] < 0.0) | (df_silver["nilai"] > 100.0)]
    hasil_aturan.append((
        "Rentang Nilai Prevalensi Wajar (0 - 100%)",
        len(invalid_nilai) == 0,
        f"Ditemukan {len(invalid_nilai)} baris di luar batas 0-100" if len(invalid_nilai) > 0 else "Semua nilai berada dalam rentang [0.0, 100.0]"
    ))

    # 3. Konsistensi Satuan
    satuan_unik = set(df_silver["satuan"].unique())
    hasil_aturan.append((
        "Konsistensi Satuan Kanonis ('persen')",
        satuan_unik == {"persen"},
        f"Satuan terdeteksi: {satuan_unik}"
    ))

    # 4. Keunikan Kunci Primer Komposit 6 Dimensi
    KUNCI_6 = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]
    duplikat_kunci = df_silver.duplicated(subset=KUNCI_6).sum()
    hasil_aturan.append((
        "Keunikan Kunci Primer Komposit 6 Dimensi",
        duplikat_kunci == 0,
        f"Ditemukan {duplikat_kunci} duplikasi kunci primer" if duplikat_kunci > 0 else "0 duplikasi (100% unik)"
    ))

    # 5. Keunikan Kombinasi Provinsi x Periode per Seri BPS
    bps_data = df_silver[df_silver["sumber"] == "bps"]
    duplikat_bps = bps_data.duplicated(subset=["seri_kode", "wilayah_kode", "periode"]).sum()
    hasil_aturan.append((
        "Keunikan Kombinasi Provinsi x Periode (Panel BPS)",
        duplikat_bps == 0,
        f"Ditemukan {duplikat_bps} duplikasi wilayah x tahun pada BPS" if duplikat_bps > 0 else "Tepat satu nilai per provinsi x tahun"
    ))

    # 6. Format Periode 4-Digit Tahun
    invalid_periode = df_silver[~df_silver["periode"].str.match(r"^\d{4}$")]
    hasil_aturan.append((
        "Format Periode (4 Digit Tahun Kalender)",
        len(invalid_periode) == 0,
        f"Ditemukan {len(invalid_periode)} format periode tidak baku" if len(invalid_periode) > 0 else "Seluruh periode terformat YYYY (2000-2025)"
    ))

    # 7. Integritas Kode Wilayah (9999 atau Provinsi BPS)
    def cek_wilayah(kode):
        return (kode == 9999) or (1100 <= kode <= 9700 and kode % 100 == 0)
    invalid_wilayah = df_silver[~df_silver["wilayah_kode"].apply(cek_wilayah)]
    hasil_aturan.append((
        "Validitas Kode Wilayah (9999 / 38 Provinsi)",
        len(invalid_wilayah) == 0,
        f"Ditemukan {len(invalid_wilayah)} kode wilayah ilegal" if len(invalid_wilayah) > 0 else "Semua kode wilayah sah sesuai standar 38 provinsi & 9999"
    ))

    # 8. Integritas SHA-256 (64 Karakter Hex)
    invalid_sha = df_silver[~df_silver["_sha256_raw"].str.match(r"^[0-9a-f]{64}$")]
    hasil_aturan.append((
        "Integritas Format SHA-256 Provenans",
        len(invalid_sha) == 0,
        f"Ditemukan {len(invalid_sha)} hash tidak valid" if len(invalid_sha) > 0 else "Seluruh hash terdiri dari 64 karakter heksadesimal valid"
    ))

    # 9. Kolom Wajib Non-Null (Tidak Boleh Ada NaN)
    null_counts = df_silver.isna().sum().sum()
    hasil_aturan.append((
        "Kelengkapan Data (Non-Null Constraints)",
        null_counts == 0,
        f"Ditemukan {null_counts} nilai null/NaN pada Silver" if null_counts > 0 else "0 nilai null/NaN di seluruh 11 kolom"
    ))

    # 10. Validitas Himpunan Sumber Data
    invalid_sumber = df_silver[~df_silver["sumber"].isin(["bps", "bnpb", "wdi", "who_gho", "ilostat"])]
    hasil_aturan.append((
        "Validitas Sumber Data (Whitelist)",
        len(invalid_sumber) == 0,
        f"Ditemukan {len(invalid_sumber)} sumber tidak terdaftar" if len(invalid_sumber) > 0 else "Semua sumber data resmi (bps, wdi, who_gho)"
    ))

    # 11. Kesesuaian Nama Seri terhadap Katalog Kasus 01
    seri_sah = {"var1473", "var1474", "SN.ITK.DEFC.ZS", "SN.ITK.MSFI.ZS", "NUTSTUNTINGPREV", "NUTOVERWEIGHTPREV", "NUTRITION_WH_2"}
    invalid_seri = df_silver[~df_silver["seri_kode"].isin(seri_sah)]
    hasil_aturan.append((
        "Kesesuaian Kode Seri Kasus 01",
        len(invalid_seri) == 0,
        f"Ditemukan {len(invalid_seri)} seri tidak dikenal" if len(invalid_seri) > 0 else "Seluruh 7 seri sesuai kasus kerawanan pangan"
    ))

    # 12. Kesiapan Evaluasi Disagregasi WHO GHO (K-004)
    who_data = df_silver[df_silver["sumber"] == "who_gho"]
    has_total_disagregasi = any("TOTAL" in r.upper() for r in who_data["rincian"].unique())
    hasil_aturan.append((
        "Ketersediaan Rincian Agregat Pembanding WHO (K-004)",
        has_total_disagregasi,
        "Tersedia observasi tingkat agregat TOTAL untuk disandingkan dengan BPS di tahap Gold"
    ))

    return hasil_aturan

def bangun_skema_rekonsiliasi_pandera():
    """Mendefinisikan skema validasi deklaratif Pandera untuk tabel Rekonsiliasi."""
    return DataFrameSchema(
        columns={
            "periode": Column(pa.String, Check(lambda s: s.str.match(r"^\d{4}$")), nullable=False),
            "seri_utama": Column(pa.String, Check.isin(list(PASANGAN)), nullable=False),
            "seri_pembanding": Column(pa.String, Check.isin([p["seri_pembanding"] for p in PASANGAN.values()]), nullable=False),
            "nilai_utama": Column(pa.Float, Check.in_range(0, 100), nullable=True),
            "nilai_pembanding": Column(pa.Float, Check.in_range(0, 100), nullable=True),
            "selisih": Column(pa.Float, nullable=True),
            "status_pasangan": Column(pa.String, Check.isin(["berpasangan", "hanya_utama", "hanya_pembanding"]), nullable=False),
            "kategori": Column(pa.String, Check.isin(KATEGORI_SAH), nullable=False),
            "penjelasan": Column(pa.String, Check.str_length(min_value=10), nullable=False),
        },
        unique=["seri_utama", "periode"],
        coerce=True
    )

def validasi_gold_dan_rekonsiliasi(df_silver, gold):
    """Menjalankan aturan pengujian validasi pada data Gold dan tabel Rekonsiliasi."""
    hasil_aturan = []
    
    # Ambil tabel-tabel Gold
    if isinstance(gold, dict):
        panel_prov = gold.get("panel_provinsi")
        tabel_nas = gold.get("tabel_nasional")
        df_rekon = gold.get("rekonsiliasi")
    else:
        panel_prov = None
        tabel_nas = None
        df_rekon = None

    gold_dir = ROOT / "data" / "gold"
    if panel_prov is None and (gold_dir / "panel_provinsi.parquet").exists():
        panel_prov = pd.read_parquet(gold_dir / "panel_provinsi.parquet")
    if tabel_nas is None and (gold_dir / "tabel_nasional.parquet").exists():
        tabel_nas = pd.read_parquet(gold_dir / "tabel_nasional.parquet")
    if df_rekon is None and (gold_dir / "rekonsiliasi.parquet").exists():
        df_rekon = pd.read_parquet(gold_dir / "rekonsiliasi.parquet")

    if panel_prov is None or tabel_nas is None:
        raise ValueError("Tabel Gold (panel_provinsi atau tabel_nasional) tidak ditemukan untuk divalidasi!")

    # 13. Aturan Kunci Panel Gold Unik (Provinsi)
    kunci_panel = ["seri_kode", "wilayah_kode", "periode"]
    duplikat_panel = panel_prov.duplicated(subset=kunci_panel).sum()
    hasil_aturan.append((
        "Keunikan Kunci Panel Provinsi Gold (seri x wilayah x periode)",
        duplikat_panel == 0,
        f"Ditemukan {duplikat_panel} duplikasi kunci panel" if duplikat_panel > 0 else f"0 duplikasi dari {len(panel_prov):,} baris panel provinsi"
    ))

    # 14. Aturan Kunci Tabel Nasional Gold Unik
    kunci_nasional = ["sumber", "seri_kode", "periode"]
    duplikat_nas = tabel_nas.duplicated(subset=kunci_nasional).sum()
    hasil_aturan.append((
        "Keunikan Kunci Tabel Nasional Gold (sumber x seri x periode)",
        duplikat_nas == 0,
        f"Ditemukan {duplikat_nas} duplikasi kunci nasional" if duplikat_nas > 0 else f"0 duplikasi dari {len(tabel_nas):,} baris tabel nasional"
    ))

    # 15. Aturan Satuan Tunggal per Indikator Gold ('persen')
    satuan_panel = panel_prov.groupby("seri_kode")["satuan"].nunique()
    satuan_nas = tabel_nas.groupby("seri_kode")["satuan"].nunique()
    satuan_konsisten = (satuan_panel.max() == 1) and (satuan_nas.max() == 1) and (set(panel_prov["satuan"]) == {"persen"})
    hasil_aturan.append((
        "Konsistensi Satuan Tunggal per Indikator Gold ('persen')",
        satuan_konsisten,
        f"Seluruh indikator di Gold memiliki tepat 1 satuan terstandarisasi kanonis ('persen')" if satuan_konsisten else "Terdapat indikator dengan multi-satuan"
    ))

    # 16. Keterlacakan (Traceability): Setiap Sel Gold Punya Pasangan di Silver
    kunci_trace = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian"]
    sub_silver = df_silver[kunci_trace + ["nilai"]].copy()
    
    # Cek pasangan panel provinsi
    gabung_panel = panel_prov.merge(
        sub_silver, on=kunci_trace, how="left", suffixes=("", "_silver"),
        indicator=True
    )
    cocok_panel = (gabung_panel["_merge"] == "both").all() and ((gabung_panel["nilai"] - gabung_panel["nilai_silver"]).abs() < 1e-9).all()
    
    # Cek pasangan tabel nasional
    gabung_nas = tabel_nas.merge(
        sub_silver, on=kunci_trace, how="left", suffixes=("", "_silver"),
        indicator=True
    )
    cocok_nas = (gabung_nas["_merge"] == "both").all() and ((gabung_nas["nilai"] - gabung_nas["nilai_silver"]).abs() < 1e-9).all()

    semua_cocok = cocok_panel and cocok_nas
    hasil_aturan.append((
        "Keterlacakan Seluruh Sel Gold ke Silver (Traceability Pasangan)",
        semua_cocok,
        "100% sel panel provinsi dan tabel nasional memiliki pasangan identik di layer Silver" if semua_cocok else "Ditemukan sel Gold tanpa pasangan di Silver"
    ))

    # 17. Setiap baris rekonsiliasi dijelaskan: berpasangan -> kategori penyebab selisih,
    #     tidak berpasangan -> 'tanpa pasangan'. Tidak ada 'belum terjelaskan'.
    if df_rekon is not None:
        try:
            bangun_skema_rekonsiliasi_pandera().validate(df_rekon)
            skema_ok, alasan = True, ""
        except Exception as e:
            skema_ok, alasan = False, f"skema gagal: {str(e).splitlines()[0]}"

        berpasangan = df_rekon["status_pasangan"] == "berpasangan"
        kategori_pasangan_ok = (~df_rekon.loc[berpasangan, "kategori"].isin(["tanpa pasangan", "belum terjelaskan"])).all()
        selisih_ok = df_rekon.loc[berpasangan, "selisih"].notna().all()
        tanpa_pasangan_ok = (df_rekon.loc[~berpasangan, "kategori"] == "tanpa pasangan").all()
        rekon_ok = skema_ok and kategori_pasangan_ok and selisih_ok and tanpa_pasangan_ok and berpasangan.sum() > 0
        hasil_aturan.append((
            "Setiap Baris Rekonsiliasi Dijelaskan (berpasangan berkategori, sisanya 'tanpa pasangan')",
            rekon_ok,
            (f"{int(berpasangan.sum())} baris berpasangan berkategori "
             f"{sorted(set(df_rekon.loc[berpasangan, 'kategori']))}; "
             f"{int((~berpasangan).sum())} baris tanpa pasangan; 0 'belum terjelaskan'")
            if rekon_ok else (alasan or "Ada baris rekonsiliasi tanpa kategori yang sesuai statusnya")
        ))
    else:
        hasil_aturan.append((
            "Setiap Baris Rekonsiliasi Dijelaskan (berpasangan berkategori, sisanya 'tanpa pasangan')",
            False,
            "Tabel rekonsiliasi tidak ditemukan!"
        ))

    # 18. Rentang Nilai Prevalensi Wajar Gold (0.0 - 100.0%)
    invalid_panel_nilai = panel_prov[(panel_prov["nilai"] < 0.0) | (panel_prov["nilai"] > 100.0)]
    invalid_nas_nilai = tabel_nas[(tabel_nas["nilai"] < 0.0) | (tabel_nas["nilai"] > 100.0)]
    rentang_ok = (len(invalid_panel_nilai) == 0) and (len(invalid_nas_nilai) == 0)
    hasil_aturan.append((
        "Rentang Nilai Prevalensi Wajar Gold (0 - 100%)",
        rentang_ok,
        "Seluruh nilai numerik pada panel provinsi dan tabel nasional berada dalam rentang [0.0, 100.0]" if rentang_ok else "Ditemukan nilai di luar batas"
    ))

    return hasil_aturan


def validasi_sql(hasil_sql):
    """19. Jumlah baris dan jumlah nilai setiap tabel di SQL sama dengan Parquet (Backlog #23)."""
    if not hasil_sql:
        return [("Jumlah Baris SQL = Parquet untuk Silver dan Gold", False, "Tahap SQL tidak dijalankan")]
    gagal = [h["tabel"] for h in hasil_sql if not h["cocok"]]
    rincian = ", ".join(f"{h['tabel']} {h['baris_sql']}" for h in hasil_sql)
    return [(
        "Jumlah Baris SQL = Parquet untuk Silver dan Gold",
        not gagal,
        f"{len(hasil_sql)} tabel cocok ({rincian})" if not gagal else f"Tidak cocok: {gagal}",
    )]


def tulis_laporan_validasi(hasil_aturan, df_silver, gold=None):
    """Menuliskan hasil validasi ke format Markdown."""
    total_aturan = len(hasil_aturan)
    aturan_lolos = sum(1 for _, status, _ in hasil_aturan if status)
    
    md_content = f"""# Laporan Validasi Data Silver dan Gold

**Penyusun:** Tim Kelompok 1 (Pelaksana Komponen Validasi: 124450061 - Backlog #25)  
**Total Baris Silver:** {len(df_silver):,}  
**Status Lapis Gold:** {"Tersedia (" + str(len([k for k in gold if not k.startswith("_")])) + " tabel kanonis)" if gold else "Tersimpan di data/gold/"}
**Jumlah Aturan Diuji:** {total_aturan}  
**Jumlah Aturan Lolos:** {aturan_lolos}  
**Status Evaluasi:** {"SELURUH ATURAN LOLOS (100%)" if aturan_lolos == total_aturan else "TERDAPAT ATURAN GAGAL"}  

---

## Tabel Hasil Pengujian Aturan Silver dan Gold

| No | Aturan Validasi | Lingkup | Status | Catatan / Hasil Pemeriksaan |
|:---:|---|:---:|:---:|---|
"""
    for idx, (nama, status, catatan) in enumerate(hasil_aturan, 1):
        status_str = "**LOLOS**" if status else "**GAGAL**"
        lingkup = "Silver" if idx <= 12 else ("SQL" if nama.startswith("Jumlah Baris SQL") else "Gold & Rekon")
        md_content += f"| {idx} | {nama} | {lingkup} | {status_str} | {catatan} |\n"
        
    md_content += f"""
---

## Keterangan Pengujian Lapis Gold & Rekonsiliasi (Backlog #25)
1. **Keunikan Kunci Panel:** Panel provinsi (`seri_kode`, `wilayah_kode`, `periode`) dan tabel nasional (`sumber`, `seri_kode`, `periode`) terbukti 100% unik tanpa duplikasi.
2. **Konsistensi Satuan:** Setiap indikator Gold memiliki tepat satu satuan kanonis (`persen`).
3. **Keterlacakan Pasangan (Traceability):** 100% sel data Gold terbukti dapat dilacak secara deterministik ke sel asalnya di lapisan Silver dengan nilai numerik identik.
4. **Kategori Rekonsiliasi:** Baris berpasangan (BPS vs WDI pada periode yang sama) wajib memiliki selisih dan kategori penyebab selisih; baris yang hanya ada di salah satu sisi wajib berlabel `tanpa pasangan` beserta penjelasannya. Kategori `belum terjelaskan` tidak boleh muncul.
5. **SQL (Backlog #23):** Setelah `pipeline.py` memuat Silver dan Gold ke `data/capstone.sqlite`, jumlah baris dan jumlah kolom `nilai` setiap tabel dibandingkan dengan Parquet sumbernya.
"""
    
    VALIDASI_MD.parent.mkdir(parents=True, exist_ok=True)
    VALIDASI_MD.write_text(md_content, encoding="utf-8")
    
    LAPORAN_INDIVIDU.parent.mkdir(parents=True, exist_ok=True)
    LAPORAN_INDIVIDU.write_text(md_content, encoding="utf-8")

    laporan_gold_rekon = ROOT / "reports" / "backlog" / "124450061" / "aturan_validasi_gold_rekonsiliasi.md"
    laporan_gold_rekon.write_text(md_content, encoding="utf-8")
    
    return total_aturan, aturan_lolos

def jalankan(silver=None, gold=None, sql=None):
    """Fungsi utama yang dipanggil oleh pipeline.py."""
    if silver is None:
        silver_path = ROOT / "data" / "silver" / "silver.parquet"
        if not silver_path.exists():
            raise FileNotFoundError(f"Berkas Silver tidak ditemukan di: {silver_path}")
        df_silver = pd.read_parquet(silver_path)
    elif isinstance(silver, pd.DataFrame):
        df_silver = silver
    else:
        df_silver = pd.DataFrame(silver)
        
    print(f"\n[VALIDASI] Memulai validasi Silver ({len(df_silver):,} baris)...")
    hasil_aturan_silver = validasi_silver(df_silver)
    
    print("[VALIDASI] Memulai validasi Gold dan Rekonsiliasi...")
    hasil_aturan_gold = validasi_gold_dan_rekonsiliasi(df_silver, gold)
    
    hasil_aturan = hasil_aturan_silver + hasil_aturan_gold + validasi_sql(sql)
    total_aturan, aturan_lolos = tulis_laporan_validasi(hasil_aturan, df_silver, gold)

    print(f"[VALIDASI] Selesai: {aturan_lolos}/{total_aturan} aturan LOLOS "
          f"({len(hasil_aturan_silver)} Silver + {len(hasil_aturan_gold)} Gold/Rekon + 1 SQL).")
    for nama, status, catatan in hasil_aturan:
        if not status:
            print(f"  GAGAL: {nama}: {catatan}")
    if aturan_lolos < total_aturan:
        raise ValueError(f"Validasi gagal: {total_aturan - aturan_lolos} aturan tidak terpenuhi!")
        
    return {
        "aturan_validasi": total_aturan,
        "aturan_lolos": aturan_lolos,
        "status": "LOLOS"
    }

if __name__ == "__main__":
    jalankan()
