import json
from pathlib import Path
import pandas as pd

ROOT = Path("C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling")
DIR_REPORTS = ROOT / "reports/profiling"
DIR_WHO = ROOT / "data/raw/who_gho/2026-10-20/datadot"
FILE_WDI = ROOT / "data/raw/wdi/2026-10-20/data/kelompok-07-hal-01.json"

DIR_REPORTS.mkdir(parents=True, exist_ok=True)

ringkasan = []

# 1. Analisis WDI
with open(FILE_WDI, 'r', encoding='utf-8') as f:
    wdi_json = json.load(f)
wdi_records = wdi_json[1] if isinstance(wdi_json, list) and len(wdi_json) > 1 else []

wdi_df = []
for item in wdi_records:
    if isinstance(item, dict):
        ind = item.get('indicator', {}).get('id')
        country = item.get('country', {}).get('id')
        val = item.get('value')
        yr = item.get('date')
        if country == 'ID' and ind in ['SN.ITK.DEFC.ZS', 'SN.ITK.MSFI.ZS'] and val is not None:
            wdi_df.append({
                'seri_kode': ind,
                'sumber': 'World Bank (WDI)',
                'indikator_nama': item.get('indicator', {}).get('value'),
                'tahun': int(yr),
                'nilai': float(val),
                'rincian': 'Total Populasi Nasional',
                'satuan': 'Persen (%)'
            })
df_wdi_clean = pd.DataFrame(wdi_df)

for ind, grp in df_wdi_clean.groupby('seri_kode'):
    thn = sorted(grp['tahun'].unique())
    irisan_bps = [t for t in thn if 2017 <= t <= 2025]
    nama = grp['indikator_nama'].iloc[0]
    ringkasan.append({
        'sumber': 'World Bank (WDI)',
        'seri_kode': ind,
        'nama_indikator': nama,
        'satuan': 'Persen (%)',
        'cakupan_wilayah': 'Nasional (Indonesia)',
        'rentang_tahun': f"{min(thn)}–{max(thn)}",
        'jumlah_tahun': len(thn),
        'irisan_tahun_bps': f"{min(irisan_bps)}–{max(irisan_bps)} ({len(irisan_bps)} tahun)",
        'dimensi_rincian_tersedia': 'Total',
        'rincian_kandidat_sebanding': 'Total Populasi Nasional',
        'alasan_pemilihan': 'Sesuai dengan agregat nasional BPS tanpa pemilahan gender/wilayah; mengukur indikator SDG 2.1.1/2.1.2 secara metodologis.'
    })

# 2. Analisis WHO GHO
# 2.1 NUTSTUNTINGPREV
df_stunt = pd.read_csv(DIR_WHO / "5F8A486_NUTSTUNTINGPREV.csv")
thn_stunt = sorted(df_stunt['DIM_TIME'].unique())
irisan_stunt = [t for t in thn_stunt if 2017 <= t <= 2025]
ringkasan.append({
    'sumber': 'WHO GHO',
    'seri_kode': 'NUTSTUNTINGPREV',
    'nama_indikator': df_stunt['IND_NAME'].iloc[0],
    'satuan': 'Persen (Rate per 100 anak < 5 tahun)',
    'cakupan_wilayah': 'Nasional (Indonesia)',
    'rentang_tahun': f"{min(thn_stunt)}–{max(thn_stunt)}",
    'jumlah_tahun': len(thn_stunt),
    'irisan_tahun_bps': f"{min(irisan_stunt)}–{max(irisan_stunt)} ({len(irisan_stunt)} tahun)",
    'dimensi_rincian_tersedia': 'DIM_SEX (FEMALE, MALE, TOTAL)',
    'rincian_kandidat_sebanding': 'DIM_SEX = TOTAL',
    'alasan_pemilihan': 'Memilih rincian total gabungan laki-laki dan perempuan agar sebanding dengan indikator makro pangan BPS yang berlaku untuk seluruh populasi balita.'
})

