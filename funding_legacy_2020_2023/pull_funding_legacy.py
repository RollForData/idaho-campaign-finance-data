"""
pull_funding_legacy.py

Cleaning script for funding_Legacy_2020_2023.
Run with: py funding_legacy_2020_2023\\pull_funding_legacy.py

This version combines:
  - Logic KEPT AS-IS from the original script (from_state core logic,
    from_zip patches, entity type corrections, the district-standardization
    prefixing mechanics, etc.)
  - Logic EDITED from the original script (from_state's "0" handling
    reversed, the encoding sweep expanded to catch lowercase mojibake,
    Russ Fulcher reassigned instead of removed, general text cleaning
    moved to run first)
  - ENTIRELY NEW logic added this session (individually-researched
    no-office candidates, "Could not be sourced" bucket, the
    to_reg_district zip-to-county backfill, Return amounts set negative)

Dead constants from an earlier draft (STATE_NAME_AS_CITY_FIX,
CITY_FALSE_POSITIVES) have been removed, per the decision to cut unused code.
"""

import pandas as pd
import re
import os

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
input_file = r"C:\Users\cathe\Documents\idaho-transparency-project\funding_legacy_2020_2023\LIVE [Raw Data] funding_Legacy_2020_2023.csv"
output_file = r"C:\Users\cathe\Documents\idaho-transparency-project\funding_legacy_2020_2023\LIVE [Clean Data] funding_Legacy_2020_2023.csv"

# ---------------------------------------------------------------------------
# CONSTANTS (KEPT from original script, unchanged)
# ---------------------------------------------------------------------------
VALID_USPS_ABBREVIATIONS = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC', 'AS', 'GU', 'MP', 'PR', 'VI', 'AA', 'AE', 'AP', 'AB', 'BC'
}

DONATE_TYPE_UNITEMIZED = 'Unitemized'
DONATE_TYPE_CREDIT_CARD_ITEM = 'Credit Card Item'
DONATE_TYPE_RETURN = 'Return'  # NEW: needed for the amount-sign fix

CITY_STATE_MAP = {
    'BOISE': 'ID', 'BOISE ID': 'ID', 'GARDEN CITY': 'ID', 'EAGLE': 'ID',
    'MERIDIAN': 'ID', 'STAR': 'ID', 'BURLEY': 'ID', 'KETCHUM': 'ID',
    'CAMBRIDGE': 'MA', 'TYLER': 'TX', 'VALDEZ': 'AK', 'POULSBO': 'WA',
    'NY': 'NY', 'NEW YORK': 'NY',
    'PHNOM PENH': None,
}

FULL_NAME_STATE_MAP = {
    'IDAHO': 'ID', 'CALIFORNIA': 'CA', 'OREGON': 'OR', 'MICHIGAN': 'MI',
    'MINNESOTA': 'MN', 'MONTANA': 'MT', 'UTAH': 'UT', 'VERMONT': 'VT',
    'WYOMING': 'WY', 'PENNSYLVANIA': 'PA', 'MASSACHUSETTS': 'MA',
    'ILLINOIS': 'IL', 'COLORADO': 'CO', 'ARIZONA': 'AZ',
    'NORTH CAROLINA': 'NC', 'WASHINGTON': 'WA', 'TENNESSE': 'TN',
    'ID - IDAHO': 'ID', 'ID IDAHO': 'ID', 'IDAHO (ID)': 'ID',
    'ILLINOIS (IL)': 'IL', 'NEW YORK': 'NY',
    '13': 'ID', 'ADA': 'ID', 'I D': 'ID', 'IF': 'ID', 'IID': 'ID',
    'CITY': 'ID',
    'ALBERTA': 'AB',
}

ZIP_ROW_PATCHES = {
    ('Boise', '8.37E+08'): '83708',
    ('Boise', '83714-375'): '83714',
    ('Boise', '837034010'): '83703',
}

ZIP_VALUE_PATCHES = {
    '692': '00692',  # Vega Alta, PR — lost its leading zeros
}

ZIP_UNRECOVERABLE = {'979014', '890606', '838343', '836223', '893206'}

ENTITY_TYPE_CORRECTIONS = {
    'Planned Parenthood Votes Idaho PAC': 'PAC',
    'Idaho Republican Party': 'PAC',
    'Idahos Future PAC': 'PAC',
    'Conservative Citizens for Thoughtful Growth': 'PAC',
}

# ---------------------------------------------------------------------------
# OFFICE_NAME_FIXES: applies ONLY to rows where to_office_name == 'Inactive'.
# This is the original ~90-name lookup from the Inactive-reclassification
# project. KEPT AS-IS. Do NOT add blank-office candidates here — they need
# NO_OFFICE_FIXES below instead, gated on a different mask. (This distinction
# is the bug we caught: several individually-researched candidates were
# previously added to this dict by mistake, where they could never fire,
# since their raw to_office_name is blank, not 'Inactive'.)
# ---------------------------------------------------------------------------
OFFICE_NAME_FIXES = {
    'dulce kersting-lark': 'State Representative - Seat A',
    'renee love': 'State Representative - Seat B',
    'christy zito': 'State Senator',
    'jake ellis': 'State Representative - Seat B',
    'sharon shari williams': 'State Senator',
    'john mccrostie': 'State Representative - Seat A',
    'marianna davis': 'State Representative - Seat A',
    'sally toone': 'State Representative - Seat B',
    'ellen spencer': 'State Senator',
    'caroline troy': 'State Representative - Seat B',
    'michelle stennett': 'State Senator',
    'aaron von ehlinger': 'State Representative - Seat A',
    'priscilla giddings': 'State Representative - Seat A',
    'regina bayer': 'State Senator',
    'jeffrey gabica': 'State Representative - Seat B',
    'david roth': 'State Representative - Seat B',
    'brenda richards': 'State Senator',
    'gregory chaney': 'State Representative - Seat B',
    'patti anne lodge': 'State Senator',
    'laura bellegante': 'State Senator',
    'jarom wagoner': 'State Representative - Seat A',
    'dorothy moon': 'State Representative - Seat B',
    'diane jensen': 'State Representative - Seat A',
    'dave radford': 'State Representative - Seat B',
    'adam frugoli': 'State Senator',
    'mary souza': 'State Senator',
    'mark nye': 'State Senator',
    'steve vick': 'State Senator',
    'grant burgoyne': 'State Senator',
    'laverne sessions': 'State Representative - Seat B',
    'dan rose': 'State Representative - Seat B',
    'gary smith': 'State Senator',
    'hari heath': 'State Representative - Seat A',
    'cindy currie': 'State Representative - Seat A',
    'chris abernathy': 'State Representative - Seat A',
    'rebecca hanson': 'State Representative - Seat A',
    'william thorpe': 'State Representative - Seat B',
    'kirk adams': 'State Representative - Seat B',
    'bryan zollinger': 'State Representative - Seat B',
    'brent hill': 'State Senator',
    'cherie buckner-webb': 'State Senator',
    'marc eberlein': 'State Senator',
    'chelsea gaona-lincoln': 'State Representative - Seat B',
    'lee heider': 'State Senator',
    'randall armstrong': 'State Representative - Seat A',
    'fred wood': 'State Representative - Seat B',
    'alex barron': 'State Senator',
    'daniel johnson': 'State Senator',
    'shane ruebush': 'State Representative - Seat A',
    'donavan harrington': 'State Representative - Seat B',
    'kim keller': 'State Representative - Seat B',
    'kenny wroten': 'State Representative - Seat B',
    'randy jackson': 'State Representative - Seat B',
    'marc gibbs': 'State Representative - Seat A',
    'marcus gibbs': 'State Representative - Seat A',
    'christopher matthews': 'State Representative - Seat A',
    'jud miller': 'State Senator',
    'jacob householder': 'State Senator',
    'william leake': 'State Representative - Seat B',
    'thyra stevenson': 'State Representative - Seat A',
    'rocky ferrenburg': 'State Senator',
    'stephen f. howlett': 'State Representative - Seat B',
    'wendy webb': 'State Senator',
    'mila wood': 'State Representative - Seat A',
    'zach brooks': 'State Senator',
    'jacob lowder': 'State Representative - Seat A',
    'patricia day hartwell': 'State Representative - Seat A',
    'gary suppiger': 'State Representative - Seat B',
    'brenda palmer': 'State Representative - Seat B',
    'donald williamson': 'State Representative - Seat A',
    'brittany love': 'State Representative - Seat A',
    'melissa wintrow': 'State Senator',
    'adriel martinez': 'State Senator',
    'marla lawson': 'State Senator',
    'dawn maglish': 'State Representative - Seat A',
    'samantha hager': 'State Representative - Seat B',
    'heidi sorenson': 'State Representative - Seat B',
    'dennis harper': 'State Representative - Seat A',
    'charlene taylor': 'State Representative - Seat B',
    'jim bratnober': 'State Senator',
    'mark bost': 'State Senator',
    'james smith': 'State Representative - Seat A',
    'walter schmid': 'State Senator',
}

