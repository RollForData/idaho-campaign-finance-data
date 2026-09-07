# Legacy Dataset Data Quality Statement

**Dataset:** funding_legacy_2020_2023
**Source:** Idaho Secretary of State, Legacy Campaign Finance Site (sunshine.sos.idaho.gov)
**Scope, per official documentation:** Timed Reports (2020 – 12/20/2023), 2020–2022 Annual Reports, and 2023 Annual Reports for county-level candidates not running in 2024, plus PACs.
**Rows:** 250,688
**Last reviewed:** September 2026

## Summary

This document records the data quality issues present in Idaho's legacy campaign finance dataset as delivered, independent of any cleaning performed on it. Every finding below was verified against the raw source file, the public portal, or an outside record; every dollar figure was checked against the raw source file directly. Ten structural issues, eight quantified data gaps, and two still-open cross-dataset questions are documented here. Individual field-level cleaning decisions are documented separately in this dataset's cleaning script; this document focuses on what the source data itself contains.

---

## Part 1: Structural Findings

These are not missing values. They reflect how the underlying system is built, and what it does and does not enforce.

**1. Published totals count returned money as if it were new money raised.** Verified against the live public portal: every returned contribution is added to a candidate's total rather than netted out. This is a limitation specific to how this dataset is modeled, flat, undifferentiated transaction rows with no relationship between an original contribution and its return. The newer live dataset (2023–present) models returns as child records tied explicitly to their parent transaction instead (see the API documentation for that dataset), so this issue is specific to this data model, not present system-wide.

**2. A whole transaction category cannot be classified.** "Credit Card Item" ($404,485.19 across 968 rows) sits ambiguously between a bank fee, an interest charge, personal card use by the candidate, and a real third-party donation. There is no way to tell which from the data, and the Secretary of State's office could not offer a definitive answer when asked directly. This category does not appear in either the archive (2000–2018) or live (2023–present) datasets, it's unique to this system's reporting window, and will need its own explicit handling decision when this dataset is normalized into the unified data model.

**3. Incomplete filings are sometimes re-filed later, and both versions are counted.** 15,114 rows carry a status of "incomplete." Only 229 have a confirmed exact duplicate filed later as complete. The portal counts every incomplete row toward public totals regardless, so an unknown share of this dataset's dollar figures are inflated by filings later superseded, with no way to identify which from the data alone.

**4. A substantial set of real transactions sits permanently unconfirmed.** 13,796 rows ($1,003,556.25) show a status of "incomplete" on every field the system uses to track filing completion. These are not blank rows, they contain real donor names, dates, and dollar amounts, and the portal counts them as real money regardless. *(See Still Open, below, this connects to Issue 2.)*

**5. Campaign committees are never required to formally close, so old accounts keep generating activity years after the person left office.** Three unrelated cases: a state senator (Dean Cameron, out of office since 2015), a state controller (J.D. Williams, out of office since 2002), and a sitting member of Congress (Russ Fulcher), each showing real filings or transactions years, in one case decades, after leaving the office tied to that account.

**6. Donor identity is not validated or deduplicated.** The same real organization appears under a dozen or more separate, unlinked internal records due to minor spelling or formatting differences. The Idaho Republican Party spans 11 different internal donor IDs; the Coeur d'Alene Tribe spans 18, both confirmed on the public search portal. A structural review of company-donor addresses found 631 distinct addresses where more than one spelling or abbreviation of a company name was registered, indicating this fragmentation is common rather than exceptional.

**7. A recipient identifier field is itself unreliable.** `to_office_id` functions as a catch-all for one internal code: ID 64 is shared across several unrelated offices and appears on all 299 rows where the office name itself is blank, effectively a default bucket rather than a meaningful identifier. ID 92 is a genuine error, shared between two legally distinct offices, State Representative Seat A and Seat B. This field is not used for reporting purposes, and no equivalent identifier exists across the other two datasets.

**8. Judicial election data is missing across more than half of Idaho's judicial districts.** Only judicial districts 1 (Kootenai), 2 (Nez Perce), and 3 (Canyon) appear anywhere in this dataset for District Judge or Magistrate Judge candidates, matching those counties correctly. No records exist for either office in judicial districts 4, 5, 6, or 7. This isn't a broader regional gap: every other office type in those same districts' counties is fully represented (10,713 rows across City Council, Mayor, County Commissioner, Sheriff, etc.), isolating this to judicial races specifically.

**9. Field-level values are not validated on intake.** Street addresses were accepted into the city field. City names were accepted into the state field. Zip codes were accepted into the city field. "Idaho" was accepted as a city name. A placeholder value, "Idaho State," was accepted into a field meant to hold one of Idaho's 44 real counties, for 71.3% of all qualifying donations. This pattern spans enough distinct fields and rows to indicate the intake system does not check submitted values against what a given field is meant to contain.

**10. Report type naming is inconsistent even within the same source.** The identical reporting period is labeled differently depending on which internal field is read: "2023 December-Annual" versus "December-Annual 2023 Report," "2023 November" versus "November 2023 Report." A report bearing the word "Annual" in its name was checked against the candidate's own signed filing and found to cover a single calendar month, not a year. A dataset's most basic organizing category, what report a transaction belongs to, is not reliably self-describing.

