# Loans Page

**URL:** `https://sunshine.voteidaho.gov/public/cf/debt`

Endpoints observed firing on a clean, unfiltered initial page load. See [candidates.md](candidates.md) for the Endpoint Type / Parameter Type conventions used throughout this documentation.

## Endpoints at a Glance

| Endpoint | Method | Type | Purpose |
|---|---|---|---|
| `/api/PublicTransactionDetails/GetPublicLoansAndDebts` | POST | Data Retrieval | Populates the Loans results table |
| `/api/PublicLookup/GetReportNameLookup` | GET | Reference Data | Disclosure Report dropdown; same as Contributions page |
| `/api/PublicLookup/GetElectionLookup` | GET | Reference Data | Same as Contributions page; function unknown |
| `/api/PublicLookup/GetPublicTransactionElectionYearLookup` | POST | Reference Data | Election Year filter values |
| `/api/PublicLookup/GetPublicTransactionLookup` | POST | Reference Data | Transaction Type dropdown (partial match — see notes) |
| `/api/PublicLookup/GetOfficeByDistrictTypeQuery` | POST | Reference Data | Office Sought dropdown — **visible here, absent on Contributions** |
| `/api/PublicLookup/GetDistrictByOfficeQuery` | POST | Reference Data | District dropdown |
| `/api/PublicLookup/GetZoneByOfficeDistrictQuery` | POST | Reference Data | Zone dropdown |
| `/api/Lookup/BindingDropDownValues` → `district-type` | POST | Reference Data | District Type dropdown |
| `/api/Lookup/BindingDropDownValues` → `jurisidiction-data` | POST | Reference Data | Not a visible filter here |
| `/api/Lookup/GetDropdownLookup/` → several variations | GET | Reference Data | See table below — mostly leftovers from other pages |
| `/api/PublicTransactionDetails/GetChildTransactionDetails` | POST | Data Retrieval | Child transactions (loan payments, forgiveness) |

---

## `POST /api/PublicTransactionDetails/GetPublicLoansAndDebts`

**Type:** Data Retrieval Endpoint
**Parameter Type:** Mixed — system-defined and user-controlled fields combined.

The primary endpoint powering the Loans results table. Unlike `GetContributionsDetails` on the Contributions page, this endpoint does **not** hardcode a `transactionTypeCode`, confirmed to return multiple transaction types in a single unfiltered pull (`TLOAN` "Loan Received" and `TOLOAN` "Outstanding Loan" both observed).

**Request payload:**
```json
{
  "pageNumber": 1,
  "pageSize": 50,
  "filerName": null,
  "sourceName": null,
  "transactionAmount": 0,
  "outstandingBalanceAmountMax": null,
  "outstandingBalanceAmountMin": null,
  "transactionAmountMax": null,
  "transactionAmountMin": null,
  "toDate": null,
  "fromDate": null,
  "committeeType": null,
  "electionID": null,
  "sourceTypeCode": null,
  "byState": "",
  "transactionSubType": null,
  "transactionTypeCode": null,
  "reportName": null,
  "electionType": null,
  "electionYear": null,
  "districtTypeId": null,
  "officeSoughtId": null,
  "ZoneId": null,
  "district": null
}
```

**Sample response (one record):**
```json
{
  "transactionId": 419033,
  "filerName": "Okuniewicz, Douglas Martin",
  "transactionAmount": 29.72,
  "transactionDate": "2026-07-31T00:00:00",
  "transactionSourceTypeCode": "TSELF",
  "filerTypeCode": "CAN",
  "sourceName": "Okuniewicz, Douglas Martin",
  "transactionSource": "Self",
  "reportName": "2026 July Monthly Report",
  "transactionTypeCode": "TLOAN",
  "transactionTypeDesc": "Loan Received",
  "childCount": 0,
  "balanceAmount": 29.72,
  "electionYear": 2026,
  "officeId": 33,
  "cityDistrictId": 534,
  "districtTypeId": 11,
  "hasChild": false,
  "loansAndDebtsChildResults": null
}
```

**Notes:** Loan Forgiven and Loan Payment do not appear as separate parent-level rows — they're represented as child records nested inline in `loansAndDebtsChildResults` when a parent loan has `hasChild: true` (see `GetChildTransactionDetails` below). Not in this project's pull scope (only Loan Received transactions are tracked, consistent with tracking contribution money rather than expenses/repayments), but documented here for completeness.