STATEWIDE_OFFICES = {
    'Governor', 'Lieutenant Governor', 'Attorney General', 'Secretary of State',
    'Superintendent of Public Instruction', 'State Controller', 'State Treasurer',
    'Supreme Court Judge'
}

JUDGE_DISTRICT_FIXES = {
    'rich christensen': '1', 'stanley mortensen': '1', 'justin coleman': '2',
    'michelle evans': '2', 'john bradbury': '2', 'thomas whitney': '3',
    'shari dodge': '3', 'anna eckhart': '1', 'james combo': '1',
}

DISTRICT_REQUIRED_OFFICES = {
    'State Representative - Seat A', 'State Representative - Seat B',
    'State Senator', 'District Judge', 'Magistrate Judge'
}

# LEGISLATIVE_DISTRICT_FIXES: districts for the original ~90 Inactive names,
# tied 1:1 to OFFICE_NAME_FIXES above. KEPT AS-IS.
LEGISLATIVE_DISTRICT_FIXES = {
    'christy zito': '23', 'dulce kersting-lark': '5', 'renee love': '5',
    'jake ellis': '15', 'sharon shari williams': '4', 'john mccrostie': '16',
    'caroline troy': '5', 'mary souza': '4', 'cherie buckner-webb': '19',
    'melissa wintrow': '19', 'grant burgoyne': '16', 'marianna davis': '26',
    'scott bedke': '27', 'ellen spencer': '14', 'michelle stennett': '26',
    'aaron von ehlinger': '6', 'priscilla giddings': '7', 'regina bayer': '21',
    'jeffrey gabica': '19', 'david roth': '33', 'sally toone': '26',
    'thyra stevenson': '6', 'dennis harper': '7', 'wendy webb': '21',
    'charlene taylor': '19', 'shane ruebush': '34', 'bryan zollinger': '33',
    'brenda richards': '23', 'gregory chaney': '10', 'patti anne lodge': '11',
    'laura bellegante': '23', 'jarom wagoner': '10', 'dorothy moon': '8',
    'diane jensen': '22', 'dave radford': '32', 'adam frugoli': '30',
    'gary smith': '17', 'zach brooks': '11', 'rebecca hanson': '10',
    'laverne sessions': '8', 'heidi sorenson': '22', 'william leake': '32',
    'brent hill': '34', 'chelsea gaona-lincoln': '10', 'marc eberlein': '3',
    'adriel martinez': '17', 'dan rose': '1', 'mark nye': '29',
    'hari heath': '5', 'cindy currie': '14', 'steve vick': '2',
    'chris abernathy': '29', 'william thorpe': '26', 'kirk adams': '11',
    'randall armstrong': '28', 'lee heider': '24', 'fred wood': '27',
    'alex barron': '3', 'daniel johnson': '6', 'donavan harrington': '31',
    'kim keller': '13', 'jud miller': '35', 'christopher matthews': '3',
    'jacob householder': '34', 'rocky ferrenburg': '24',
    'stephen f. howlett': '1', 'mila wood': '11', 'gary suppiger': '1',
    'brenda palmer': '21', 'randy jackson': '13', 'donald williamson': '21',
    'brittany love': '17', 'marla lawson': '8', 'samantha hager': '20',
    'jacob lowder': '11', 'dawn maglish': '20', 'patricia day hartwell': '12',
    'jim bratnober': '15', 'mark bost': '18', 'kenny wroten': '13',
    'james smith': '9', 'walter schmid': '15',
}

# ---------------------------------------------------------------------------
# NEW: individually-researched candidates whose raw to_office_name is BLANK
# (not 'Inactive'). This is a separate mask from OFFICE_NAME_FIXES above —
# confirmed against the real data that these people's raw rows show NaN,
# not 'Inactive'. James Hartley is handled separately below since his office
# depends on elec_year (ran for two different offices in this window).
# 'Could not be sourced' cases are handled separately further below.
# ---------------------------------------------------------------------------
NO_OFFICE_FIXES = {
    'ronald bair': 'State Senator',
    'christopher trakel': 'State Senator',
    'gary marshall': 'State Representative - Seat A',
    'sarah clendenon': 'State Senator',
    'benjamin lee': 'State Representative - Seat A',
    'michaella franklin': 'State Senator',
    'edward savala': 'State Representative - Seat B',
    'john hodson': 'State Representative - Seat B',
    'luke malek': 'Lieutenant Governor',
    'gary collins': 'State Representative - Seat B',
    'william sifford': 'State Senator',
    'khloe briglio buzzell': 'State Representative - Seat A',
    'brett surplus': 'State Senator',
    'george judd': 'State Representative - Seat B',
    'lisa adams': 'State Representative - Seat B',
    'elaine smith': 'State Representative - Seat B',
    'nina turner': 'State Representative - Seat B',
    'gary aldous': 'State Representative - Seat B',
    'john goedde': 'State Senator',
    'dean cameron': 'State Senator',
    'melissa robinson': 'State Senator',
    'glenneda zuiderveld': 'State Senator',
    'bill goesling': 'State Representative - Seat A',
    'maryanne jordan': 'State Senator',
    'robert mason': 'State Representative - Seat B',
    'andrew hiatt': 'State Senator',
    'thomas paterson': 'State Representative - Seat A',
    'shem hanks': 'State Representative - Seat B',
    'jerry pierce': 'County Commissioner',
    'j.d. williams': 'State Controller',
    'patrick mcdonald': 'State Representative - Seat B',
    'clark kauffman': 'State Representative - Seat B',
    'marcus j gibbs': 'State Representative - Seat A',
    'chelle gluch': 'State Senator',
    'michelle gluch': 'State Senator',
    'julie ellsworth': 'State Treasurer',
    # NEW: added after the first verification pass found these 6 names
    # never got resolved (5 were confirmed decisions that never made it
    # into the script, 1 was a name-key mismatch — see below).
    'mike duff': 'State Representative - Seat A',
    'matt dorsey': 'State Representative - Seat B',
    'leland lay': 'State Senator',
    'neil anderson': 'State Representative - Seat A',
    'brian bishop': 'Trustee School',
}

