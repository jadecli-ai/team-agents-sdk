"""MLflow autolog setup for Claude Agent SDK tracing.

Configures local SQLite tracking for MLflow traces. Coexists with
src/hooks/ which write directly to Neon — autolog captures additional
trace-level data locally, synced to Neon by mlflow-sync timer.

schema: mlflow_traces
depends_on:
  - src/get_env.py
depended_by:
  - tests/test_tracing.py
semver: minor
"""

from __future__ import annotations

import logging
from pathlib import Path

from src.get_env import env

logger = logging.getLogger(__name__)

_initialized = False


def setup_local_tracing(clone_id: str | None = None) -> str:
    """Configure MLflow for local SQLite tracking with Anthropic autolog.

    Args:
        clone_id: Override clone identity. If None, reads from
                  /etc/mlflow/clone.env or defaults to "unknown".

    Returns:
        The tracking URI that was set.
    """
    global _initialized
    if _initialized:
        logger.debug("MLflow tracing already initialized, skipping")
        return _get_tracking_uri()

    import mlflow

    # Resolve clone identity
    if clone_id is None:
        clone_id = _read_clone_id()

    # Set up local SQLite tracking
    mlflow_dir = Path.home() / ".mlflow"
    mlflow_dir.mkdir(parents=True, exist_ok=True)
    tracking_uri = f"sqlite:///{mlflow_dir / 'mlruns.db'}"
    mlflow.set_tracking_uri(tracking_uri)

    # Set experiment name from env or default
    experiment_name = env("PRJ_MLFLOW_EXPERIMENT_NAME", default="jadecli-agents")
    mlflow.set_experiment(experiment_name)

    # Enable Anthropic autolog
    mlflow.anthropic.autolog()

    # Tag active run with clone identity
    mlflow.set_system_metrics_sampling_interval(None)
    if clone_id:
        try:
            mlflow.set_tag("clone_id", clone_id)
        except Exception:
            # No active run yet — tags will be set when a run starts
            pass

    _initialized = True
    logger.info("MLflow tracing initialized: uri=%s clone=%s", tracking_uri, clone_id)
    return tracking_uri


def _get_tracking_uri() -> str:
    """Return the current MLflow tracking URI."""
    import mlflow

    return mlflow.get_tracking_uri()


def _read_clone_id() -> str:
    """Read CLONE_ID from /etc/mlflow/clone.env, fallback to 'unknown'."""
    clone_env = Path("/etc/mlflow/clone.env")
    if clone_env.exists():
        for line in clone_env.read_text().splitlines():
            line = line.strip()
            if line.startswith("CLONE_ID=") and not line.startswith("#"):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value
    return "unknown"
