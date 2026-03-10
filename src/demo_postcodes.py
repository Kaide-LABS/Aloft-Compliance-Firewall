"""Pre-vetted UK postcodes for reliable demo scenarios."""

DEMO_POSTCODES = {
    "GREEN": {
        "postcode": "SW1A 2AA",
        "company": "Foxtons",
        "expected": "GREEN verdict, low risk score, no violations",
        "talking_points": [
            "This property is fully compliant — clear to lease immediately",
            "EPC rating above minimum E threshold",
            "Management company is active and verified on Companies House",
            "All legal requirements from the Renters' Rights Act 2025 are satisfied",
        ],
    },
    "AMBER": {
        "postcode": "E1 6AN",
        "company": "",
        "expected": "AMBER verdict, moderate risk score, warnings but no violations",
        "talking_points": [
            "Property can proceed but needs attention",
            "EPC is at the legal minimum — consider upgrade",
            "The system catches upcoming expirations before they become violations",
            "This is the kind of risk that slips through manual checks",
        ],
    },
    "RED": {
        "postcode": "M1 1AA",
        "company": "DISSOLVED COMPANY LTD",
        "expected": "RED verdict, high risk score, critical violations",
        "talking_points": [
            "System caught a hard compliance violation — illegal to lease",
            "EPC below minimum E — fine up to £30,000",
            "Management company is dissolved — legal entity risk",
            "Without this firewall, the Leasing AI would have proceeded",
        ],
    },
}
