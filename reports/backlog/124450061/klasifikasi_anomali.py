import pandas as pd
from pathlib import Path

ROOT = Path("C:/Users/daffascript_/.gemini/antigravity/scratch/capstone-data-wrangling")
DIR_REPORTS = ROOT / "reports/profiling"
FILE_ANOMALI = DIR_REPORTS / "daftar_calon_anomali_seri_utama.csv"

df = pd.read_csv(FILE_ANOMALI)

def kategorikan_anomali(row):
    seri = row['seri_kode']
    thn = row['tahun']
    wid = row['wilayah_id']
    wil = str(row['nama_wilayah']).upper()
    val = row['nilai']
    
    # 1. Patahan Seri: Pemekaran Wilayah Papua 2024-2025
    if wid in [9200, 9500, 9600, 9700] and thn in [2024, 2025]:
        return "Patahan Seri (Structural Break)", "Pemekaran wilayah: Provinsi DOB Papua baru terbentuk dan mulai dicatat tersendiri oleh BPS pada 2024."
    
    # 2. Patahan Seri: Pergeseran Induk Papua pasca pemekaran
    if wid == 9400 and thn in [2024, 2025]:
        return "Patahan Seri (Structural Break)", "Perubahan cakupan wilayah induk Papua setelah 4 DOB dimekarkan, menyebabkan penurunan persentase drastis."
    
    # 3. Patahan Seri: Kalibrasi awal instrumen FIES 2017 (NTT & Gorontalo)
    if seri == 'var1474' and thn in [2017, 2018] and wid in [5300, 7500]:
        return "Patahan Seri (Metodologi)", "Tahun awal penerapan instrumen FIES (Susenas 2017-2018) sebelum stabilisasi metodologi pengukuran."
        
    # 4. Patahan Seri: Kejutan Pandemi COVID-19 (2020) & Krisis Pangan Global (2022)
    if seri == 'var1473' and thn in [2020, 2022] and wid not in [8100, 8200, 9400]:
        return "Patahan Seri (Kejutan Makro)", "Pergeseran serentak akibat syok ekonomi/rantai pasok pangan pandemi 2020 dan krisis pangan global 2022."
        
    # 5. Outlier Asli: Maluku & Maluku Utara (konsisten tinggi sepanjang masa)
    if wid in [8100, 8200]:
        return "Outlier Asli (Sosio-Geografis)", "Kondisi struktural riil wilayah kepulauan Indonesia Timur: tantangan logistik distribusi bahan pokok pangan antarpulau."
        
    # 6. Outlier Asli: Papua pra-pemekaran (2017-2023)
    if wid == 9400 and thn <= 2023:
        return "Outlier Asli (Sosio-Geografis)", "Tingkat kerawanan pangan riil di pedalaman Papua dengan akses infrastruktur terbatas."
        
    # 7. Outlier Asli lainnya (provinsi dengan capaian sangat baik / terendah seperti DKI atau Bali jika masuk batas)
    if val < 3.0:
        return "Outlier Asli (Wilayah Maju)", "Capaian ketahanan pangan sangat baik pada pusat ekonomi dengan aksesibilitas tinggi."
        
    return "Outlier Asli (Sosio-Geografis)", "Variasi ekstrem riil antardaerah; bukan kesalahan pengukuran data."

kategori_list = []
keterangan_list = []
for _, r in df.iterrows():
    kat, ket = kategorikan_anomali(r)
    kategori_list.append(kat)
    keterangan_list.append(ket)

df['kategori_anomali'] = kategori_list
df['penjelasan_kategori'] = keterangan_list
df['tindakan_wrangling'] = "Dipertahankan (TIDAK DIBUANG) & Didokumentasikan"

df.to_csv(DIR_REPORTS / "daftar_anomali_terklasifikasi.csv", index=False)
print("Berhasil mengklasifikasikan anomali dan menyimpan ke daftar_anomali_terklasifikasi.csv!")
print("\nRingkasan per kategori anomali:")
print(df['kategori_anomali'].value_counts())
