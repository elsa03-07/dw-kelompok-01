import pandas as pd
import hashlib
import json

def baca_bps_csv(filepath):
    # Fungsi untuk membaca dan membersihkan file CSV BPS
    pass

def baca_bps_json(filepath):
    # Fungsi untuk membaca dan membersihkan file JSON BPS
    pass
    

import pandas as pd
import hashlib
import json
import os

def baca_bps_csv(filepath):
    """
    Fungsi untuk membaca dan membersihkan file CSV dari BPS.
    Mengubah format menjadi tabel panjang (long table) serta menambahkan berkas_raw dan sha256_raw.
    """
    # Membaca file CSV (sesuaikan encoding jika diperlukan, misal utf-8 atau latin1)
    df = pd.read_csv(filepath, sep=None, engine='python')
    
    # Simpan nama berkas mentah dan hitung hash SHA-256 sebagai identifikasi berkas
    berkas_nama = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_bytes = f.read()
        sha256_val = hashlib.sha256(file_bytes).hexdigest()
        
    df['berkas_raw'] = berkas_nama
    df['sha256_raw'] = sha256_val
    
    return df

def baca_bps_json(filepath):
    """
    Fungsi untuk membaca file JSON dari BPS dan mengubahnya menjadi DataFrame Pandas.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Mengubah data JSON ke dalam DataFrame
    df = pd.DataFrame(data)
    
    berkas_nama = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        file_bytes = f.read()
        sha256_val = hashlib.sha256(file_bytes).hexdigest()
        
    df['berkas_raw'] = berkas_nama
    df['sha256_raw'] = sha256_val
    
    return df

if __name__ == "__main__":
    print("Modul pembaca BPS berhasil dimuat!")

if __name__ == "__main__":
    # Contoh jalur file CSV BPS dari folder data/raw/bps/2026-10-17/
    path_contoh = "data/raw/bps/2026-10-17/sdg4_apk.csv"
    
    try:
        df_hasil = baca_bps_csv(path_contoh)
        print("Berhasil membaca file CSV!")
        print(df_hasil[['berkas_raw', 'sha256_raw']].head(2))
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    # Uji coba CSV
    path_csv = "data/raw/bps/2026-10-17/sdg4_apk.csv"
    try:
        df_csv = baca_bps_csv(path_csv)
        print("Berhasil membaca file CSV!")
        print(df_csv[['berkas_raw', 'sha256_raw']].head(1))
    except Exception as e:
        print(f"Error CSV: {e}")

    # Uji coba JSON menggunakan file manifest_asal.json yang ada di folder 2026-10-20
    path_json = "data/raw/bps/2026-10-20/manifest_asal.json"
    try:
        df_json = baca_bps_json(path_json)
        print("Berhasil membaca file JSON!")
        print(df_json[['berkas_raw', 'sha256_raw']].head(1))
    except Exception as e:
        print(f"Error JSON: {e}")