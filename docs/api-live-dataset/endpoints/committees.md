# Committees Page

**URL:** `https://sunshine.voteidaho.gov/public/cf/publiccommitte`

Endpoints observed firing on a clean, unfiltered initial page load. See [candidates.md](candidates.md) for the Endpoint Type / Parameter Type conventions used throughout this documentation.

This page shares its core template with the Candidates page — most endpoints below are identical in URL and response to their Candidates-page counterparts, with confirmed differences in payload and which filters are actually visible.

## Endpoints at a Glance

| Endpoint | Method | Type | Purpose |
|---|---|---|---|
| `/api/PublicFilerDetails/GetCommitteeDetails` | POST | Data Retrieval | Populates the Committees results table |
| `/api/PublicLookup/GetElectionYearLookup` | GET | Reference Data | Same as Candidates page; dropdown hidden here |
| `/api/PublicLookup/GetOfficeSoughtLookup` | GET | Reference Data | Same as Candidates page; dropdown hidden here |
| `/api/PublicLookup/GetPublicFilingYear` | POST | Reference Data | Report filing year — confirmed visible filter on this page |
| `/api/Lookup/GetDropdownLookup/` → `CFRegistrationTypes` | GET | Reference Data | Registration type codes; hidden system parameter |
| `/api/Lookup/GetDropdownLookup/` → `Party` | GET | Reference Data | Party filter — confirmed visible on this page |
| `/api/Lookup/GetDropdownLookup/` → `Filer Status` | GET | Reference Data | Account Status filter — confirmed visible on this page |
| `/api/Lookup/BindingDropDownValues` → `jurisidiction-data` | POST | Reference Data | Jurisdiction filter — confirmed visible on this page |
| `/api/Lookup/BindingDropDownValues` → `district-type` | POST | Reference Data | District Type dropdown; leftover, hidden here |
| `/api/PublicLookup/GetDistrictByDistrictTypeQuery` | POST | Dependent Lookup | Leftover call; no district filters exist on this page |

---

## `POST /api/PublicFilerDetails/GetCommitteeDetails`

**Type:** Data Retrieval Endpoint
**Parameter Type:** Mixed — `filerTypeCode: "COM"` is fixed by the page; the remaining fields (search name, party, district, office, jurisdiction, fundraising ranges, pagination) are user-controlled filter and search criteria.

This is a separate endpoint from `GetCandidateDetails` on the Candidates page — a distinct URL, not the same endpoint reused. It shares a nearly identical request payload shape and response schema with `GetCandidateDetails`, and both endpoints send a `filerTypeCode` value (`COM` here, `CAN` on Candidates) even though the entity type is already implied by which URL is called. Worth noting as a pattern: the API appears to duplicate this endpoint per entity type rather than using one shared endpoint with a type parameter, unlike some other pages in this system.

**Request payload (abbreviated, key fields):**
```json
{
  "filerTypeCode": "COM",
  "pageNumber": 1,
  "pageSize": 50,
  "filerName": null,
  "chairPersonName": null,
  "committeeType": null,
  "committeeMakingIE": null,
  "politicalPartyCode": null,
  "jurisdictionId": null,
  "accountStatus": null,
  "totalRaisedMin": null,
  "totalRaisedMax": null,
  "totalSpentMin": null,
  "totalSpentMax": null,
  "balanceFundsMin": null,
  "balanceFundsMax": null,
  "treasurerName": null,
  "filingEntityId": null,
  "filingYear": null
}
```

**Sample response (one record):**
```json
{
  "balanceAmount": 130.75,
  "balanceOfFundsNew": "$130.75",
  "candidateAddressLine1": null,
  "chairPerson": "Harding, Rob",
  "chairpersonFirstName": "Rob",
  "chairpersonFullName": "Rob Harding",
  "chairpersonLastName": "Harding",
  "cityDistrict": null,
  "committeeName": "Ag Sustaining Aquifer Protection Political Action Committee",
  "electionYear": "2023",
  "filerEntityID": 597,
  "filerName": "Ag Sustaining Aquifer Protection Political Action Committee",
  "filerStatus": "Active",
  "filerStatusCode": "FACT",
  "filerType": "Political Committee",
  "filerTypeCode": "PAC",
  "filerTypeDesc": "Political Committee",
  "firstName": null,
  "jurisdiction": "Idaho State",
  "jurisdictionId": 1,
  "lastName": null,
  "office": null,
  "officeId": null,
  "partyCode": null,
  "politicalParty": "Non-Partisan",
  "totalRaised": 0.0,
  "totalSpent": 188.0,
  "treasurerFirstLastName": "Rob Harding",
  "treasurerName": "Harding, Rob",
  "isLegacyRecord": false,
  "totalRows": 1
}
```

