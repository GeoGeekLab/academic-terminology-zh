# Terminology data

The public repository includes the **minimal searchable term index** for four domains (2,060 entries across eight GB/T standards).

| Directory | Entries |
|---|---:|
| `oceanography/` | 1,175 |
| `artificial_intelligence/` | 75 |
| `remote_sensing/` | 594 |
| `statistics/` | 216 |

Each `indexes/terms.csv` contains only term identifiers, Chinese/English names, abbreviations, aliases, standard and clause identifiers, physical PDF page references, and verification labels.

The Skill's read-only lookup uses this directory by default. To use your separately acquired full database, specify `--db path/to/gb_terminology_databases.zip` or set `GB_TERMINOLOGY_DB_ROOT`. Original standard PDFs, source-text definitions, audit artifacts, OCR outputs, and intermediate files are not shipped.