# NEW: corrected key. Previously 'bill goesling', which never matched the
# real raw display name "William Goesling", so this fix silently never
# fired. William Goesling is intentionally a SEPARATE dict, applied after
# NO_OFFICE_FIXES above, purely to isolate this corrected entry so it's
# easy to spot in a diff — functionally identical to adding it inline.
WILLIAM_GOESLING_FIX = {'william goesling': 'State Representative - Seat A'}

# Districts for the NO_OFFICE_FIXES names above that are legislative offices.
# County-wide (Pierce), statewide (Malek, Williams, Ellsworth), and judicial
# offices don't need an entry here — their district is handled by the
# group-level standardization logic later, not a name lookup.
NO_OFFICE_LEGISLATIVE_DISTRICT_FIXES = {
    'ronald bair': '31', 'christopher trakel': '11', 'gary marshall': '30',
    'sarah clendenon': '15', 'benjamin lee': '23', 'michaella franklin': '13',
    'edward savala': '11', 'john hodson': '21', 'gary collins': '13',
    'william sifford': '8', 'khloe briglio buzzell': '17', 'brett surplus': '3',
    'george judd': '35', 'lisa adams': '21', 'elaine smith': '29',
    'nina turner': '22', 'gary aldous': '28', 'john goedde': '3',
    'dean cameron': '27', 'melissa robinson': '13', 'glenneda zuiderveld': '24',
    'bill goesling': '5', 'maryanne jordan': '17', 'robert mason': '16',
    'andrew hiatt': '1', 'thomas paterson': '16', 'shem hanks': '4',
    'patrick mcdonald': '15', 'clark kauffman': '25', 'marcus j gibbs': '32',
    'chelle gluch': '12', 'michelle gluch': '12',
    # NEW: districts for the 5 candidates added above.
    'mike duff': '31', 'matt dorsey': '11', 'leland lay': '16',
    'neil anderson': '31', 'william goesling': '5',
}

# NEW: Brian Bishop's single unresolved row shows to_district_name = 'SW'
# (a real placeholder string, not blank), unlike his other 6 rows which
# already correctly show 'VALLIVUE'. Because 'SW' isn't null, the normal
# blank-backfill logic in the school-office standardization step wouldn't
# touch it, so this needs its own keyed correction, applied before that
# standardization runs, matching his other rows.
BISHOP_DISTRICT_FIX_FROM = 'SW'
BISHOP_DISTRICT_FIX_TO = 'VALLIVUE'

# NEW: genuinely blank Trustee School rows found during verification
# (Valley County has two real districts — Cascade and McCall-Donnelly —
# so unlike the Kootenai/North Idaho College case, there's no safe 1:1
# default; each person needed individual research).
SCHOOL_BLANK_DISTRICT_BY_NAME = {
    'jim cole': 'MCCALL-DONNELLY',
    "pauline 'paula' bartlett": 'CASCADE',
    'anna kinney': 'MCCALL-DONNELLY',
}

# James Hartley ran for two different offices in this window — split by
# elec_year rather than a single name lookup.
JAMES_HARTLEY_BY_YEAR = {
    '2020': ('State Representative - Seat B', '5'),
    '2022': ('State Senator', '6'),
}

# NEW: candidates given real, individual research effort where no confident
# office/district match could be found (G. Chris Holdaway, Michael Oliver,
# Jess Smith), plus David Erlanson, who opened an account and accepted
# contributions but never declared a candidacy before dropping out. Both
# groups get this literal value rather than blank, so this genuine data hole
# is visually distinguishable from a legitimate PAC blank.
COULD_NOT_BE_SOURCED_NAMES = {
    'g. chris holdaway', 'g chris holdaway', 'michael oliver', 'jess smith',
    'david erlanson',
}
COULD_NOT_BE_SOURCED_VALUE = 'Could not be sourced'

# NEW: Russ Fulcher is reassigned to his last known Idaho state office, NOT
# removed. (An earlier version of this script removed his 16 rows entirely,
# on the theory this was federal-candidate contamination. That theory was
# investigated via a pulled C-5 filing and retracted — this is real,
# election-timed state-committee activity, not federal money misfiled with
# the state. See tracker 2.20 for the full correction.)
FULCHER_OFFICE = 'State Senator'
FULCHER_DISTRICT = '22'

# ---------------------------------------------------------------------------
# OFFICE_NAME_RENAMES: KEPT AS-IS from the original script.
# ---------------------------------------------------------------------------
OFFICE_NAME_RENAMES = {
    'County Commissioner - Seat B': 'County Commissioner',
    'BEAR LAKE Commissioner for District II': 'County Commissioner',
    'Trustee Commissioner': 'County Commissioner',
    'Commissioner HIGHWAY DISTRICT 42': 'Trustee Highway',
    'Trustee TRUSTEE ZONE District 201-4': 'Trustee School',
    'Library District Trustee - Meridian': 'Trustee Library',
    'Library District Trustee - Ada County Free': 'Trustee Library',
    'Library District Trustee - Kuna': 'Trustee Library',
}

# Office groups — KEPT AS-IS.
COUNTY_WIDE_OFFICES = {
    'Assessor', 'Clerk', 'Coroner', 'Prosecuting Attorney', 'Sheriff',
    'Treasurer', 'County Commissioner'
}
LEGISLATIVE_OFFICES = {
    'State Senator', 'State Representative - Seat A', 'State Representative - Seat B'
}
CITY_OFFICES = {'Mayor', 'City Council'}
JUDICIAL_OFFICES = {'District Judge', 'Magistrate Judge'}
HIGHWAY_OFFICES = {'Trustee Highway'}
LIBRARY_OFFICES = {'Trustee Library'}
HOSPITAL_OFFICES = {'Trustee Hospital'}
FIRE_OFFICES = {'Commissioner Fire'}
SCHOOL_OFFICES = {'Trustee School', 'Trustee College'}

