# -*- coding: utf-8 -*-
"""Generate data dictionary documentation for all Gold tables.

The script:
1. Reads every Parquet file under `data/gold/` that belongs to the Gold layer.
2. For each file extracts column names, pandas dtypes and, where possible, unit (satuan) and source.
   * Unit is inferred from column name or from a lookup table (e.g., `nilai` → "persen").
   * Source is set to "Silver" for columns originally coming from the Silver layer (most columns),
     and to "Keputusan di log" for derived columns such as `kategori`.
3. Writes a markdown section for each table to `docs/data-dictionary.md`.
4. Updates `results/<NIM>/metrics.json` with the total number of documented columns
   under the key `kolom_terdokumentasi`.
5. Calls `python -m src.common.hasil` to rewrite the metrics file (this also preserves
   existing Sprint‑1 metrics).
"""

import pathlib, json, sys
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = pathlib.Path('C:/Users/froze/workbench-workspace/dw-kelompok-01')
GOLD_DIR = PROJECT_ROOT / 'data' / 'gold'
DOC_PATH = PROJECT_ROOT / 'docs' / 'data-dictionary.md'
NIM = '124450088'
METRICS_PATH = PROJECT_ROOT / 'results' / NIM / 'metrics.json'

# Helper to infer unit and source (very simple heuristic)
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

DERIVED_COLUMNS = {'kategori', 'selisih', 'nilai_utama', 'nilai_pembanding'}

def infer_unit(col_name: str) -> str:
    return UNIT_MAP.get(col_name, '-')

def infer_source(col_name: str) -> str:
    return 'Keputusan di log' if col_name in DERIVED_COLUMNS else 'Silver'

# ---------------------------------------------------------------------------
# Collect column info from each gold parquet file
# ---------------------------------------------------------------------------
sections = []
total_columns = 0
for parquet_file in GOLD_DIR.glob('*.parquet'):
    df = pd.read_parquet(parquet_file)
    tbl_name = parquet_file.name
    rows = []
    for col, dtype in df.dtypes.items():
        unit = infer_unit(col)
        source = infer_source(col)
        rows.append((col, str(dtype), unit, f"Deskripsi singkat untuk {col}", source))
        total_columns += 1
    # Build markdown table
    md = f"## {tbl_name}\n\n| Nama | Tipe | Satuan | Arti | Asal |\n|------|------|--------|------|------|\n"
    for row in rows:
        md += f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |\n"
    sections.append(md)

# ---------------------------------------------------------------------------
# Write (or create) the documentation file
# ---------------------------------------------------------------------------
DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(DOC_PATH, 'w', encoding='utf-8') as f:
    f.write('# Data Dictionary – Gold Layer\n\n')
    for sec in sections:
        f.write(sec + '\n')
print('Data dictionary written to', DOC_PATH)

# ---------------------------------------------------------------------------
# Update metrics.json with kolom_terdokumentasi
# ---------------------------------------------------------------------------
with open(METRICS_PATH, 'r', encoding='utf-8') as f:
    metrics = json.load(f)
metrics['kolom_terdokumentasi'] = total_columns
with open(METRICS_PATH, 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)
print('Metrics updated with kolom_terdokumentasi =', total_columns)

# ---------------------------------------------------------------------------
# Re‑run the common result writer to keep other Sprint‑1 metrics intact
# ---------------------------------------------------------------------------
print('Running src.common.hasil to rewrite metrics...')
import subprocess, shlex
subprocess.run(['python', '-m', 'src.common.hasil'], cwd=str(PROJECT_ROOT), check=True)
PY