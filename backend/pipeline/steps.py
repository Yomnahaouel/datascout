"""Built-in pipeline steps for common transformations."""

from typing import Any


async def normalize_keys(data: dict[str, Any]) -> dict[str, Any]:
    """Lower-case all keys in each record."""
    if "records" in data:
        data["records"] = [
            {k.lower().strip(): v for k, v in record.items()}
            for record in data["records"]
        ]
    return data


async def deduplicate(data: dict[str, Any]) -> dict[str, Any]:
    """Remove duplicate records based on serialised content."""
    if "records" in data:
        seen: set[str] = set()
        unique = []
        for record in data["records"]:
            key = str(sorted(record.items()))
            if key not in seen:
                seen.add(key)
                unique.append(record)
        data["records"] = unique
    return data
