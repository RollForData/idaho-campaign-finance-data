# Idaho Campaign Finance Data

*Decoding, cleaning, and aggregating Idaho's campaign finance records across three incompatible government data systems into a single, usable database.*

## Why This Exists

Idaho's campaign finance data is technically public, but it's split across three government systems that don't agree on structure or terminology, and none of them are built to answer the question that actually matters: who is funding influence in this state, and how much of it repeats. A donor list on its own is just names. The same handful of donors giving tens of thousands of dollars across dozens of candidates who share their interests, that's a pattern, and patterns require unified data to see. This project exists to turn three fragmented, individually unreliable datasets into one clean, aggregated source, the foundation a real donor-pattern or influence-mapping story would actually require.

## The Core Challenge

Idaho's Secretary of State maintains three separate campaign finance systems, and each one represents the same underlying kind of data, who gave money to whom, differently:

- **Archive (2000–2018):** CSV downloads only, split into separate files for candidates and PACs, with a completely different data structure kicking in partway through the range. One entire year, 2019, was never published as data at all, only as scanned paper filings.
- **Legacy (2020–2023):** A different structure again, this time with candidates and PACs unified in one table, but its own set of transaction codes and its own gaps. Which records live here versus in the live system isn't determined by year or office, it's determined by whether a candidate happened to run again in 2024, an inconsistency that isn't documented anywhere and has to be discovered by cross-referencing the data itself.
- **Live (2023–present):** No usable bulk export exists. The state's own CSV download omits office and district entirely, the fields needed to know which race a contribution actually belongs to. Getting that data at all required reverse-engineering the system's undocumented internal API.

None of these systems were built to be combined. Donor identity isn't stable across any of them, the same real organization can appear under a dozen different internal IDs depending on how its name was typed. Reconciling all three into one dataset means understanding each system's specific failure modes well enough to know what's fixable, what's a permanent gap in the public record, and what only becomes visible once you try to join them together.

## What's Built

This is a research-and-discovery phase across all three datasets. What's finished is the investigative work: documented findings on how each government system actually behaves, where its data is wrong, inconsistent, or incomplete, and how the three systems fail to line up with each other. What's not yet finished is the production pipeline, the actual scripts that will pull, clean, and load each dataset into its final form.

**Archive (2000–2018):** A cleaning script exists and correctly processes the candidate-side data it was built against, but it's missing PAC contributions entirely, a gap only discovered later while working through the other two datasets. Since Archive has no API, there's no alternative data source to reconsider, this script's *approach* is the right one, but it needs to be revisited and rebuilt to include PAC data before it reflects the full picture.

**Legacy (2020–2023):** Extensively developed against a CSV export, and that work surfaced substantial, real findings about the source data's structure and quality (documented in this dataset's data-integrity statement). But the plan going forward is to pull this dataset through its own API instead, likely one year at a time, and rebuild it into the same data model the live system uses. The CSV-based script stays as a record of what was learned, not as the method going forward.

**Live (2023–present):** No usable bulk export exists for this system at all, the state's own CSV omits the fields this project needs. Its undocumented internal API was reverse-engineered directly, endpoints, request/response structures, and how contribution, loan, candidate, and committee data relate to each other are documented in full (see `/docs/api-live-dataset`).

## Repo Structure

    idaho-campaign-finance-data/
    ├── README.md
    ├── scripts/
    │   ├── archive/
    │   ├── legacy/
    │   └── live/
    ├── docs/
    │   ├── data-integrity/
    │   │   ├── archive.md
    │   │   ├── legacy.md
    │   │   └── live.md
    │   ├── api-live-dataset/
    │   │   ├── README.md
            ├── ERD_api-live-dataset_V1.png        
    │   │   └── endpoints/
    │   │       ├── candidates.md
    │   │       ├── committees.md
    │   │       ├── contributions.md
    │   │       └── loans.md
    │   └── api-legacy-dataset/

Each dataset's `scripts/` folder holds its current cleaning script plus a README explaining what it does and how to run it. Where a script reflects an earlier exploratory approach (e.g. a CSV-based pull that will be replaced by an API-based one), its README notes that directly. `docs/data-integrity/` holds the factual findings for each dataset, what's wrong, missing, or inconsistent in the source data. `docs/api-live-dataset/` is the full reverse-engineered documentation of the live system's API. `docs/api-legacy-dataset/` is reserved for the same work once Legacy's own API is investigated.

## Methodology & Findings

Each dataset was approached the same way: pull the raw data as completely as possible first, then investigate what's actually in it before deciding how to clean or model it. For the live dataset, this meant reverse-engineering the system's internal API directly from browser network traffic, since its bulk export only covers one piece of its data, a process documented in full, including the testing methods used to confirm findings rather than infer them from naming or assumption alone.

The initial plan was to pull all three datasets from their bulk CSV exports: one consistent process across all three, and a pull method not dependent on an undocumented API staying stable over time, if the government changed how the API worked, a CSV-based pipeline could still be rebuilt from scratch, an API-based one couldn't be guaranteed to. Working through those exports also built real familiarity with the data, transaction types, loan structures, field patterns, that made it possible to later recognize what the live system's API was doing right or wrong. That approach held for Archive and Legacy, which bundle candidate, office, and transaction data together in a single export. It broke down for the live dataset, which splits candidate, committee, office, and transaction data into separate, relational tables rather than one flat file, and whose only bulk export covers transactions alone. Getting office and district data at all meant going around that export and directly to the API. That same structural split also meant the live system's data model already solved standardization and join problems the older CSVs weren't going to address, so rebuilding the older datasets to match the live model, rather than aggregating three independently-cleaned CSVs, became the better path forward.

A few findings that stood out:

- **The government's own donor records in the Legacy (2020–2023) and Archive (2000–2018) datasets don't reliably identify the same donor twice.** The Idaho Republican Party alone spans 11 separate internal donor IDs in the Legacy dataset; the Coeur d'Alene Tribe spans 18, both fragmented purely by formatting differences in how the name was entered. The live system appears to have solved this with a standardized donor ID join, one of the reasons the project's plan is to recreate that structure and use it to reconcile and normalize donor identity back into the older datasets, rather than solve deduplication independently in each one.
- **Where a given 2023 record actually lives, Legacy or Live, depends on the candidate's status in the current election cycle, not the record's own year or office.** A researcher pulling "county candidates from 2023" could miss real records depending on whether that same candidate happened to run again in 2024, a rule that isn't documented anywhere and was only discoverable by cross-referencing the two datasets directly. This is specific to the ambiguous handoff between the Legacy and Live systems; Archive's boundaries don't share this issue.
- **Campaign finance data for judicial elections is missing across more than half of Idaho's judicial districts.** No District Judge or Magistrate Judge records exist for districts 4, 5, 6, or 7, while every other office type in those same counties is fully represented, isolating this as a gap specific to judicial races, not a broader regional absence of data.

Full documentation:
- [Live dataset API reference](docs/api-live-dataset/README.md)
- [Archive data-integrity findings](docs/data-integrity/archive.md)
- [Legacy data-integrity findings](docs/data-integrity/legacy.md)
- [Live dataset data-integrity findings](docs/data-integrity/live.md)

## Data Sources

- Idaho Secretary of State campaign finance archive, 2000–2018 (sos.idaho.gov)
- Idaho Secretary of State legacy campaign finance portal, 2020–2023 (sunshine.sos.idaho.gov)
- Idaho Sunshine campaign finance portal, 2023–present (sunshine.voteidaho.gov)

## Built By

RollForData
