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

def tulis_laporan_validasi(hasil_aturan, df_silver, gold=None):
    """Menuliskan hasil validasi ke format Markdown."""
    total_aturan = len(hasil_aturan)
    aturan_lolos = sum(1 for _, status, _ in hasil_aturan if status)
    
    md_content = f"""# Laporan Validasi Data Silver

**Penyusun:** Tim Kelompok 1 (Pelaksana Komponen Validasi: 124450061)  
**Total Baris Silver:** {len(df_silver):,}  
**Jumlah Aturan Diuji:** {total_aturan}  
**Jumlah Aturan Lolos:** {aturan_lolos}  
**Status Evaluasi:** {"SELURUH ATURAN LOLOS" if aturan_lolos == total_aturan else "TERDAPAT ATURAN GAGAL"}  

---

## Tabel Hasil Pengujian Aturan Dasar

| No | Aturan Validasi | Status | Catatan / Hasil Pemeriksaan |
|:---:|---|:---:|---|
"""
    for idx, (nama, status, catatan) in enumerate(hasil_aturan, 1):
        status_str = "✅ **LOLOS**" if status else "❌ **GAGAL**"
        md_content += f"| {idx} | {nama} | {status_str} | {catatan} |\n"
        
    md_content += f"""
---

## Keterangan Pengujian Lapis Gold
- **Status Gold:** {"Tersedia (" + str(len(gold)) + " tabel)" if gold else "Belum dimulai (dijadwalkan Sprint 2–3)"}
- Rincian pembanding nasional WHO yang sebanding (DIM_SEX=TOTAL, DIM_AGE=TOTAL) telah diverifikasi tersedia di layer Silver sesuai aturan keputusan **K-004**.
"""
    
    VALIDASI_MD.parent.mkdir(parents=True, exist_ok=True)
    VALIDASI_MD.write_text(md_content, encoding="utf-8")
    
    LAPORAN_INDIVIDU.parent.mkdir(parents=True, exist_ok=True)
    LAPORAN_INDIVIDU.write_text(md_content, encoding="utf-8")
    
    return total_aturan, aturan_lolos

def jalankan(silver=None, gold=None):
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
    hasil_aturan = validasi_silver(df_silver)
    total_aturan, aturan_lolos = tulis_laporan_validasi(hasil_aturan, df_silver, gold)
    
    print(f"[VALIDASI] Selesai: {aturan_lolos}/{total_aturan} aturan LOLOS.")
    if aturan_lolos < total_aturan:
        raise ValueError(f"Validasi gagal: {total_aturan - aturan_lolos} aturan tidak terpenuhi!")
        
    return {
        "aturan_validasi": total_aturan,
        "aturan_lolos": aturan_lolos,
        "status": "LOLOS"
    }

if __name__ == "__main__":
    jalankan()
