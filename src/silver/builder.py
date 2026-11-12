import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
from src.common.manifest import sha256_raw, baca, RAW
from src.common.skema import periksa_silver

def bangun_silver(raw_dir=RAW):
    manifest = baca(raw_dir)
    rows = []

    # 1. BPS var1473 (PoU)
    file_1473 = "bps/2026-10-20/sdg2_2_1_1_v1473.csv"
    sha_1473 = sha256_raw(file_1473, raw_dir)
    df_1473 = pd.read_csv(Path(raw_dir) / file_1473)
    for _, r in df_1473.iterrows():
        rows.append({
            'sumber': 'bps',
            'seri_kode': 'var1473',
            'wilayah_kode': int(r['wilayah_id']),
            'nama_wilayah': str(r['wilayah']).strip().upper(),
            'periode': str(int(r['tahun'])),
            'jenis_periode': 'tahun',
            'rincian': 'Total',
            'nilai': float(r['nilai']),
            'satuan': 'persen',
            '_berkas_raw': file_1473,
            '_sha256_raw': sha_1473
        })

    # 2. BPS var1474 (FIES)
    file_1474 = "bps/2026-10-20/sdg2_2_1_2_v1474.csv"
    sha_1474 = sha256_raw(file_1474, raw_dir)
    df_1474 = pd.read_csv(Path(raw_dir) / file_1474)
    for _, r in df_1474.iterrows():
        rows.append({
            'sumber': 'bps',
            'seri_kode': 'var1474',
            'wilayah_kode': int(r['wilayah_id']),
            'nama_wilayah': str(r['wilayah']).strip().upper(),
            'periode': str(int(r['tahun'])),
            'jenis_periode': 'tahun',
            'rincian': 'Total',
            'nilai': float(r['nilai']),
            'satuan': 'persen',
            '_berkas_raw': file_1474,
            '_sha256_raw': sha_1474
        })

    # 3. WDI (World Bank)
    file_wdi = "wdi/2026-10-20/data/kelompok-07-hal-01.json"
    sha_wdi = sha256_raw(file_wdi, raw_dir)
    with open(Path(raw_dir) / file_wdi, 'r', encoding='utf-8') as f:
        wdi_json = json.load(f)
    if isinstance(wdi_json, list) and len(wdi_json) > 1:
        for item in wdi_json[1]:
            if isinstance(item, dict):
                ind = item.get('indicator', {}).get('id')
                country = item.get('country', {}).get('id')
                val = item.get('value')
                yr = item.get('date')
                if country == 'ID' and ind in ['SN.ITK.DEFC.ZS', 'SN.ITK.MSFI.ZS'] and val is not None:
                    rows.append({
                        'sumber': 'wdi',
                        'seri_kode': str(ind),
                        'wilayah_kode': 9999,
                        'nama_wilayah': 'INDONESIA',
                        'periode': str(int(yr)),
                        'jenis_periode': 'tahun',
                        'rincian': 'Total',
                        'nilai': float(val),
                        'satuan': 'persen',
                        '_berkas_raw': file_wdi,
                        '_sha256_raw': sha_wdi
                    })

    # 4. WHO GHO NUTSTUNTINGPREV
    file_stunt = "who_gho/2026-10-20/datadot/5F8A486_NUTSTUNTINGPREV.csv"
    sha_stunt = sha256_raw(file_stunt, raw_dir)
    df_stunt = pd.read_csv(Path(raw_dir) / file_stunt)
    for _, r in df_stunt.iterrows():
        val = r['RATE_PER_100_N']
        if pd.notna(val):
            rows.append({
                'sumber': 'who_gho',
                'seri_kode': 'NUTSTUNTINGPREV',
                'wilayah_kode': 9999,
                'nama_wilayah': 'INDONESIA',
                'periode': str(int(r['DIM_TIME'])),
                'jenis_periode': 'tahun',
                'rincian': f"SEX={r['DIM_SEX']}",
                'nilai': float(val),
                'satuan': 'persen',
                '_berkas_raw': file_stunt,
                '_sha256_raw': sha_stunt
            })

    # 5. WHO GHO NUTOVERWEIGHTPREV
    file_ow = "who_gho/2026-10-20/datadot/64E2430_NUTOVERWEIGHTPREV.csv"
    sha_ow = sha256_raw(file_ow)
    df_ow = pd.read_csv(Path(raw_dir) / file_ow)
    for _, r in df_ow.iterrows():
        val = r['RATE_PER_100_N']
        if pd.notna(val):
            rows.append({
                'sumber': 'who_gho',
                'seri_kode': 'NUTOVERWEIGHTPREV',
                'wilayah_kode': 9999,
                'nama_wilayah': 'INDONESIA',
                'periode': str(int(r['DIM_TIME'])),
                'jenis_periode': 'tahun',
                'rincian': f"SEX={r['DIM_SEX']}",
                'nilai': float(val),
                'satuan': 'persen',
                '_berkas_raw': file_ow,
                '_sha256_raw': sha_ow
            })

    # 6. WHO GHO NUTRITION_WH_2 (Wasting)
    file_wh2 = "who_gho/2026-10-20/datadot/FC5231F_NUTRITION_WH_2.csv"
    sha_wh2 = sha256_raw(file_wh2, raw_dir)
    df_wh2 = pd.read_csv(Path(raw_dir) / file_wh2)
    dim_cols = [c for c in df_wh2.columns if c.startswith('DIM_') and c not in ['DIM_TIME', 'DIM_TIME_TYPE', 'DIM_GEO_CODE_M49', 'DIM_GEO_CODE_TYPE', 'DIM_PUBLISH_STATE_CODE']]
    for _, r in df_wh2.iterrows():
        val = r['RATE_PER_100_N']
        if pd.notna(val):
            parts = [c[4:] + '=' + str(r[c]) for c in dim_cols if pd.notna(r[c])]
            rincian_str = '; '.join(parts) if parts else 'TOTAL'
            rows.append({
                'sumber': 'who_gho',
                'seri_kode': 'NUTRITION_WH_2',
                'wilayah_kode': 9999,
                'nama_wilayah': 'INDONESIA',
                'periode': str(int(r['DIM_TIME'])),
                'jenis_periode': 'tahun',
                'rincian': rincian_str,
                'nilai': float(val),
                'satuan': 'persen',
                '_berkas_raw': file_wh2,
                '_sha256_raw': sha_wh2
            })

    df = pd.DataFrame(rows)
    KUNCI = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]
    # Deduplikasi sesuai aturan K-003: baris ganda dipertahankan observasi terakhir
    df = df.drop_duplicates(subset=KUNCI, keep='last').reset_index(drop=True)
    
    # Validasi skema
    salah = periksa_silver(df, manifest)
    if salah:
        raise ValueError(f"Validasi silver gagal: {salah}")
        
    return df

if __name__ == "__main__":
    df = bangun_silver()
    print("Hasil bangun_silver berhasil!")
    print(f"Total baris: {len(df):,}")
    print(f"Seri kode: {df['seri_kode'].unique()}")
    print(f"Wilayah unik: {df['wilayah_kode'].nunique()}")
