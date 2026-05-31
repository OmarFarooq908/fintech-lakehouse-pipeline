from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
from typing import Any
from uuid import uuid4

import pyarrow as pa
import pyarrow.parquet as pq

from .fintech import GenerationRequest, build_manifest, generate_records


RAW_PARQUET_SCHEMA = pa.schema(
    [
        ("ingestion_batch_id", pa.string()),
        ("source_endpoint", pa.string()),
        ("event_ts", pa.string()),
        ("arrived_at", pa.string()),
        ("payload_hash", pa.string()),
        ("load_status", pa.string()),
        ("is_malformed", pa.bool_()),
        ("raw_payload", pa.string()),
        ("loaded_at", pa.string()),
        ("partition_date", pa.string()),
        ("partition_hour", pa.string()),
    ]
)


def _parse_timestamp(value: str | None, fallback_value: str) -> datetime:
    candidate = value or fallback_value
    normalized = candidate.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _to_raw_row(record: dict[str, Any], loaded_at: str) -> dict[str, Any]:
    event_reference = record.get("event_ts") or record.get("updated_at")
    arrived_at = str(record.get("arrived_at", loaded_at))
    event_time = _parse_timestamp(event_reference, arrived_at)
    payload_json = json.dumps(record, sort_keys=True, separators=(",", ":"))
    is_malformed = "error" in record

    return {
        "ingestion_batch_id": str(record.get("ingestion_batch_id")),
        "source_endpoint": str(record.get("source_endpoint")),
        "event_ts": event_time.isoformat(),
        "arrived_at": arrived_at,
        "payload_hash": str(record.get("payload_hash")),
        "load_status": "QUARANTINED" if is_malformed else "LOADED",
        "is_malformed": is_malformed,
        "raw_payload": payload_json,
        "loaded_at": loaded_at,
        "partition_date": event_time.date().isoformat(),
        "partition_hour": f"{event_time.hour:02d}",
    }


def _write_chunk(rows: list[dict[str, Any]], endpoint_root: Path) -> None:
    if not rows:
        return

    table = pa.Table.from_pylist(rows, schema=RAW_PARQUET_SCHEMA)
    pq.write_to_dataset(
        table,
        root_path=str(endpoint_root),
        partition_cols=["ingestion_batch_id", "partition_date", "partition_hour"],
        compression="zstd",
        basename_template=f"part-{uuid4().hex}-{{i}}.parquet",
        existing_data_behavior="overwrite_or_ignore",
    )


def write_raw_batch_to_lakehouse(
    request: GenerationRequest,
    raw_root: str | Path,
    manifest_root: str | Path,
    chunk_rows: int = 100_000,
) -> dict[str, Any]:
    raw_root_path = Path(raw_root)
    manifest_root_path = Path(manifest_root)
    endpoint_root = raw_root_path / request.endpoint
    batch_root = endpoint_root / f"ingestion_batch_id={request.batch_id}"
    manifest_root_path.mkdir(parents=True, exist_ok=True)
    endpoint_root.mkdir(parents=True, exist_ok=True)

    if batch_root.exists():
        shutil.rmtree(batch_root)

    loaded_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    chunk: list[dict[str, Any]] = []
    delivered_rows = 0
    late_rows = 0
    malformed_rows = 0

    for record in generate_records(request):
        delivered_rows += 1
        late_rows += int(bool(record.get("is_late_arrival")))
        malformed_rows += int("error" in record)
        chunk.append(_to_raw_row(record, loaded_at))
        if len(chunk) >= chunk_rows:
            _write_chunk(chunk, endpoint_root)
            chunk.clear()

    _write_chunk(chunk, endpoint_root)

    file_count = sum(1 for _ in batch_root.rglob("*.parquet"))
    manifest = build_manifest(request)
    manifest.update(
        {
            "delivered_rows": delivered_rows,
            "duplicate_rows": manifest["expected_duplicate_rows"],
            "late_rows": late_rows,
            "malformed_rows": malformed_rows,
            "file_name": str(batch_root.relative_to(raw_root_path)),
            "storage_path": str(batch_root),
            "file_count": file_count,
            "chunk_rows": chunk_rows,
        }
    )

    manifest_path = manifest_root_path / request.endpoint / f"{request.batch_id}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))
    manifest["manifest_path"] = str(manifest_path)
    return manifest
