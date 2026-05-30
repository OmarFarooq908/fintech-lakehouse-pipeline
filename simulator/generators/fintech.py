from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import json
import random
from typing import Any, Iterable


COUNTRIES = ["US", "CA", "GB", "DE", "FR", "IN", "SG", "AU"]
CURRENCIES = ["USD", "CAD", "GBP", "EUR", "INR", "SGD", "AUD"]
ACCOUNT_PRODUCTS = ["checking", "savings", "wallet", "merchant_settlement"]
CARD_BRANDS = ["visa", "mastercard", "amex"]
MCC_CODES = ["5411", "5732", "5812", "5944", "5999", "4121", "4814"]
RISK_REASONS = ["velocity", "ip_mismatch", "device_reuse", "chargeback_history", "sanctions_match"]
CHARGEBACK_REASONS = ["fraud", "duplicate", "product_not_received", "merchant_dispute"]
PAYMENT_STATUSES = ["authorized", "captured", "settled", "refunded"]

SCALE_PRESETS = {
    "dev": {"rows_per_request": 50_000, "merchant_count": 500, "customer_count": 10_000},
    "perf": {"rows_per_request": 500_000, "merchant_count": 5_000, "customer_count": 500_000},
    "stress": {"rows_per_request": 5_000_000, "merchant_count": 50_000, "customer_count": 5_000_000},
}


@dataclass(frozen=True)
class GenerationRequest:
    endpoint: str
    batch_id: str
    scale_tier: str = "dev"
    rows: int | None = None
    duplicate_pct: float = 0.01
    late_pct: float = 0.02
    malformed_pct: float = 0.001
    start_ts: datetime | None = None