# 2.2 NUTOVERWEIGHTPREV
df_ow = pd.read_csv(DIR_WHO / "64E2430_NUTOVERWEIGHTPREV.csv")
thn_ow = sorted(df_ow['DIM_TIME'].unique())
irisan_ow = [t for t in thn_ow if 2017 <= t <= 2025]
ringkasan.append({
    'sumber': 'WHO GHO',
    'seri_kode': 'NUTOVERWEIGHTPREV',
    'nama_indikator': df_ow['IND_NAME'].iloc[0],
    'satuan': 'Persen (Rate per 100 anak < 5 tahun)',
    'cakupan_wilayah': 'Nasional (Indonesia)',
    'rentang_tahun': f"{min(thn_ow)}–{max(thn_ow)}",
    'jumlah_tahun': len(thn_ow),
    'irisan_tahun_bps': f"{min(irisan_ow)}–{max(irisan_ow)} ({len(irisan_ow)} tahun)",
    'dimensi_rincian_tersedia': 'DIM_SEX (FEMALE, MALE, TOTAL)',
    'rincian_kandidat_sebanding': 'DIM_SEX = TOTAL',
    'alasan_pemilihan': 'Memilih rincian total populasi anak balita (gabungan gender) untuk keterbandingan langsung pada tingkat makro nasional.'
})

# 2.3 NUTRITION_WH_2 (Wasting)
df_wasting = pd.read_csv(DIR_WHO / "FC5231F_NUTRITION_WH_2.csv")
thn_wasting = sorted(df_wasting['DIM_TIME'].unique())
irisan_wasting = [t for t in thn_wasting if 2017 <= t <= 2025]
ringkasan.append({
    'sumber': 'WHO GHO',
    'seri_kode': 'NUTRITION_WH_2',
    'nama_indikator': df_wasting['IND_NAME'].iloc[0],
    'satuan': 'Persen (Rate per 100 anak < 5 tahun)',
    'cakupan_wilayah': 'Nasional (Indonesia)',
    'rentang_tahun': f"{min(thn_wasting)}–{max(thn_wasting)}",
    'jumlah_tahun': len(thn_wasting),
    'irisan_tahun_bps': f"{min(irisan_wasting)}–{max(irisan_wasting)} ({len(irisan_wasting)} tahun)",
    'dimensi_rincian_tersedia': 'DIM_SEX, DIM_DEG_URB, DIM_AGE, DIM_HOUSEHOLDWEALTH, dll.',
    'rincian_kandidat_sebanding': 'DIM_SEX = TOTAL, DIM_DEG_URB = TOTAL, DIM_AGE = TOTAL',
    'alasan_pemilihan': 'Menyaring baris agregat nasional di mana seluruh sub-dimensi bernilai TOTAL/agregat, menghindari distorsi pemilahan umur tertentu.'
})

df_hasil_pembanding = pd.DataFrame(ringkasan)
df_hasil_pembanding.to_csv(DIR_REPORTS / "ketersediaan_pembanding_nasional.csv", index=False)
print("Berhasil menyusun ketersediaan_pembanding_nasional.csv!")

# Simpan juga rincian lengkap tahun x seri
ketersediaan_detail = []
for t in range(1996, 2026):
    row = {'tahun': t}
    row['BPS_var1473'] = 'Ada (34-38 Prov + Nas)' if 2017 <= t <= 2025 else 'Tidak ada'
    row['BPS_var1474'] = 'Ada (34-38 Prov + Nas)' if 2017 <= t <= 2025 else 'Tidak ada'
    row['WDI_DEFC'] = 'Ada' if t in thn and t in df_wdi_clean[df_wdi_clean['seri_kode'] == 'SN.ITK.DEFC.ZS']['tahun'].values else 'Tidak ada'
    row['WDI_MSFI'] = 'Ada' if t in df_wdi_clean[df_wdi_clean['seri_kode'] == 'SN.ITK.MSFI.ZS']['tahun'].values else 'Tidak ada'
    row['WHO_STUNTING'] = 'Ada (Sex: Total/M/F)' if t in thn_stunt else 'Tidak ada'
    row['WHO_OVERWEIGHT'] = 'Ada (Sex: Total/M/F)' if t in thn_ow else 'Tidak ada'
    row['WHO_WASTING'] = 'Ada (Multidimensi)' if t in thn_wasting else 'Tidak ada'
    ketersediaan_detail.append(row)

pd.DataFrame(ketersediaan_detail).to_csv(DIR_REPORTS / "matriks_ketersediaan_tahunan.csv", index=False)
print("Berhasil menyusun matriks_ketersediaan_tahunan.csv!")
