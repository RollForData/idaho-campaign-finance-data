# funding_legacy_2020_2023

This folder contains the script that cleans and standardizes Idaho's legacy campaign finance contribution data (2020–2023), pulled from the Idaho Secretary of State's legacy campaign finance system.

## Contents

`pull_funding_legacy.py` — reads the raw exported CSV, applies all cleaning and standardization steps below, and writes a cleaned CSV ready for database loading.

## To run

From the project root run: `py funding_legacy_2020_2023\pull_funding_legacy.py`

## What the script does

- Applies general text cleanup across every text field: trims whitespace, removes stray encoding artifacts, and collapses embedded line breaks.
- Standardizes contributor location fields (state, city, zip): resolves inconsistent placeholder values, corrects known data-entry errors (swapped city/address fields, zip codes entered in the wrong field, state names duplicated into the wrong field), and backfills recoverable zip codes using matching address records elsewhere in the dataset.
- Standardizes recipient office and district information: resolves inconsistent or placeholder office labels to a single standardized office name per candidate, and rebuilds the district field into a consistent `TYPE - VALUE` format (e.g., `LEGISLATURE - 12`, `COUNTY - ADA`, `SCHOOL - KUNA JOINT SCHOOL DISTRICT #3`) so office types are never ambiguous with each other.
- Reassigns a small number of individually-researched candidates whose office was never populated in the source data, using outside public records to confirm the correct office and district. A few candidates could not be confirmed through any available public record; these are explicitly labeled `Could not be sourced` rather than left blank, to distinguish a real data gap from an expected blank (e.g., PAC records, which have no office).
- Backfills contributor registration county (`to_reg_district`) using zip code, replacing an improper placeholder value ("Idaho State") that is not an actual Idaho county.
- Sets `Return` transactions to a negative dollar amount so totals net out correctly with a simple sum, rather than requiring a separate filter.
- Adds several new flag fields (`missing_contr_data`, `missing_state_data`, `missing_city_data`) that identify rows with a genuine, unexplained data gap versus fields that are expected to be blank.

## Data notes

- `donate_type = Return` amounts are stored as negative numbers as of this version, this differs from the original source data, which reports all amounts as positive regardless of transaction direction.
- `donate_type = Credit Card Item` is preserved as its own distinct category rather than merged into another type, since its correct treatment (loan, expense, or something else) has not been definitively established.
- Loan repayments are not included in this dataset. Only contribution-side activity was pulled; expenditure data (including loan repayments) is out of scope for this project.
- A small number of rows retain a known, uncorrected gap where the source data simply does not support a confident correction (see the dataset integrity README for details and dollar figures).

## Dependencies

No database connection or external API required for this script. Input is a raw CSV export; output is a cleaned CSV ready for loading into PostgreSQL.