# Candidates Page

**URL:** `https://sunshine.voteidaho.gov/public/cf/publiccandidate`

Endpoints observed firing on a clean, unfiltered initial page load, verified by inspecting network traffic in Chrome DevTools. Endpoint categories follow the convention below:

- **Data Retrieval Endpoint** — returns the actual records displayed to the user (candidates, contributions, reports, etc.)
- **Reference Data Endpoint** — returns predefined values used to populate dropdowns, filters, or classifications
- **Dependent Lookup** — returns reference values that change based on another selection or parameter

Parameter Type follows this convention:

- **System Parameter** — a value the application sets automatically, not controlled by the user
- **User-Controlled Parameter** — a value the user can change through filters, searches, or selections
- **Mixed** — the request contains both system-defined and user-controlled values

## Endpoints at a Glance

| Endpoint | Method | Type | Purpose |
|---|---|---|---|
| `/api/PublicFilerDetails/GetCandidateDetails` | POST | Data Retrieval | Populates the Candidates results table |
| `/api/PublicLookup/GetElectionYearLookup` | GET | Reference Data | Election Year filter values (2024–2030) |
| `/api/PublicLookup/GetOfficeSoughtLookup` | GET | Reference Data | Office Sought filter values (38 offices) |
| `/api/PublicLookup/GetPublicFilingYear` | POST | Reference Data | Report filing year values (2020–2030); purpose on this page unconfirmed |
| `/api/PublicLookup/GetDistrictByDistrictTypeQuery` | POST | Dependent Lookup | District filter values, dependent on selected District Type |
| `/api/Lookup/BindingDropDownValues` → `district-type` | POST | Reference Data | District Type dropdown values |
| `/api/Lookup/BindingDropDownValues` → `jurisidiction-data` | POST | Reference Data | Idaho counties list; purpose on this page unconfirmed |
| `/api/Lookup/GetDropdownLookup/` → `CFRegistrationTypes` | GET | Reference Data | Registration type codes (CAN/PAC/CENC) |
| `/api/Lookup/GetDropdownLookup/` → `Party` | GET | Reference Data | Party filter values |
| `/api/Lookup/GetDropdownLookup/` → `Filer Status` | GET | Reference Data | Account Status filter values |

---

## `POST /api/PublicFilerDetails/GetCandidateDetails`

**Type:** Data Retrieval Endpoint
**Parameter Type:** Mixed — `filerTypeCode: "CAN"` is fixed by the page; the remaining fields (search name, party, district, office, jurisdiction, fundraising ranges, pagination) are user-controlled filter and search criteria.

The primary endpoint powering the Candidates results table.

**Request payload (abbreviated, key fields):**
```json
{
  "filerTypeCode": "CAN",
  "pageNumber": 1,
  "pageSize": 50,
  "filerName": null,
  "election": null,
  "politicalPartyCode": null,
  "districtTypeId": null,
  "cityDistrictId": null,
  "jurisdictionId": null,
  "OfficeSought": null,
  "accountStatus": null,
  "totalRaisedMin": null,
  "totalRaisedMax": null,
  "totalSpentMin": null,
  "totalSpentMax": null,
  "balanceFundsMin": null,
  "balanceFundsMax": null,
  "treasurerName": null,
  "campaignName": null,
  "filingEntityId": null
}
```

**Sample response (one record):**
```json
{
  "balanceAmount": 115.9,
  "balanceOfFundsNew": "$115.90",
  "candidateAddressLine1": "1934 Normal Ave",
  "candidateCity": "Burley",
  "candidateState": "ID",
  "candidateZipCode": "83318",
  "chairPerson": "",
  "cityDistrict": "Cassia County",
  "cityDistrictId": 149,
  "committeeName": "Martin K Adams",
  "districtType": "County",
  "districtTypeId": 6,
  "electionYear": "2022",
  "filerEntityID": 1347,
  "filerName": "Adams, Martin Kyle",
  "filerRegistrationId": 1204,
  "filerStatus": "Active",
  "filerStatusCode": "FACT",
  "filerType": "Candidate",
  "filerTypeCode": "CAN",
  "filerTypeDesc": "Candidate",
  "firstName": "Martin",
  "jurisdiction": "Cassia",
  "jurisdictionId": 17,
  "lastName": "Adams",
  "middleName": "Kyle",
  "office": "Assessor",
  "officeId": 3,
  "partyCode": "REP",
  "politicalParty": "Republican Party",
  "totalRaised": 0.0,
  "totalSpent": 0.0,
  "treasurerName": "Adams, Martin K",
  "className": "greenText",
  "isLegacyRecord": false,
  "totalRows": 1
}
```

**Notes:**
- `filerTypeCode: "CAN"` restricts results to Candidate records specifically; the equivalent Committees page request uses `"COM"` instead (see [committees.md](committees.md)).
- The `className` field (e.g. `"greenText"`) is present on every Candidates record observed and confirmed absent from every Committees record. Purpose unknown; likely a UI/front-end styling flag rather than underlying data.
- Confirmed the endpoint's response schema is shared across entity types: candidate-specific fields (`office`, `officeId`, address fields) populate for Candidate records and go null for Committee records; committee-specific fields (`chairPerson`, `chairpersonFirstName`) do the reverse. Treasurer-related fields are populated for both.

