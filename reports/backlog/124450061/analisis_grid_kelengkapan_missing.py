import sys
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SILVER_PATH = ROOT / "data" / "silver" / "silver.parquet"
OUTPUT_DIR = Path(__file__).resolve().parent

def main():
    print(f"Membaca Silver dari: {SILVER_PATH}")
    df = pd.read_parquet(SILVER_PATH)
    
    # 1. Filter hanya sumber BPS (seri utama var1473 dan var1474)
    bps = df[df['sumber'] == 'bps'].copy()
    
    # 2. Pisahkan baris agregat Indonesia (wilayah_kode == 9999) dari provinsi
    indo = bps[bps['wilayah_kode'] == 9999].copy()
    prov = bps[bps['wilayah_kode'] != 9999].copy()
    
    print(f"Total baris BPS: {len(bps)}")
    print(f"Baris Indonesia (9999): {len(indo)} (dipisahkan)")
    print(f"Baris Provinsi: {len(prov)}")
    
    # Daftar 38 provinsi standar
    provinsi_master = prov[['wilayah_kode', 'nama_wilayah']].drop_duplicates().sort_values('wilayah_kode').reset_index(drop=True)
    periode_master = sorted(prov['periode'].unique()) # ['2017', ..., '2025'] (9 tahun)
    
    print(f"Jumlah provinsi unik terdaftar: {len(provinsi_master)}")
    print(f"Periode tahun: {periode_master} ({len(periode_master)} tahun)")
    
    # 3. Bentuk Grid Lengkap 38 Provinsi x 9 Periode per seri
    grid_rows = []
    for seri in ['var1473', 'var1474']:
        s_df = prov[prov['seri_kode'] == seri]
        for _, p in provinsi_master.iterrows():
            w_kode = p['wilayah_kode']
            w_nama = p['nama_wilayah']
            for thn in periode_master:
                match = s_df[(s_df['wilayah_kode'] == w_kode) & (s_df['periode'] == thn)]
                if len(match) > 0:
                    val = match.iloc[0]['nilai']
                    status = 'TERISI'
                else:
                    val = np.nan
                    status = 'KOSONG_STRUKTURAL' if w_kode in [9200, 9500, 9600, 9700] and int(thn) < 2024 else 'MISSING'
                grid_rows.append({
                    'seri_kode': seri,
                    'wilayah_kode': w_kode,
                    'nama_wilayah': w_nama,
                    'periode': thn,
                    'nilai': val,
                    'status': status
                })
                
    df_grid = pd.DataFrame(grid_rows)
    csv_grid_path = OUTPUT_DIR / "kelengkapan_panel_provinsi.csv"
    df_grid.to_csv(csv_grid_path, index=False)
    print(f"Grid panel lengkap tersimpan di: {csv_grid_path}")
    
    # 4. Ringkasan Kelengkapan per Seri dan per Tahun
    rekap_thn = []
    for seri in ['var1473', 'var1474']:
        s_grid = df_grid[df_grid['seri_kode'] == seri]
        for thn in periode_master:
            thn_grid = s_grid[s_grid['periode'] == thn]
            total_sel = len(thn_grid)
            terisi = (thn_grid['status'] == 'TERISI').sum()
            kosong = (thn_grid['status'] != 'TERISI').sum()
            persen = (terisi / total_sel) * 100
            rekap_thn.append({
                'seri_kode': seri,
                'tahun': thn,
                'total_provinsi_grid': total_sel,
                'provinsi_terisi': terisi,
                'sel_kosong': kosong,
                'persen_kelengkapan': round(persen, 2)
            })
            
    df_rekap = pd.DataFrame(rekap_thn)
    csv_rekap_path = OUTPUT_DIR / "matriks_kelengkapan_tahunan_grid.csv"
    df_rekap.to_csv(csv_rekap_path, index=False)
    print(f"Matriks kelengkapan tahunan tersimpan di: {csv_rekap_path}")
    
    print("\nRingkasan Kelengkapan Tahunan (%):")
    print(df_rekap.to_string(index=False))
    
    # Total statistik
    total_grid_per_seri = len(provinsi_master) * len(periode_master) # 38 * 9 = 342
    terisi_per_seri = (df_grid[df_grid['seri_kode'] == 'var1473']['status'] == 'TERISI').sum() # 314
    kosong_per_seri = (df_grid[df_grid['seri_kode'] == 'var1473']['status'] != 'TERISI').sum() # 28
    
    print(f"\n--- STATISTIK KUNCI ---")
    print(f"Total baris Silver keseluruhan: {len(df)}")
    print(f"Grid teoritis 38 x 9 per seri: {total_grid_per_seri} sel")
    print(f"Sel terisi per seri: {terisi_per_seri} sel")
    print(f"Sel kosong per seri: {kosong_per_seri} sel (4 DOB Papua x 7 tahun)")
    print(f"Persentase kelengkapan keseluruhan: {round((terisi_per_seri / total_grid_per_seri)*100, 2)}%")

if __name__ == "__main__":
    main()