**Notes:**
- The `className` field (e.g. `"greenText"`) present on every Candidates page record is confirmed absent from every Committees page record. This is a real, confirmed schema difference between the two, purpose unknown, likely a UI/front-end styling flag rather than underlying data.
- The response returned `filerTypeCode: "PAC"` even though the request sent `filerTypeCode: "COM"`. This suggests `COM` functions as a page-level umbrella value requesting all committee types (likely both PAC and Central Committee), while each individual record reports its own specific type. Not yet confirmed whether Central Committee (`CENC`) records also appear under this same query, or are queried separately on their own page.
- Candidate-specific fields (`office`, `officeId`, address fields) are null for committee records; committee-specific fields (`chairPerson`, `chairpersonFirstName`) are populated. Treasurer fields are populated for both entity types.

---

## `GET /api/PublicLookup/GetElectionYearLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter
**Payload:** `?key=null&isSelectReq=false`

Identical endpoint and response to the Candidates page (see [candidates.md](candidates.md)).

**Notes:** Fires on page load, but the Election Year dropdown it would populate is not visible on this page — the only observed difference from the Candidates page is that this dropdown is hidden here.

---

## `GET /api/PublicLookup/GetOfficeSoughtLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter
**Payload:** `?key=office`

Identical endpoint and response to the Candidates page (see [candidates.md](candidates.md) for the full office list).

**Notes:** Same pattern as above — fires on load, but the Office Sought dropdown is not visible on this page.

---

## `POST /api/PublicLookup/GetPublicFilingYear`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter

Identical endpoint and response to the Candidates page.

**Notes:** Unlike on the Candidates page, this is a genuinely available, visible filter here (Disclosure Report filing year).

---

## `GET /api/Lookup/GetDropdownLookup/`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter

### Variation: `?key=CFRegistrationTypes&isSelectReq=false`

Identical response to the Candidates page.

**Notes:** Called on load, not user-selectable as a dropdown — this page is already scoped to Committees. Corresponds to the `filerTypeCode` sent in `GetCommitteeDetails` above.

### Variation: `?key=Party&name=lookup-masters&isSelectReq=false`

Identical response to the Candidates page. Confirmed visible, active filter on this page.

### Variation: `?key=Filer%20Status&name=lookup-masters&isSelectReq=false`

Identical response to the Candidates page. Confirmed visible, active filter on this page.

---

## `POST /api/Lookup/BindingDropDownValues`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter

### Variation: `{ "name": "jurisidiction-data", "isSelectReq": false }`

Identical response to the Candidates page (Idaho's 44 counties plus a statewide entry).

**Notes:** Unlike on the Candidates page, this dropdown is visible and active here.

### Variation: `{ "name": "district-type", "isSelectReq": false }`

Identical response to the Candidates page.

**Notes:** Appears to be a leftover from the shared page template — this populates a District Type dropdown that's visible on Candidates but hidden here.

---

## `POST /api/PublicLookup/GetDistrictByDistrictTypeQuery`

**Type:** Dependent Lookup
**Parameter Type:** Mixed

**Notes:** Fires on load as a leftover call from the shared Candidates/Committees template. District type and district name are not available filters on this page at all.

---

## Notable Page-Level Findings

- **This page confirms the shared-template pattern first suspected on Candidates.** Several reference lookups (Filer Status, Jurisdiction) that fire but appear to do nothing on the Candidates page turn out to be genuine, active filters here. This is strong evidence that Candidates, Committees, and (likely) Central Committee all share one underlying page template, with each individual page simply not rendering the filters it doesn't need — the lookup calls fire regardless.
- **Confirmed via request blocking**, not just inference: selectively blocking a request and reloading the page directly proved which shared lookups are load-bearing on this page (Party, Filer Status, Jurisdiction) versus genuinely inert leftovers (District Type, District-by-Type). This is a reliable, repeatable technique for resolving "does this call actually do anything" questions on this API, rather than guessing from endpoint naming.