---

## `GET /api/PublicLookup/GetElectionYearLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter
**Payload:** `?key=null&isSelectReq=false`

Returns valid election years for the Election Year filter (2024–2030 on this dataset).

**Notes:** Election years begin at 2024, distinct from the filing year range below (2020–2030). This is a meaningful distinction, not a discrepancy: filing years track when a report was submitted, election years track the actual election cycle. Report filings on this system go back to 2020, but no election year prior to 2024 is offered — worth remembering when aggregating legacy data (2020–2023) into this data model.

---

## `GET /api/PublicLookup/GetOfficeSoughtLookup`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter
**Payload:** `?key=office`

Returns valid office names for the Office Sought filter, including a numeric `value` per office (used elsewhere as `officeId`) and a `sortOrder` field controlling dropdown display order.

Full list of 38 offices returned, including Governor, Lieutenant Governor, Secretary of State, State Controller, State Treasurer, Superintendent of Public Instruction, Supreme Court Justice, State Senator, State Representative, County Commissioner, Sheriff, Assessor, Clerk, Coroner, Prosecuting Attorney, County Treasurer, City Council, Mayor, District Judge, Magistrate Judge, Appellate Court Judge, School Trustee, College Trustee, Library Trustee, Highway Commissioner, Hospital Trustee, Fire Commissioner, Cemetery Commissioner, Ambulance Trustee, Auditorium Board Member, Mosquito Trustee, Port Commissioner, Recreation Director, Sewer Director, Soil Supervisor, Water Director, Water & Sewer Director.

---

## `POST /api/PublicLookup/GetPublicFilingYear`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter

Returns available report filing years (2020–2030), distinct from election years above (see the Election Year vs. Filing Year note above).

**Notes:** No visible filing-year filter or table field was found on this page. Function on this page unconfirmed; likely shared page template functionality, since this same endpoint is confirmed to be an active filter on the Committees page (see [committees.md](committees.md)).

---

## `POST /api/PublicLookup/GetDistrictByDistrictTypeQuery`

**Type:** Dependent Lookup
**Parameter Type:** Mixed — the request depends on the user's selected District Type.
**Payload:** `{ "districtTypeId": "1,2" }`

Returns valid District filter values based on the selected District Type. Response is a full list of Idaho district names and IDs; too large to include inline here — see the project's District Name Values reference for the complete list.

---

## `POST /api/Lookup/BindingDropDownValues`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter

A generic, reusable lookup endpoint. The specific values returned depend on the `name` parameter sent in the request. Despite the endpoint's generic name, not every value returned corresponds to a visible, user-facing dropdown on this page.

### Variation: `{ "name": "district-type", "isSelectReq": false }`

Populates the District Type dropdown (Ambulance, Auditorium, Cemetery, City, College, County, Fire, Highway, Hospital, Judicial, Legislative, Library, Mosquito, Port, Recreation, School, Sewer, Soil, State, Water, Water & Sewer — 21 total).

### Variation: `{ "name": "jurisidiction-data", "isSelectReq": false }`

Returns Idaho's 44 counties plus a statewide entry ("Idaho State"). Function on this page unconfirmed — no visible jurisdiction filter or table field was found. Likely shared page template functionality; confirmed to be a visible, active filter on the Committees page (see [committees.md](committees.md)).

---

## `GET /api/Lookup/GetDropdownLookup/`

**Type:** Reference Data Endpoint
**Parameter Type:** System Parameter

A second, separate generic lookup endpoint (distinct from `BindingDropDownValues` above). Response is determined by query parameters, and this same endpoint is reused across multiple pages.

### Variation: `?key=CFRegistrationTypes&isSelectReq=false`

Returns Campaign Finance registration type values: `CAN` (Candidate), `PAC` (Political Committee), `CENC` (Central Committee).

**Notes:** Called on page load but not user-selectable as a visible dropdown on this page — the page is already scoped to Candidates. This value corresponds to the `filerTypeCode` sent in the `GetCandidateDetails` request above.

### Variation: `?key=Party&name=lookup-masters&isSelectReq=false`

Returns political party values used to populate the visible Party filter dropdown: `CNSP` (Constitution), `DEM` (Democratic), `LIB` (Libertarian), `REP` (Republican), `UNA` (Unaffiliated).

### Variation: `?key=Filer%20Status&name=lookup-masters&isSelectReq=false`

Returns filer status values used to populate the visible Account Status filter dropdown: `FACT` (Active), `TERMN` (Terminated), `INA` (Inactive).

---

## Notable Page-Level Findings

- **Election Year vs. Filing Year:** these are two distinct concepts on this system. Election years only extend back to 2024; filing years extend back to 2020. This directly affects how legacy data (2020–2023) should be reconciled against this data model — a report can be filed well before the earliest available election year.
