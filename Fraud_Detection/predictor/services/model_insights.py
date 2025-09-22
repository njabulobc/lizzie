"""Utilities to extract fraud model insights."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd
import pytz

FEATURE_FIELDS: Sequence[str] = (
    "merchant",
    "category",
    "amt",
    "gender",
    "city",
    "province",
    "latitude",
    "longitude",
    "city_pop",
    "job",
    "unix_time",
    "merch_latitude",
    "merch_longitude",
    "processed_at",
)


def prepare_prediction_dataframe(source: Any) -> pd.DataFrame:
    """Build a feature DataFrame from serializer data or a model instance."""

    if hasattr(source, "_meta"):
        row = {field: getattr(source, field) for field in FEATURE_FIELDS if hasattr(source, field)}
    elif isinstance(source, Mapping):
        row = {field: source.get(field) for field in FEATURE_FIELDS}
    else:
        raise TypeError("Unsupported source type for feature preparation")

    if "processed_at" not in row or row["processed_at"] is None:
        raise ValueError("processed_at is required to build the prediction dataframe")

    df = pd.DataFrame([row])

    df["processed_at"] = pd.to_datetime(df["processed_at"])
    if df["processed_at"].dt.tz is None:
        df["processed_at"] = df["processed_at"].dt.tz_localize(pytz.UTC)
    else:
        df["processed_at"] = df["processed_at"].dt.tz_convert(pytz.UTC)

    df["hour"] = df["processed_at"].dt.hour
    df["day_of_week"] = df["processed_at"].dt.dayofweek
    df["month"] = df["processed_at"].dt.month
    df["is_weekend"] = df["day_of_week"].apply(lambda value: 1 if value >= 5 else 0)

    return df.drop(columns=["processed_at"])


def _get_feature_names(preprocessor: Any, transformed_row: Any) -> Sequence[str]:
    if hasattr(preprocessor, "get_feature_names_out"):
        try:
            return preprocessor.get_feature_names_out()
        except Exception:  # pragma: no cover - fall back if unsupported
            pass
    return [f"feature_{index}" for index in range(transformed_row.shape[1])]


def generate_model_insights(model: Any, df: pd.DataFrame, *, top_n: int = 5) -> Tuple[float, List[Dict[str, float]]]:
    """Return fraud probability and top contributing factors for a transaction."""

    proba = float(model.predict_proba(df)[0][1])

    preprocessor = getattr(model, "named_steps", {}).get("preprocessor") if hasattr(model, "named_steps") else None
    classifier = getattr(model, "named_steps", {}).get("classifier") if hasattr(model, "named_steps") else None

    if preprocessor is None or classifier is None or not hasattr(classifier, "coef_"):
        return proba, []

    try:
        transformed = preprocessor.transform(df)
    except Exception:
        return proba, []
    if hasattr(transformed, "toarray"):
        transformed_row = transformed.toarray()[0]
    else:
        transformed_row = np.asarray(transformed)[0]

    coefficients = classifier.coef_[0] if classifier.coef_.ndim > 1 else classifier.coef_
    feature_names = _get_feature_names(preprocessor, transformed)

    if len(coefficients) != len(transformed_row):
        return proba, []

    contributions = coefficients * transformed_row

    factors = []
    for name, value, weight, contribution in zip(feature_names, transformed_row, coefficients, contributions):
        factors.append(
            {
                "feature": str(name),
                "value": float(value),
                "weight": float(weight),
                "contribution": float(contribution),
            }
        )

    factors.sort(key=lambda item: abs(item["contribution"]), reverse=True)
    return proba, factors[:top_n]
