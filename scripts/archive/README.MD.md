# funding_archive_2000_2018

This folder contains the script used to evaluate and clean Idaho's oldest campaign finance dataset (2000–2018), sourced from the Idaho Secretary of State's data archive. This dataset is static and will not be updated by the state.

**Status: research pass, not yet the final pipeline.** This script was built as a first-level evaluation of the archive's candidate-side contribution data, identifying its structural issues and cleaning requirements. That evaluation surfaced a significant gap after the fact: this dataset's bulk export splits PAC contributions into a separate file from candidate contributions, and this script currently processes candidate data only. Unlike the legacy dataset, this dataset has no API, so the pull method itself isn't changing, but this script needs a substantial rebuild to incorporate the PAC-side export before it reflects a complete dataset. See this dataset's data-integrity statement for full detail.

## Contents

`clean_funding_archive.py` — reads the raw archive spreadsheet, applies standardization and cleanup transformations, outputs a cleaned single-sheet Excel file, and loads records into PostgreSQL as a flat table.

`funding_data_archive_2000_2018.xlsx` — raw source data downloaded from the Idaho SOS archive. This file should never be replaced or modified; it is the permanent source of record for this dataset. Not tracked in git.

`funding_data_archive_2000_2018_cleaned.xlsx` — cleaned output file produced by the script. Not tracked in git.

## To run

From the project root:

`py funding_archive_2000_2018\clean_funding_archive.py`

This will overwrite the cleaned Excel file and drop and recreate the `funding_archive_2000_2018` table in PostgreSQL.

## What the script does

- Trims leading and trailing whitespace from all string fields.
- Strips trailing commas, semicolons, and colons from the end of any cell value.
- Corrects specific known malformed city values (Spokane, Cranbury, Milwaukee) where trailing commas were present in the source data.
- Converts numeric state codes to their correct two-letter abbreviations (8, 10, 55, 83 to ID; 11 to NY; 50 to ID).
- Corrects "Ae" to "AE" and uppercases any mixed or lowercase value that matches a valid USPS state or military mail abbreviation; non-standard values that cannot be resolved are left as-is and noted as source data quality issues.
- Converts party abbreviations to full names (REP to Republican, DEM to Democratic, etc.).
- Standardizes Election values G and P to General and Primary; all other values, including blank, are set to NULL. Election data was not recorded in years 2000–2010; NULL values in those years reflect the source data, not a script error.
- Sets ElectionYear to NULL where no data exists in the source; not inferred from the report year tab, for the same reason as above.
- Adds a `report_year` column populated from the source tab name, preserving the original report year grouping after all tabs are merged into a single flat table.
- Derives Contributor Type from the original ContrCP field; where contributor name matches candidate name exactly, the value is overridden to Self.
- Derives Transaction Type and Transaction Sub Type from ContrType and contribution amount sign (negative amounts become Returned Contribution or Loan Repayment; positive Loan amounts become Loan; In-Kind maps from its source code; all other positive amounts default to Itemized).
- Standardizes ContrDate to YYYY-MM-DD format; unparseable dates are set to NULL.
- Cleans zip codes to 5-digit format; zero-pads 4-digit codes; nulls invalid entries.
- Adds a `ContrDateDiscrepancy` flag where the ContrDate year falls more than 2 years outside the report year tab; informational only, no data is altered.

## Data notes

- This script currently processes candidate-side contributions only. PAC contributions exist as a separate export from the state and are not yet incorporated, see this dataset's data-integrity statement.
- 2019 data does not exist as structured data in this archive; the state's response to a public records request confirmed this is their permanent position, not a pending gap.
- Election and ElectionYear were not consistently recorded in years 2000–2010. NULL values in those fields for those years reflect the source data, not a script error.
- Non-standard ContributorState values, including Canadian provinces and unrecognized codes, exist in the source data and are left as-is; these are source data quality issues, not corrected by this script.
- 90 rows are flagged in ContrDateDiscrepancy as having a contribution date more than 2 years outside their report year tab. These rows have not been altered.
- This dataset covers report years 2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, and 2018 — even years only, reflecting how the source system grouped records by election cycle.

## Dependencies

Raw source file `funding_data_archive_2000_2018.xlsx` must be present in this folder before running the script.
