"""
Quality Engine - Data quality scoring across 5 dimensions
Completeness, Consistency, Uniqueness, Validity, Timeliness
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DimensionScore:
    """Score for a single quality dimension."""
    name: str
    score: float  # 0.0 - 1.0
    weight: float
    weighted_score: float
    issues: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ColumnQuality:
    """Quality assessment for a single column."""
    name: str
    completeness: float
    validity: float
    uniqueness: float
    overall: float
    issues: list[str] = field(default_factory=list)


@dataclass
class QualityReport:
    """Complete data quality report."""
    overall_score: float
    grade: str  # A, B, C, D, F
    dimensions: list[DimensionScore]
    column_quality: list[ColumnQuality]
    critical_issues: list[str]
    recommendations: list[str]
    metadata: dict[str, Any]


# Validation rules for common data patterns
VALIDATION_PATTERNS = {
    "email": re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
    "phone": re.compile(r"^\+?[\d\s\-\(\)]{7,20}$"),
    "url": re.compile(r"^https?://[^\s]+$"),
    "uuid": re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I),
    "date_iso": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
    "zipcode_us": re.compile(r"^\d{5}(-\d{4})?$"),
}


class QualityEngine:
    """
    Engine for comprehensive data quality assessment.
    Scores data across 5 dimensions with configurable weights.
    """

    def __init__(
        self,
        weights: dict[str, float] | None = None,
        freshness_days: int = 30,
        custom_validators: dict[str, Callable] | None = None,
    ):
        """
        Initialize the quality engine.

        Args:
            weights: Custom weights for each dimension (must sum to 1.0)
            freshness_days: Days threshold for timeliness scoring
            custom_validators: Additional validation functions by column name pattern
        """
        self.weights = weights or {
            "completeness": 0.30,
            "consistency": 0.20,
            "uniqueness": 0.20,
            "validity": 0.20,
            "timeliness": 0.10,
        }
        self.freshness_days = freshness_days
        self.custom_validators = custom_validators or {}

    async def assess_quality(
        self,
        data: pd.DataFrame,
        date_column: str | None = None,
    ) -> QualityReport:
        """
        Generate comprehensive quality report for a dataset.

        Args:
            data: DataFrame to assess
            date_column: Column name containing timestamps for timeliness

        Returns:
            QualityReport with all scores and recommendations
        """
        logger.info(f"Assessing quality for dataset with shape {data.shape}")

        dimensions = []
        critical_issues = []

        # 1. Completeness
        completeness = await self._assess_completeness(data)
        dimensions.append(completeness)
        if completeness.score < 0.5:
            critical_issues.append(f"Low completeness ({completeness.score:.0%}): Many missing values")

        # 2. Consistency
        consistency = await self._assess_consistency(data)
        dimensions.append(consistency)
        if consistency.score < 0.5:
            critical_issues.append(f"Low consistency ({consistency.score:.0%}): Data format inconsistencies")

        # 3. Uniqueness
        uniqueness = await self._assess_uniqueness(data)
        dimensions.append(uniqueness)
        if uniqueness.score < 0.5:
            critical_issues.append(f"Low uniqueness ({uniqueness.score:.0%}): High duplicate rate")

        # 4. Validity
        validity = await self._assess_validity(data)
        dimensions.append(validity)
        if validity.score < 0.5:
            critical_issues.append(f"Low validity ({validity.score:.0%}): Invalid data patterns")

        # 5. Timeliness
        timeliness = await self._assess_timeliness(data, date_column)
        dimensions.append(timeliness)
        if timeliness.score < 0.5:
            critical_issues.append(f"Low timeliness ({timeliness.score:.0%}): Stale data detected")

        # Calculate overall score
        overall_score = sum(d.weighted_score for d in dimensions)
        grade = self._score_to_grade(overall_score)

        # Column-level quality
        column_quality = await self._assess_columns(data)

        # Generate recommendations
        recommendations = self._generate_recommendations(dimensions, column_quality)

        return QualityReport(
            overall_score=round(overall_score, 3),
            grade=grade,
            dimensions=dimensions,
            column_quality=column_quality,
            critical_issues=critical_issues,
            recommendations=recommendations,
            metadata={
                "row_count": len(data),
                "column_count": len(data.columns),
                "assessed_at": datetime.utcnow().isoformat(),
            },
        )

    async def _assess_completeness(self, data: pd.DataFrame) -> DimensionScore:
        """Assess data completeness (non-null values)."""
        total_cells = data.size
        non_null_cells = data.count().sum()
        score = non_null_cells / total_cells if total_cells > 0 else 0.0

        issues = []
        details = {"columns_with_nulls": {}}

        for col in data.columns:
            null_pct = data[col].isna().mean()
            if null_pct > 0:
                details["columns_with_nulls"][col] = round(null_pct * 100, 1)
                if null_pct > 0.5:
                    issues.append(f"Column '{col}' is {null_pct:.0%} empty")

        return DimensionScore(
            name="completeness",
            score=round(score, 3),
            weight=self.weights["completeness"],
            weighted_score=round(score * self.weights["completeness"], 3),
            issues=issues,
            details=details,
        )

    async def _assess_consistency(self, data: pd.DataFrame) -> DimensionScore:
        """Assess data consistency (format uniformity)."""
        scores = []
        issues = []
        details = {"inconsistent_columns": []}

        for col in data.columns:
            col_score = await self._check_column_consistency(data[col])
            scores.append(col_score)
            if col_score < 0.8:
                issues.append(f"Column '{col}' has inconsistent formats")
                details["inconsistent_columns"].append(col)

        score = np.mean(scores) if scores else 1.0

        return DimensionScore(
            name="consistency",
            score=round(score, 3),
            weight=self.weights["consistency"],
            weighted_score=round(score * self.weights["consistency"], 3),
            issues=issues,
            details=details,
        )

    async def _check_column_consistency(self, series: pd.Series) -> float:
        """Check consistency within a single column."""
        non_null = series.dropna()
        if len(non_null) == 0:
            return 1.0

        # For string columns, check type consistency
        if series.dtype == "object":
            # Check if all values are same "type" (numeric string, text, etc.)
            type_counts = {"numeric": 0, "alpha": 0, "mixed": 0, "empty": 0}
            
            sample = non_null.head(1000).astype(str)
            for val in sample:
                if val.strip() == "":
                    type_counts["empty"] += 1
                elif val.replace(".", "").replace("-", "").isdigit():
                    type_counts["numeric"] += 1
                elif val.isalpha():
                    type_counts["alpha"] += 1
                else:
                    type_counts["mixed"] += 1

            total = sum(type_counts.values())
            if total == 0:
                return 1.0
            
            # High consistency if dominated by one type
            max_count = max(type_counts.values())
            return max_count / total

        return 1.0  # Numeric columns assumed consistent

    async def _assess_uniqueness(self, data: pd.DataFrame) -> DimensionScore:
        """Assess data uniqueness (duplicate detection)."""
        total_rows = len(data)
        if total_rows == 0:
            return DimensionScore(
                name="uniqueness",
                score=1.0,
                weight=self.weights["uniqueness"],
                weighted_score=self.weights["uniqueness"],
            )

        # Check row-level duplicates
        duplicate_rows = data.duplicated().sum()
        row_uniqueness = 1 - (duplicate_rows / total_rows)

        issues = []
        details = {
            "duplicate_rows": int(duplicate_rows),
            "duplicate_percentage": round(duplicate_rows / total_rows * 100, 2),
        }

        if duplicate_rows > 0:
            issues.append(f"{duplicate_rows} duplicate rows found ({details['duplicate_percentage']}%)")

        # Check potential key columns (columns named 'id' or similar)
        for col in data.columns:
            if "id" in col.lower() or "key" in col.lower():
                unique_ratio = data[col].nunique() / len(data[col])
                if unique_ratio < 1.0:
                    issues.append(f"Potential key column '{col}' has duplicates")
                    details[f"{col}_unique_ratio"] = round(unique_ratio, 3)

        return DimensionScore(
            name="uniqueness",
            score=round(row_uniqueness, 3),
            weight=self.weights["uniqueness"],
            weighted_score=round(row_uniqueness * self.weights["uniqueness"], 3),
            issues=issues,
            details=details,
        )

    async def _assess_validity(self, data: pd.DataFrame) -> DimensionScore:
        """Assess data validity (format and range validation)."""
        scores = []
        issues = []
        details = {"invalid_columns": {}}

        for col in data.columns:
            col_score, col_issues = await self._validate_column(data[col], col)
            scores.append(col_score)
            if col_issues:
                issues.extend(col_issues)
                details["invalid_columns"][col] = col_issues

        score = np.mean(scores) if scores else 1.0

        return DimensionScore(
            name="validity",
            score=round(score, 3),
            weight=self.weights["validity"],
            weighted_score=round(score * self.weights["validity"], 3),
            issues=issues,
            details=details,
        )

    async def _validate_column(
        self, series: pd.Series, col_name: str
    ) -> tuple[float, list[str]]:
        """Validate a single column based on inferred type."""
        issues = []
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 1.0, issues

        col_lower = col_name.lower()
        valid_count = len(non_null)
        total_count = len(non_null)

        # Apply pattern-based validation
        pattern_key = None
        if "email" in col_lower:
            pattern_key = "email"
        elif "phone" in col_lower or "tel" in col_lower:
            pattern_key = "phone"
        elif "url" in col_lower or "link" in col_lower:
            pattern_key = "url"
        elif "zip" in col_lower:
            pattern_key = "zipcode_us"

        if pattern_key and pattern_key in VALIDATION_PATTERNS:
            pattern = VALIDATION_PATTERNS[pattern_key]
            sample = non_null.head(1000).astype(str)
            invalid = sum(1 for v in sample if not pattern.match(v))
            valid_count = len(sample) - invalid
            total_count = len(sample)
            
            if invalid > 0:
                invalid_pct = invalid / total_count * 100
                issues.append(f"{col_name}: {invalid_pct:.1f}% invalid {pattern_key} format")

        # Check for negative values in count/amount columns
        if pd.api.types.is_numeric_dtype(series):
            if any(kw in col_lower for kw in ["count", "qty", "quantity", "age"]):
                negative_count = (non_null < 0).sum()
                if negative_count > 0:
                    issues.append(f"{col_name}: {negative_count} unexpected negative values")
                    valid_count -= negative_count

        # Check for future dates
        if pd.api.types.is_datetime64_any_dtype(series):
            future_dates = (non_null > datetime.now()).sum()
            if future_dates > 0:
                issues.append(f"{col_name}: {future_dates} future dates detected")

        score = valid_count / total_count if total_count > 0 else 1.0
        return score, issues

    async def _assess_timeliness(
        self, data: pd.DataFrame, date_column: str | None
    ) -> DimensionScore:
        """
        Spec: If date column — 30d→100, 90d→75, 1y→50, older→25 (we store 0-1).
        If no date column, use neutral 0.5 (pipeline does not pass file mtime).
        """
        issues = []
        details = {}

        if date_column is None:
            datetime_cols = data.select_dtypes(include=["datetime64"]).columns
            if len(datetime_cols) > 0:
                date_column = datetime_cols[0]
            else:
                for col in data.columns:
                    if any(kw in col.lower() for kw in ["date", "time", "created", "updated"]):
                        try:
                            pd.to_datetime(data[col])
                            date_column = col
                            break
                        except Exception:
                            continue

        if date_column is None or date_column not in data.columns:
            return DimensionScore(
                name="timeliness",
                score=0.5,
                weight=self.weights["timeliness"],
                weighted_score=round(0.5 * self.weights["timeliness"], 3),
                issues=["No date column found for timeliness assessment"],
                details={"date_column": None},
            )

        try:
            dates = pd.to_datetime(data[date_column], errors="coerce")
            valid_dates = dates.dropna()
            if len(valid_dates) == 0:
                return DimensionScore(
                    name="timeliness",
                    score=0.5,
                    weight=self.weights["timeliness"],
                    weighted_score=round(0.5 * self.weights["timeliness"], 3),
                    issues=["No valid dates in date column"],
                    details={"date_column": date_column},
                )

            now = datetime.now()
            max_date = valid_dates.max()
            days_since = (now - max_date).days

            # Spec bands: within 30d→100, 90d→75, 1y→50, older→25 (store 0-1)
            if days_since <= 30:
                score = 1.0
            elif days_since <= 90:
                score = 0.75
            elif days_since <= 365:
                score = 0.50
            else:
                score = 0.25

            details = {
                "date_column": date_column,
                "max_date": str(max_date),
                "days_since_latest": days_since,
            }
            if days_since > 30:
                issues.append(f"Latest record is {days_since} days old")

        except Exception as e:
            logger.warning(f"Timeliness assessment failed: {e}")
            score = 0.5
            issues.append(str(e))

        return DimensionScore(
            name="timeliness",
            score=round(score, 3),
            weight=self.weights["timeliness"],
            weighted_score=round(score * self.weights["timeliness"], 3),
            issues=issues,
            details=details,
        )

    async def _assess_columns(self, data: pd.DataFrame) -> list[ColumnQuality]:
        """Assess quality for each column."""
        column_quality = []

        for col in data.columns:
            series = data[col]
            
            # Completeness
            completeness = 1 - series.isna().mean()
            
            # Validity (simple check)
            validity_score, validity_issues = await self._validate_column(series, col)
            
            # Uniqueness
            uniqueness = series.nunique() / len(series) if len(series) > 0 else 1.0
            
            # Overall (average)
            overall = (completeness + validity_score + min(uniqueness * 2, 1.0)) / 3
            
            issues = []
            if completeness < 0.9:
                issues.append(f"{(1-completeness)*100:.1f}% missing values")
            issues.extend(validity_issues)

            column_quality.append(ColumnQuality(
                name=col,
                completeness=round(completeness, 3),
                validity=round(validity_score, 3),
                uniqueness=round(uniqueness, 3),
                overall=round(overall, 3),
                issues=issues,
            ))

        return column_quality

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        return "F"

    def _generate_recommendations(
        self,
        dimensions: list[DimensionScore],
        columns: list[ColumnQuality],
    ) -> list[str]:
        """Generate actionable recommendations based on findings."""
        recommendations = []

        for dim in dimensions:
            if dim.name == "completeness" and dim.score < 0.9:
                recommendations.append(
                    "Address missing values: Consider imputation strategies or data collection improvements"
                )
            elif dim.name == "consistency" and dim.score < 0.9:
                recommendations.append(
                    "Standardize data formats: Implement data validation at ingestion"
                )
            elif dim.name == "uniqueness" and dim.score < 0.95:
                recommendations.append(
                    "Remove duplicates: Implement deduplication in ETL pipeline"
                )
            elif dim.name == "validity" and dim.score < 0.9:
                recommendations.append(
                    "Validate data patterns: Add schema validation and input constraints"
                )
            elif dim.name == "timeliness" and dim.score < 0.8:
                recommendations.append(
                    "Update stale data: Review data refresh schedules and sources"
                )

        # Column-specific recommendations
        low_quality_cols = [c for c in columns if c.overall < 0.7]
        if low_quality_cols:
            col_names = ", ".join(c.name for c in low_quality_cols[:5])
            recommendations.append(
                f"Focus on improving columns: {col_names}"
            )

        if not recommendations:
            recommendations.append("Data quality is good. Maintain current practices.")

        return recommendations
