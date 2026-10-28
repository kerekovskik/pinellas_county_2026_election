# Research brief: Pinellas County 2026 General Election voter guide

Today is October 27, 2026. Election Day is November 3, 2026. Early voting is underway.
Your knowledge cutoff predates most of this campaign, so you MUST use WebSearch (mode "extended"
for anything thin) and WebFetch to get CURRENT facts. Do not rely on memory for polling, money,
endorsements, or results of the August 18, 2026 primaries.

The ballot (authoritative list of contests and candidates) is at:
/Users/kerekovskik/repos/pinellas_county_2026_election/pinellas-2026-general-election-ballot.md
Read it first. Only research the candidates in YOUR assigned section (given in your prompt).

## Honesty rules (most important)
- Never invent a number. If no public poll exists for a race, write polling: "No public poll",
  pollingStatus: "No public polling", and explain in pollingDetails what IS known (primary result
  margins, district partisan lean, incumbency, etc.).
- Campaign finance: use FEC (federal), Florida Division of Elections (state), Pinellas SOE
  campaign finance reports (county/municipal) or news reports summarizing them. Give the report
  date. If you cannot find a figure, write raised: "Not found" and set raisedNumeric/spentNumeric to 0.
- Every candidate record must carry a `sources` array of the URLs you actually used.
- Mark anything uncertain in the text itself ("reportedly", "per Florida Politics, Oct 2026").
- For LGBTQ+ stance, base it on votes, public statements, endorsements (Equality Florida, HRC,
  Stonewall Dems, Victory Fund, Moms for Liberty, Florida Family Policy Council, etc.). If there is
  no record, say so: lgbtqStance "Neutral / Standard", lgbtqBadge "⚖️ No Public Record".
- For controversies, only include things reported by identifiable outlets; name the outlet.

## Alignment taxonomy (pick exactly one `alignment` value)
- "Progressive"  — left of Democratic establishment; labor/grassroots; DSA/Progressive Caucus
- "Establishment" — mainstream Democratic / center-left institutional
- "Conservative Establishment" — Republican / conservative
- "Nonpartisan / Moderate" — nonpartisan office-holder with no clear partisan lane, or judges
- "Independent / Third Party" — LPF, NPA, write-in candidates
`alignmentBadge` is a short free-text label with the matching emoji prefix:
🟢 Progressive, 🔵 Establishment, 🔴 Conservative Establishment, ⚪ Nonpartisan / Moderate, 🟡 Independent / Third Party

## LGBTQ+ stance taxonomy (pick exactly one `lgbtqStance` value)
"Vanguard" (🏳️‍🌈 outspoken champion / openly LGBTQ+ / Victory Fund), "Consistent Support" (✅),
"Neutral / Standard" (⚖️), "Opposed / Culture War" (⚠️ supported HB 1557, SB 254, book removals,
Moms for Liberty-backed, etc.)

## Candidate record schema (write valid JSON, an array of these)
{
  "id": "lastname",                // lowercase letters only; unique; for tickets use governor's last name
  "name": "Full Name",             // for Gov tickets: "Byron Donalds / Brian Avila"
  "party": "REP" | "DEM" | "LPF" | "NPA" | "WRI" | "Nonpartisan",
  "incumbent": true | false,
  "contest": "exact contest title from the ballot markdown",
  "category": "short category given in your prompt",
  "alignment": "...", "alignmentBadge": "...",
  "polling": "50%" | "No public poll",
  "pollingStatus": "Leading (+8%)" | "Trailing (-8%)" | "Toss-up" | "No public polling" | "Heavy favorite" ...,
  "pollingDetails": "1-3 sentences; name pollster, date, sample, and general-election matchup numbers",
  "raised": "$1.2M ($400k COH, FEC Oct 15 2026)" | "Not found",
  "raisedNumeric": 1200000, "spentNumeric": 800000,
  "backers": "major donor groups / PACs / unions, comma-separated",
  "lgbtqStance": "...", "lgbtqBadge": "...", "lgbtqDetails": "1-2 sentences with evidence",
  "platform": "2-3 sentences: background + top policy positions",
  "controversy": "1-3 sentences, with the outlet named; or 'None significant reported.'",
  "endorsements": "comma-separated notable endorsements",
  "primaryResult": "won Aug 18 primary 54%-46% over X" | "unopposed in primary" | "n/a",
  "sources": ["https://...", "..."]
}

## Output
Write your JSON array to the file path given in your prompt (use the Write tool). Then reply with
a SHORT summary (under 200 words): how many records, which candidates had thin information, and
any notable cross-race context (e.g., statewide polling environment) that the page author should know.
Work efficiently: batch several WebSearch calls in one turn. Aim for depth on competitive, high-profile
races and brevity on obscure ones, but every candidate needs a complete record.
