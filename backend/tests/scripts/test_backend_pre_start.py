from unittest.mock import MagicMock, patch

from sqlmodel import select

from app.backend_pre_start import init, logger


def test_init_successful_connection() -> None:
    engine_mock = MagicMock()

    session_mock = MagicMock()
    exec_mock = MagicMock(return_value=True)
    session_mock.exec = exec_mock

    # Make Session work as a context manager
    session_context_mock = MagicMock()
    session_context_mock.__enter__ = MagicMock(return_value=session_mock)
    session_context_mock.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.backend_pre_start.Session", return_value=session_context_mock),
        patch.object(logger, "info"),
        patch.object(logger, "error"),
        patch.object(logger, "warn"),
    ):
        try:
            init(engine_mock)
            connection_successful = True
        except Exception:
            connection_successful = False

        assert (
            connection_successful
        ), "The database connection should be successful and not raise an exception."

        assert session_mock.exec.called, "The session should execute a select statement."
