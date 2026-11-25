"""Modul Aturan Pemilihan Satu Nilai per Sel Gold (Tahap 4 - Persiapan Gold).
Milik tim — Penanggung jawab: 124450061 (Backlog #20).

Aturan pemilihan:
1. Snapshot terbaru (keep='last') bila terdapat revisi data.
2. Penyaringan rincian:
   - BPS: rincian == 'Total'
   - WDI: rincian == 'Total'
   - WHO GHO: hanya rincian agregat total yang sebanding (SEX=TOTAL atau TOTAL).
   Rincian subkelompok usia/gender tetap berada hanya di Silver.
3. Periode: wajib tahunan ('tahun'), tidak melakukan agregasi non-tahunan.
4. Flag anomali: mempertahankan penanda outlier dan patahan seri dari Sprint 1.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
ANOMALI_FILE = ROOT / "reports" / "backlog" / "124450061" / "daftar_anomali_terklasifikasi.csv"

def muat_peta_anomali():
    """Memuat daftar anomali terklasifikasi dari Sprint 1."""
    if not ANOMALI_FILE.exists():
        return {}
    df_anom = pd.read_csv(ANOMALI_FILE)
    peta = {}
    for _, r in df_anom.iterrows():
        kunci = (str(r['seri_kode']), int(r['wilayah_id']), str(int(r['tahun'])))
        peta[kunci] = {
            'kategori': str(r['kategori_anomali']),
            'is_outlier': 'Outlier' in str(r['kategori_anomali']),
            'is_patahan': 'Patahan' in str(r['kategori_anomali'])
        }
    return peta

def pilih_baris_gold(silver_df):
    """
    Menjalankan aturan pemilihan satu nilai per sel dari Silver.
    Mengembalikan: (df_provinsi_terpilih, df_nasional_terpilih, jumlah_baris_tidak_terpilih)
    """
    total_silver = len(silver_df)
    
    # 1. Aturan Deduplikasi Snapshot (K-003): Kunci 6 dimensi
    KUNCI_6 = ["sumber", "seri_kode", "wilayah_kode", "periode", "rincian", "_berkas_raw"]
    df = silver_df.drop_duplicates(subset=KUNCI_6, keep='last').copy()
    
    # 2. Filter hanya periode tahunan (K-008)
    df = df[df['jenis_periode'] == 'tahun'].copy()
    
    # 3. Pemisahan Panel Provinsi (BPS: var1473, var1474)
    bps_prov = df[(df['sumber'] == 'bps') & (df['wilayah_kode'] != 9999) & (df['rincian'] == 'Total')].copy()
    
    # 4. Pemisahan Tabel Nasional (BPS, WDI, WHO sebanding)
    # Rincian WHO yang sebanding:
    # - NUTSTUNTINGPREV: SEX=TOTAL
    # - NUTOVERWEIGHTPREV: SEX=TOTAL
    # - NUTRITION_WH_2: TOTAL
    kondisi_bps_nasional = (df['sumber'] == 'bps') & (df['wilayah_kode'] == 9999) & (df['rincian'] == 'Total')
    kondisi_wdi = (df['sumber'] == 'wdi') & (df['rincian'] == 'Total')
    kondisi_who_stunt = (df['seri_kode'] == 'NUTSTUNTINGPREV') & (df['rincian'] == 'SEX=TOTAL')
    kondisi_who_ow = (df['seri_kode'] == 'NUTOVERWEIGHTPREV') & (df['rincian'] == 'SEX=TOTAL')
    kondisi_who_wh2 = (df['seri_kode'] == 'NUTRITION_WH_2') & (df['rincian'] == 'TOTAL')
    
    nasional_terpilih = df[
        kondisi_bps_nasional | kondisi_wdi | kondisi_who_stunt | kondisi_who_ow | kondisi_who_wh2
    ].copy()
    
    # Hitung jumlah baris yang tidak terpilih masuk ke Gold
    # Seluruh baris yang tidak masuk ke panel provinsi maupun nasional
    baris_terpilih_total = len(bps_prov) + len(nasional_terpilih)
    jumlah_tidak_terpilih = total_silver - baris_terpilih_total
    
    return bps_prov, nasional_terpilih, jumlah_tidak_terpilih

def bangun_panel_provinsi(bps_prov_df):
    """
    Membentuk panel Gold provinsi x tahun x indikator dalam bentuk wide table,
    lengkap dengan penanda outlier dan patahan seri dari Sprint 1.
    """
    peta_anomali = muat_peta_anomali()
    
    # Pivot nilai indikator
    pivot = bps_prov_df.pivot(
        index=['wilayah_kode', 'nama_wilayah', 'periode'],
        columns='seri_kode',
        values='nilai'
    ).reset_index()
    
    # Tambahkan atribut penanda anomali
    status_1473, status_1474 = [], []
    is_outlier, is_patahan = [], []
    
    for _, r in pivot.iterrows():
        w_kode = int(r['wilayah_kode'])
        thn = str(r['periode'])
        
        anom_1473 = peta_anomali.get(('var1473', w_kode, thn), {'kategori': 'NORMAL', 'is_outlier': False, 'is_patahan': False})
        anom_1474 = peta_anomali.get(('var1474', w_kode, thn), {'kategori': 'NORMAL', 'is_outlier': False, 'is_patahan': False})
        
        status_1473.append(anom_1473['kategori'])
        status_1474.append(anom_1474['kategori'])
        
        outl = anom_1473['is_outlier'] or anom_1474['is_outlier']
        patah = anom_1473['is_patahan'] or anom_1474['is_patahan']
        
        # Patahan pemekaran DOB Papua 2024-2025
        if w_kode in [9200, 9500, 9600, 9700] and int(thn) >= 2024:
            patah = True
            
        is_outlier.append(outl)
        is_patahan.append(patah)
        
    pivot['status_anomali_var1473'] = status_1473
    pivot['status_anomali_var1474'] = status_1474
    pivot['is_outlier'] = is_outlier
    pivot['is_patahan'] = is_patahan
    
    pivot = pivot.sort_values(['wilayah_kode', 'periode']).reset_index(drop=True)
    return pivot

def bangun_rekonsiliasi_nasional(nasional_df):
    """
    Membentuk tabel nasional yang menyandingkan BPS, WDI, dan WHO per tahun.
    """
    df = nasional_df.copy()
    # Beri nama kolom indikator yang jelas: <sumber>_<seri>
    df['kolom_indikator'] = df['sumber'] + '_' + df['seri_kode']
    
    pivot = df.pivot(
        index='periode',
        columns='kolom_indikator',
        values='nilai'
    ).reset_index()
    
    pivot['wilayah_kode'] = 9999
    pivot['nama_wilayah'] = 'INDONESIA'
    
    cols_order = ['periode', 'wilayah_kode', 'nama_wilayah'] + [c for c in pivot.columns if c not in ['periode', 'wilayah_kode', 'nama_wilayah']]
    pivot = pivot[cols_order].sort_values('periode').reset_index(drop=True)
    return pivot

def proses_gold(silver_df):
    """Fungsi orkestrasi pembentukan seluruh tabel Gold."""
    bps_prov, nasional_terpilih, tidak_terpilih = pilih_baris_gold(silver_df)
    
    panel_prov = bangun_panel_provinsi(bps_prov)
    rekon_nas = bangun_rekonsiliasi_nasional(nasional_terpilih)
    
    return {
        'panel_provinsi': panel_prov,
        'rekonsiliasi_nasional': rekon_nas,
        'baris_tidak_terpilih': tidak_terpilih
    }
