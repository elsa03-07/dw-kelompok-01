import json
import hashlib
from pathlib import Path
import pandas as pd

def hitung_sha256(file_path):
    """Menghitung hash SHA-256 dari berkas mentah."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def baca_wdi(file_path):
    """
    Membaca berkas WDI JSON, mengekstrak metadata raw,
    serta mengubah struktur data bersarang menjadi tabel panjang (tidy data).
    """
    path_obj = Path(file_path)
    berkas_raw = str(path_obj)
    sha256_raw = hitung_sha256(path_obj)
    
    with open(path_obj, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    parsed_rows = []
    
    # Format World Bank API: data[0] adalah metadata, data[1] adalah list data aktual
    if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
        records = data[1]
        for item in records:
            if isinstance(item, dict):
                # Ekstraksi aman untuk struktur bersarang (nested dict)
                country_dict = item.get('country', {})
                indicator_dict = item.get('indicator', {})
                
                row = {
                    'country_code': country_dict.get('id') if isinstance(country_dict, dict) else None,
                    'country_name': country_dict.get('value') if isinstance(country_dict, dict) else None,
                    'indicator_code': indicator_dict.get('id') if isinstance(indicator_dict, dict) else None,
                    'indicator_name': indicator_dict.get('value') if isinstance(indicator_dict, dict) else None,
                    'year': item.get('date'),
                    'value': item.get('value'),
                    '_berkas_raw': berkas_raw,
                    '_sha256_raw': sha256_raw
                }
                parsed_rows.append(row)
                
    df = pd.DataFrame(parsed_rows)
    return df

if __name__ == "__main__":
    dir_wdi = Path("data/raw/wdi/2026-10-20/data")
    
    if dir_wdi.exists():
        total_baris_global = 0
        for file_json in dir_wdi.glob("*.json"):
            print(f"\nMemproses: {file_json.name}")
            df_hasil = baca_wdi(file_json)
            print(f"Jumlah baris terekstraksi: {len(df_hasil)}")
            if not df_hasil.empty:
                print(df_hasil.head(2))  # Menampilkan 2 sampel baris pertama
            total_baris_global += len(df_hasil)
        print(f"\nTotal keseluruhan baris data WDI: {total_baris_global}")
    else:
        print(f"Direktori {dir_wdi} tidak ditemukan.")