CITY_DISTRICT_NORMALIZATION = {
    'BOISE CITY': 'BOISE', 'MERIDIAN CITY': 'MERIDIAN',
    "CITY - CDA 202": "COEUR D'ALENE", 'EAGLE CITY': 'EAGLE',
    'CITY OF POCATELLO': 'POCATELLO', 'City of Moscow': 'MOSCOW',
    'CALDWELL': 'CALDWELL', 'GARDEN CITY': 'GARDEN CITY',
    'CITY - HAYDEN 207': 'HAYDEN', 'IDAHO FALLS': 'IDAHO FALLS',
    'LEWISTON': 'LEWISTON', 'KETCHUM CITY': 'KETCHUM',
    'SANDPOINT': 'SANDPOINT', 'CITY - POST FALLS 210': 'POST FALLS',
    'MOUNTAIN HOME': 'MOUNTAIN HOME', 'CITY OF TWIN FALLS': 'TWIN FALLS',
    'NAMPA': 'NAMPA', 'STAR CITY': 'STAR',
    'CITY - RATHDRUM 211': 'RATHDRUM', 'HAILEY CITY': 'HAILEY',
    'SUN VALLEY CITY': 'SUN VALLEY', 'MIDDLETON': 'MIDDLETON',
    'REXBURG HILL': 'REXBURG', 'CITY - DALTON 203': 'DALTON',
    'KUNA CITY': 'KUNA', 'POCATELLO': 'POCATELLO',
    'CITY L-6': 'LEWISTON', 'CITY OF CHUBBUCK': 'CHUBBUCK',
    '100-Driggs': 'DRIGGS', 'CITY OF EMMETT': 'EMMETT',
    '110-Victor': 'VICTOR', 'WEISER CITY': 'WEISER',
    'CITY OF BURLEY': 'BURLEY', 'KELLOGG': 'KELLOGG',
    'WALLACE': 'WALLACE', 'BLACKFOOT': 'BLACKFOOT',
    'CITY MC CALL': 'MCCALL', 'CITY L-7': 'LEWISTON',
    'GLENNS FERRY': 'GLENNS FERRY',
    'CITY OF BLACKFOOT PRECINCT 1': 'BLACKFOOT',
    'City of Soda Springs': 'SODA SPRINGS',
    'CHALLIS CITY NO. 1': 'CHALLIS',
    'NO. HOMEDALE CITY NO. 1': 'HOMEDALE',
    'CITY - ATHOL 201': 'ATHOL', 'AMERICAN FALLS': 'AMERICAN FALLS',
    'PAYETTE': 'PAYETTE', 'OROFINO': 'OROFINO', 'TETONIA': 'TETONIA',
    'WEISER CITY NO 1': 'WEISER', 'VICTOR': 'VICTOR',
    'GOODING CITY': 'GOODING', 'CITY OF HEYBURN': 'HEYBURN',
    'NOTUS': 'NOTUS', 'BELLEVUE CITY': 'BELLEVUE',
    'CITY OF KIMBERLY': 'KIMBERLY', 'CITY OF BUHL': 'BUHL',
    'CITY OF SHELLEY': 'SHELLEY', 'CITY OF RUPERT': 'RUPERT',
    'SALMON 01': 'SALMON', 'PINEHURST': 'PINEHURST',
    'CITY OF INKOM': 'INKOM', 'CITY OF HORSESHOE BEND': 'HORSESHOE BEND',
}

LIBRARY_DISTRICT_NORMALIZATION = {
    'E BONNER LIB': 'EAST BONNER COUNTY DISTRICT LIBRARY',
    'LIBRARY': 'LATAH COUNTY LIBRARY DISTRICT',
    'LIBRARY DIST': 'BOUNDARY COUNTY LIBRARY DISTRICT',
    'LIBRARY ZONE 5': 'BOUNDARY COUNTY LIBRARY DISTRICT',
    'MERIDIAN LIBRARY': 'MERIDIAN LIBRARY',
    'ADA COUNTY FREE LIBRARY': 'ADA COUNTY FREE LIBRARY',
    'KUNA LIBRARY': 'KUNA LIBRARY',
}
LIBRARY_BLANK_BY_CITY = {
    'Post Falls': 'COMMUNITY LIBRARY NETWORK',
    'Hayden': 'COMMUNITY LIBRARY NETWORK',
    'Rathdrum': 'COMMUNITY LIBRARY NETWORK',
    "Coeur d'Alene": "COEUR D'ALENE PUBLIC LIBRARY",
}

SCHOOL_DISTRICT_NORMALIZATION = {
    'CDA SCH 271': "COEUR D'ALENE SCHOOL DISTRICT #271",
    'SD #271 ZONE 2': "COEUR D'ALENE SCHOOL DISTRICT #271",
    'SD #271 ZONE 3': "COEUR D'ALENE SCHOOL DISTRICT #271",
    'SD #271 ZONE 5': "COEUR D'ALENE SCHOOL DISTRICT #271",
    'WEST ADA SCHOOL DISTRICT NO. 2': 'WEST ADA SCHOOL DISTRICT #2',
    'WEST ADA SCH 8-2': 'WEST ADA SCHOOL DISTRICT #2',
    'WEST ADA SCH 8-3': 'WEST ADA SCHOOL DISTRICT #2',
    'WEST ADA SCH 8-4': 'WEST ADA SCHOOL DISTRICT #2',
    'WEST ADA SCH 8-5': 'WEST ADA SCHOOL DISTRICT #2',
    'IDAHO FALLS SD 91': 'IDAHO FALLS SCHOOL DISTRICT #91',
    'SD 91 Z2': 'IDAHO FALLS SCHOOL DISTRICT #91',
    'SD 91 Z3': 'IDAHO FALLS SCHOOL DISTRICT #91',
    'SD 91 Z5': 'IDAHO FALLS SCHOOL DISTRICT #91',
    'MOSCOW SD 1': 'MOSCOW SCHOOL DISTRICT #281',
    'MOSCOW SD 3': 'MOSCOW SCHOOL DISTRICT #281',
    'MOSCOW SD 4': 'MOSCOW SCHOOL DISTRICT #281',
    'TETON SCH DIST 401': 'TETON SCHOOL DISTRICT #401',
    'TETON 401 SCHZ-03': 'TETON SCHOOL DISTRICT #401',
    'TETON 401 SCHZ-04': 'TETON SCHOOL DISTRICT #401',
    'KUNA SCH 9-1': 'KUNA JOINT SCHOOL DISTRICT #3',
    'KUNA SCH 9-2': 'KUNA JOINT SCHOOL DISTRICT #3',
    'KUNA SCH 9-5': 'KUNA JOINT SCHOOL DISTRICT #3',
    'KUNA': 'KUNA JOINT SCHOOL DISTRICT #3',
    'PF SCH 273': 'POST FALLS SCHOOL DISTRICT #273',
    'SD #273 ZONE 4': 'POST FALLS SCHOOL DISTRICT #273',
    'SD #273 ZONE 5': 'POST FALLS SCHOOL DISTRICT #273',
    'LAKE SCH 272': 'LAKELAND SCHOOL DISTRICT #272',
    'SD #272 ZONE 2': 'LAKELAND SCHOOL DISTRICT #272',
    'LAKE PO SCH #84': 'LAKE PEND OREILLE SCHOOL DISTRICT #84',
    'BONNEVILLE SD 93': 'BONNEVILLE JOINT SCHOOL DISTRICT #93',
    'BONN Z2': 'BONNEVILLE JOINT SCHOOL DISTRICT #93',
    'WEI SCH 431A': 'WEISER SCHOOL DISTRICT #431',
    'WEISER #431-2': 'WEISER SCHOOL DISTRICT #431',
    'SCHOOL #421': 'MCCALL-DONNELLY SCHOOL DISTRICT #421',
    'JSD151-2': 'CASSIA COUNTY JOINT SCHOOL DISTRICT #151',
    'JSD151-4': 'CASSIA COUNTY JOINT SCHOOL DISTRICT #151',
    'trustee zone': 'WEST BONNER COUNTY SCHOOL DISTRICT #83',
    'TRUSTEE ZONE': 'WEST BONNER COUNTY SCHOOL DISTRICT #83',
    'W BONNER SCH#83': 'WEST BONNER COUNTY SCHOOL DISTRICT #83',
    'TRUSTEE ZONE 2': 'BLAINE COUNTY SCHOOL DISTRICT #61',
    'TRUSTEE ZONE 3': 'BLAINE COUNTY SCHOOL DISTRICT #61',
    'TRUSTEE ZONE 5': 'BLAINE COUNTY SCHOOL DISTRICT #61',
    'SCHOOL DIST #61': 'BLAINE COUNTY SCHOOL DISTRICT #61',
    'ZONE 2': 'POCATELLO/CHUBBUCK SCHOOL DISTRICT #25',
    'ZONE 4': 'POCATELLO/CHUBBUCK SCHOOL DISTRICT #25',
    "CLASS 'A' SCHOOL #25": 'POCATELLO/CHUBBUCK SCHOOL DISTRICT #25',
    'SCH 41/TRUSTEE ZONE 3': 'ST. MARIES JOINT SCHOOL DISTRICT #41',
    'SCH 41/TRUSTEE ZONE 4': 'ST. MARIES JOINT SCHOOL DISTRICT #41',
    '391 K - TR ZONE 3': 'KELLOGG SCHOOL DISTRICT #391',
    '391 K - TR ZONE 4': 'KELLOGG SCHOOL DISTRICT #391',
    'SCHOOL #171 ZONE 5': 'OROFINO SCHOOL DISTRICT #171',
    'MTN VIEW ZONE 2': 'MOUNTAIN VIEW SCHOOL DISTRICT #244',
    'MTN VIEW ZONE 3': 'MOUNTAIN VIEW SCHOOL DISTRICT #244',
    'MTN VIEW ZONE 4': 'MOUNTAIN VIEW SCHOOL DISTRICT #244',
    'SCHOOL # 244': 'MOUNTAIN VIEW SCHOOL DISTRICT #244',
    'SCH DIST 322': 'MADISON SCHOOL DISTRICT #321',
    'SCHOOL #193': 'MOUNTAIN HOME SCHOOL DISTRICT #193',
    'PRESTON 201-4': 'PRESTON JOINT SCHOOL DISTRICT #201',
    'CALDWELL': 'CALDWELL SCHOOL DISTRICT',
    'NAMPA': 'NAMPA SCHOOL DISTRICT',
    'PARMA': 'PARMA SCHOOL DISTRICT',
    'MIDDLETON': 'MIDDLETON SCHOOL DISTRICT',
    'VALLIVUE': 'VALLIVUE SCHOOL DISTRICT',
    'LEWISTON 1': 'LEWISTON SCHOOL DISTRICT #1',
    'MCCALL ZONE 3': 'MCCALL-DONNELLY SCHOOL DISTRICT #421',
    'BLFT SCHOOL ZONE 4': 'BLACKFOOT SCHOOL DISTRICT #55',
    'BOISE SCHOOL DISTRICT NO. 1': 'BOISE SCHOOL DISTRICT #1',
    # NEW: raw values used by the Cole/Bartlett keyed fix above.
    'MCCALL-DONNELLY': 'MCCALL-DONNELLY SCHOOL DISTRICT #421',
    'CASCADE': 'CASCADE SCHOOL DISTRICT #422',
}