---

## `GET /api/PublicLookup/GetReportNameLookup`, `GET /api/PublicLookup/GetElectionLookup`, `POST /api/PublicLookup/GetPublicTransactionElectionYearLookup`

Identical endpoints and responses to the Contributions page — see [contributions.md](contributions.md) for full detail. All three fire and function the same way here.

---

## `POST /api/PublicLookup/GetPublicTransactionLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** None — confirmed empty payload.

Returns loan and debt transaction classifications (`TDEBT`, `TDPAY`, `TLFRG`, `TLOAN`, `TLPAY`, `TODEBT`, `TOLOAN`).

**Notes:** Confirmed via request blocking to power the visible Transaction Type dropdown on this page — but the dropdown only shows 5 of the 7 values returned (All, Debt, Loan Received, Outstanding Debt, Outstanding Loan). The 3 missing values — Debt Payment, Loan Forgiven, Loan Payment — correspond exactly to the transaction types observed only as nested child records, never as top-level parent rows. Likely intentional: filtering the main table by a child-only type wouldn't return meaningful top-level results.

---

## `POST /api/PublicLookup/GetOfficeByDistrictTypeQuery`

**Type:** Reference Data Endpoint
**Parameter Type:** None — confirmed empty payload.
**Payload:** `{"districtTypeId":""}`

Returns the full list of 38 offices (same set as `GetOfficeSoughtLookup` on Candidates).

**Notes:** Confirmed via request blocking to power the visible Office Sought dropdown on this page. This is a notable asymmetry worth flagging: Loans can be filtered by office sought, but Contributions cannot — despite office/district being an equally reasonable, arguably more common, use case for filtering contribution data. Neither the Contributions UI nor its bulk CSV export exposes office/district at all (see [contributions.md](contributions.md)).

---

## `POST /api/PublicLookup/GetDistrictByOfficeQuery`

**Type:** Reference Data Endpoint
**Parameter Type:** None — confirmed empty payload.
**Payload:** `{"officeId":""}`

Returns the full district list. Response too large to include here — see the project's District Type Values reference for the complete list.

**Notes:** Confirmed via request blocking to power the visible District dropdown on this page.

---

## `POST /api/PublicLookup/GetZoneByOfficeDistrictQuery`

**Type:** Reference Data Endpoint
**Parameter Type:** None — confirmed empty payload.
**Payload:** `{"officeId":null,"cityDistrictId":null}`

Returns zone values scoped to an office/district combination.

**Notes:** Confirmed via request blocking to power the visible Zone dropdown on this page.

---

## `POST /api/Lookup/BindingDropDownValues`

### Variation: `{ "name": "district-type", "isSelectReq": false }`

Identical response to the Candidates page. Confirmed via request blocking to power the visible District Type dropdown here.

### Variation: `{ "name": "jurisidiction-data", "isSelectReq": false }`

Identical response to the Candidates page. Not a visible filter on this page.

---

## `GET /api/Lookup/GetDropdownLookup/`

Several plain/lookup-masters pairs and standalone variations fire on this page, most confirmed as leftovers from the Contributions page's shared template rather than functional here.

