SCENARIOS = {
    "steady_state": {
        "duplicate_pct": 0.01,
        "late_pct": 0.02,
        "malformed_pct": 0.001,
        "description": "Baseline daily production load.",
    },
    "merchant_burst": {
        "duplicate_pct": 0.02,
        "late_pct": 0.05,
        "malformed_pct": 0.002,
        "description": "Traffic spike concentrated on a small merchant cohort.",
    },
    "retry_storm": {
        "duplicate_pct": 0.08,
        "late_pct": 0.03,
        "malformed_pct": 0.001,
        "description": "Upstream retries create duplicate-heavy delivery pressure.",
    },
    "schema_drift": {
        "duplicate_pct": 0.01,
        "late_pct": 0.02,
        "malformed_pct": 0.02,
        "description": "Malformed records simulate contract drift and payload corruption.",
    },
}
