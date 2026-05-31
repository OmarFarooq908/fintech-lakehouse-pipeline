from __future__ import annotations

from datetime import UTC, datetime
import json
import os
from typing import Iterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

from generators.fintech import GENERATORS, GenerationRequest, build_manifest, generate_records


app = FastAPI(
    title="Synthetic Fintech API",
    description="Synthetic batch API used to stress-test Airflow, DuckDB, and dbt pipelines.",
    version="1.0.0",
)


def _request_from_query(
    endpoint: str,
    batch_id: str | None,
    scale_tier: str,
    rows: int | None,
    duplicate_pct: float,
    late_pct: float,
    malformed_pct: float,
) -> GenerationRequest:
    if endpoint not in GENERATORS:
        raise HTTPException(status_code=404, detail=f"Unsupported endpoint: {endpoint}")

    return GenerationRequest(
        endpoint=endpoint,
        batch_id=batch_id or f"{endpoint}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        scale_tier=scale_tier,
        rows=rows,
        duplicate_pct=duplicate_pct,
        late_pct=late_pct,
        malformed_pct=malformed_pct,
    )


def _ndjson_stream(request: GenerationRequest) -> Iterator[bytes]:
    for record in generate_records(request):
        yield (json.dumps(record) + "\n").encode("utf-8")


@app.get("/health")
def healthcheck() -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "service": "synthetic-fintech-api",
            "default_scale_tier": os.getenv("SIMULATOR_SCALE_TIER", "dev"),
        }
    )


@app.get("/v1/endpoints")
def list_endpoints() -> JSONResponse:
    return JSONResponse({"endpoints": sorted(GENERATORS.keys())})


@app.get("/v1/{endpoint}")
def stream_endpoint(
    endpoint: str,
    batch_id: str | None = Query(default=None),
    scale_tier: str = Query(default=os.getenv("SIMULATOR_SCALE_TIER", "dev")),
    rows: int | None = Query(default=None, ge=1),
    duplicate_pct: float = Query(default=0.01, ge=0.0, le=0.5),
    late_pct: float = Query(default=0.02, ge=0.0, le=0.5),
    malformed_pct: float = Query(default=0.001, ge=0.0, le=0.05),
) -> StreamingResponse:
    request = _request_from_query(
        endpoint=endpoint,
        batch_id=batch_id,
        scale_tier=scale_tier,
        rows=rows,
        duplicate_pct=duplicate_pct,
        late_pct=late_pct,
        malformed_pct=malformed_pct,
    )
    return StreamingResponse(_ndjson_stream(request), media_type="application/x-ndjson")


@app.get("/v1/{endpoint}/manifest")
def endpoint_manifest(
    endpoint: str,
    batch_id: str | None = Query(default=None),
    scale_tier: str = Query(default=os.getenv("SIMULATOR_SCALE_TIER", "dev")),
    rows: int | None = Query(default=None, ge=1),
    duplicate_pct: float = Query(default=0.01, ge=0.0, le=0.5),
    late_pct: float = Query(default=0.02, ge=0.0, le=0.5),
    malformed_pct: float = Query(default=0.001, ge=0.0, le=0.05),
) -> JSONResponse:
    request = _request_from_query(
        endpoint=endpoint,
        batch_id=batch_id,
        scale_tier=scale_tier,
        rows=rows,
        duplicate_pct=duplicate_pct,
        late_pct=late_pct,
        malformed_pct=malformed_pct,
    )
    manifest = build_manifest(request)
    manifest["generated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    return JSONResponse(manifest)