| Variation | Confirmed Function on This Page |
|---|---|
| `?key=CFRegistrationTypes&isSelectReq=false` | No observed effect when blocked |
| `?key=CFRegistrationTypes&name=lookup-masters&isSelectReq=false` | Populates Filer Type dropdown |
| `?key=TransactionSourceType&isSelectReq=false` | No observed effect when blocked, despite a similarly-named "Filer Type" dropdown existing |
| `?key=TransactionSourceType&name=lookup-masters&isSelectReq=false` | Populates the visible **Lender Type** dropdown (returns the same 6 values as "Contributor Type" elsewhere, but this page's terminology is Lender/Filer, not Contributor) |
| `?key=StateType&name=lookup-masters&isSelectReq=false` | No filtering UI exists for this on Loans; likely leftover from Contributions |
| `?key=State&name=lookup-masters&isSelectReq=false` | No filtering ability by state exists on this page; likely leftover |
| `?key=TransactionCategory&name=lookup-masters&isSelectReq=false` | Returns expense categories, including "Returned Contributions" and "Repayment of Loans" as values — plausible alternate path to return/repayment data, but not used by this page's UI |
| `?key=TEXP&name=transaction-sub-type&isSelectReq=false` | Returns donation-type values (Itemized, Unitemized, In-Kind); none apply to loans, likely leftover |
| `?key=TCON&name=transaction-sub-type&isSelectReq=false` | Same as above; not applicable to this page |
| `?key=ElectionTypes&name=lookup-masters&isSelectReq=false` | Powers the visible Election Type dropdown |
| `?key=Purpose&isSelectReq=false` | Returns expenditure purpose codes; not applicable to loans, likely leftover from an expenditures page |
| `?key=TIECOM&name=transaction-sub-type&isSelectReq=false` | Independent Expenditure / Electioneering Communication values; not applicable here |

**Notes:** On this page, the terminology shift matters — what's called "Contributor Type" on Contributions is "Lender Type" on Loans, even though both pull from the same underlying `TransactionSourceType` lookup values (Person, Company, Candidate, Political Committee, Central Committee, Self). Confirmed via request blocking that the `lookup-masters` variant, not the plain variant, powers this dropdown, consistent with the pattern established on Contributions.

---

## `POST /api/PublicTransactionDetails/GetChildTransactionDetails`

**Type:** Data Retrieval Endpoint
**Parameter Type:** User-Controlled — `transactionID` tied to whichever parent record the user expands.
**Payload:** `{"pageNumber":1,"pageSize":50,"transactionID":98289}`

Same shared endpoint documented on the Contributions page (not Loans-specific).

**Sample response:**
```json
{
  "data": {
    "items": [
      {
        "transactionID": 98305,
        "transactionAmount": 600.00,
        "transactionTypeCode": "TLPAY",
        "transactionTypeDesc": "Loan Payment",
        "transactionDate": "2023-01-01T00:00:00",
        "reportName": "2023 Annual Report",
        "totalRows": 1
      }
    ],
    "totalItems": 1
  }
}
```

**Notes:** Tested against a record with `childCount: 2` (Knight, Creighton): this call returned both children in full ($64.37 and $71.68), confirmed identical to what was already present inline in the parent `GetPublicLoansAndDebts` response's `loansAndDebtsChildResults` field. The inline data is complete, not a partial preview — a pull script for Loans can rely on `loansAndDebtsChildResults` alone and does not need to call this endpoint separately, unlike Contributions, where this endpoint is the only way to retrieve child (Return Contribution) data. Note: both children shared the same `transactionID` as their parent, rather than having distinct IDs of their own — confirmed different from Contributions, where a child's `transactionID` was distinct from its parent's. `guid` is the only reliably unique identifier at the child level on Loans.

---

## Notable Page-Level Findings

- **Loans can be filtered by office sought and district; Contributions cannot.** Both the UI and the underlying API support this on Loans, while Contributions offers neither the filter nor the underlying field. Given office/district filtering is arguably a more common use case for contributions than for loans, this asymmetry is worth flagging as a real design choice by the state, not an oversight — whether intentional or not is unconfirmed.
- **The same underlying entity-type terminology (Person, Company, Candidate, Political Committee, Central Committee, Self) is labeled differently across pages** — "Contributor Type" on Contributions, "Lender Type" here — despite sharing the identical `TransactionSourceType` lookup values.
- **This page confirms, via a second independent test, that Loans' child-record data is genuinely complete inline**, unlike Contributions. This distinction is central to how a future pull script must be built differently for each page (see [contributions.md](contributions.md) Outstanding Investigation for the still-open question of why).

## Outstanding Investigation

- **Does Loans' child-data behavior hold up under the same conditions that caused inconsistency on Contributions?** All tested Loans child records (payments, forgiveness) returned inline with no separate call needed, but none of those tests involved a record filed on a 2023 report — the specific condition tied to inconsistent behavior on the Contributions page. It's not yet known whether Loans is structurally different from Contributions, or whether it's simply governed by the same unresolved factor and hasn't been tested against it. Until tested directly, a pull script can't safely assume Loans' child data is always inline — treating this as confirmed 100% coverage could quietly drop data the same way it would on Contributions.
