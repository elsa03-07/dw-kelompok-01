import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Direktori proyek
ROOT = Path("C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling")
DIR_DATA = ROOT / "data/raw/bps/2026-10-20"
DIR_GAMBAR = ROOT / "reports/gambar"
DIR_REPORTS = ROOT / "reports/profiling"

DIR_GAMBAR.mkdir(parents=True, exist_ok=True)
DIR_REPORTS.mkdir(parents=True, exist_ok=True)

# 1. Baca Data Mentah
file_1473 = DIR_DATA / "sdg2_2_1_1_v1473.csv"
file_1474 = DIR_DATA / "sdg2_2_1_2_v1474.csv"

df1473 = pd.read_csv(file_1473)
df1474 = pd.read_csv(file_1474)

# Filter: Pisahkan data agregat nasional (9999) dan level provinsi
prov1473 = df1473[df1473['wilayah_id'] != 9999].copy()
prov1474 = df1474[df1474['wilayah_id'] != 9999].copy()
nas1473 = df1473[df1473['wilayah_id'] == 9999].copy().sort_values('tahun')
nas1474 = df1474[df1474['wilayah_id'] == 9999].copy().sort_values('tahun')

# 2. Statistik Deskriptif Per Tahun
def hitung_deskriptif_tahunan(df, seri_nama):
    stats = []
    for thn, grp in df.groupby('tahun'):
        vals = grp['nilai']
        q1 = vals.quantile(0.25)
        q3 = vals.quantile(0.75)
        iqr = q3 - q1
        stats.append({
            'seri': seri_nama,
            'tahun': thn,
            'jumlah_provinsi': len(vals),
            'mean': round(vals.mean(), 2),
            'std': round(vals.std(), 2),
            'median': round(vals.median(), 2),
            'min': round(vals.min(), 2),
            'q1': round(q1, 2),
            'q3': round(q3, 2),
            'iqr': round(iqr, 2),
            'max': round(vals.max(), 2),
            'batas_bawah_iqr': round(max(0, q1 - 1.5 * iqr), 2),
            'batas_atas_iqr': round(q3 + 1.5 * iqr, 2)
        })
    return pd.DataFrame(stats)

stat1473 = hitung_deskriptif_tahunan(prov1473, 'var1473 (PoU)')
stat1474 = hitung_deskriptif_tahunan(prov1474, 'var1474 (FIES)')
stat_tahunan = pd.concat([stat1473, stat1474], ignore_index=True)
stat_tahunan.to_csv(DIR_REPORTS / "statistik_deskriptif_tahunan.csv", index=False)
print("Berhasil menyimpan statistik deskriptif tahunan.")

# 3. Deteksi Calon Anomali (Metode IQR & Z-Score per tahun)
def deteksi_anomali(df, seri_kode, seri_nama):
    anomali = []
    for thn, grp in df.groupby('tahun'):
        mu = grp['nilai'].mean()
        sigma = grp['nilai'].std()
        q1 = grp['nilai'].quantile(0.25)
        q3 = grp['nilai'].quantile(0.75)
        iqr = q3 - q1
        upper_iqr = q3 + 1.5 * iqr
        lower_iqr = q1 - 1.5 * iqr
        
        for _, row in grp.iterrows():
            val = row['nilai']
            z = (val - mu) / sigma if sigma > 0 else 0
            is_iqr_outlier = (val > upper_iqr) or (val < lower_iqr)
            is_z_outlier = abs(z) >= 2.0
            
            if is_iqr_outlier or is_z_outlier:
                alasan = []
                if val > upper_iqr:
                    alasan.append(f"Nilai ({val}%) > Batas Atas IQR ({upper_iqr:.2f}%)")
                elif val < lower_iqr:
                    alasan.append(f"Nilai ({val}%) < Batas Bawah IQR ({lower_iqr:.2f}%)")
                if abs(z) >= 2.0:
                    alasan.append(f"Z-score ekstrem (z = {z:.2f})")
                
                anomali.append({
                    'seri_kode': seri_kode,
                    'seri_nama': seri_nama,
                    'tahun': thn,
                    'wilayah_id': row['wilayah_id'],
                    'nama_wilayah': row['wilayah'],
                    'nilai': val,
                    'mean_tahun': round(mu, 2),
                    'std_tahun': round(sigma, 2),
                    'z_score': round(z, 2),
                    'iqr_threshold_upper': round(upper_iqr, 2),
                    'alasan_ditandai': "; ".join(alasan)
                })
    return pd.DataFrame(anomali)

anomali1473 = deteksi_anomali(prov1473, 'var1473', 'PoU (Prevalensi Ketidakcukupan Konsumsi Pangan)')
anomali1474 = deteksi_anomali(prov1474, 'var1474', 'FIES (Prevalensi Kerawanan Pangan Sedang/Berat)')
daftar_anomali = pd.concat([anomali1473, anomali1474], ignore_index=True)
daftar_anomali.to_csv(DIR_REPORTS / "daftar_calon_anomali_seri_utama.csv", index=False)
print(f"Total calon anomali ditemukan: {len(daftar_anomali)} baris.")

# 4. Pembuatan Grafik
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

# Grafik 1: Boxplot Tahunan var1473
plt.figure(figsize=(10, 6))
tahuns = sorted(prov1473['tahun'].unique())
data_boxplot_1473 = [prov1473[prov1473['tahun'] == t]['nilai'].values for t in tahuns]
plt.boxplot(data_boxplot_1473, tick_labels=tahuns, patch_artist=True,
            boxprops=dict(facecolor='#aec7e8', color='#1f77b4'),
            medianprops=dict(color='darkred', linewidth=2),
            flierprops=dict(marker='o', color='red', markersize=6, alpha=0.7))
