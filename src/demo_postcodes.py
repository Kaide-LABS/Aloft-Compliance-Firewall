"""Pre-vetted UK postcodes for reliable demo scenarios.

Verified against live EPC API on 2026-03-10:
  SW11 7AY -> EPC C (Flat D26, The Modern, Battersea) — lodged 2026-01-16
  SW8 4BG  -> EPC E (Studio Flat 1a, 8 Battersea Park Rd) — lodged 2025-07-05
  SE22 8EP -> EPC G (57 Lordship Lane, East Dulwich) — lodged 2025-04-07
"""

DEMO_POSTCODES = {
    "GREEN": {
        "postcode": "SW11 7AY",
        "company": "Foxtons",
        "expected": "GREEN verdict, low risk score, no violations",
        "talking_points": [
            "This property is fully compliant — clear to lease immediately",
            "EPC rating C, well above the minimum E threshold",
            "Management company is active and verified on Companies House",
            "All legal requirements from the Renters' Rights Act 2025 are satisfied",
        ],
    },
    "AMBER": {
        "postcode": "SW8 4BG",
        "company": "",
        "expected": "AMBER verdict, moderate risk score, warnings but no violations",
        "talking_points": [
            "Property can proceed but needs attention",
            "EPC rating E — at the legal minimum, consider upgrade",
            "No company provided — flags as potential risk for sole traders",
            "The system catches borderline compliance before it becomes a violation",
        ],
    },
    "RED": {
        "postcode": "SE22 8EP",
        "company": "DISSOLVED COMPANY LTD",
        "expected": "RED verdict, high risk score, critical violations",
        "talking_points": [
            "System caught a hard compliance violation — illegal to lease",
            "EPC rating G — well below minimum E, fine up to 30,000 pounds",
            "Management company is dissolved — legal entity risk",
            "Without this firewall, the Leasing AI would have proceeded",
        ],
    },
}
