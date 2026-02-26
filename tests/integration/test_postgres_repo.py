import os
import pytest
import threading
from counter.adapters.count_repo import CountPostgresRepo
from counter.domain.models import ObjectCount

@pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or
    os.getenv("COUNT_BACKEND_TYPE") != "postgres",
    reason="Postgres backend not configured."
)
def test_postgres_increment_accumulates_counts():
    """
    Verify that repeated updates correctly accumulate counts
    using atomic upsert.
    """

    repo = CountPostgresRepo(os.getenv("DATABASE_URL"))

    repo.update_values([ObjectCount("cat", 2)])
    repo.update_values([ObjectCount("cat", 3)])

    results = repo.read_values(["cat"])

    assert len(results) == 1
    assert results[0].count == 5

    repo.close()

@pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or
    os.getenv("COUNT_BACKEND_TYPE") != "postgres",
    reason="Postgres backend not configured."
)
def test_postgres_concurrent_updates():
    """
    Verify that concurrent updates do not lose increments.
    """

    repo = CountPostgresRepo(os.getenv("DATABASE_URL"))

    def worker():
        repo.update_values([ObjectCount("dog", 1)])

    threads = []

    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    results = repo.read_values(["dog"])

    assert results[0].count == 10

    repo.close()