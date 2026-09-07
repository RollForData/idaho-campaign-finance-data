# Contributions Page

**URL:** `https://sunshine.voteidaho.gov/public/cf/contribution`

Endpoints observed firing on a clean, unfiltered initial page load. See [candidates.md](candidates.md) for the Endpoint Type / Parameter Type conventions used throughout this documentation.

## Endpoints at a Glance

| Endpoint | Method | Type | Purpose |
|---|---|---|---|
| `/api/PublicTransactionDetails/GetContributionsDetails` | POST | Data Retrieval | Populates the Contributions results table |
| `/api/PublicLookup/GetReportNameLookup` | GET | Reference Data | Disclosure Report dropdown values |
| `/api/PublicLookup/GetElectionLookup` | GET | Reference Data | Master election list; function on this page unknown |
| `/api/PublicLookup/GetSourceEntityNameLookup` | GET | Reference Data | Function unconfirmed; unresolved capture anomaly |
| `/api/PublicLookup/GetPublicTransactionLookup` | POST | Reference Data | Loan/debt transaction codes; function on this page unclear |
| `/api/PublicLookup/GetPublicTransactionElectionYearLookup` | POST | Reference Data | Election Year filter values |
| `/api/Lookup/BindingDropDownValues` → `jurisidiction-data` | POST | Reference Data | Idaho counties list; not a visible filter here |
| `/api/Lookup/GetDropdownLookup/` → several variations | GET | Reference Data | See table below |
| `/api/Transaction/GetTransactionDetailsByGuid` | POST | Data Retrieval | Full detail for one transaction, on row click |
| `/api/PublicTransactionDetails/GetChildTransactionDetails` | POST | Data Retrieval | Child transactions (e.g. Returns) tied to a parent |

---

## `POST /api/PublicTransactionDetails/GetContributionsDetails`

**Type:** Data Retrieval Endpoint
**Parameter Type:** Mixed — `transactionTypeCode: "TCON"` is fixed by the page; the rest of the payload (filer name, source name, date/amount ranges, etc.) is user-controlled search criteria.

The primary endpoint powering the Contributions results table. Unlike Candidates/Committees, this endpoint does not specify a filer type (`CFRegistrationTypes`), so it returns data across Candidates, PACs, Central Committees, and non-registered filers alike.

**Request payload:**
```json
{
  "pageNumber": 1,
  "pageSize": 50,
  "sortBy": "TransactionDate",
  "sortType": "desc",
  "transactionTypeCode": "TCON",
  "filerName": null,
  "sourceName": null,
  "transactionAmountMax": null,
  "transactionAmountMin": null,
  "sourceTypeCode": null,
  "committeeType": null,
  "transactionSubTypeCode": null,
  "electionID": null,
  "reportName": null,
  "toDate": null,
  "fromDate": null,
  "byState": null,
  "electionType": null,
  "electionYear": null,
  "filerRegistrationGuid": null
}
```

**Sample response (one record):**
```json
{
  "guid": "f6e31779-5abd-493c-ba3d-a5c940a3a56f",
  "filerName": "Little, Brad",
  "contributorAddressLine1": "PO Box 4676",
  "contributorCity": "Ketchum",
  "contributorState": "ID",
  "contributorZipCode": "83340",
  "transactionAmount": 1000.0,
  "transactionDate": "07/31/2026",
  "filerTypeCode": "CAN",
  "transactionSourceTypeCode": "TIND",
  "transactionSource": "Person",
  "transactionTypeCode": "TCON",
  "transactionTypeDescription": "Contribution",
  "transactionSubTypeDesc": "Itemized",
  "transactionSubTypeCode": "ITMY",
  "electionTypeDescription": "General",
  "electionTypeCode": "GRNELEC",
  "sourceName": "Carroll, Christina",
  "hasChild": false,
  "transactionSourceFullName": "Christina Carroll",
  "transactionId": 418992,
  "sourceEntityId": 155120,
  "filerEntityId": 392,
  "transactionStatusCode": "TPEN",
  "electionYear": 2026,
  "childCount": 0,
  "rowNo": 1,
  "publicChildContributionResult": null,
  "totalRows": 0
}
```

