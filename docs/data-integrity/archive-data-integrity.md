# Archive Dataset Data Quality Statement

**Dataset:** funding_archive_2000_2018
**Source:** Idaho Secretary of State campaign finance data archive (sos.idaho.gov)
**Scope, per official documentation:** Bulk CSV downloads covering even-numbered report years 2000–2018.
**Rows:** [to be filled in once the PAC gap below is resolved and the dataset is rebuilt]
**Last reviewed:** September 2026

## Summary

This document records the data quality issues identified in Idaho's oldest campaign finance dataset, both from the source data itself and from what the current cleaning script does and does not yet account for. This review is less complete than the legacy dataset's equivalent statement, the current script only processes candidate-side contributions and was found, after later work on the other two datasets, to be missing an entire filer category (PACs) as a result. What's documented here reflects the current state of that investigation, not a finished audit.

---

## Part 1: Structural Findings

**1. This dataset currently omits Political Action Committee (PAC) contributions entirely.** The state provides PAC contribution data as a separate export from candidate contribution data for this archive period; the current pull covers candidate data only. Archive is the outlier among the three datasets in this respect, legacy and live both include PAC activity within their standard pull. Completing this dataset will require locating and aggregating that separate PAC export the same way candidate data was originally obtained, since archive has no API to fall back on.

**2. The dataset's underlying data model changes partway through its own date range, without documentation.** Report years roughly before and after 2010 use different transaction codes and field structures. This is not currently corrected for in the cleaning script beyond what the code already handles (state code translation, contributor type derivation, etc.); it is noted here as a real structural discontinuity within a single "dataset" that a reader might otherwise assume is uniform across its full 2000–2018 range.

**3. One full year, 2019, does not exist as structured data at all, and the state has confirmed this is intentional, not an oversight.** The state's own archive skips 2019 entirely; only scanned paper filings are available for that year. A public records request was filed asking for this year's data in a structured format. The state's response confirmed 2019 is not available as structured data, and that the state considers the existing collection of scanned filings sufficient to meet its reporting obligations for that year. This means a full year of Idaho campaign finance activity is only accessible one scanned document at a time, with no path to programmatic access, an official position rather than a temporary gap.

**4. Election and Election Year were not consistently recorded by the state for report years 2000–2010.** Both fields are blank for this range in the source data itself, this is a real government reporting gap, not an artifact of the cleaning script.

**5. Non-standard contributor state values exist in the source data and are not corrected.** This includes Canadian province codes and other unrecognized values sitting in what's meant to be a US state field. These are preserved as-is; they reflect a source data quality issue not yet resolved.

**6. State values were sometimes entered as raw numeric codes rather than standard two-letter abbreviations.** Values like `8`, `10`, `55`, and `83` appear in the state field where a real USPS abbreviation should be, resolved by the cleaning script to `ID`; `11` resolves to `NY`. This is a genuine source data quality issue, not a formatting preference, whatever internal system produced these exports allowed raw numeric codes to leak into a field meant to hold a standard state abbreviation.

**7. State abbreviations were entered inconsistently in case and format.** A malformed value ("Ae" instead of the standard military mail code "AE") was found and corrected; the cleaning script also normalizes valid abbreviations that were entered in mixed or lowercase. This points to the same intake-validation weakness documented more extensively in the legacy dataset, values were accepted into this field regardless of whether they matched an expected format.

**8. City field values contained embedded formatting corruption.** Specific city names (Spokane, Cranbury, Milwaukee) appeared in the source data with a trailing comma attached directly to the name itself, evidence of a formatting or export error at the source rather than a data-entry mistake by a filer.

---

## Part 2: Quantified Data Gaps

Work on this project prioritized the most recent, most structurally complex dataset first (live, 2023–present), with legacy and archive to follow, so a usable dataset could ship sooner rather than requiring all three to be complete simultaneously. Archive's full quantified review is planned as part of that later pass.

- **90 rows** are flagged where the contribution date falls more than 2 years outside the report year they're filed under. These rows have not been altered or investigated further; flagged only, not resolved.
- **PAC contributions: scope currently unknown.** Because this category is entirely absent from the current pull rather than present-but-flawed, there is no row count or dollar figure to report yet, the gap itself hasn't been quantified because the missing data hasn't been located and pulled.

---

## Part 3: Resolved

The state-code, city-formatting, and abbreviation-casing issues documented in Findings 6, 7, and 8 above are already corrected by the current script, in the same sense that Legacy's routine field-level cleaning is corrected by its script: real, working fixes, but not the kind of individually-researched investigation this section is meant to highlight. No finding in this dataset has yet reached that deeper level of resolution, the PAC gap and the pre/post-2010 structural change are both still open questions requiring real investigation, not just a data-cleaning pass.

---

## Part 4: Still Open

**Issue 1: PAC data needs to be located, pulled, and integrated.** See Structural Finding 1. This is the most significant open item for this dataset, since it means the dataset as currently built is incomplete by an entire filer category, not just missing individual fields.

**Issue 2: The pre/post-2010 structural change has not been fully characterized.** It's confirmed that something changes partway through the date range, but the specific fields, codes, or transaction types affected haven't been individually documented the way legacy's office/district issues were. This needs its own review pass.

**Issue 3: 2019 remains entirely unavailable as structured data.** Per the state's own response to a public records request, this is confirmed as their permanent position, not a pending resolution. The open question is whether this project pursues manual extraction from the scanned filings for that year, or documents 2019 as a permanent, unrecoverable gap in this dataset's coverage.

---

## Methodology

Findings in this document reflect direct review of the script's own cleaning logic and comments, cross-referenced against what was later learned while working through the legacy and live datasets, most notably the PAC gap, which only became visible by comparison rather than from reviewing this dataset in isolation. The full methodology used across this project is documented in this project's root README.

---

*This document reflects an early-stage review of this dataset and will be substantially expanded once the PAC data gap is resolved and this dataset's cleaning script is rebuilt to match.*
