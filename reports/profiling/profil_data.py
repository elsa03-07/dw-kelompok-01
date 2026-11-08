
from pathlib import Path
import pandas as pd
import json

# Lokasi data mentah
RAW_DIR = Path("data/raw")

# Lokasi laporan
OUTPUT_DIR = Path("reports/profiling")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EXCLUDE_FILES = {"MANIFEST.csv"}

hasil = []


def simpan_profil(df, nama_file, format_data):
    df_profil = df.copy()

    # Mengubah data bertingkat menjadi teks
    # agar bisa dihitung duplikatnya
    for kolom in df_profil.columns:
        df_profil[kolom] = df_profil[kolom].map(
            lambda nilai: json.dumps(nilai, ensure_ascii=False)
            if isinstance(nilai, (dict, list))
            else nilai
        )

    hasil.append({
        "nama_file": nama_file,
        "format": format_data,
        "jumlah_baris": len(df_profil),
        "jumlah_kolom": len(df_profil.columns),
        "nama_kolom": ", ".join(map(str, df_profil.columns)),
        "nilai_kosong": int(df_profil.isna().sum().sum()),
        "baris_duplikat": int(df_profil.duplicated().sum()),
        "tipe_data": json.dumps(
            {str(k): str(v) for k, v in df_profil.dtypes.items()}
        )
    })


def profil_json(data, nama_file):

    # Format WHO OData
    if isinstance(data, dict) and isinstance(data.get("value"), list):
        df = pd.DataFrame(data["value"])
        simpan_profil(df, nama_file, "JSON - WHO OData")
        return

    # Format WDI
    if (
        isinstance(data, list)
        and len(data) == 2
        and isinstance(data[0], dict)
        and isinstance(data[1], list)
    ):
        df = pd.DataFrame(data[1])
        simpan_profil(df, nama_file, "JSON - WDI")
        return

    # Format BPS
    if isinstance(data, list) and data and all(
        isinstance(item, dict) for item in data
    ):
        for nomor, item in enumerate(data, start=1):
            catatan = {
                "kelompok_ke": nomor,
                "jumlah_properti": len(item),
                "nama_properti": ", ".join(item.keys()),
                "jumlah_data": (
                    len(item["datacontent"])
                    if isinstance(item.get("datacontent"), dict)
                    else 0
                )
            }

            simpan_profil(
                pd.DataFrame([catatan]),
                nama_file,
                "JSON - BPS"
            )
        return

    # Format JSON lainnya
    if isinstance(data, dict):
        catatan = {
            "jumlah_properti": len(data),
            "nama_properti": ", ".join(data.keys())
        }

    elif isinstance(data, list):
        catatan = {
            "jumlah_record": len(data),
            "tipe_record_pertama": (
                type(data[0]).__name__ if data else "kosong"
            )
        }

    else:
        catatan = {
            "tipe_data": type(data).__name__
        }

    simpan_profil(
        pd.DataFrame([catatan]),
        nama_file,
        "JSON - Struktur"
    )


# Membaca semua file data mentah
for file in RAW_DIR.rglob("*"):

    if not file.is_file():
        continue

    if file.name in EXCLUDE_FILES:
        continue

    try:
        if file.suffix.lower() == ".csv":

            try:
                df = pd.read_csv(file)
            except UnicodeDecodeError:
                df = pd.read_csv(file, encoding="latin1")

            simpan_profil(df, str(file), "CSV")

        elif file.suffix.lower() in [".xlsx", ".xls"]:

            df = pd.read_excel(file)
            simpan_profil(df, str(file), "Excel")

        elif file.suffix.lower() == ".json":

            with open(file, encoding="utf-8") as f:
                data = json.load(f)

            profil_json(data, str(file))

    except Exception as error:
        print(f"Gagal membaca {file}: {error}")


# Membuat laporan akhir
laporan = pd.DataFrame(hasil)

laporan.to_csv(
    OUTPUT_DIR / "ringkasan_profil.csv",
    index=False,
    encoding="utf-8-sig"
)

print("=" * 50)
print("PROFILING DATA SELESAI")
print("=" * 50)
print(f"Total tabel/struktur terbaca: {len(hasil)}")
print(f"Laporan tersimpan di: {OUTPUT_DIR / 'ringkasan_profil.csv'}")
