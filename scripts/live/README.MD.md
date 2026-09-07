# funding_live_2023_current

This folder contains the script used to evaluate and clean Idaho's current campaign finance transactions (2023–present) against a one-time bulk CSV export from the Idaho Sunshine portal.

**Status: research pass, not the production pipeline.** This script was built against the state's bulk CSV export as a first-level evaluation of this dataset, before it became clear that export doesn't include office or district data, fields this project's data model requires. The plan going forward is to pull this dataset through its underlying API instead (documented in full in this project's API reference), which does provide access to that data. This script and its findings are retained here because the cleaning work it performed surfaced real, confirmed issues about the underlying data, several of which are documented in this dataset's data-integrity statement, not because this CSV-based approach is the method going forward. Unlike the archive and legacy scripts, this one was never intended to be re-run against a refreshed export; a separate refresh mechanism for this dataset was never built, since the API-based approach superseded this one before that became necessary.

## Contents

`pull_funding_live.py` — reads the raw workbook, repairs known encoding and column-offset corruption, applies confirmed row-specific patches, standardizes currency, zip code, state, and date formatting, separates rows into clean data, rows needing manual review, and permanently excluded records, and outputs a cleaned Excel file.

`LIVE [Raw Data] funding_data_New_2023_current.xlsx` — raw source data compiled from the Idaho Sunshine portal's bulk CSV downloads for transaction years 2023 through 2026, one tab per year. Not tracked in git.

`LIVE [Clean Data] funding_data_New_2023_current.xlsx` — cleaned output produced by the script, containing Clean Data, Needs Manual Review, and Excluded Incomplete Records tabs. Not tracked in git.

## To run

From the project root:

`py funding_live_2023_current\pull_funding_live.py`

## What the script does

- Detects and repairs a corrupted-apostrophe encoding artifact (e.g. "O'Farrell", "Coeur d'Alene") that splits a field in two and shifts every subsequent column right by one position; merges the fragments and restores correct column alignment.
- Applies four confirmed row-specific patches for rows with unescaped commas or collapsed address fields that could not be repaired by a general rule, each keyed to its exact source tab and row number.
- Validates every remaining row (Transaction Id numeric, Transaction Type recognized, Transaction Date parseable, Transaction Amount present and numeric where required, no column overflow).
- Permanently excludes 147 specific, individually reviewed rows (missing required identity or amount data, joint-filer records with no recoverable identity). Any new row resembling these patterns in a future run would go to Needs Manual Review rather than being silently dropped.
- Routes any row that fails validation, and isn't a confirmed patch or exclusion, to a Needs Manual Review tab with a specific reason.
- Applies general text cleanup, zip code formatting, and currency field parsing.
- Corrects the Election Type and Election Year fields, which are swapped at the source.
- Adds `source_row_number` and `source_sheet` to every row so any record can be traced back to its exact position in the raw file.

## Data notes

- **Election Type and Election Year are swapped at the source.** This is a confirmed government data quality issue, not a cleaning preference, corrected here for the CSV evaluation.
- Transaction Id is not guaranteed unique in this export: some legitimate transactions appear twice, restated once in a monthly report and once in the year-end annual report. This is the same report-restatement pattern documented in this dataset's data-integrity statement.
- Outstanding Loan rows may represent a balance carried forward from a prior year rather than new money, consistent with the finding documented in this dataset's data-integrity statement.
- Roughly 20,000 rows have no Contributor Type, Last Name, or Company Name. This is expected, not an error: Idaho does not require donor identity disclosure for contributions under $50, for Anonymous contributions, or for bank Interest income.
- The 2023 tab in the raw export contains the full calendar year, though the state has stated this dataset's data is only accurate from 12/20/2023 forward. This overlaps with the legacy dataset's coverage and was deliberately left unfiltered here, since resolving the actual date boundary between the two datasets is an open cross-dataset question (see this dataset's data-integrity statement).

## Dependencies

Raw source file `LIVE [Raw Data] funding_data_New_2023_current.xlsx` must be present in this folder to run this script. Requires PostgreSQL connection via `.env` file.
