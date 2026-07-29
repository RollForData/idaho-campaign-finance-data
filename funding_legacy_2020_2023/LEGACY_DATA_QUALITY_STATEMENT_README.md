# Legacy Dataset Data Quality Statement

**Dataset:** funding_legacy_2020_2023
**Source:** Idaho Secretary of State, Legacy Campaign Finance Site (sunshine.sos.idaho.gov)
**Scope, per the government's own documentation:** Timed Reports (2020 – 12/20/2023), 2020–2022 Annual Reports, and 2023 Annual Reports for county-level candidates not running in 2024, plus PACs.
**Rows:** 250,688
**Pulled:** 7.8.2026

This document exists to state, plainly and with evidence, what is wrong with this dataset as delivered by the government, independent of any cleaning performed on it. It is not a description of the cleaning process, individual field-level decisions are documented separately. This is a record of what a transparency law that exists to produce accountable, usable public records has actually produced.

---

## Part 1: Structural Findings

These are not missing values. They are evidence of how the underlying system is built, and what it does and does not enforce.

**1. The government's own published totals count returned money as if it were new money raised.** Confirmed directly against the live public portal, not inferred: every returned contribution is added to a candidate's total rather than netted out. Every "total raised" figure published by the state is inflated by the value of every refund ever issued.

**2. A whole transaction category cannot be classified, and the state agency itself could not define it when asked.** "Credit Card Item" ($404,485.19 across 968 rows) sits ambiguously between a bank fee, an interest charge, personal card use by the candidate, and a real third-party donation. There is no way to tell which from the data, and Idaho's own SOS office could not give a definitive answer when the question was raised directly.

**3. Incomplete filings are sometimes re-filed later and the portal counts both.** 15,114 rows carry a status of "incomplete." Only 229 have a confirmed exact duplicate filed later as complete. The government's own portal counts every incomplete row toward public totals regardless, so an unknown share of this dataset's dollar figures are inflated by filings that were later superseded, and there is no way to identify which ones from the data alone.

**4. Real transaction data sits permanently unconfirmed, on both tracking fields the system provides, with nothing forcing resolution.** 13,796 rows across the dataset ($1,003,556.25) show a status of "incomplete" on every field the system uses to track filing completion. These are not blank rows, they contain real donor names, dates, and dollar amounts. The government's portal counts them as real money regardless. *(See Unresolved Issues, below, this connects directly to Finding 9.)*

**5. Campaign committees are never required to formally close, so old accounts keep generating real financial activity years after the person left office.** Confirmed independently in three unrelated cases: a state senator (Dean Cameron, out of office since 2015), a state controller (J.D. Williams, out of office since 2002), and a sitting member of Congress (Russ Fulcher), each showing real filings or transactions years, in one case decades, after leaving the office tied to that account.

**6. The government's own donor-identity system performs no validation or deduplication.** The same real organization appears under a dozen or more separate, unlinked internal records because of nothing more than minor spelling or formatting differences. The Idaho Republican Party alone spans 11 different internal donor IDs; the Coeur d'Alene Tribe spans 18. This is independently confirmed on the government's own public search portal, not an artifact of this project's data pull. A structural review of company-donor addresses found 631 distinct addresses where more than one spelling or abbreviation of a company name was registered, evidence this fragmentation is common, not exceptional.

**7. A recipient identifier field the government provides is itself unreliable.** `to_office_id` functions as a catch-all for one internal code (shared across several unrelated offices) and is a genuine, contradictory error for another (shared between two legally distinct offices, State Representative Seat A and Seat B).

**8. An entire category of judicial office has zero records for more than half of Idaho's judicial districts.** No campaign finance records exist for District Judge or Magistrate Judge candidates in judicial districts 4, 5, 6, or 7. Every other office type in those same counties is fully represented (10,713 rows across City Council, Mayor, County Commissioner, Sheriff, etc. for those counties alone), isolating this as a gap specific to judicial races, not a broader regional absence of data.

**9. The intake system does not validate that a value belongs in the field it was entered into.** Street addresses were accepted into the city field. City names were accepted into the state field. Zip codes were accepted into the city field. The state name "Idaho" was accepted as a city. A placeholder value, "Idaho State," was accepted into a field meant to hold one of Idaho's 44 real counties, for 71.3% of all qualifying donations. This is not a handful of typos. It is direct evidence the system will accept any text into any field, with no check against what that field is supposed to contain.

