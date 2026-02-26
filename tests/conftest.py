import io
import pytest
from pathlib import Path
from counter.entrypoints.webapp import create_app


# -------------------------------------------------------------------
# Global Test Environment Configuration
# -------------------------------------------------------------------

@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """
    Ensures deterministic ENV configuration across all tests.
    Prevents CI or shell-level ENV leakage.
    """
    monkeypatch.setenv("ENV", "dev")


# -------------------------------------------------------------------
# Flask Test Client (Integration Boundary)
# -------------------------------------------------------------------

@pytest.fixture
def client():
    """
    Provides Flask test client with TESTING mode enabled.
    """
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# -------------------------------------------------------------------
# Shared Image Utilities
# -------------------------------------------------------------------

@pytest.fixture(scope="session")
def image_dir():
    """
    Base directory for test image assets.
    """
    ref_dir = Path(__file__).parent
    return ref_dir.parent / "resources" / "images"


@pytest.fixture
def image_file_factory(image_dir):
    """
    Factory fixture to load any image by filename.
    Returns a fresh BytesIO object per call to avoid
    stream reuse issues across tests.
    """

    def _load(filename: str):
        with open(image_dir / filename, "rb") as f:
            return io.BytesIO(f.read())

    return _load