import sys, pathlib, pandas as pd, json, numpy as np
sys.path.append('C:/Users/froze/workbench-workspace/dw-kelompok-01')
from src.gold.builder import bangun_panel, bangun_nasional, rekonsiliasi_golongan

# Load silver data
silver_path = pathlib.Path('C:/Users/froze/workbench-workspace/dw-kelompok-01/data/silver/silver.parquet')
silver = pd.read_parquet(silver_path)

# Build panel and nasional data frames
panel = bangun_panel(silver)
nasional = bangun_nasional(silver)

# Create reconciliation table
rek = rekonsiliasi_golongan(panel, nasional)

# Save reconciliation parquet
out_path = pathlib.Path('C:/Users/froze/workbench-workspace/dw-kelompok-01/data/gold/rekonsiliasi.parquet')
out_path.parent.mkdir(parents=True, exist_ok=True)
rek.to_parquet(out_path)
print('Reconciliation saved to', out_path)

# Update metrics.json for this NIM
nim = '124450088'
metrics_path = pathlib.Path(f'C:/Users/froze/workbench-workspace/dw-kelompok-01/results/{nim}/metrics.json')
with open(metrics_path, 'r', encoding='utf-8') as f:
    metrics = json.load(f)
# Add new fields
pair_count = int(rek.shape[0])
median_diff = float(np.nanmedian(rek['selisih'].astype(float))) if not rek['selisih'].isna().all() else None
metrics.setdefault('pasangan_rekonsiliasi', pair_count)
metrics['selisih_median'] = median_diff
# Write back
with open(metrics_path, 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2, ensure_ascii=False)
print('Metrics updated')