---

## Part 2: Quantified Data Gaps

Every figure below was checked against the raw source file directly, not estimated. Percentages are of all "qualifying" donations, meaning all rows excluding Unitemized and Credit Card Item transactions, the standard used throughout this project. "Resolved" describes issues addressed by this project's cleaning script against this dataset's own data, not a claim that no further data quality work remains possible.

- **$2,022,536.83 across 6,054 rows (2.51%)** were tied to a real candidate with no usable office recorded at all, blank, or the "Inactive" placeholder. **Resolved** through individual, sourced research into each candidate.
- **$4,417,680.42 across 12,603 rows (5.22%)** were tied to a candidate whose office was known but whose district, the specific county, city, school district, or legislative seat, was missing or reduced to a meaningless placeholder. **Resolved.**
- **$47,981,172.65 across 172,107 rows (71.26%)**, the single largest figure in this dataset, could not be tied to the recipient's actual registration county. The field recorded a placeholder ("Idaho State") instead, for both candidates and PACs.
- **$1,058,427.78 across 6,781 rows (2.81%)** had a missing or invalid contributor zip code. Resolved to 173 rows ($65,758.35) remaining, an unrecoverable gap.
- **$375,749.05 across 2,992 rows (1.24%)** had a missing or invalid contributor state. Resolved to 157 rows ($58,340.04) remaining.
- **$194,063.27 across 282 rows (0.12%)** showed unvalidated contributor city data across five distinct failure patterns (see Finding 9, above). Resolved for all five identified patterns. A separate, pre-existing gap of 200 rows ($71,256.19) with no city value at all remains, unrelated to these five patterns.
- **$353,635.03 across 2,738 rows (1.13%)** cannot be tied to a specific election year. This is a permanent, unrecoverable gap in the source data.
- **$51,516.05 across 118 rows (0.05%)** could not be tied to an actual donor identity at all. Resolved to 116 rows ($51,486.90) remaining.

---

## Part 3: Resolved

Findings that initially looked like open problems, were investigated further, and now have a confirmed answer.

**Russ Fulcher's committee activity was initially suspected to be federal-candidate contamination**, misfiled state data belonging to his U.S. House campaign rather than his prior Idaho state office. That theory was tested against his actual filed report (a pulled C-5 filing) and retracted: his activity is legitimate, election-timed state-committee activity, not federal money misfiled with the state. His records were reassigned to his last known Idaho state office rather than removed, and remain in this dataset as verified data.

---

## Part 4: Still Open

These findings are evidenced but not yet closed. They are logged separately from Parts 1 and 2 because there is not yet enough information to state their full scope or resolution as fact.

**Issue 1: This dataset does not match its own stated scope for 2023 Annual Reports, and at least one confirmed case proves real duplication across datasets.**

Per official documentation, this legacy dataset should only contain 2023 Annual Reports for county-level candidates not running in 2024, and PACs. Everyone else's 2023 Annual data is meant to live on the newer Vote Idaho Sunshine portal instead. It does not: this dataset contains 2023 Annual data for state legislators, statewide officeholders, and others outside its documented scope.

One case has been fully confirmed: State Senator Jim Woodward's certified 2023 Annual Report exists on the new portal, dollar-for-dollar matching transactions that also sit unresolved in this legacy dataset. This is a genuine risk of double-counting the same money if the two datasets are ever aggregated without reconciliation.

What remains unknown: how many other candidates and PACs follow this same pattern, and how much total dollar overlap exists. This connects to separate, ongoing findings on the live dataset side: reverse-engineering that system's API found at least one entire 2023 report missing for a given filer despite that filer having other reports present, and found that whether a 2023-era transaction is retrievable at all depends on a factor not yet fully identified (see the live dataset's API documentation, Outstanding Investigation). These may be two symptoms of the same underlying boundary problem between the two systems. **Next step:** cross-reference this dataset directly against the live dataset once its own pull is built.

**Issue 2: A broader, related pattern exists across the whole dataset, not just 2023 Annual filings.**

13,796 rows ($1,003,556.25) show a status of "incomplete" on every completion-tracking field the system provides, real donor names, dates, and dollar amounts, with no confirmation anywhere that the filing was ever finalized. Within this dataset, the duplication risk from this pattern is small and already quantified (229 of 15,114 incomplete rows have a confirmed later duplicate). The larger open question is whether the remaining stuck-incomplete rows are, like Jim Woodward's, accounted for correctly elsewhere, or represent real money never properly disclosed anywhere. **Next step:** cross-reference the full 13,796-row set against the new dataset once built, the same way Issue 1 will be.

---

## Methodology

Findings in this document were verified against the raw source file, the public portal, or an outside record. Where a candidate's office or district was missing or unreliable, resolution required individually researching that specific person against outside public records rather than applying a blanket rule; where a rule could safely apply broadly (e.g. backfilling a registration county from zip code), it was cross-checked against the dataset's own already-correct values first. The full methodology used across this project, including how findings on the live (2023–present) dataset's API were established, is documented in this project's root README and the live dataset's API reference.

---

*This document reflects the state of this dataset as of the most recent review. It will be revisited once the live dataset (2023–present) has been fully built and can be used to resolve the Still Open issues logged above.*
