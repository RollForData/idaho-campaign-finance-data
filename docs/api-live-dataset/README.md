# Idaho Sunshine Portal API — Reverse-Engineered Documentation

Idaho's campaign finance disclosure portal ([sunshine.voteidaho.gov](https://sunshine.voteidaho.gov)) publishes bulk CSV downloads, but the underlying web application runs on a REST API with no public documentation. This project reconstructs that API by directly observing live network traffic, in order to acquire and normalize the underlying data more effectively than the alternatives:

- **The bulk exports are inconsistent** across years, field sets and even transaction categories vary, and reconciling them has historically required significant contextual cleanup.
- **The site is a dynamic, JavaScript-driven application** — the data isn't in the page source, it's fetched at runtime from a separate API host (`api-sunshine.voteidaho.gov`).
- **A browser-driven scraper could technically render the page and extract the data**, but at the cost of reliability, processing overhead, and speed compared to acquiring the same data directly from the API the page itself is built on.

## Project Context

This is part of a larger project building an independent, normalized database of Idaho campaign finance data across three structurally different state-published sources (a 2000–2019 archive, a 2020–2023 legacy system, and this current 2023–present system). This API represents the state's current and most granular data model, and understanding its actual structure, not just its bulk export, was a prerequisite for correctly reconciling the older datasets against it.

## Methodology

The state provides no API schema, so the process here was direct observation and testing of a live application, rather than reading documentation:

1. Loaded each page of the portal with the browser's network inspector open, on a clean, unfiltered initial load, and recorded every request made to the underlying API, excluding unrelated third-party traffic.
2. Captured, per request: endpoint URL, HTTP method, request payload, response schema, and any observable connection to a visible page element (a filter, dropdown, or table).
3. Where a request's function was ambiguous, resolved it with a targeted test rather than an inference from naming or response shape alone:
   - **Selective request blocking** — disabling one specific request and reloading, to directly confirm or rule out whether it's what actually powers a given UI element.
   - **Controlled field comparison** — querying the same endpoint under different parameters (e.g. the same entity-lookup endpoint for a Candidate vs. a Committee record) to isolate which fields are shared, entity-specific, or context-dependent.
   - **Targeted interaction traces** — triggering a specific filter or expanding a specific record to observe what new request fires, rather than assuming an initial page load captures the full behavior.
4. Cross-referenced response field names, response headers, and the plain-language values behind each visible page filter against what's already known about the older (2000–2019 and 2020–2023) datasets, to identify where this system's definitions of the same underlying data, contribution types, entity classifications, filing categories, align with, or diverge from, how those values were structured in the legacy systems. This step was necessary because the goal isn't just to document this API in isolation, it's to determine how its data model should inform a single normalized schema across all three datasets.

Throughout, the rule was to separate confirmed, tested behavior from inference: something is documented as fact only once directly observed or verified with a targeted test; anything else is labeled as a hypothesis or logged as an open question (see Outstanding Investigation). This mattered in practice: several endpoint names and apparent patterns in this API turned out to be misleading once tested directly (see Notable Findings).

## Scope & Status

This documentation covers the pages relevant to modeling contribution, loan, and return-contribution data: **Candidates, Committees, Contributions, and Loans.**

**Expenditures, Independent Expenditures, and Filings & Reports** were deliberately excluded. These fall outside the transaction types this project tracks (funds and debt coming into a campaign, not expenditures or disbursements going out), and initial review did not surface any new endpoint patterns, entity relationships, or data structures beyond what's already documented here, several lookup endpoints intended for those pages already surface, unused, on the pages that are documented. They may be added in a future pass if project scope expands.

## Notable Findings

Findings that go beyond simple endpoint cataloging, several of which directly affect how a data pull against this API needs to be built:

- **Not all related ("child") data is retrieved the same way, even within a single page.** Return Contributions on the Contributions page have been observed both inline in the initial response and requiring a separate follow-up call, depending on circumstances not yet identified (see Outstanding Investigation). Loans' related records (payments, forgiveness) have only tested as inline so far, but haven't been tested against the specific condition that caused inconsistency on Contributions, so it isn't yet confirmed whether Loans is genuinely more consistent or simply untested against that condition. Either way, a pull script cannot assume any one page's child-data behavior is uniform without direct testing.

- **A visible entity-type filter (`CFRegistrationTypes`) does not account for all filterable entity types.** The portal's own registration-type lookup returns three values (Candidate, Political Committee, Central Committee), but a fourth, undocumented option ("Non Registered Filer") is available in the Contributions filter UI. Selecting it sends an entity code (`ELECM`) that does not appear anywhere in the standard lookup response, indicating the UI's available filter options are not fully derivable from the API's own reference/lookup endpoints alone.