**10. The government's own reporting system does not consistently name its own report types.** The identical reporting period is labeled differently depending on which internal field is read: "2023 December-Annual" versus "December-Annual 2023 Report," "2023 November" versus "November 2023 Report." A report bearing the word "Annual" in its name was confirmed, against the candidate's own signed filing, to cover a single calendar month, not a year. A dataset's most basic organizing category, what report a transaction belongs to, is not reliably self-describing even within the government's own records.

---

## Part 2: Quantified Data Gaps

Every figure below was verified directly against the raw source file, not estimated. Percentages are of all "qualifying" donations, meaning all rows excluding Unitemized and Credit Card Item transactions, the same standard used throughout this project.

- **$2,022,536.83 across 6,054 rows (2.51%)** were tied to a real candidate with no usable office recorded at all, blank, or the government's own "Inactive" placeholder. **Fully resolved** through individual, sourced research into each candidate.
- **$4,417,680.42 across 12,603 rows (5.22%)** were tied to a candidate whose office was known but whose district, the specific county, city, school district, or legislative seat, was missing or reduced to a meaningless placeholder. **Fully resolved.**
- **$47,981,172.65 across 172,107 rows (71.26%)**, the single largest figure in this dataset, could not be tied to the recipient's actual registration county. The government's own field recorded a placeholder ("Idaho State") instead, for both candidates and PACs.
- **$1,058,427.78 across 6,781 rows (2.81%)** had a missing or invalid contributor zip code. Resolved to 173 rows ($65,758.35) remaining, an unrecoverable gap.
- **$375,749.05 across 2,992 rows (1.24%)** had a missing or invalid contributor state. Resolved to 157 rows ($58,340.04) remaining.
- **$194,063.27 across 282 rows (0.12%)** showed unvalidated contributor city data across five distinct failure patterns (see Finding 9, above). Resolved for all five identified patterns. A separate, pre-existing gap of 200 rows ($71,256.19) with no city value at all remains, unrelated to these five patterns.
- **$353,635.03 across 2,738 rows (1.13%)** cannot be tied to a specific election year. This is a permanent, unrecoverable government reporting gap.
- **$51,516.05 across 118 rows (0.05%)** could not be tied to an actual donor identity at all, despite legal disclosure requirements. Resolved to 116 rows ($51,486.90) remaining.

---

## Part 3: Unresolved Issues

These findings are real, evidenced, and not yet closed. They are logged here rather than folded into Parts 1 or 2 because we do not yet have enough information to state their full scope or resolution as fact. Work on them will resume once the newer (2023–current) dataset has been built and can be directly cross-referenced.

**Issue 1: This dataset does not match the government's own stated scope for 2023 Annual Reports, and at least one confirmed case proves real duplication across datasets.**

Per the government's own documentation, this legacy dataset should only contain 2023 Annual Reports for county-level candidates not running in 2024, and PACs. Everyone else's 2023 Annual data is supposed to live on the newer Vote Idaho Sunshine portal instead. It does not, this dataset contains 2023 Annual data for state legislators, statewide officeholders, and others outside its documented scope.

One case has been fully proven: State Senator Jim Woodward's real, certified 2023 Annual Report exists on the new portal, dollar-for-dollar matching transactions that sit unresolved in this legacy dataset. This confirms a genuine risk of double-counting the same real money if this dataset and the new one are ever aggregated together without reconciliation.

What remains unknown: how many other candidates and PACs follow this same pattern, and how much total dollar overlap exists. **Next step:** cross-reference against the new dataset directly once it is built.

**Issue 2: A broader, related pattern exists across the whole dataset, not just 2023 Annual filings.**

13,796 rows ($1,003,556.25) show a status of "incomplete" on every completion-tracking field the system provides, real donor names, dates, and dollar amounts, with no confirmation anywhere that the filing was ever finalized. Within this dataset alone, the duplication risk from this pattern is small and already quantified (229 of 15,114 incomplete rows have a confirmed later duplicate). The larger, unresolved risk is whether the remaining stuck-incomplete rows are, like Jim Woodward's, actually accounted for correctly elsewhere, or whether they represent real money that was never properly disclosed anywhere at all. **Next step:** cross-reference the full 13,796-row set against the new dataset once built, the same way Issue 1 will be.

---

*This document reflects the state of this dataset as of the most recent cleaning pass. It will be revisited and updated once the newer campaign finance dataset (2023–current) has been built and can be used to resolve the issues logged above.*