def _seed(endpoint: str, batch_id: str) -> int:
    digest = hashlib.sha256(f"{endpoint}:{batch_id}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def _random_for_request(request: GenerationRequest) -> random.Random:
    return random.Random(_seed(request.endpoint, request.batch_id))


def _base_time(request: GenerationRequest) -> datetime:
    return request.start_ts or datetime.now(UTC).replace(microsecond=0)


def _resolve_row_count(request: GenerationRequest) -> int:
    preset = SCALE_PRESETS.get(request.scale_tier, SCALE_PRESETS["dev"])
    return request.rows or preset["rows_per_request"]


def _stable_hash(payload: dict[str, Any]) -> str:
    return hashlib.md5(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def _rand_amount(rng: random.Random, minimum: int = 100, maximum: int = 200_000) -> int:
    return rng.randint(minimum, maximum)


def _rand_country(rng: random.Random) -> str:
    return rng.choice(COUNTRIES)


def _rand_currency(rng: random.Random, country: str) -> str:
    mapping = {
        "US": "USD",
        "CA": "CAD",
        "GB": "GBP",
        "DE": "EUR",
        "FR": "EUR",
        "IN": "INR",
        "SG": "SGD",
        "AU": "AUD",
    }
    return mapping.get(country, rng.choice(CURRENCIES))


def _entity_suffix(index: int) -> str:
    return f"{index:012d}"


def _customer_record(index: int, rng: random.Random, event_ts: datetime) -> dict[str, Any]:
    country = _rand_country(rng)
    return {
        "customer_id": f"CUST_{_entity_suffix(index)}",
        "customer_segment": rng.choice(["consumer", "small_business", "enterprise"]),
        "country_code": country,
        "preferred_currency": _rand_currency(rng, country),
        "kyc_status": rng.choices(["pending", "approved", "rejected"], weights=[5, 92, 3], k=1)[0],
        "risk_band": rng.choices(["low", "medium", "high"], weights=[78, 18, 4], k=1)[0],
        "updated_at": event_ts.isoformat(),
    }


def _account_record(index: int, rng: random.Random, event_ts: datetime) -> dict[str, Any]:
    customer_index = rng.randint(1, max(index, 2))
    country = _rand_country(rng)
    return {
        "account_id": f"ACCT_{_entity_suffix(index)}",
        "customer_id": f"CUST_{_entity_suffix(customer_index)}",
        "product_type": rng.choice(ACCOUNT_PRODUCTS),
        "account_status": rng.choices(["active", "restricted", "closed"], weights=[94, 4, 2], k=1)[0],
        "country_code": country,
        "currency_code": _rand_currency(rng, country),
        "opened_at": (event_ts - timedelta(days=rng.randint(1, 3650))).isoformat(),
        "updated_at": event_ts.isoformat(),
    }


def _card_record(index: int, rng: random.Random, event_ts: datetime) -> dict[str, Any]:
    account_index = rng.randint(1, max(index, 2))
    return {
        "card_id": f"CARD_{_entity_suffix(index)}",
        "account_id": f"ACCT_{_entity_suffix(account_index)}",
        "card_brand": rng.choice(CARD_BRANDS),
        "card_type": rng.choice(["debit", "credit", "virtual"]),
        "card_status": rng.choices(["active", "blocked", "expired"], weights=[91, 5, 4], k=1)[0],
        "issued_at": (event_ts - timedelta(days=rng.randint(1, 1825))).isoformat(),
        "updated_at": event_ts.isoformat(),
    }


def _merchant_record(index: int, rng: random.Random, event_ts: datetime) -> dict[str, Any]:
    country = _rand_country(rng)
    return {
        "merchant_id": f"MERCH_{_entity_suffix(index)}",
        "merchant_name": f"Merchant {index}",
        "merchant_country": country,
        "merchant_category_code": rng.choice(MCC_CODES),
        "pricing_tier": rng.choices(["standard", "plus", "strategic"], weights=[85, 12, 3], k=1)[0],
        "updated_at": event_ts.isoformat(),
    }


def _payment_event_record(index: int, rng: random.Random, event_ts: datetime) -> dict[str, Any]:
    customer_index = rng.randint(1, max(index, 2))
    account_index = rng.randint(1, max(index, 2))
    card_index = rng.randint(1, max(index, 2))
    merchant_index = rng.randint(1, max(index // 10, 2))
    country = _rand_country(rng)
    amount_minor = _rand_amount(rng)
    status = rng.choices(PAYMENT_STATUSES, weights=[45, 28, 22, 5], k=1)[0]
    return {
        "payment_event_id": f"PAYEVT_{_entity_suffix(index)}",
        "payment_id": f"PAY_{_entity_suffix(index // 2 + 1)}",
        "customer_id": f"CUST_{_entity_suffix(customer_index)}",
        "account_id": f"ACCT_{_entity_suffix(account_index)}",
        "card_id": f"CARD_{_entity_suffix(card_index)}",
        "merchant_id": f"MERCH_{_entity_suffix(merchant_index)}",
        "payment_status": status,
        "country_code": country,
        "currency_code": _rand_currency(rng, country),
        "amount_minor": amount_minor,
        "fee_minor": int(amount_minor * rng.uniform(0.005, 0.03)),
        "event_ts": event_ts.isoformat(),
        "ingested_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }


def _chargeback_record(index: int, rng: random.Random, event_ts: datetime) -> dict[str, Any]:
    payment_index = rng.randint(1, max(index * 10, 2))
    amount_minor = _rand_amount(rng, minimum=500, maximum=100_000)
    return {
        "chargeback_id": f"CB_{_entity_suffix(index)}",
        "payment_id": f"PAY_{_entity_suffix(payment_index)}",
        "merchant_id": f"MERCH_{_entity_suffix(rng.randint(1, max(index, 2)))}",
        "chargeback_reason": rng.choice(CHARGEBACK_REASONS),
        "chargeback_status": rng.choices(["open", "won", "lost"], weights=[55, 20, 25], k=1)[0],
        "amount_minor": amount_minor,
        "event_ts": event_ts.isoformat(),
    }


def _risk_event_record(index: int, rng: random.Random, event_ts: datetime) -> dict[str, Any]:
    payment_index = rng.randint(1, max(index * 10, 2))
    return {
        "risk_event_id": f"RISK_{_entity_suffix(index)}",
        "payment_id": f"PAY_{_entity_suffix(payment_index)}",
        "device_id": f"DEV_{_entity_suffix(rng.randint(1, max(index // 2, 2)))}",
        "risk_reason": rng.choice(RISK_REASONS),
        "risk_score": round(rng.uniform(0.01, 0.99), 4),
        "decision": rng.choices(["approve", "review", "decline"], weights=[85, 10, 5], k=1)[0],
        "event_ts": event_ts.isoformat(),
    }


def _fx_rate_record(index: int, rng: random.Random, event_ts: datetime) -> dict[str, Any]:
    base_currency = "USD"
    quote_currency = rng.choice([currency for currency in CURRENCIES if currency != base_currency])
    return {
        "fx_rate_id": f"FX_{_entity_suffix(index)}",
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "rate_date": event_ts.date().isoformat(),
        "conversion_rate": round(rng.uniform(0.5, 95.0), 6),
        "event_ts": event_ts.isoformat(),
    }


GENERATORS = {
    "customers": _customer_record,
    "accounts": _account_record,
    "cards": _card_record,
    "merchants": _merchant_record,
    "payment_events": _payment_event_record,
    "chargebacks": _chargeback_record,
    "risk_events": _risk_event_record,
    "fx_rates": _fx_rate_record,
}


def generate_records(request: GenerationRequest) -> Iterable[dict[str, Any]]:
    if request.endpoint not in GENERATORS:
        raise ValueError(f"Unsupported endpoint: {request.endpoint}")

    rng = _random_for_request(request)
    generator = GENERATORS[request.endpoint]
    row_count = _resolve_row_count(request)
    base_time = _base_time(request)

    duplicates_remaining = int(row_count * request.duplicate_pct)
    malformed_every = max(int(1 / request.malformed_pct), 1) if request.malformed_pct else None

    for index in range(1, row_count + 1):
        event_ts = base_time + timedelta(seconds=index % 86_400)
        if rng.random() < request.late_pct:
            event_ts = event_ts - timedelta(days=rng.randint(1, 3))

        payload = generator(index=index, rng=rng, event_ts=event_ts)
        payload.update(
            {
                "source_endpoint": request.endpoint,
                "ingestion_batch_id": request.batch_id,
                "payload_hash": "",
                "arrived_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
                "is_late_arrival": event_ts < base_time,
            }
        )
        payload["payload_hash"] = _stable_hash(payload)
        yield payload

        if duplicates_remaining > 0 and rng.random() < request.duplicate_pct:
            duplicates_remaining -= 1
            yield payload.copy()

        if malformed_every and index % malformed_every == 0:
            malformed_payload = {
                "source_endpoint": request.endpoint,
                "ingestion_batch_id": request.batch_id,
                "error": "synthetic_malformed_payload",
                "arrived_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
            }
            malformed_payload["payload_hash"] = _stable_hash(malformed_payload)
            yield malformed_payload


def build_manifest(request: GenerationRequest) -> dict[str, Any]:
    row_count = _resolve_row_count(request)
    duplicates = int(row_count * request.duplicate_pct)
    late_rows = int(row_count * request.late_pct)
    malformed_rows = int(row_count * request.malformed_pct)
    return {
        "ingestion_batch_id": request.batch_id,
        "source_endpoint": request.endpoint,
        "scale_tier": request.scale_tier,
        "requested_rows": row_count,
        "expected_duplicate_rows": duplicates,
        "expected_late_rows": late_rows,
        "expected_malformed_rows": malformed_rows,
    }
