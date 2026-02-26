import io
import os
import pytest
from pathlib import Path
from sqlalchemy import create_engine, text

from counter.entrypoints.webapp import create_app


# -------------------------------------------------------------------
# Deterministic Environment
# -------------------------------------------------------------------

@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """
    Ensures deterministic configuration across tests.
    """
    monkeypatch.setenv("MODEL_TYPE", "fake")
    # Do not override COUNT_BACKEND_TYPE here
    # CI sets it to postgres
    # Local dev defaults to inmemory


# -------------------------------------------------------------------
# Clean Postgres Between Tests (CI Safe)
# -------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_postgres():
    if (
        os.getenv("DATABASE_URL")
        and os.getenv("COUNT_BACKEND_TYPE") == "postgres"
    ):
        engine = create_engine(os.getenv("DATABASE_URL"))
        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE IF EXISTS object_counts"))
        engine.dispose()


# -------------------------------------------------------------------
# Flask Test Client
# -------------------------------------------------------------------

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# -------------------------------------------------------------------
# Shared Image Utilities
# -------------------------------------------------------------------

@pytest.fixture(scope="session")
def image_dir():
    ref_dir = Path(__file__).parent
    return ref_dir.parent / "resources" / "images"


@pytest.fixture
def image_file_factory(image_dir):
    def _load(filename: str):
        with open(image_dir / filename, "rb") as f:
            return io.BytesIO(f.read())
    return _load