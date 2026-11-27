import pathlib, json, sys, subprocess
import pandas as pd

PROJECT_ROOT = pathlib.Path('C:/Users/froze/workbench-workspace/dw-kelompok-01')
GOLD_DIR = PROJECT_ROOT / 'data' / 'gold'
DOC_PATH = PROJECT_ROOT / 'docs' / 'data-dictionary.md'
NIM = '124450088'
METRICS_PATH = PROJECT_ROOT / 'results' / NIM / 'metrics.json'

# Helper maps for unit and source
UNIT_MAP = {
    'nilai': 'persen',
    'selisih': 'persen',
    'periode': '-',
    'seri_kode': '-',
    'nilai_utama': 'persen',
    'nilai_pembanding': 'persen',
    'kategori': '-',
    'wilayah_kode': '-',
    'nama_wilayah': '-',
    'sumber': '-',
    'satuan': '-',
}
DERIVED = {'kategori', 'selisih', 'nilai_utama', 'nilai_pembanding'}

def unit(col):
    return UNIT_MAP.get(col, '-')

def source(col):
    return 'Keputusan di log' if col in DERIVED else 'Silver'

sections = []
col_count = 0
for p in GOLD_DIR.glob('*.parquet'):
    df = pd.read_parquet(p)
    rows = []
    for col, dtype in df.dtypes.items():
        rows.append((col, str(dtype), unit(col), f'Deskripsi singkat untuk {col}', source(col)))
        col_count += 1
    md = f'## {p.name}\n\n| Nama | Tipe | Satuan | Arti | Asal |\n|------|------|--------|------|------|\n'
    for r in rows:
        md += f'| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |\n'
    sections.append(md)

DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(DOC_PATH, 'w', encoding='utf-8') as f:
    f.write('# Data Dictionary – Gold Layer\n\n')
    for sec in sections:
        f.write(sec + '\n')
print('Data dictionary written to', DOC_PATH)

# Load existing metrics, keep existing metrik dict
with open(METRICS_PATH, 'r', encoding='utf-8') as f:
    metrics = json.load(f)
existing = metrics.get('metrik', {})
# Add new metric
existing['kolom_terdokumentasi'] = col_count
# Build command args for src.common.hasil
args = ['python', '-m', 'src.common.hasil', NIM]
for k, v in existing.items():
    args.append(f"{k}={v}")
# call subprocess
subprocess.run(args, cwd=str(PROJECT_ROOT), check=True)
print('Metrics rewritten via src.common.hasil')
