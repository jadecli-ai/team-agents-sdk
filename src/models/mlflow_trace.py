"""MlflowTrace model matching semantic/mlflow_traces.yaml.

schema: mlflow_traces
depends_on:
  - src/models/base.py
depended_by:
  - src/models/__init__.py
  - src/db/tables.py
  - tests/test_models.py
semver: minor
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import Field

from src.models.base import BaseEntity


class MlflowTrace(BaseEntity):
    """Synced trace summary from local SQLite to Neon (one row per MLflow run)."""

    clone_id: str = Field(..., max_length=50)
    experiment_name: str = Field(..., max_length=200)
    run_id: str = Field(..., max_length=64)
    start_time: datetime
    end_time: datetime | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    status: str = Field(..., max_length=20)
    total_tokens: int | None = Field(default=None, ge=0)
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    model_id: str | None = Field(default=None, max_length=100)
    synced_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
