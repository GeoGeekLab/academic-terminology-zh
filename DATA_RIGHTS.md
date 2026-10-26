# Code license and terminology data rights

## Scope of the MIT license

The root LICENSE covers original software code and original documentation in
this repository. It does **not** grant copyright or database reuse rights in
third-party standards, standards-derived material, imported glossaries, or
third-party paper excerpts. Those materials retain their respective rights.

The public terms under data/gb_terminology_databases/ are available for viewing,
but **no independent, general-purpose redistribution or sublicensing license is
asserted for them**. Users must independently establish permissions before
redistributing the indexes or including them in another product.

## Preliminary source inventory (2026-10-26)

The four public CSV indexes contain 2,060 records and cite eight GB/T standards:

| Domain | Records | Standards |
| --- | ---: | --- |
| oceanography | 1,175 | GB/T 15919—2010; GB/T 15920—2010; GB/T 15921—2010 |
| artificial_intelligence | 75 | GB/T 41867—2022 |
| remote_sensing | 594 | GB/T 36299—2018; GB/T 14950—2009 |
| statistics | 216 | GB/T 3358.3—2009; GB/T 3358.1—2009 |

Each index stores term labels, English equivalents, aliases, source standard,
clause, PDF page, and a review-status field. Original PDF files and full
definitions are not shipped. Some review-status labels explicitly state that
verification was not independent or did not cover the full entry.

**Status: redistribution rights NOT VERIFIED.** The machine-readable inventory is [data/rights_manifest.json](data/rights_manifest.json). Run `python scripts/audit_rights.py` to verify record counts and source coverage. Run `python scripts/audit_rights.py --require-clearance` to enforce the release gate. The existence of a public
national standard is not evidence that redistribution of a derived index is
permitted. The repository's MIT LICENSE does not cure this issue. The
maintainers have not published written permission, a definitive legal opinion,
or a row-by-row copyright analysis. This inventory is NOT legal clearance.

## Release gate: required before a licensed data distribution

1. Identify the rights holder and any applicable publication terms for all
   eight standards. Record the source URL, date, and edition.
2. Have a qualified reviewer assess whether each published field represents
   copyright-protected expression, unprotected facts, or material covered by
   explicit permission. Do not assume that a short term is automatically free.
3. Record written permissions or the documented legal basis for each standard;
   obtain legal advice where needed.
4. Decide whether to keep a metadata-only public index, secure permission,
   substitute independently curated terminology, or remove affected records.
5. Audit the indexes for accuracy separately from the legal review. Track who
   verified each entry, when, and against which edition.
6. Only after clearance, publish the applicable DATA LICENSE and approved
   redistribution scope. Until then, do not label data/ as MIT, CC0 or CC BY.

Local use of the current index and packaging for third parties may have
different legal implications; users must check their own jurisdiction and use.

## Research benchmark excerpts

The file evals/real_papers.jsonl uses short excerpts from individually
attributed Creative Commons Attribution 4.0 research publications. Each
record provides its original paper URL, title, license and DOI. Those excerpts
remain under their source license, not this repository's MIT license. Any
translation or adapted excerpt must retain attribution and disclose changes.

## Sources for the rights assessment

- GitHub license guidance:
  https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository
- State Administration for Market Regulation, reply dated 2025-05-16:
  https://www.samr.gov.cn/zw/zfxxgk/fdzdgknr/bzcxs/art/2025/art_382e63d487424d19b7ca80971c7ff13d.html
- Official GB standard catalogue: https://std.samr.gov.cn/
- National standards text access: https://openstd.samr.gov.cn/

This is a preliminary engineering inventory, not legal advice.
