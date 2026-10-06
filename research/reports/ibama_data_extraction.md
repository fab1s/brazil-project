# IBAMA - Data Extraction

Research report · [Python report script](../../code/reports/ibama_data_extraction.py) · Saved local results; full datasets stay outside Git.


    {'records': 8494,
     'unknown_sectors': 0,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:22:58.743667+00:00'}

We will extract three layers separately containing point, line and
polygon geometries from the
[PAMGIA](https://pamgia.ibama.gov.br/server/rest/services/SIGAGEO)
endpoint:

- tb_empreendimento_repr_p

- tb_empreendimento_repr_l

- tb_empreendimento_repr_a

<!-- -->

    {'records': 8494,
     'unknown_sectors': 0,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:22:58.743667+00:00'}

|     | tp_sector_en        | projects |
|-----|---------------------|----------|
| 0   | Energy              | 2013     |
| 1   | Mining              | 420      |
| 2   | Nuclear/Radioactive | 25       |
| 3   | Oil and Gas         | 219      |
| 4   | Other               | 512      |
| 5   | Transportation      | 5233     |
| 6   | Water Resources     | 72       |

    {'artifact_rows': 7, 'path': 'data/intermediate/ibama/sector_counts.parquet'}

    {'records': 8494,
     'unknown_sectors': 0,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:22:58.743667+00:00'}

Interactive maps are local HTML artifacts under `outputs/maps/`; see [workflow commands](../../docs/workflow.md).

    {'records': 8494,
     'unknown_sectors': 0,
     'source': 'copied_snapshot',
     'generated_at': '2026-10-05T10:22:58.743667+00:00'}
