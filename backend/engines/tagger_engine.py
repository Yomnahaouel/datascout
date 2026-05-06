"""
Tagger Engine - Domain classification and PII detection per PROJECT_SPECIFICATION.md
Domain: BART zero-shot with labels Finance, Risk, Marketing, HR, Operations, Compliance, Products (top 1).
PII: per-column sample of 20 values; regex (email, phone, SSN, credit card) >50% → flag; spaCy NER PERSON >50% → person_name.
Dataset tag sensitivity/contains_pii if any column has PII.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Lazy imports for heavy ML libraries
_nlp = None
_classifier = None

# Spec domain labels (single-label, top one)
DOMAIN_LABELS_SPEC = [
    "Finance",
    "Risk",
    "Marketing",
    "HR",
    "Operations",
    "Compliance",
    "Products",
]

# Spec PII regex patterns (50% of sample match → flag)
PII_PATTERNS_SPEC = {
    "email": re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        re.IGNORECASE,
    ),
    "phone": re.compile(
        r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    ),
    "ssn": re.compile(r"\d{3}-\d{2}-\d{4}"),
    "credit_card": re.compile(
        r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}"
    ),
}

PII_SAMPLE_SIZE = 20
PII_MATCH_THRESHOLD = 0.5  # >50% of sample match → flag


def _get_spacy_nlp():
    """Lazy load spaCy model en_core_web_sm."""
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Downloading spaCy model en_core_web_sm...")
            from spacy.cli import download
            download("en_core_web_sm")
            import spacy
            _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _get_zero_shot_classifier():
    """Lazy load BART zero-shot (facebook/bart-large-mnli)."""
    global _classifier
    if _classifier is None:
        from transformers import pipeline
        import torch
        device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Loading zero-shot classifier on device: {'GPU' if device == 0 else 'CPU'}")
        _classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=device,
        )
    return _classifier


@dataclass
class PIIMatch:
    """A single PII detection match."""
    pii_type: str
    value: str
    column: str
    row_index: int
    confidence: float = 1.0


@dataclass
class PIIReport:
    """PII detection report (spec: pii_by_column, pii_by_type; dataset tag contains_pii if any)."""
    total_pii_found: int
    pii_by_type: dict[str, int]
    pii_by_column: dict[str, list[str]]
    sample_matches: list[PIIMatch]
    risk_level: str
    recommendations: list[str]


@dataclass
class DomainTag:
    """Domain classification result (spec: single top label)."""
    label: str
    confidence: float


@dataclass
class TaggingResult:
    """Complete tagging result for a dataset."""
    domains: list[DomainTag]
    data_types: list[DomainTag]
    pii_report: PIIReport
    column_tags: dict[str, list[str]] = field(default_factory=dict)
    sensitivity_score: float = 0.0


class TaggerEngine:
    """
    Auto-tagger per spec:
    - Domain: name + column names → BART zero-shot → top 1 label from Finance, Risk, Marketing, HR, Operations, Compliance, Products.
    - PII: per column sample 20 values; regex (email, phone, SSN, credit_card) >50% → flag; then spaCy NER PERSON >50% → person_name.
    - If any column has PII, add dataset tag sensitivity/contains_pii, method ner_regex.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.3,
        pii_sample_size: int = PII_SAMPLE_SIZE,
        pii_match_threshold: float = PII_MATCH_THRESHOLD,
        max_pii_samples: int = 50,
    ):
        self.confidence_threshold = confidence_threshold
        self.pii_sample_size = pii_sample_size
        self.pii_match_threshold = pii_match_threshold
        self.max_pii_samples = max_pii_samples

    async def tag_dataset(self, data: pd.DataFrame) -> TaggingResult:
        """Generate tags: domain (top 1), PII by column (regex + NER)."""
        logger.info(f"Tagging dataset with shape {data.shape}")

        # Sub-task A: Domain classification (name + column names → zero-shot → top 1)
        text_for_domain = self._text_for_domain(data)
        domains = await self._classify_domain_spec(text_for_domain)

        # Sub-task B: PII detection (per column, sample 20, regex then NER)
        pii_report = await self._detect_pii_spec(data)

        # Dataset-level tag: if any PII, add contains_pii (handled in pipeline via pii_report)
        column_tags = await self._tag_columns(data)

        sensitivity_score = 0.7 if pii_report.pii_by_column else 0.0

        return TaggingResult(
            domains=domains,
            data_types=[],  # Spec only requires domain + PII
            pii_report=pii_report,
            column_tags=column_tags,
            sensitivity_score=sensitivity_score,
        )

    def _text_for_domain(self, data: pd.DataFrame) -> str:
        """Spec: concatenate dataset name + column names. Example: 'credit_card_fraud amount time V1 V2 class'."""
        parts = list(data.columns.astype(str))
        return " ".join(parts)

    async def _classify_domain_spec(self, text: str) -> list[DomainTag]:
        """Zero-shot with DOMAIN_LABELS_SPEC; take top label only."""
        try:
            classifier = _get_zero_shot_classifier()
            # Spec: single-label, top one
            result = classifier(text[:2000], DOMAIN_LABELS_SPEC, multi_label=False)
            labels = result.get("labels", [])
            scores = result.get("scores", [])
            if labels and scores:
                return [DomainTag(label=labels[0], confidence=round(float(scores[0]), 3))]
            return []
        except Exception as e:
            logger.error(f"Domain classification failed: {e}")
            return []

    async def _detect_pii_spec(self, data: pd.DataFrame) -> PIIReport:
        """
        Per spec: for each column sample 20 non-null values.
        Regex: email, phone, SSN, credit_card — if >50% match → flag column.
        Then for remaining text columns: spaCy NER PERSON — if >50% have PERSON → person_name.
        """
        pii_by_type: dict[str, int] = {}
        pii_by_column: dict[str, list[str]] = {}
        sample_matches: list[PIIMatch] = []

        string_cols = data.select_dtypes(include=["object", "string"]).columns.tolist()

        for col in data.columns:
            sample = data[col].dropna().head(self.pii_sample_size)
            if len(sample) == 0:
                continue
            sample_list = sample.astype(str).tolist()
            n = len(sample_list)
            col_pii_types: list[str] = []

            # Regex checks (spec patterns)
            for pii_type, pattern in PII_PATTERNS_SPEC.items():
                matches = sum(1 for v in sample_list if pattern.search(v))
                if matches / n >= self.pii_match_threshold:
                    col_pii_types.append(pii_type)
                    pii_by_type[pii_type] = pii_by_type.get(pii_type, 0) + matches
                    if len(sample_matches) < self.max_pii_samples:
                        for v in sample_list:
                            if pattern.search(v):
                                sample_matches.append(PIIMatch(pii_type=pii_type, value=v[:50], column=col, row_index=0))
                                break

            # spaCy NER for PERSON (spec: if >50% of values contain PERSON → person_name)
            if col in string_cols and "person_name" not in col_pii_types:
                person_count = 0
                for v in sample_list:
                    if len(v) > 10 and len(v) < 500:
                        if await self._has_person_entity(v):
                            person_count += 1
                if person_count / n >= self.pii_match_threshold:
                    col_pii_types.append("person_name")
                    pii_by_type["person_name"] = pii_by_type.get("person_name", 0) + person_count

            if col_pii_types:
                pii_by_column[col] = col_pii_types

        total = sum(pii_by_type.values())
        risk_level = "high" if total > 0 else "none"
        recommendations = []
        if pii_by_column:
            recommendations.append("Dataset contains PII: consider anonymization or access controls.")
        if not recommendations:
            recommendations.append("No significant PII detected.")

        return PIIReport(
            total_pii_found=total,
            pii_by_type=pii_by_type,
            pii_by_column=pii_by_column,
            sample_matches=sample_matches,
            risk_level=risk_level,
            recommendations=recommendations,
        )

    async def _has_person_entity(self, text: str) -> bool:
        """Run spaCy NER; return True if any entity label is PERSON."""
        try:
            nlp = _get_spacy_nlp()
            doc = nlp(text)
            return any(ent.label_ == "PERSON" for ent in doc.ents)
        except Exception:
            return False

    async def _tag_columns(self, data: pd.DataFrame) -> dict[str, list[str]]:
        """Column-level semantic tags (optional)."""
        column_tags: dict[str, list[str]] = {}
        for col in data.columns:
            tags = []
            col_lower = col.lower()
            if any(k in col_lower for k in ["id", "key", "code"]):
                tags.append("identifier")
            if any(k in col_lower for k in ["date", "time"]):
                tags.append("date")
            if any(k in col_lower for k in ["amount", "price"]):
                tags.append("numeric")
            if pd.api.types.is_numeric_dtype(data[col]):
                tags.append("numeric")
            else:
                tags.append("text")
            column_tags[col] = tags
        return column_tags