COLLEGE_DISTRICT_NORMALIZATION = {
    'CWI (ZONE)': 'COLLEGE OF WESTERN IDAHO',
    'COLLEGE OF WESTERN IDAHO': 'COLLEGE OF WESTERN IDAHO',
    'COLLEGE OF EASTERN ID Z1': 'COLLEGE OF EASTERN IDAHO',
}

# ---------------------------------------------------------------------------
# from_city helpers/constants — KEPT AS-IS.
# ---------------------------------------------------------------------------
_STREET_SUFFIX_END = re.compile(
    r'(St|Street|Ave|Avenue|Blvd|Rd|Road|Dr|Drive|Ln|Lane|Ct|Court|Way|Hwy|'
    r'Highway|Pl|Place|Trail|Circle)\.?$', re.IGNORECASE
)

CITY_GLUED_TEXT_MAP = {
    'Hailey, Idaho': 'Hailey', 'Indian Valley, ID 83632, USA': 'Indian Valley',
    'Nampa, ID': 'Nampa', 'Boise, ID': 'Boise', 'BOISE, ID': 'Boise',
    'Coeur D Alene, ID': "Coeur D'Alene", 'Emmett, ID': 'Emmett',
    'Albuquerque, NM': 'Albuquerque', 'Ketchum,Id': 'Ketchum',
    'Boise, Idaho': 'Boise', 'Garden City,Id': 'Garden City',
    "Coeur D' Alene,Id.": "Coeur D'Alene",
    'Nampa, Idaho, United States': 'Nampa', 'MERIDIAN, ID': 'Meridian',
    'Grand View, ID': 'Grand View', 'Sappor, Japan': 'Sapporo',
    'Caldwell, Idaho': 'Caldwell', 'Boise, Idaho 83713': 'Boise',
    'Aptos,Ca,95003': 'Aptos', 'Ashton,Id': 'Ashton',
    'Pocatello,Id 83201': 'Pocatello', 'Caldwell, Id. 83605': 'Caldwell',
    'Sunnyside,Ny': 'Sunnyside', 'Boise 83702': 'Boise',
    'Boise ID 83706': 'Boise', 'Boise Id 83706': 'Boise',
    'Boise Id 83712': 'Boise', 'Sandpoint ID 83864': 'Sandpoint',
}

ZIP_IN_CITY_FIX = {
    '83702': 'Boise',
    '97214': 'Portland',
}

IDAHO_CITY_BY_ZIP = {
    '83402': 'Idaho Falls', '83404': 'Idaho Falls',
    '83843': 'Moscow', '83530': 'Kamiah',
}

TO_CITY_GLUED_STATE_MAP = {
    'POCATELLO, ID': 'POCATELLO',
    'Caldwell, Idaho': 'Caldwell',
    'Preston, ID': 'Preston',
}

# ---------------------------------------------------------------------------
# NEW: to_reg_district zip-to-county backfill.
# Two zips need individual handling instead of a blanket lookup:
#   - 83644 (Middleton): officially, entirely within Canyon County per
#     USPS/Census reference data. The 177 rows showing "Ada" for this exact
#     zip are a source-data error, not real ambiguity — override ALL rows
#     with this zip to Canyon, including ones that already show Ada.
#   - 83442 (Rigby): officially split across two real counties (Jefferson
#     and Bonneville). No single lookup value is correct for every address
#     in that zip, so this is resolved by researched candidate address
#     instead of a blanket zip rule.
# ---------------------------------------------------------------------------
REG_DISTRICT_ZIP_OVERRIDE = {
    '83644': 'CANYON',
}

# Keyed on (to_display_name lowercased, to_address) since the same zip
# (83442) legitimately splits between two counties for different people.
REG_DISTRICT_RIGBY_BY_NAME = {
    'rodney furniss': 'JEFFERSON',
    'stephanie mickelsen': 'BONNEVILLE',
    'frances bryson': 'JEFFERSON',
    'thomas duclos': 'JEFFERSON',
    'jud miller': 'JEFFERSON',
}
RIGBY_ZIP = '83442'


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def clean_text_series(series):
    """Vectorized: strip whitespace, trailing punctuation, and stray
    encoding artifacts across an entire column at once (fast).

    EDITED from the original: the encoding pattern previously only matched
    uppercase Â/Ã plus a single continuation byte, missing the lowercase â
    mojibake pattern (e.g. "Coeur Dâ€™alene") found in from_city/
    from_address/from_display_name. Pattern now strips both cases."""
    s = series.astype('string')
    s = s.str.replace(r'[ÂÃ][\x80-\xbf\xa0]?', '', regex=True)
    s = s.str.replace(r'â€[™œ\x80-\xbf]?', "'", regex=True)
    s = s.str.replace(r'â(?=[A-Za-z])', '', regex=True)
    s = s.str.replace('\n', ' ', regex=False).str.replace('\r', ' ', regex=False)
    s = s.str.strip()
    s = s.str.replace(r'[,;:]+$', '', regex=True)
    s = s.str.strip()
    s = s.mask(s == '', None)
    return s