**Notes:**
- Both `rowNo` and `totalRows` were confirmed static across every record in a multi-row response (`rowNo: 1` and `totalRows: 0` regardless of actual position or result count). Neither field reliably tracks position or total count for this endpoint — do not rely on them for pagination logic; compare array length against requested `pageSize` instead.
- Tested whether office/district filtering is silently supported despite no UI or response field for it: manually added an `officeId` parameter to the request. The request succeeded (no validation error, confirming the endpoint doesn't reject unrecognized fields outright), but had no effect on the results — same result set with or without the parameter. Confirms office/district filtering is not supported here, rather than just unconfirmed.
- Sample records show `transactionStatusCode: "TPEN"`, but this was only checked against a small sample of the full 200,000+ row result set. No visible filter or lookup call corresponds to this field. `TPEN` is suspected to mean "pending," but other status codes almost certainly exist and haven't been observed. Possibly relevant to a similar status concept in the legacy dataset, but unconfirmed — may be a related or entirely separate system.

---

## `GET /api/PublicLookup/GetReportNameLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter
**Payload:** `?key=null`

Retrieves Disclosure Report names for the Disclosure Report dropdown filter — a full list of annual and monthly reports spanning 2023–2030, plus special report types (First $500 Report, September Monthly Report).

---

## `GET /api/PublicLookup/GetElectionLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** None observed — no query parameters on the captured request.

Returns a master list of specific elections, not just years: near-term elections show resolved type/scope (e.g. `"2024 Primary Statewide"`), while far-future years show only a generic placeholder (e.g. `"2026 Election"`).

**Notes:** Confirmed not to be the source of the visible Election Year filter (that's `GetPublicTransactionElectionYearLookup`, below). Function on this page unknown. The resolved-vs-placeholder pattern suggests election type/scope isn't determined by the system until closer to the actual election date — worth remembering when reconciling data across election cycles.

---

## `GET /api/PublicLookup/GetSourceEntityNameLookup`

**Type:** Reference Data Endpoint (best guess — flag as unconfirmed given the anomaly below)
**Parameter Type:** None observed — no query string on the captured request.

**Notes:** Fires on page load with no visible parameters, returning a large response (~2,433 KB per the Network tab). The actual response body could not be captured — evicted from DevTools' cache before it could be inspected — and manual reproduction (matching URL, method, and headers exactly) consistently returns an empty array rather than the observed response. Headers, method, and credentials were all tested and ruled out as the cause. Purpose unconfirmed; likely a full contributor/entity name index given the size and endpoint name, possibly supporting a search or autocomplete feature elsewhere in the app. Not resolved further — would require inspecting the app's JS source directly.

---

## `POST /api/PublicLookup/GetPublicTransactionLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** None — confirmed empty payload, no parameters sent.

Returns loan and debt transaction classifications (`TDEBT`, `TDPAY`, `TLFRG`, `TLOAN`, `TLPAY`, `TODEBT`, `TOLOAN`).

**Notes:** Function on this page unclear — none of these classifications are visibly used, counted, or filterable anywhere on the Contributions page. Likely a leftover from a shared template intended for the Loans page.

---

## `POST /api/PublicLookup/GetPublicTransactionElectionYearLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter — the `key` value (`electionyear`) is fixed by the page, not user-set.
**Payload:** `{"key":"electionyear","isSelectReq":false}`

Retrieves election years 2024–2030, matching the visible Election Year dropdown on this page.

---

## `POST /api/Lookup/BindingDropDownValues` → `jurisidiction-data`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter
**Payload:** `{"name":"jurisidiction-data","isSelectReq":false}`

Returns Idaho's 44 counties plus a statewide entry. Not present as a visible filter on this page.

---

## `GET /api/Lookup/GetDropdownLookup/`

**Type:** Reference Data Endpoint

Multiple variations fire on this page. Several exist as **confirmed pairs**: a plain version (`?key=X&isSelectReq=false`) and a `lookup-masters` version (`?key=X&name=lookup-masters&isSelectReq=false`) that return identical data. Using request blocking to test causation, the `lookup-masters` version was confirmed in every tested case to be the one actually powering the visible dropdown; the plain version had no observed effect on page functionality when blocked. This blocking technique is a reliable way to confirm which of two identical-looking calls is functional versus inert, and should be checked for on any future page.

| Variation | Confirmed Function | Powers Visible Filter? |
|---|---|---|
| `?key=CFRegistrationTypes&isSelectReq=false` | No observed effect when blocked | No |
| `?key=CFRegistrationTypes&name=lookup-masters&isSelectReq=false` | Populates Filer Type dropdown | **Yes** |
| `?key=TransactionSourceType&isSelectReq=false` | No observed effect when blocked | No |
| `?key=TransactionSourceType&name=lookup-masters&isSelectReq=false` | Populates Contributor Type dropdown | **Yes** |
| `?key=StateType&name=lookup-masters&isSelectReq=false` | Defines "In State"/"Out of State" values | Unconfirmed |
| `?key=State&name=lookup-masters&isSelectReq=false` | Full US state list | Unconfirmed — see data quality note below |
| `?key=TransactionCategory&name=lookup-masters&isSelectReq=false` | Expense categories | Likely leftover (expenditures page) |
| `?key=TEXP&name=transaction-sub-type&isSelectReq=false` | 3 transaction sub-types | Partial — see note below |
| `?key=TCON&name=transaction-sub-type&isSelectReq=false` | 5 transaction sub-types | Partial — see note below |
| `?key=ElectionTypes&name=lookup-masters&isSelectReq=false` | Election Type dropdown | **Yes**, confirmed complete match |
| `?key=Purpose&isSelectReq=false` | Expense purpose codes | Likely leftover (expenditures page) |
| `?key=TIECOM&name=transaction-sub-type&isSelectReq=false` | Independent Expenditure / Electioneering Communication | Partial — see note below |

**Sample response — `CFRegistrationTypes` (either variation):**
```json
{"data": [
  {"value": "CAN", "name": "Candidate", "sortOrder": 1},
  {"value": "PAC", "name": "Political Committee", "sortOrder": 3},
  {"value": "CENC", "name": "Central Committee", "sortOrder": 3}
]}
```

**Sample response — `TransactionSourceType` (either variation):**
```json
{"data": [
  {"value": "TIND", "name": "Person"},
  {"value": "TBSN", "name": "Company"},
  {"value": "TCAN", "name": "Candidate"},
  {"value": "TPAC", "name": "Political Committee"},
  {"value": "TCENC", "name": "Central Committee"},
  {"value": "TSELF", "name": "Self"}
]}
```

**Notes:**
- **Data quality finding:** the `State` lookup's Mississippi entry returns `value: "MIS"`, `name: "MS"` — the only state where `value` and `name` don't match. Every other state entry is identical between the two fields. If this value is ever used as a request parameter, `"MIS"` rather than the standard `"MS"` would be sent.
- Contributor state values in actual contribution records already return as plain two-letter abbreviations, not coded values needing this lookup. Function of the `State` lookup on this page is unconfirmed.
- The `CFRegistrationTypes` (`lookup-masters`) response only returns 3 values (CAN/PAC/CENC), but the visible Filer Type dropdown shows a 4th option, "Non Registered Filer." Selecting it sends `committeeType: "ELECM"` in the `GetContributionsDetails` payload — a code not present in this lookup response at all. Confirmed as an independent value (appears alone or comma-appended with others, e.g. `"CENC,ELECM"`). Origin unclear: may be a real registration type not exposed through this lookup, or a synthetic code representing "no registration on file." Unresolved.
- `TEXP` and `TCON` variations both return values that appear in the visible Contribution Type dropdown, but neither alone accounts for the full dropdown. The dropdown includes "Electioneering Communication," which isn't in either — that value only appears in the separate `TIECOM` lookup. This suggests the Contribution Type dropdown is populated by combining results from multiple lookup calls, not a single source. Not fully confirmed.

---

## `POST /api/Transaction/GetTransactionDetailsByGuid`

**Type:** Data Retrieval Endpoint
**Parameter Type:** User-Controlled — the `guid` is tied to whichever row the user clicks; not fired on page load.
**Payload:** `{"guid": "3b758b7f-d43e-4ccd-9224-c418ed50897e"}`

Retrieves full detail for a single transaction, triggered by clicking a specific row in the results table. Includes fields not shown in the list view — notably the true transaction sub-type.

**Sample response (abbreviated):**
```json
{
  "data": {
    "transactionDetails": {
      "transactionId": 77743,
      "transactionTypeCode": "TCON",
      "transactionSubTypeCode": "ITR",
      "type": "Interest Earned",
      "transactionAmount": 1.38,
      "electionType": "Primary",
      "filingPeriod": "2024 February Monthly Report",
      "comments": "Beehive FCU",
      "isAmended": false
    },
    "guarantors": null,
    "childTransactionDetails": null
  }
}
```

**Notes:** Confirms transaction sub-type detail (e.g. "Interest Earned," via `transactionSubTypeCode: "ITR"`) exists in the underlying data even when the list view and public UI display only a generic label like "Unitemized Contribution." This resolves why "Interest" transactions weren't identifiable in bulk CSV downloads or the results table — the classification exists, but isn't surfaced or filterable at the list level, only visible by opening each transaction individually.

---

## `POST /api/PublicTransactionDetails/GetChildTransactionDetails`

**Type:** Data Retrieval Endpoint
**Parameter Type:** User-Controlled — `transactionID` is tied to whichever parent record the user expands.
**Payload:** `{"pageNumber":1,"pageSize":50,"transactionID":29913}`

Retrieves child transactions (e.g. Return Contributions) associated with a specific parent transaction. Triggered by expanding a record in the results table with `hasChild: true`.

**Sample response:**
```json
{
  "data": {
    "items": [
      {
        "transactionID": 208365,
        "transactionAmount": 50.00,
        "transactionTypeCode": "TRCON",
        "transactionTypeDesc": "Return Contribution",
        "transactionDate": "2024-03-26T00:00:00",
        "comments": "Campaign suspended",
        "totalRows": 2
      }
    ],
    "totalItems": 2
  }
}
```

**Notes:** Return Contributions (`TRCON`) are structurally excluded from the main `GetContributionsDetails` results, which requests only `transactionTypeCode: "TCON"`. This is why returns appear in bulk CSV downloads (which aggregate across transaction types) but never in the live results table or API response regardless of filters applied. **Confirmed but unresolved:** whether a return appears inline in the parent response's `publicChildContributionResult` field or requires this separate call is not consistently determined by any single factor tested so far — not the original transaction date, and not conclusively the return's own filing date either. See "Outstanding Investigation" below.

---

## Notable Page-Level Findings

- **This endpoint returns data across all filer types with no `CFRegistrationTypes` restriction**, unlike Candidates/Committees. Results include Candidates, PACs, Central Committees, and non-registered filers together.
- **The plain-vs-`lookup-masters` pattern, first confirmed on this page**, has now held across two separate tested pairs (CFRegistrationTypes, TransactionSourceType): the `lookup-masters` version consistently powers the real dropdown, the plain version is consistently inert. This is now a confirmed project-wide pattern, not a one-off.
- **`officeId` filtering was actively tested and ruled out**, not just assumed absent, by adding the parameter manually and confirming it has no effect on results, despite the request succeeding without error.

## Outstanding Investigation

- **What determines whether a Return Contribution is included inline vs. requires a separate API call (`GetChildTransactionDetails`)?** Confirmed to appear inline in some cases and to require the separate call in others; the determining factor is not yet confirmed. Every hypothesis tested so far (tied to the original transaction's date, tied to the return's own filing date) has been contradicted by at least one observed example. A complete data pull covering Return Contributions must account for both possibilities per record rather than assuming one consistent behavior.
- **Some 2023 filings appear to be entirely absent from this dataset for certain filers.** In one confirmed example, an entire monthly report (not just a return) that exists in the legacy dataset for a given committee could not be found anywhere in this system, despite that same committee having other reports present. Confirmed in a single case; not yet tested broadly enough to characterize scope. If broader, the live dataset cannot be treated as a complete record of 2023 activity on its own.
- **`GetSourceEntityNameLookup`'s actual response could not be captured**, and its purpose remains unconfirmed (see notes above).
- **How contributor identity resolution actually works is not yet understood.** The results table displays a "Contributor Name," but that value doesn't come from a field literally named that — it's derived from `sourceName` / `transactionSourceFullName`. This suggests some form of server-side entity resolution or lookup, possibly connected to the `sourceEntityId` field observed consistently across records. Not yet confirmed whether this represents a genuinely stable, deduplicated donor identity system, which would be a meaningful structural difference from the legacy and archive datasets' donor identity fragmentation (see the project's cross-dataset findings).
