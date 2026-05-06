"""
DataScout demo API - lightweight FastAPI backend for classroom demos.

This version avoids heavy ML/vector dependencies and uses synthetic CSV seed data.
It is intentionally deterministic and fast to run locally.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import random

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
UPLOAD_DIR = DATA_DIR / "uploads"
MANIFEST_PATH = SYNTHETIC_DIR / "manifest.json"

SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="DataScout Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATASETS: dict[int, dict[str, Any]] = {}


def _value_for_column(column: str, idx: int) -> Any:
    c = column.lower()
    if "id" in c:
        return f"ID{idx:06d}"
    if "date" in c or "time" in c or "at" == c[-2:]:
        return f"2026-03-{(idx % 28) + 1:02d}"
    if "amount" in c or "balance" in c or "income" in c or "value" in c or "price" in c:
        return round(50 + (idx * 13.7) % 5000, 2)
    if "score" in c or "quality" in c or "probability" in c or "rate" in c:
        return round((idx * 7) % 100, 2)
    if "fraud" in c or "pii" in c or c.startswith("is_") or c.startswith("has_"):
        return idx % 7 == 0
    if "currency" in c:
        return random.choice(["USD", "EUR", "GBP"])
    if "country" in c:
        return random.choice(["TN", "FR", "US", "DE"])
    if "status" in c:
        return random.choice(["completed", "pending", "approved", "rejected"])
    if "category" in c or "type" in c or "segment" in c:
        return random.choice(["retail", "risk", "credit", "customer", "operations"])
    if "email" in c:
        return f"client{idx}@example.com"
    if "name" in c:
        return f"Demo {column.title()} {idx}"
    return f"{column}_{idx}"


def _ensure_demo_csv(filename: str, columns: list[str]) -> Path:
    path = SYNTHETIC_DIR / filename
    if path.exists():
        return path
    rows = []
    safe_columns = columns or ["id", "amount", "category", "date", "status"]
    for i in range(1, 101):
        rows.append({col: _value_for_column(col, i) for col in safe_columns})
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _quality_detail(dataset_id: int, score: int) -> dict[str, Any]:
    grade = "A" if score >= 90 else "B" if score >= 80 else "C"
    return {
        "id": dataset_id,
        "dataset_id": dataset_id,
        "completeness": min(score + 4, 100),
        "consistency": max(score - 2, 0),
        "uniqueness": max(score - 8, 0),
        "validity": min(score + 2, 100),
        "timeliness": max(score - 5, 0),
        "overall_score": score,
        "grade": grade,
        "details": {"mode": "demo", "computed_from": "synthetic metadata"},
        "recommendations": [
            "Check missing values before production use.",
            "Validate PII columns and access permissions.",
        ],
        "created_at": datetime.now().isoformat(),
    }


def _profile_for_csv(dataset_id: int, path: Path) -> list[dict[str, Any]]:
    try:
        df = pd.read_csv(path, nrows=100)
    except Exception:
        df = pd.DataFrame({"id": [1, 2, 3], "amount": [100, 250, 175], "category": ["A", "B", "A"]})

    profiles: list[dict[str, Any]] = []
    for idx, col in enumerate(df.columns):
        series = df[col]
        is_numeric = pd.api.types.is_numeric_dtype(series)
        missing = int(series.isna().sum())
        is_pii = any(key in col.lower() for key in ["email", "phone", "ssn", "name", "address", "card"])
        profiles.append({
            "id": idx + 1,
            "dataset_id": dataset_id,
            "column_name": col,
            "column_index": idx,
            "raw_dtype": str(series.dtype),
            "inferred_type": "numeric" if is_numeric else "categorical",
            "missing_count": missing,
            "missing_pct": round((missing / max(len(series), 1)) * 100, 2),
            "unique_count": int(series.nunique(dropna=True)),
            "mean": float(series.mean()) if is_numeric else None,
            "median": float(series.median()) if is_numeric else None,
            "std_dev": float(series.std()) if is_numeric and len(series) > 1 else None,
            "min_value": float(series.min()) if is_numeric else None,
            "max_value": float(series.max()) if is_numeric else None,
            "distribution": None,
            "outlier_count": 0,
            "sample_values": series.dropna().head(5).tolist(),
            "is_pii": is_pii,
            "pii_detected": is_pii,
            "pii_type": "personal" if is_pii else None,
        })
    return profiles


def _dataset_from_manifest(dataset_id: int, item: dict[str, Any]) -> dict[str, Any]:
    path = _ensure_demo_csv(item.get("filename", f"dataset_{dataset_id}.csv"), item.get("column_names", []))
    score = int(float(item.get("quality_level", 0.88)) * 100)
    created_at = "2026-03-06T21:00:40"
    dataset = {
        "id": dataset_id,
        "name": item.get("name", f"dataset_{dataset_id}"),
        "description": f"Synthetic banking dataset: {item.get('name', f'dataset_{dataset_id}')}",
        "source": "synthetic seed pack",
        "file_path": str(path),
        "file_format": "csv",
        "file_size": path.stat().st_size if path.exists() else int(item.get("size_bytes", 0)),
        "file_size_bytes": path.stat().st_size if path.exists() else int(item.get("size_bytes", 0)),
        "row_count": int(item.get("rows", 100)),
        "column_count": int(item.get("columns", len(item.get("column_names", [])) or 5)),
        "quality_score": score,
        "status": "completed",
        "error_message": None,
        "created_at": created_at,
        "processed_at": created_at,
        "uploaded_at": created_at,
        "has_pii": bool(item.get("has_pii", False)),
        "tags": [
            {"id": dataset_id * 10 + 1, "category": "domain", "value": "Finance", "tag_category": "domain", "tag_value": "Finance", "confidence": 0.95, "method": "demo", "created_at": created_at},
            {"id": dataset_id * 10 + 2, "category": "data_type", "value": "CSV", "tag_category": "format", "tag_value": "CSV", "confidence": 1.0, "method": "demo", "created_at": created_at},
        ],
    }
    dataset["column_profiles"] = _profile_for_csv(dataset_id, path)
    dataset["quality_score_detail"] = _quality_detail(dataset_id, score)
    dataset["quality_details"] = dataset["quality_score_detail"]
    dataset["dashboard_config"] = _dashboard_for_dataset(dataset)
    return dataset


def _dashboard_for_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    columns = dataset.get("column_profiles", [])
    numeric = next((c for c in columns if c["inferred_type"] == "numeric"), None)
    categorical = next((c for c in columns if c["inferred_type"] != "numeric"), None)
    charts = [
        {
            "chart_type": "histogram",
            "type": "histogram",
            "title": f"Distribution of {(numeric or {'column_name': 'amount'})['column_name']}",
            "column": (numeric or {"column_name": "amount"})["column_name"],
            "data": [
                {"bin_start": 0, "bin_end": 100, "count": 12},
                {"bin_start": 100, "bin_end": 500, "count": 35},
                {"bin_start": 500, "bin_end": 1000, "count": 26},
                {"bin_start": 1000, "bin_end": 5000, "count": 18},
            ],
        },
        {
            "chart_type": "pie",
            "type": "pie",
            "title": f"Breakdown by {(categorical or {'column_name': 'category'})['column_name']}",
            "column": (categorical or {"column_name": "category"})["column_name"],
            "data": [
                {"name": "credit", "value": 35},
                {"name": "risk", "value": 25},
                {"name": "customer", "value": 20},
                {"name": "operations", "value": 20},
            ],
        },
        {
            "chart_type": "missing",
            "type": "missing_values",
            "title": "Missing values overview",
            "data": [
                {"column": c["column_name"], "missing_pct": c["missing_pct"], "missing_count": c["missing_count"]}
                for c in columns[:8]
            ],
        },
    ]
    return {
        "id": dataset["id"],
        "dataset_id": dataset["id"],
        "charts": charts,
        "kpis": [],
        "filters": [],
        "layout": {"columns": 2, "rows": 2, "chart_height": 320},
        "created_at": datetime.now().isoformat(),
        "generated_at": datetime.now().isoformat(),
        "summary": {"mode": "demo"},
    }


def load_demo_data() -> None:
    DATASETS.clear()
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text())
        for idx, item in enumerate(manifest.get("datasets", [])[:30], start=1):
            DATASETS[idx] = _dataset_from_manifest(idx, item)
    if not DATASETS:
        fallback = {
            "name": "credit_risk_demo",
            "filename": "credit_risk_demo.csv",
            "rows": 100,
            "columns": 5,
            "quality_level": 0.91,
            "has_pii": False,
            "column_names": ["customer_id", "amount", "credit_score", "segment", "status"],
        }
        DATASETS[1] = _dataset_from_manifest(1, fallback)


load_demo_data()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/stats")
async def get_stats() -> dict[str, Any]:
    total_rows = sum(int(d.get("row_count") or 0) for d in DATASETS.values())
    avg_quality = sum(int(d.get("quality_score") or 0) for d in DATASETS.values()) / max(len(DATASETS), 1)
    return {
        "total_datasets": len(DATASETS),
        "total_rows": total_rows,
        "avg_quality": round(avg_quality, 1),
        "domain_count": 6,
        "domains": 6,
    }


@app.get("/api/v1/datasets/search")
async def search_datasets(q: str, limit: int = 10) -> list[dict[str, Any]]:
    q_lower = q.lower()
    results = []
    for d in DATASETS.values():
        text = f"{d['name']} {d.get('description') or ''} {' '.join(t['value'] for t in d.get('tags', []))}".lower()
        if q_lower in text:
            results.append({
                "dataset_id": d["id"],
                "name": d["name"],
                "description": d.get("description"),
                "relevance_score": 0.92,
                "matched_columns": [c["column_name"] for c in d.get("column_profiles", [])[:3]],
                "snippet": d.get("description"),
            })
    return results[:limit]


@app.get("/api/v1/search")
async def legacy_search(q: str) -> dict[str, Any]:
    results = await search_datasets(q, limit=20)
    return {"results": results, "total": len(results)}


@app.get("/api/v1/datasets")
async def list_datasets(
    skip: int = Query(0, ge=0),
    page: Optional[int] = Query(None, ge=1),
    limit: int = Query(10, ge=1, le=100),
    q: Optional[str] = None,
    search_name: Optional[str] = None,
    format: Optional[str] = None,
    min_quality: Optional[int] = None,
    sort_by: str = "created_at",
    sort_desc: bool = True,
) -> dict[str, Any]:
    items = list(DATASETS.values())
    query = (q or search_name or "").lower().strip()
    if query:
        items = [d for d in items if query in d["name"].lower() or query in (d.get("description") or "").lower()]
    if format:
        items = [d for d in items if d.get("file_format") == format]
    if min_quality is not None:
        items = [d for d in items if int(d.get("quality_score") or 0) >= min_quality]
    reverse = bool(sort_desc)
    items.sort(key=lambda d: d.get(sort_by) or "", reverse=reverse)
    if page is not None:
        skip = (page - 1) * limit
    total = len(items)
    return {"items": items[skip: skip + limit], "total": total, "skip": skip, "limit": limit}


@app.get("/api/v1/datasets/{dataset_id}")
async def get_dataset(dataset_id: int) -> dict[str, Any]:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DATASETS[dataset_id]


@app.delete("/api/v1/datasets/{dataset_id}", status_code=204)
async def delete_dataset(dataset_id: int) -> None:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    del DATASETS[dataset_id]


@app.post("/api/v1/datasets/{dataset_id}/reprocess")
async def reprocess_dataset(dataset_id: int) -> dict[str, Any]:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    DATASETS[dataset_id]["processed_at"] = datetime.now().isoformat()
    return DATASETS[dataset_id]


@app.get("/api/v1/datasets/{dataset_id}/profile")
async def get_profile(dataset_id: int) -> list[dict[str, Any]]:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DATASETS[dataset_id].get("column_profiles", [])


@app.get("/api/v1/datasets/{dataset_id}/quality")
async def get_quality(dataset_id: int) -> dict[str, Any]:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DATASETS[dataset_id]["quality_score_detail"]


@app.get("/api/v1/datasets/{dataset_id}/tags")
async def get_tags(dataset_id: int) -> list[dict[str, Any]]:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DATASETS[dataset_id].get("tags", [])


@app.get("/api/v1/datasets/{dataset_id}/preview")
async def get_preview(dataset_id: int, rows: int = 50, offset: int = 0) -> dict[str, Any]:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    path = Path(DATASETS[dataset_id]["file_path"])
    df = pd.read_csv(path).iloc[offset: offset + rows]
    data = df.where(pd.notnull(df), None).values.tolist()
    return {
        "columns": list(df.columns),
        "data": data,
        "rows": data,
        "total_rows": int(DATASETS[dataset_id].get("row_count") or len(df)),
        "preview_rows": len(data),
    }


@app.get("/api/v1/datasets/{dataset_id}/dashboard")
async def get_dashboard(dataset_id: int) -> dict[str, Any]:
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return DATASETS[dataset_id]["dashboard_config"]


@app.post("/api/v1/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = None,
    description: Optional[str] = None,
    source: Optional[str] = None,
) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    path = UPLOAD_DIR / Path(file.filename).name
    content = await file.read()
    path.write_bytes(content)
    try:
        df = pd.read_csv(path, nrows=100)
        columns = list(df.columns)
        row_count = len(pd.read_csv(path, usecols=[columns[0]])) if columns else 0
    except Exception:
        columns = ["id", "value"]
        row_count = 0
    dataset_id = max(DATASETS.keys(), default=0) + 1
    item = {
        "name": name or path.stem,
        "filename": path.name,
        "rows": row_count,
        "columns": len(columns),
        "quality_level": 0.85,
        "has_pii": any("email" in c.lower() or "name" in c.lower() for c in columns),
        "column_names": columns,
    }
    dataset = _dataset_from_manifest(dataset_id, item)
    dataset["description"] = description or "Uploaded demo dataset"
    dataset["source"] = source or "upload"
    dataset["file_path"] = str(path)
    dataset["file_size"] = path.stat().st_size
    dataset["file_size_bytes"] = path.stat().st_size
    dataset["column_profiles"] = _profile_for_csv(dataset_id, path)
    dataset["dashboard_config"] = _dashboard_for_dataset(dataset)
    DATASETS[dataset_id] = dataset
    return dataset


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
