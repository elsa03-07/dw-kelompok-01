# Data Dictionary – Gold Layer

## panel_provinsi.parquet

| Nama | Tipe | Satuan | Arti | Asal |
|------|------|--------|------|------|
| sumber | str | - | Deskripsi singkat untuk sumber | Silver |
| seri_kode | str | - | Deskripsi singkat untuk seri_kode | Silver |
| nama_indikator | str | - | Deskripsi singkat untuk nama_indikator | Silver |
| kode_sdg | str | - | Deskripsi singkat untuk kode_sdg | Silver |
| wilayah_kode | int64 | - | Deskripsi singkat untuk wilayah_kode | Silver |
| nama_wilayah | str | - | Deskripsi singkat untuk nama_wilayah | Silver |
| periode | str | - | Deskripsi singkat untuk periode | Silver |
| jenis_periode | str | - | Deskripsi singkat untuk jenis_periode | Silver |
| rincian | str | - | Deskripsi singkat untuk rincian | Silver |
| nilai | float64 | persen | Deskripsi singkat untuk nilai | Silver |
| satuan | str | - | Deskripsi singkat untuk satuan | Silver |
| _berkas_raw | str | - | Deskripsi singkat untuk _berkas_raw | Silver |
| _sha256_raw | str | - | Deskripsi singkat untuk _sha256_raw | Silver |

## panel_provinsi_anomali.parquet

| Nama | Tipe | Satuan | Arti | Asal |
|------|------|--------|------|------|
| wilayah_kode | int64 | - | Deskripsi singkat untuk wilayah_kode | Silver |
| nama_wilayah | str | - | Deskripsi singkat untuk nama_wilayah | Silver |
| periode | str | - | Deskripsi singkat untuk periode | Silver |
| var1473 | float64 | - | Deskripsi singkat untuk var1473 | Silver |
| var1474 | float64 | - | Deskripsi singkat untuk var1474 | Silver |
| status_anomali_var1473 | str | - | Deskripsi singkat untuk status_anomali_var1473 | Silver |
| status_anomali_var1474 | str | - | Deskripsi singkat untuk status_anomali_var1474 | Silver |
| is_outlier | bool | - | Deskripsi singkat untuk is_outlier | Silver |
| is_patahan | bool | - | Deskripsi singkat untuk is_patahan | Silver |

## rekonsiliasi.parquet

| Nama | Tipe | Satuan | Arti | Asal |
|------|------|--------|------|------|
| periode | str | - | Deskripsi singkat untuk periode | Silver |
| seri_kode | str | - | Deskripsi singkat untuk seri_kode | Silver |
| nilai_utama | float64 | persen | Deskripsi singkat untuk nilai_utama | Keputusan di log |
| nilai_pembanding | float64 | persen | Deskripsi singkat untuk nilai_pembanding | Keputusan di log |
| selisih | float64 | persen | Deskripsi singkat untuk selisih | Keputusan di log |
| kategori | str | - | Deskripsi singkat untuk kategori | Keputusan di log |

## rekonsiliasi_nasional.parquet

| Nama | Tipe | Satuan | Arti | Asal |
|------|------|--------|------|------|
| periode | str | - | Deskripsi singkat untuk periode | Silver |
| wilayah_kode | int64 | - | Deskripsi singkat untuk wilayah_kode | Silver |
| nama_wilayah | str | - | Deskripsi singkat untuk nama_wilayah | Silver |
| bps_var1473 | float64 | - | Deskripsi singkat untuk bps_var1473 | Silver |
| bps_var1474 | float64 | - | Deskripsi singkat untuk bps_var1474 | Silver |
| wdi_SN.ITK.DEFC.ZS | float64 | - | Deskripsi singkat untuk wdi_SN.ITK.DEFC.ZS | Silver |
| wdi_SN.ITK.MSFI.ZS | float64 | - | Deskripsi singkat untuk wdi_SN.ITK.MSFI.ZS | Silver |
| who_gho_NUTOVERWEIGHTPREV | float64 | - | Deskripsi singkat untuk who_gho_NUTOVERWEIGHTPREV | Silver |
| who_gho_NUTRITION_WH_2 | float64 | - | Deskripsi singkat untuk who_gho_NUTRITION_WH_2 | Silver |
| who_gho_NUTSTUNTINGPREV | float64 | - | Deskripsi singkat untuk who_gho_NUTSTUNTINGPREV | Silver |

## tabel_nasional.parquet

| Nama | Tipe | Satuan | Arti | Asal |
|------|------|--------|------|------|
| sumber | str | - | Deskripsi singkat untuk sumber | Silver |
| seri_kode | str | - | Deskripsi singkat untuk seri_kode | Silver |
| nama_indikator | str | - | Deskripsi singkat untuk nama_indikator | Silver |
| kode_sdg | str | - | Deskripsi singkat untuk kode_sdg | Silver |
| kelompok_indikator | str | - | Deskripsi singkat untuk kelompok_indikator | Silver |
| wilayah_kode | int64 | - | Deskripsi singkat untuk wilayah_kode | Silver |
| nama_wilayah | str | - | Deskripsi singkat untuk nama_wilayah | Silver |
| periode | str | - | Deskripsi singkat untuk periode | Silver |
| jenis_periode | str | - | Deskripsi singkat untuk jenis_periode | Silver |
| rincian | str | - | Deskripsi singkat untuk rincian | Silver |
| nilai | float64 | persen | Deskripsi singkat untuk nilai | Silver |
| satuan | str | - | Deskripsi singkat untuk satuan | Silver |
| dapat_dibandingkan_dengan | str | - | Deskripsi singkat untuk dapat_dibandingkan_dengan | Silver |
| catatan_perbandingan | str | - | Deskripsi singkat untuk catatan_perbandingan | Silver |
| _berkas_raw | str | - | Deskripsi singkat untuk _berkas_raw | Silver |
| _sha256_raw | str | - | Deskripsi singkat untuk _sha256_raw | Silver |

## tabel_nasional_lebar.parquet

| Nama | Tipe | Satuan | Arti | Asal |
|------|------|--------|------|------|
| periode | str | - | Deskripsi singkat untuk periode | Silver |
| bps_var1473 | float64 | - | Deskripsi singkat untuk bps_var1473 | Silver |
| bps_var1474 | float64 | - | Deskripsi singkat untuk bps_var1474 | Silver |
| wdi_defc | float64 | - | Deskripsi singkat untuk wdi_defc | Silver |
| wdi_msfi | float64 | - | Deskripsi singkat untuk wdi_msfi | Silver |
| who_stunting | float64 | - | Deskripsi singkat untuk who_stunting | Silver |
| who_overweight | float64 | - | Deskripsi singkat untuk who_overweight | Silver |
| who_wasting | float64 | - | Deskripsi singkat untuk who_wasting | Silver |

