# funding_legacy_2020_2023

This folder contains the script used to evaluate and clean Idaho's legacy campaign finance contribution data (2020–2023) against itself, pulled from the Idaho Secretary of State's legacy campaign finance system.

**Status: research pass, not the production pipeline.** This script was built against a bulk CSV export as a first-level pass at understanding this dataset, identifying its structural issues, data gaps, and cleaning requirements before any decision was made about how this dataset would ultimately be pulled. That evaluation is what surfaced most of the findings documented in this dataset's data-integrity statement. The plan going forward is to pull this dataset through its own API instead (see this project's root README), rebuilding it to match the same data model used for the live dataset. This script and its output are retained here because the findings behind its cleaning logic remain accurate and relevant regardless of pull method, not because this is the method that will be used going forward.

## Contents

`pull_funding_legacy.py` — reads the raw exported CSV, applies all cleaning and standardization steps below, and writes a cleaned CSV.

## To run

From the project root run: `py funding_legacy_2020_2023\pull_funding_legacy.py`

## What the script does

- Applies general text cleanup across every text field: trims whitespace, removes stray encoding artifacts, and collapses embedded line breaks.
- Standardizes contributor location fields (state, city, zip): resolves inconsistent placeholder values, corrects known data-entry errors (swapped city/address fields, zip codes entered in the wrong field, state names duplicated into the wrong field), and backfills recoverable zip codes using matching address records elsewhere in the dataset.
- Standardizes recipient office and district information: resolves inconsistent or placeholder office labels to a single standardized office name per candidate, and rebuilds the district field into a consistent `TYPE - VALUE` format (e.g., `LEGISLATURE - 12`, `COUNTY - ADA`, `SCHOOL - KUNA JOINT SCHOOL DISTRICT #3`) so office types are never ambiguous with each other.
- Reassigns a small number of individually-researched candidates whose office was never populated in the source data, using outside public records to confirm the correct office and district. A few candidates could not be confirmed through any available public record; these are explicitly labeled `Could not be sourced` rather than left blank, to distinguish a real data gap from an expected blank (e.g., PAC records, which have no office).
- Backfills contributor registration county (`to_reg_district`) using zip code, replacing an improper placeholder value ("Idaho State") that is not an actual Idaho county.
- Sets `Return` transactions to a negative dollar amount so totals net out correctly with a simple sum, rather than requiring a separate filter.
- Adds several flag fields (`missing_contr_data`, `missing_state_data`, `missing_city_data`) that identify rows with a genuine, unexplained data gap versus fields that are expected to be blank.

## Data notes

- `donate_type = Return` amounts are stored as negative numbers as of this version; this differs from the original source data, which reports all amounts as positive regardless of transaction direction.
- `donate_type = Credit Card Item` is preserved as its own distinct category rather than merged into another type, since its correct treatment (loan, expense, or something else) has not been definitively established.
- Loan repayments are not included in this pull. Only contribution-side activity was pulled; expenditure data (including loan repayments) was out of scope for this evaluation.
- A number of rows retain known, uncorrected gaps where the source data does not support a confident correction. See this dataset's data-integrity statement for full detail and dollar figures.

## Dependencies

No database connection or external API required for this script. Input is a raw CSV export; output is a cleaned CSV.
