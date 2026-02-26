import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, ListDetectedPredictions

ALLOWED_ENVS = {"dev", "prod"}

def get_env():
    env = str(os.getenv("ENV", "dev")).lower()

    if env not in ALLOWED_ENVS:
        raise RuntimeError(
            f"Invalid ENV '{env}'. Allowed: {ALLOWED_ENVS}"
        )
    return env

# --- DEV INFRA ---
def _dev_object_detector():
    return FakeObjectDetector()

def _dev_count_repo():
    return CountInMemoryRepo()

# --- PROD INFRA ---
def _prod_object_detector():
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    model_name = os.environ.get('MODEL_NAME', 'ssd_mobilenet_v2')
    return TFSObjectDetector(tfs_host, tfs_port, model_name)

def _prod_count_repo():
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = os.environ.get('MONGO_PORT', 27017)
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db)

# --- Loader Functions ---
def get_object_detector():
    env = get_env()
    count_action_fn = f"_{env}_object_detector"
    return globals()[count_action_fn]()

def get_count_repo():
    env = get_env()
    count_action_fn = f"_{env}_count_repo"
    return globals()[count_action_fn]()

def get_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(
        get_object_detector(),
        get_count_repo()
    )

def get_prediction_action() -> ListDetectedPredictions:
    return ListDetectedPredictions(
        get_object_detector()
    )