- **Candidates and Committees are served by two separate, near-identical endpoints, each still carrying a redundant filter field.** `GetCandidateDetails` and `GetCommitteeDetails` are distinct URLs, not one shared endpoint, but both send a `filerTypeCode` value (`CAN` or `COM`) even though the entity type is already implied by which endpoint is called. This kind of redundant, page-specific duplication rather than one shared endpoint with a type parameter is worth checking for elsewhere in this API before assuming either pattern applies by default.

- **The state's own reference data contains a data quality error.** The State abbreviation lookup returns Mississippi with a `value` of `MIS` and a `name` of `MS`, the only entry in that table where the two fields don't match. Every other state's `value` and `name` are identical.

- **Not every request that fires on page load is meaningful to that page.** Several reference/lookup calls consistently fire across multiple pages regardless of whether that page uses them, confirmed via request blocking to have no effect on the pages where they're inert. This appears to be a shared front-end template loading a fixed batch of lookups rather than each page requesting only what it needs, an important distinction when deciding which calls a pull script actually needs to replicate versus which are page-load noise.

- **Contribution records in the new system don't include office or district information, unlike the legacy dataset, and this was confirmed rather than assumed.** In the legacy system's exports, a donation record includes contextual candidate information like the office and district it relates to. In this API, that link doesn't exist at the contribution level: `GetContributionsDetails`'s response schema has no office or district fields, and there's no visible UI filter for it. To rule out an undocumented server-side capability, an `officeId` parameter was manually added to the request payload; the request succeeded (no validation error) but had no effect on the results returned, confirming the endpoint doesn't support filtering by office even though it silently accepts the field. Office and district data is only retrievable from a separate endpoint (`GetCandidateDetails`). Reconstructing that relationship, joining contribution records back to a candidate's office and district, requires explicitly joining these two endpoints' data rather than relying on either one alone.

## Outstanding Investigation

Areas where research surfaced a real, confirmed observation, but the underlying cause hasn't been determined yet. These are documented deliberately, as a record of what's been found and what's still open, rather than left out or forced into a premature conclusion.

- **What determines whether a Return Contribution is included inline vs. requires a separate API call?** Return Contributions (a child record type on the Contributions page) have been confirmed to appear inline in the main data-retrieval response in some cases, and to require a separate follow-up call (`GetChildTransactionDetails`) in others. The determining factor is not yet confirmed; initial hypotheses (tied to the original transaction's date, or to the return's filing date) have each been contradicted by at least one observed example. **Why it matters:** a complete data pull covering Return Contributions must account for both possibilities per record rather than assuming one consistent behavior.

- **Does Loans' child-data behavior hold up under the same conditions that caused inconsistency on Contributions?** All Loans-related child records (payments, forgiveness) tested so far returned inline with no separate call needed, but none of those tests involved a record filed on a 2023 report, the specific condition tied to inconsistent behavior on Contributions. It's not yet known whether Loans is structurally different from Contributions, or whether it's simply governed by the same unresolved factor and hasn't been tested against it. **Why it matters:** until this is tested directly, a pull script can't safely assume Loans' child data is always inline; treating this as confirmed 100% coverage could quietly drop data the same way it would have on Contributions.

- **Some 2023 filings appear to be entirely absent from the new dataset for certain filers.** In one confirmed example, an entire monthly report (not just a specific transaction or return) that exists in the legacy dataset for a given committee could not be found anywhere in the new dataset, despite that same committee having other reports present and retrievable. This has only been confirmed in a single case so far and hasn't been tested broadly enough to characterize which filers or reports are affected, or why. **Why it matters:** if this is a broader pattern, the new dataset can't be treated as a complete record of 2023 activity on its own, and the legacy dataset may need to remain the authoritative source for some portion of 2023, not just as a historical backup.

- **`GetSourceEntityNameLookup`** fires on Contributions page load with no query parameters and a large response (~2.4 MB observed), but its actual contents couldn't be captured (evicted from the browser's response cache before inspection), and a manual reproduction of the same request consistently returns an empty result. The cause of this discrepancy wasn't resolved, request headers, method, and credentials were all tested and ruled out as explanations. Its function remains unconfirmed.

## Contents

- [Candidates](endpoints/candidates.md)
- [Committees](endpoints/committees.md)
- [Contributions](endpoints/contributions.md)
- [Loans](endpoints/loans.md)

## Disclaimer

This is not official documentation and is not affiliated with the Idaho Secretary of State's office. It reflects observed behavior of a public-facing web application as of the dates the underlying research was conducted, and may not remain accurate if the portal changes.