plt.title('Distribusi Nilai Prevalensi Ketidakcukupan Pangan (PoU / var1473) Per Tahun (2017–2025)', fontsize=12, fontweight='bold')
plt.xlabel('Tahun Pengamatan', fontsize=11)
plt.ylabel('Prevalensi (%)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(DIR_GAMBAR / "boxplot_var1473_tahunan.png", dpi=300)
plt.close()

# Grafik 2: Boxplot Tahunan var1474
plt.figure(figsize=(10, 6))
data_boxplot_1474 = [prov1474[prov1474['tahun'] == t]['nilai'].values for t in tahuns]
plt.boxplot(data_boxplot_1474, tick_labels=tahuns, patch_artist=True,
            boxprops=dict(facecolor='#ffbb78', color='#ff7f0e'),
            medianprops=dict(color='darkred', linewidth=2),
            flierprops=dict(marker='o', color='red', markersize=6, alpha=0.7))
plt.title('Distribusi Prevalensi Kerawanan Pangan Sedang/Berat (FIES / var1474) Per Tahun (2017–2025)', fontsize=12, fontweight='bold')
plt.xlabel('Tahun Pengamatan', fontsize=11)
plt.ylabel('Prevalensi (%)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(DIR_GAMBAR / "boxplot_var1474_tahunan.png", dpi=300)
plt.close()

# Grafik 3: Deret Waktu Tren Nasional vs Rata-rata Provinsi
rerata1473 = prov1473.groupby('tahun')['nilai'].mean().reset_index()
rerata1474 = prov1474.groupby('tahun')['nilai'].mean().reset_index()

plt.figure(figsize=(12, 6))
plt.plot(nas1473['tahun'], nas1473['nilai'], 'b-o', label='var1473 - Nasional BPS (9999)', linewidth=2.5)
plt.plot(rerata1473['tahun'], rerata1473['nilai'], 'b--', label='var1473 - Rerata Provinsi', alpha=0.8)
plt.plot(nas1474['tahun'], nas1474['nilai'], 'r-s', label='var1474 - Nasional BPS (9999)', linewidth=2.5)
plt.plot(rerata1474['tahun'], rerata1474['nilai'], 'r--', label='var1474 - Rerata Provinsi', alpha=0.8)
plt.title('Tren Deret Waktu Indikator Kerawanan Pangan: Agregat Nasional vs Rerata Provinsi', fontsize=12, fontweight='bold')
plt.xlabel('Tahun', fontsize=11)
plt.ylabel('Prevalensi (%)', fontsize=11)
plt.xticks(tahuns)
plt.legend(frameon=True)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(DIR_GAMBAR / "deret_waktu_tren_nasional_vs_provinsi.png", dpi=300)
plt.close()

# Grafik 4: Deret Waktu Provinsi Ekstrem var1473 (Papua, Papua Tengah, Maluku, Maluku Utara vs DKI Jakarta & Bali)
plt.figure(figsize=(12, 6))
prov_pantau_1473 = [9400, 9600, 9700, 8100, 8200, 3100, 5100]
label_map = {9400: 'Papua (Induk)', 9600: 'Papua Tengah (DOB 2024)', 9700: 'Papua Pegunungan (DOB 2024)',
             8100: 'Maluku', 8200: 'Maluku Utara', 3100: 'DKI Jakarta (Terendah)', 5100: 'Bali (Terendah)'}
for pid in prov_pantau_1473:
    sub = prov1473[prov1473['wilayah_id'] == pid].sort_values('tahun')
    if not sub.empty:
        plt.plot(sub['tahun'], sub['nilai'], '-o', label=label_map.get(pid, sub['wilayah'].iloc[0]), linewidth=2)
plt.plot(nas1473['tahun'], nas1473['nilai'], 'k--', label='INDONESIA (Nasional)', linewidth=2.5)
plt.title('Deret Waktu Kasus Ekstrem vs Terendah: var1473 (PoU) 2017–2025', fontsize=12, fontweight='bold')
plt.xlabel('Tahun', fontsize=11)
plt.ylabel('Prevalensi (%)', fontsize=11)
plt.xticks(tahuns)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(DIR_GAMBAR / "deret_waktu_provinsi_ekstrem_var1473.png", dpi=300)
plt.close()

# Grafik 5: Deret Waktu Provinsi Ekstrem var1474 (NTT, Gorontalo, Papua Selatan vs DKI Jakarta & Bali)
plt.figure(figsize=(12, 6))
prov_pantau_1474 = [5300, 7500, 9500, 9400, 3100, 5100]
label_map_1474 = {5300: 'Nusa Tenggara Timur', 7500: 'Gorontalo', 9500: 'Papua Selatan (DOB 2024)',
                  9400: 'Papua', 3100: 'DKI Jakarta', 5100: 'Bali'}
for pid in prov_pantau_1474:
    sub = prov1474[prov1474['wilayah_id'] == pid].sort_values('tahun')
    if not sub.empty:
        plt.plot(sub['tahun'], sub['nilai'], '-s', label=label_map_1474.get(pid, sub['wilayah'].iloc[0]), linewidth=2)
plt.plot(nas1474['tahun'], nas1474['nilai'], 'k--', label='INDONESIA (Nasional)', linewidth=2.5)
plt.title('Deret Waktu Kasus Ekstrem vs Terendah: var1474 (FIES) 2017–2025', fontsize=12, fontweight='bold')
plt.xlabel('Tahun', fontsize=11)
plt.ylabel('Prevalensi (%)', fontsize=11)
plt.xticks(tahuns)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(DIR_GAMBAR / "deret_waktu_provinsi_ekstrem_var1474.png", dpi=300)
plt.close()

print("Seluruh grafik berhasil disimpan di reports/gambar/!")