def clean_zip_value(val, city_key=None):
    if city_key is not None and (city_key, val) in ZIP_ROW_PATCHES:
        return ZIP_ROW_PATCHES[(city_key, val)]
    if pd.isna(val):
        return None
    s = str(val).strip()
    if s == '' or s == '--' or s == '00000':
        return None
    if s in ZIP_VALUE_PATCHES:
        return ZIP_VALUE_PATCHES[s]
    if s in ZIP_UNRECOVERABLE:
        return None
    s = re.sub(r'[^0-9\-]', '', s)
    if '-' in s:
        s = s.split('-')[0]
    if len(s) == 4 and s.isdigit():
        s = '0' + s
    if len(s) != 5 or not s.isdigit():
        return None
    return s


def clean_state_value(state_val, city_val):
    """EDITED: '0' is no longer preserved. The earlier theory that '0'
    sometimes meant something other than 'missing' was never confirmed
    against real data, and has been reversed. '--', '0', and blank all
    now resolve to true NULL, with missing_state_data carrying the signal
    for whether that absence is expected (Unitemized/Credit Card Item) or
    a genuine government data gap."""
    if pd.isna(state_val):
        return None
    s = str(state_val).strip()
    if s == '' or s == '--' or s == '0':
        return None

    s_upper = s.upper()

    if s_upper == 'DEFAULT':
        return 'NV'

    city_clean = str(city_val).strip().upper() if pd.notna(city_val) else None
    if city_clean is not None and city_clean == s_upper:
        return CITY_STATE_MAP.get(city_clean, s_upper)

    if city_clean == 'GARDEN' and s_upper == 'CITY':
        return 'ID'

    if s_upper in FULL_NAME_STATE_MAP:
        return FULL_NAME_STATE_MAP[s_upper]

    if s_upper == 'BC':
        return 'BC'

    return s_upper


def looks_like_street_address(val):
    if pd.isna(val):
        return False
    v = str(val).strip()
    if re.match(r'^\d', v):
        return True
    if _STREET_SUFFIX_END.search(v) and re.search(r'\d', v):
        return True
    return False


def looks_like_plain_place_name(val):
    if pd.isna(val):
        return False
    v = str(val).strip()
    if v in ('0', '--', ''):
        return False
    if re.search(r'\d', v):
        return False
    if _STREET_SUFFIX_END.search(v):
        return False
    return True


def _collapse_whitespace(series):
    return series.astype('string').str.replace(r'\s+', ' ', regex=True).str.strip()


def build_zip_to_county_lookup(df):
    """NEW: builds a zip -> county crosswalk directly from this dataset's
    own already-populated to_reg_district values (majority vote per zip),
    rather than a hardcoded external table. This mirrors exactly how the
    lookup was validated during analysis. The two known-ambiguous zips
    (Middleton, Rigby) are excluded here and handled by explicit override
    logic instead, so a majority vote never silently overrides the
    individually-researched Rigby candidates or masks the Middleton error."""
    known = df[df['to_reg_district'].notna() & (df['to_reg_district'] != 'Idaho State')]
    known = known[~known['to_zip'].isin([RIGBY_ZIP] + list(REG_DISTRICT_ZIP_OVERRIDE.keys()))]
    lookup = (
        known.groupby('to_zip')['to_reg_district']
        .agg(lambda x: x.value_counts().idxmax())
    )
    return lookup.to_dict()


