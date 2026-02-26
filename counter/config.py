import os

from counter.adapters.count_repo import (
    CountMongoDBRepo,
    CountInMemoryRepo,
    CountPostgresRepo,
)
from counter.adapters.object_detector import (
    TFSObjectDetector,
    FakeObjectDetector,
)
from counter.domain.actions import (
    CountDetectedObjects,
    ListDetectedPredictions,
)


# ==========================================================
# Object Detector Builders
# ==========================================================

def _build_fake_detector():
    return FakeObjectDetector()


def _build_tensorflow_detector():
    tfs_host = os.getenv("TFS_HOST", "localhost")
    tfs_port = int(os.getenv("TFS_PORT", 8501))
    model_name = os.getenv("MODEL_NAME", "ssd_mobilenet_v2")

    return TFSObjectDetector(tfs_host, tfs_port, model_name)


DETECTOR_BUILDERS = {
    "fake": _build_fake_detector,
    "tensorflow": _build_tensorflow_detector,
}


def get_object_detector():
    detector_type = str(os.getenv("MODEL_TYPE", "fake")).lower()

    builder = DETECTOR_BUILDERS.get(detector_type)
    if builder is None:
        raise RuntimeError(
            f"Unsupported MODEL_TYPE '{detector_type}'. "
            f"Allowed: {list(DETECTOR_BUILDERS.keys())}"
        )

    return builder()


# ==========================================================
# Count Repository Builders
# ==========================================================

def _build_inmemory_repo():
    return CountInMemoryRepo()


def _build_mongo_repo():
    mongo_host = os.getenv("MONGO_HOST", "localhost")
    mongo_port = int(os.getenv("MONGO_PORT", 27017))
    mongo_db = os.getenv("MONGO_DB", "prod_counter")

    return CountMongoDBRepo(
        host=mongo_host,
        port=mongo_port,
        database=mongo_db,
    )


def _build_postgres_repo():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError(
            "DATABASE_URL must be set when COUNT_BACKEND_TYPE=postgres"
        )

    return CountPostgresRepo(db_url=db_url)


BACKEND_BUILDERS = {
    "inmemory": _build_inmemory_repo,
    "mongo": _build_mongo_repo,
    "postgres": _build_postgres_repo,
}


def get_count_repo():
    backend_type = str(os.getenv("COUNT_BACKEND_TYPE", "inmemory")).lower()

    builder = BACKEND_BUILDERS.get(backend_type)
    if builder is None:
        raise RuntimeError(
            f"Unsupported COUNT_BACKEND_TYPE '{backend_type}'. "
            f"Allowed: {list(BACKEND_BUILDERS.keys())}"
        )

    return builder()


# ==========================================================
# Actions (Config Root)
# ==========================================================

def get_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(
        get_object_detector(),
        get_count_repo(),
    )


def get_prediction_action() -> ListDetectedPredictions:
    return ListDetectedPredictions(
        get_object_detector()
    )