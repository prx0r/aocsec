"""Per-qualification verification methods. Data, not code paths."""

from __future__ import annotations

# qualification keyword -> how to verify without handling documents.
# urls verified live 2026-09-23 unless noted.
VERIFICATION_METHODS: dict[str, dict] = {
    "gas_safe": {
        "applies_to": ["plumber", "heating", "gas"],
        "method": "human_lookup",
        "register": "Gas Safe Register — find an engineer",
        "url": "https://www.gassaferegister.co.uk/find-an-engineer/",
        "note": "Bot-blocked (403 to scripts) — a human performs the "
                "lookup. Record business name + registration number only.",
    },
    "niceic": {
        "applies_to": ["electrician"],
        "method": "human_lookup",
        "register": "NICEIC Find a Tradesperson",
        "url": "https://www.niceic.com/find-a-tradesperson",
        "note": "Confirm enrolled status for notifiable work.",
    },
    "trustmark": {
        "applies_to": ["electrician", "plumber", "builder", "heating"],
        "method": "human_lookup",
        "register": "TrustMark directory",
        "url": "https://www.trustmark.org.uk/find-a-tradesperson",
        "note": "Government-endorsed quality mark lookup.",
    },
    "adi": {
        "applies_to": ["driving-instructors"],
        "method": "human_lookup",
        "register": "DVSA instructor records",
        "url": "https://www.gov.uk/become-a-driving-instructor",
        "note": "Confirm ADI registration + badge grade via DVSA.",
    },
    "companies_house": {
        "applies_to": ["all"],
        "method": "api",
        "register": "Companies House (free API key)",
        "url": "https://developer.company-information.service.gov.uk/",
        "note": "Automated via company/ module. Status, type, SIC only.",
    },
    "waste_carrier": {
        "applies_to": ["gardeners-window-cleaners", "cleaners"],
        "method": "human_lookup",
        "register": "Environment Agency public register",
        "url": "https://www.gov.uk/register-renew-waste-carrier-broker-dealer-england",
        "note": "Confirm tier + validity dates.",
    },
    "insurance": {
        "applies_to": ["all"],
        "method": "attestation",
        "register": "None public — customer attests",
        "url": "",
        "note": "Record policy type + renewal date attested by owner. "
                "Never collect policy documents.",
    },
}


def method_for(qualification: str) -> dict:
    """Verification method for a qualification keyword. Unknown keywords
    return the safe default: human lookup with no assumed register."""
    key = qualification.strip().lower().replace(" ", "_")
    if key in VERIFICATION_METHODS:
        return {"qualification": key, **VERIFICATION_METHODS[key]}
    return {
        "qualification": key,
        "method": "human_lookup",
        "register": "No known public register — research before asserting.",
        "url": "",
        "note": "Do not invent a verification path. Attestation only.",
    }
