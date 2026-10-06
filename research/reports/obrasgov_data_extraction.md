# Obrasgov.br Data

Research report · [Python report script](../../code/reports/obrasgov_data_extraction.py) · Saved local results; full datasets stay outside Git.


## Data Extraction

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

First we retrieve all projects.

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

Then we transform the nested tables into columns.

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

The Obrasgov API only allows for the extraction of point geometries. In
order to enrich the dataset with multidimensional geometries we have to
resort to another endpoint. Using Obrasgovr we first extract the
geo-data metadata to identify which geometries are potentially
multidimensional.

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

With the filtered IDs, we extract the full geometries.

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}

> [!NOTE]
>
> - Metadata can be extracted for the individual geometries. For now,
>   geometries were merged by project ID.

We then join both tables and end up with the final data set for further
manipulation.

    {'records': 134929,
     'cleaned_records': 133417,
     'removed': 1512,
     'baseline_cleaned_records': 133417,
     'count_matches_baseline': True,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:23:02.890635+00:00'}
