# Live Dataset Data Quality Statement

**Dataset:** funding_live_2023_current
**Source:** Idaho Sunshine Portal (sunshine.voteidaho.gov), including its underlying internal API
**Scope, per official documentation:** 2023–present, statewide candidates and any candidate running for office in 2024, most PACs, and timed reports filed after January 1, 2024.
**Rows:** Not yet finalized; no production pull has been built.
**Last reviewed:** September 2026

## Summary

This document records findings about Idaho's current campaign finance system, gathered through two phases of work: an initial evaluation of the system's bulk CSV export, and a subsequent reverse-engineering of its underlying API once the CSV export was found insufficient. Findings from both phases are included here, since both concern the actual content and behavior of the underlying data, independent of which access method surfaced them.

The initial approach evaluated the state's bulk CSV export for this system, the same method used for the archive and legacy datasets. That export was ultimately not adopted as this dataset's pull method: unlike archive and legacy, whose exports bundle candidate, office, and transaction data together, this system's only bulk export covers contribution and loan transactions alone, with no office or district information at all. Since office and district are required for this project's data model, the CSV evaluation was set aside in favor of reverse-engineering the system's API directly, documented in full in this project's API reference. The findings below, several of which were surfaced during the CSV evaluation before that decision was made, remain accurate regardless of which access method is ultimately used, since they describe the underlying data and government reporting behavior, not an artifact of either pull method.

---

## Part 1: Structural Findings

**1. "Outstanding Loan" represents a balance restatement, not a new transaction.** This transaction type reflects a loan's remaining balance being carried forward and re-stated on a later report, not a new loan being issued. Treating every "Outstanding Loan" row as new money would overstate total loan activity; this needs explicit handling when defining what counts toward a candidate's total funds raised.

**2. The same underlying transaction can appear on more than one report.** A transaction filed on a monthly report can also appear, restated, on the year-end annual report covering that same period. Without deduplication logic, aggregating monthly and annual reports together would double-count real transactions.

**3. The bulk CSV export for this system does not include office or district information**, unlike the archive and legacy datasets' exports, which both include this data by default. This was confirmed to be a genuine limitation of the endpoint, not an omission from the CSV specifically: manually adding an `officeId` parameter to the underlying API request that CSV export theoretically relies on succeeded without error but had no effect on returned results, confirming the data-retrieval endpoint itself does not support this filtering, regardless of access method. Office and district data is only obtainable from a separate part of the system (the Candidates/Committees endpoints), requiring an explicit join that neither the CSV nor a naive API pull would produce automatically. See the API reference for full detail.

**4. The bulk export enforces a row limit that was reached during evaluation.** A single year's Contributions export hit a cap in the low hundreds of thousands of rows during testing. Any future reliance on bulk export for this system, in whole or in part, needs to account for this limit rather than assuming a single request returns a complete dataset.

**5. At least one entire monthly report, not just an individual transaction, is confirmed absent from this system for a given filer**, despite that same filer having other reports present and retrievable. This was confirmed for one committee's January 2023 report; the scope of this pattern across other filers and reports has not yet been characterized. See Still Open, below.

---

## Part 2: Quantified Data Gaps

No production pull has been built for this dataset yet, so this section does not yet contain the kind of dollar-figure, row-count analysis present in the legacy dataset's statement. This section will be populated once the API-based pull is built and run against real, complete data.

---

## Part 3: Resolved

Nothing in this dataset has reached full resolution yet, given no production pull exists. One methodological question was resolved during investigation, however: whether office/district data could be obtained through the CSV export by any available means was tested directly (manually adding an `officeId` filter parameter) and confirmed unsupported, rather than left as an assumption. See Structural Finding 3.

---

## Part 4: Still Open

**Issue 1: Whether returned contributions are netted out of displayed totals is unconfirmed for this system.** Returns are structurally nested as child records tied to their parent transaction (unlike the legacy dataset's flat, undifferentiated rows), but whether that nested amount is still added into the parent's displayed total, the same issue confirmed in the legacy dataset, has not been directly tested here. Not a priority to resolve, since this project calculates its own totals from raw transaction records rather than relying on the portal's displayed figures, but noted as an open question rather than assumed either way.

**Issue 2: What determines whether a Return Contribution is retrievable inline versus requiring a separate API call, or not retrievable at all?** Confirmed through direct testing: a return tied to a 2024-or-later filing is retrievable, either inline in the main results or via a secondary call. A return filed specifically on a 2023 report was not found retrievable through either method in every case tested so far. Neither the original transaction's date nor the return's own filing date alone fully explains this pattern; multiple hypotheses have been tested and contradicted by at least one observed example. Full detail and testing history is documented in the API reference's Outstanding Investigation section.

**Issue 3: How widespread is the missing-report pattern identified in Structural Finding 5?** Confirmed in one case; not yet tested broadly enough to know whether this affects many filers and reports from the 2023 transition period, or is isolated. If widespread, this dataset cannot be treated as a complete record of 2023 activity on its own, and the legacy dataset may need to remain authoritative for some portion of that year.

**Issue 4: Does this system use a genuinely stable, deduplicated donor identity system?** Every contribution record includes a `sourceEntityId` field that appears consistent across records from the same real donor, a potential structural improvement over the donor-identity fragmentation documented extensively in the legacy and archive datasets. This has not yet been confirmed at scale. If real, this would be a meaningful basis for reconciling donor identity across all three datasets, rather than solving deduplication independently in each one. Related to this: the results table's displayed "Contributor Name" is not stored under a field literally named that, it's derived from `sourceName`/`transactionSourceFullName`, suggesting some form of server-side entity resolution. See the API reference for full technical detail.

**Issue 5: This dataset's actual scope boundary against the legacy dataset is not fully mapped.** Per official documentation, some records that would otherwise seem to belong here (e.g. certain 2023 reports for candidates not running in 2024) instead live in the legacy dataset. The exact rule governing this split has not been fully characterized and appears related to, and possibly the same underlying issue as, Issue 2 and Issue 3 above. See the legacy dataset's data-integrity statement, Still Open Issue 1, for the corresponding finding from that side of the boundary.

---

## Methodology

Findings in this document come from two sources: direct evaluation of the system's bulk CSV export, and reverse-engineering of the system's underlying API through direct observation of browser network traffic, including targeted tests (such as manually modifying request parameters) used to confirm behavior rather than infer it from assumption. The full API reverse-engineering methodology, including the specific techniques used to test and confirm findings, is documented in this project's API reference.

---

*This document reflects an early-stage review of this dataset. It will be substantially expanded once the API-based production pull is built and run against complete data, at which point Part 2 in particular will be populated with real, quantified findings.*