def run():
    print("Reading raw file...")
    df = pd.read_csv(input_file, dtype=str, encoding='utf-8')
    print(f"Loaded {len(df)} rows.")

    # -----------------------------------------------------------------
    # STEP 1 (EDITED — moved to run first): general text cleaning.
    # Runs before any swap-detection or dictionary-lookup logic below,
    # since those depend on already-stripped, already-clean text.
    # -----------------------------------------------------------------
    print("Applying general text cleaning...")
    text_cols = [c for c in df.columns if c not in ('amount', 'date')]
    for col in text_cols:
        df[col] = clean_text_series(df[col])

    # -----------------------------------------------------------------
    # STEP 2: office name / entity type fixes.
    # -----------------------------------------------------------------
    is_inactive = df['to_office_name'] == 'Inactive'
    name_lower = df['to_display_name'].astype(str).str.strip().str.lower()

    # Bedke split by year — KEPT AS-IS.
    is_bedke = is_inactive & (name_lower == 'scott bedke')
    df.loc[is_bedke & (df['elec_year'] == '2020'), 'to_office_name'] = 'State Representative - Seat A'
    df.loc[is_bedke & (df['elec_year'] == '2022'), 'to_office_name'] = 'Lieutenant Governor'

    # Original ~90-name Inactive lookup — KEPT AS-IS.
    for name_key, office_val in OFFICE_NAME_FIXES.items():
        mask = is_inactive & (name_lower == name_key) & (~is_bedke)
        df.loc[mask, 'to_office_name'] = office_val

    # NEW: Russ Fulcher reassigned to his last known Idaho state office,
    # NOT removed. Replaces the earlier removal logic entirely.
    is_fulcher = is_inactive & (name_lower == 'russ fulcher')
    df.loc[is_fulcher, 'to_office_name'] = FULCHER_OFFICE
    print(f"Reassigned {int(is_fulcher.sum())} Russ Fulcher rows to {FULCHER_OFFICE}.")

    # Any row still 'Inactive' after the above (no confirmed real-office
    # match) resolves to true NULL — KEPT AS-IS.
    still_inactive = df['to_office_name'] == 'Inactive'
    df.loc[still_inactive, 'to_office_name'] = None

    # NEW: individually-researched candidates whose raw to_office_name is
    # blank (not Inactive) — separate mask from the Inactive lookups above.
    is_blank_office = df['to_office_name'].isna()
    for name_key, office_val in NO_OFFICE_FIXES.items():
        mask = is_blank_office & (name_lower == name_key)
        df.loc[mask, 'to_office_name'] = office_val
    # NEW: corrected William Goesling key, applied the same way.
    for name_key, office_val in WILLIAM_GOESLING_FIX.items():
        mask = is_blank_office & (name_lower == name_key)
        df.loc[mask, 'to_office_name'] = office_val

    # NEW: James Hartley, split by elec_year.
    for year, (office_val, _) in JAMES_HARTLEY_BY_YEAR.items():
        mask = is_blank_office & (name_lower == 'james hartley') & (df['elec_year'] == year)
        df.loc[mask, 'to_office_name'] = office_val

    # NEW: "Could not be sourced" — real research attempted, no confident
    # match found, or an account opened with no candidacy ever declared.
    still_blank_office = df['to_office_name'].isna()
    could_not_source_mask = still_blank_office & name_lower.isin(COULD_NOT_BE_SOURCED_NAMES)
    df.loc[could_not_source_mask, 'to_office_name'] = COULD_NOT_BE_SOURCED_VALUE
    print(f"Set {int(could_not_source_mask.sum())} rows to '{COULD_NOT_BE_SOURCED_VALUE}'.")

    # Entity type corrections — KEPT AS-IS.
    for name, correct_type in ENTITY_TYPE_CORRECTIONS.items():
        mask = (df['to_display_name'] == name) & (df['to_entity_type'] == 'Candidate')
        df.loc[mask, 'to_entity_type'] = correct_type

    # -----------------------------------------------------------------
    # STEP 3: office_name standardization renames — KEPT AS-IS. Must run
    # before district-standardization logic, since several rules key off
    # to_office_name, and after all the name-lookup steps above, so every
    # candidate has their real office assigned before renames/grouping.
    # -----------------------------------------------------------------
    print("Standardizing office names...")
    df['to_office_name'] = df['to_office_name'].replace(OFFICE_NAME_RENAMES)

    # -----------------------------------------------------------------
    # STEP 4: from_state cleaning — EDITED ('0' no longer preserved).
    # -----------------------------------------------------------------
    print("Cleaning from_state...")
    df['from_state'] = [
        clean_state_value(s, c) for s, c in zip(df['from_state'], df['from_city'])
    ]
    raglan_mask = (df['from_city'] == 'Raglan') & (df['from_zip'].isin(['3225', '03225']))
    df.loc[raglan_mask, 'from_state'] = 'NH'

    # -----------------------------------------------------------------
    # STEP 5: from_city cleanup — KEPT AS-IS.
    # -----------------------------------------------------------------
    print("Cleaning from_city...")
    swap_mask = (
        df['from_city'].apply(looks_like_street_address)
        & df['from_address'].apply(looks_like_plain_place_name)
    )
    swapped_city = df.loc[swap_mask, 'from_address']
    swapped_address = df.loc[swap_mask, 'from_city']
    df.loc[swap_mask, 'from_city'] = swapped_city
    df.loc[swap_mask, 'from_address'] = swapped_address
    print(f"  Swapped city/address for {int(swap_mask.sum())} rows.")

    df['from_city'] = df['from_city'].replace(CITY_GLUED_TEXT_MAP)
    df['from_city'] = df['from_city'].replace(ZIP_IN_CITY_FIX)

    idaho_as_city_mask = df['from_city'] == 'Idaho'
    for zip_val, real_city in IDAHO_CITY_BY_ZIP.items():
        mask = idaho_as_city_mask & (df['from_zip'] == zip_val)
        df.loc[mask, 'from_city'] = real_city

    df['from_city'] = df['from_city'].apply(
        lambda v: None if pd.isna(v) or str(v).strip() in ('0', '--', '') else v
    )
    print("  from_city placeholder cleanup complete.")

    # -----------------------------------------------------------------
    # STEP 6: zip cleaning — KEPT AS-IS (692 keyed patch, blank-zip
    # backfill via exact address match).
    # -----------------------------------------------------------------
    print("Cleaning zip codes...")
    df['from_zip'] = [
        clean_zip_value(z, c) for z, c in zip(df['from_zip'], df['from_city'])
    ]
    df['to_zip'] = [clean_zip_value(z) for z in df['to_zip']]

    print("  Backfilling recoverable blank zip codes...")
    known_zip_lookup = (
        df.loc[df['from_zip'].notna(), ['from_address', 'from_city', 'from_state', 'from_zip']]
        .drop_duplicates(subset=['from_address', 'from_city', 'from_state'])
        .set_index(['from_address', 'from_city', 'from_state'])['from_zip']
    )
    blank_zip_mask = df['from_zip'].isna()
    lookup_keys = list(zip(df.loc[blank_zip_mask, 'from_address'],
                           df.loc[blank_zip_mask, 'from_city'],
                           df.loc[blank_zip_mask, 'from_state']))
    filled = [known_zip_lookup.get(k) for k in lookup_keys]
    df.loc[blank_zip_mask, 'from_zip'] = filled
    print(f"  Recovered {sum(1 for v in filled if v is not None)} zip codes via exact address match.")

    # -----------------------------------------------------------------
    # STEP 7: to_city cleanup — KEPT AS-IS.
    # -----------------------------------------------------------------
    print("Cleaning to_city...")
    df['to_city'] = df['to_city'].replace(TO_CITY_GLUED_STATE_MAP)

    # -----------------------------------------------------------------
    # STEP 8: judge district / statewide SW backfill — KEPT AS-IS, but now
    # benefits from the expanded LEGISLATIVE_DISTRICT_FIXES/NO_OFFICE_
    # LEGISLATIVE_DISTRICT_FIXES coverage from Step 2 above.
    # -----------------------------------------------------------------
    print("Fixing judge districts and statewide designation...")
    name_lower_current = df['to_display_name'].astype(str).str.strip().str.lower()
    needs_district_fix = df['to_district_name'].isin(['SW', 'COUNTY', 'KOOTENAI'])

    for judge_name, district_num in JUDGE_DISTRICT_FIXES.items():
        mask = needs_district_fix & (name_lower_current == judge_name) & \
               df['to_office_name'].isin(DISTRICT_REQUIRED_OFFICES)
        df.loc[mask, 'to_district_name'] = district_num

    for leg_name, district_num in LEGISLATIVE_DISTRICT_FIXES.items():
        mask = (df['to_district_name'] == 'SW') & (name_lower_current == leg_name) & \
               df['to_office_name'].isin(LEGISLATIVE_OFFICES)
        df.loc[mask, 'to_district_name'] = district_num

    # NEW: districts for the individually-researched no-office candidates.
    for leg_name, district_num in NO_OFFICE_LEGISLATIVE_DISTRICT_FIXES.items():
        mask = (name_lower_current == leg_name) & \
               df['to_office_name'].isin(LEGISLATIVE_OFFICES) & \
               (df['to_district_name'].isna() | (df['to_district_name'] == 'SW'))
        df.loc[mask, 'to_district_name'] = district_num

    # NEW: James Hartley's district, split by elec_year (paired with his
    # office assignment in Step 2).
    for year, (_, district_num) in JAMES_HARTLEY_BY_YEAR.items():
        mask = (name_lower_current == 'james hartley') & (df['elec_year'] == year) & \
               df['to_office_name'].isin(LEGISLATIVE_OFFICES)
        df.loc[mask, 'to_district_name'] = district_num

    sw_statewide_mask = (df['to_district_name'] == 'SW') & (df['to_office_name'].isin(STATEWIDE_OFFICES))
    df.loc[sw_statewide_mask, 'to_district_name'] = 'Statewide'

    # -----------------------------------------------------------------
    # STEP 9: full to_district_name "Type - Value" standardization —
    # KEPT AS-IS. Runs after every office-name resolution step above, so
    # every candidate (original + newly researched) is correctly grouped.
    # -----------------------------------------------------------------
    print("Standardizing to_district_name by office group...")
    df['to_district_name'] = _collapse_whitespace(df['to_district_name'])

    # NEW: Brian Bishop's one unresolved row — correct 'SW' to 'VALLIVUE'
    # before school-office standardization runs, so it matches his other
    # 6 rows and correctly resolves to 'VALLIVUE SCHOOL DISTRICT' below.
    bishop_mask = (name_lower_current == 'brian bishop') & \
                  (df['to_district_name'] == BISHOP_DISTRICT_FIX_FROM)
    df.loc[bishop_mask, 'to_district_name'] = BISHOP_DISTRICT_FIX_TO

    # NEW: Cole/Bartlett — genuinely blank to_district_name, filled in by
    # individual research rather than a blanket county default (Valley
    # County has two real districts). Anna Kinney intentionally omitted,
    # still unresolved as of this version.
    for name_key, district_val in SCHOOL_BLANK_DISTRICT_BY_NAME.items():
        mask = (name_lower_current == name_key) & (df['to_district_name'].isna())
        df.loc[mask, 'to_district_name'] = district_val

    office = df['to_office_name']
    reg = df['to_reg_district']

    county_mask = office.isin(COUNTY_WIDE_OFFICES)
    df.loc[county_mask, 'to_district_name'] = 'COUNTY - ' + reg.loc[county_mask].astype(str)

    statewide_mask = office.isin(STATEWIDE_OFFICES)
    df.loc[statewide_mask, 'to_district_name'] = 'STATEWIDE'

    legislative_mask = office.isin(LEGISLATIVE_OFFICES)
    df.loc[legislative_mask, 'to_district_name'] = (
        'LEGISLATURE - ' + df.loc[legislative_mask, 'to_district_name'].astype(str)
    )

    city_mask = office.isin(CITY_OFFICES)
    blank_city_mask = city_mask & df['to_district_name'].isna()
    df.loc[blank_city_mask, 'to_district_name'] = df.loc[blank_city_mask, 'to_city']
    normalized_city = df.loc[city_mask, 'to_district_name'].replace(CITY_DISTRICT_NORMALIZATION)
    df.loc[city_mask, 'to_district_name'] = 'CITY - ' + normalized_city.astype(str).str.upper()

    judicial_mask = office.isin(JUDICIAL_OFFICES)
    df.loc[judicial_mask, 'to_district_name'] = (
        'JUDICIAL - ' + df.loc[judicial_mask, 'to_district_name'].astype(str)
    )

    highway_mask = office.isin(HIGHWAY_OFFICES)
    df.loc[highway_mask, 'to_district_name'] = (
        'HIGHWAY - ' + df.loc[highway_mask, 'to_district_name'].astype(str)
    )

    library_mask = office.isin(LIBRARY_OFFICES)
    to_city_upper = df['to_city'].astype('string').str.upper()
    for city_key, district_val in LIBRARY_BLANK_BY_CITY.items():
        mask = library_mask & df['to_district_name'].isna() & (to_city_upper == city_key.upper())
        df.loc[mask, 'to_district_name'] = district_val
    normalized_library = df.loc[library_mask, 'to_district_name'].replace(LIBRARY_DISTRICT_NORMALIZATION)
    df.loc[library_mask, 'to_district_name'] = 'LIBRARY - ' + normalized_library.astype(str).str.upper()

    hospital_mask = office.isin(HOSPITAL_OFFICES)
    df.loc[hospital_mask, 'to_district_name'] = (
        'HOSPITAL - ' + df.loc[hospital_mask, 'to_district_name'].astype(str)
    )
    fire_mask = office.isin(FIRE_OFFICES)
    df.loc[fire_mask, 'to_district_name'] = (
        'FIRE - ' + df.loc[fire_mask, 'to_district_name'].astype(str)
    )

    school_mask = office.isin(SCHOOL_OFFICES)
    college_blank_mask = (df['to_office_name'] == 'Trustee College') & df['to_district_name'].isna()
    df.loc[college_blank_mask, 'to_district_name'] = 'NORTH IDAHO COLLEGE'
    normalized_school = df.loc[school_mask, 'to_district_name'].replace(SCHOOL_DISTRICT_NORMALIZATION)
    normalized_school = normalized_school.replace(COLLEGE_DISTRICT_NORMALIZATION)
    df.loc[school_mask, 'to_district_name'] = 'SCHOOL - ' + normalized_school.astype(str).str.upper()

    # -----------------------------------------------------------------
    # STEP 10: NEW — to_reg_district zip-to-county backfill.
    # Runs after to_zip is cleaned (Step 6). Independent of the office/
    # district chain above, since it operates on a different field.
    # -----------------------------------------------------------------
    print("Backfilling to_reg_district from zip code...")
    zip_to_county = build_zip_to_county_lookup(df)

    idaho_state_mask = df['to_reg_district'] == 'Idaho State'
    df.loc[idaho_state_mask, 'to_reg_district'] = df.loc[idaho_state_mask, 'to_zip'].map(zip_to_county)

    # Middleton override: force Canyon for every row with this zip,
    # including ones that already (incorrectly) show Ada.
    middleton_mask = df['to_zip'] == '83644'
    df.loc[middleton_mask, 'to_reg_district'] = REG_DISTRICT_ZIP_OVERRIDE['83644']

    # Rigby override: resolved by researched candidate name, not a
    # blanket zip value, since 83442 is officially split between two
    # real counties.
    to_name_lower = df['to_display_name'].astype(str).str.strip().str.lower()
    rigby_zip_mask = df['to_zip'] == RIGBY_ZIP
    for cand_name, county in REG_DISTRICT_RIGBY_BY_NAME.items():
        mask = rigby_zip_mask & (to_name_lower == cand_name)
        df.loc[mask, 'to_reg_district'] = county

    print(f"  to_reg_district backfill complete. Remaining 'Idaho State' rows: {(df['to_reg_district']=='Idaho State').sum()}.")

    # -----------------------------------------------------------------
    # STEP 11: elec_year cleaning — KEPT AS-IS.
    # -----------------------------------------------------------------
    print("Cleaning elec_year...")
    df['elec_year'] = df['elec_year'].apply(lambda x: None if pd.isna(x) or str(x).strip() in ('0', '') else x)

    # -----------------------------------------------------------------
    # STEP 12: from_display_name cleanup — KEPT AS-IS.
    # -----------------------------------------------------------------
    print("Cleaning from_display_name...")
    df['from_display_name'] = df['from_display_name'].apply(
        lambda v: None if pd.notna(v) and str(v).strip() == '1978' else v
    )

    # -----------------------------------------------------------------
    # STEP 13: NEW — Return amounts set to negative, so summing amount
    # directly nets returns out with no separate filter/subtraction step.
    # -----------------------------------------------------------------
    print("Setting Return amounts to negative...")
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    return_mask = df['donate_type'] == DONATE_TYPE_RETURN
    df.loc[return_mask, 'amount'] = -df.loc[return_mask, 'amount'].abs()
    print(f"  {int(return_mask.sum())} Return rows set to negative.")

    # -----------------------------------------------------------------
    # STEP 14: flags — KEPT AS-IS (missing_contr_data), NEW
    # (missing_state_data, missing_city_data).
    # -----------------------------------------------------------------
    print("Computing missing_contr_data flag...")
    df['missing_contr_data'] = (
        (df['donate_type'] != DONATE_TYPE_UNITEMIZED) & (df['from_display_name'].isna())
    ).map({True: 'Yes', False: 'No'})

    print("Computing missing_state_data / missing_city_data flags...")
    expected_gap_types = {DONATE_TYPE_UNITEMIZED, DONATE_TYPE_CREDIT_CARD_ITEM}
    not_expected_gap = ~df['donate_type'].isin(expected_gap_types)

    df['missing_state_data'] = (
        not_expected_gap & df['from_state'].isna()
    ).map({True: 'Yes', False: 'No'})

    df['missing_city_data'] = (
        not_expected_gap & df['from_city'].isna()
    ).map({True: 'Yes', False: 'No'})

    if os.path.exists(output_file):
        os.remove(output_file)

    print("Writing clean output file...")
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"Done. {len(df)} rows written.")
    print(f"Output: {output_file}")


if __name__ == '__main__':
    run()