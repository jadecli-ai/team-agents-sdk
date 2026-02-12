"""Tests for src/tracing — MLflow autolog setup."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestSetupLocalTracing:
    """Test MLflow local tracing configuration."""

    @patch("src.tracing.mlflow", create=True)
    @patch("src.tracing._read_clone_id", return_value="test-clone")
    def test_tracking_uri_is_sqlite(self, mock_clone, mock_mlflow):
        """Tracking URI points to ~/.mlflow/mlruns.db."""
        import src.tracing

        src.tracing._initialized = False

        with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
            mock_mlflow.anthropic = MagicMock()
            mock_mlflow.get_tracking_uri.return_value = "sqlite:///test"

            src.tracing.setup_local_tracing()

        expected_db = Path.home() / ".mlflow" / "mlruns.db"
        mock_mlflow.set_tracking_uri.assert_called_once()
        call_uri = mock_mlflow.set_tracking_uri.call_args[0][0]
        assert call_uri == f"sqlite:///{expected_db}"

        # Cleanup
        src.tracing._initialized = False

    @patch("src.tracing.mlflow", create=True)
    @patch("src.tracing._read_clone_id", return_value="test-clone")
    def test_autolog_called(self, mock_clone, mock_mlflow):
        """mlflow.anthropic.autolog() is called."""
        import src.tracing

        src.tracing._initialized = False

        with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
            mock_mlflow.anthropic = MagicMock()
            src.tracing.setup_local_tracing()

        mock_mlflow.anthropic.autolog.assert_called_once()
        src.tracing._initialized = False

    @patch("src.tracing.mlflow", create=True)
    def test_clone_id_override(self, mock_mlflow):
        """Explicit clone_id is used instead of reading from file."""
        import src.tracing

        src.tracing._initialized = False

        with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
            mock_mlflow.anthropic = MagicMock()
            src.tracing.setup_local_tracing(clone_id="my-clone")

        mock_mlflow.set_tag.assert_called_with("clone_id", "my-clone")
        src.tracing._initialized = False

    @patch("src.tracing.mlflow", create=True)
    @patch("src.tracing._read_clone_id", return_value="test-clone")
    def test_idempotent(self, mock_clone, mock_mlflow):
        """Second call is a no-op."""
        import src.tracing

        src.tracing._initialized = False

        with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
            mock_mlflow.anthropic = MagicMock()
            mock_mlflow.get_tracking_uri.return_value = "sqlite:///test"
            src.tracing.setup_local_tracing()
            src.tracing.setup_local_tracing()

        # set_tracking_uri called only once despite two calls
        assert mock_mlflow.set_tracking_uri.call_count == 1
        src.tracing._initialized = False

    @patch("src.tracing.env")
    @patch("src.tracing.mlflow", create=True)
    @patch("src.tracing._read_clone_id", return_value="test-clone")
    def test_experiment_name_from_env(self, mock_clone, mock_mlflow, mock_env):
        """Experiment name read from PRJ_MLFLOW_EXPERIMENT_NAME."""
        import src.tracing

        src.tracing._initialized = False
        mock_env.return_value = "my-experiment"

        with patch.dict("sys.modules", {"mlflow": mock_mlflow}):
            mock_mlflow.anthropic = MagicMock()
            src.tracing.setup_local_tracing()

        mock_mlflow.set_experiment.assert_called_once_with("my-experiment")
        src.tracing._initialized = False


class TestReadCloneId:
    """Test clone ID reading from /etc/mlflow/clone.env."""

    def test_missing_file_returns_unknown(self, tmp_path):
        """Missing clone.env returns 'unknown'."""
        from src.tracing import _read_clone_id

        with patch("src.tracing.Path") as mock_path:
            mock_file = MagicMock()
            mock_file.exists.return_value = False
            mock_path.return_value = mock_file
            result = _read_clone_id()
        assert result == "unknown"

    def test_reads_clone_id_from_file(self, tmp_path):
        """Valid clone.env returns the CLONE_ID value."""
        clone_env = tmp_path / "clone.env"
        clone_env.write_text("CLONE_ID=team-alpha\nCLONE_NAME=team-alpha\n")

        from src.tracing import _read_clone_id

        with patch("src.tracing.Path", return_value=clone_env):
            result = _read_clone_id()
        assert result == "team-alpha"


class TestMlflowTraceModel:
    """Test MlflowTrace Pydantic model."""

    def test_create_minimal(self):
        from datetime import datetime, timezone

        from src.models.mlflow_trace import MlflowTrace

        t = MlflowTrace(
            clone_id="team-alpha",
            experiment_name="jadecli-agents",
            run_id="abc123",
            start_time=datetime.now(timezone.utc),
            status="FINISHED",
        )
        assert t.clone_id == "team-alpha"
        assert t.status == "FINISHED"

    def test_negative_tokens_rejected(self):
        from datetime import datetime, timezone

        from src.models.mlflow_trace import MlflowTrace

        with pytest.raises(ValueError):
            MlflowTrace(
                clone_id="test",
                experiment_name="test",
                run_id="abc",
                start_time=datetime.now(timezone.utc),
                status="FINISHED",
                total_tokens=-1,
            )

    def test_negative_cost_rejected(self):
        from datetime import datetime, timezone

        from src.models.mlflow_trace import MlflowTrace

        with pytest.raises(ValueError):
            MlflowTrace(
                clone_id="test",
                experiment_name="test",
                run_id="abc",
                start_time=datetime.now(timezone.utc),
                status="FINISHED",
                estimated_cost_usd=-0.5,
            )

    def test_negative_duration_rejected(self):
        from datetime import datetime, timezone

        from src.models.mlflow_trace import MlflowTrace

        with pytest.raises(ValueError):
            MlflowTrace(
                clone_id="test",
                experiment_name="test",
                run_id="abc",
                start_time=datetime.now(timezone.utc),
                status="FINISHED",
                duration_ms=-100,
            )
