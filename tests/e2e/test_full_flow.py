import os
import json
import pytest


@pytest.mark.skipif(
    not os.getenv("DATABASE_URL") or
    os.getenv("COUNT_BACKEND_TYPE") != "postgres",
    reason="Postgres backend not configured."
)
def test_full_object_count_flow(client, image_file_factory):
    """
    Full request lifecycle test:
    HTTP → Domain → Postgres → Response
    """

    image_file1 = image_file_factory("boy.jpg")

    response1 = client.post(
        "/object-count",
        data={
            "threshold": "0.5",
            "file": (image_file1, "boy.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response1.status_code == 200
    body1 = json.loads(response1.data)

    image_file2 = image_file_factory("boy.jpg")

    response2 = client.post(
        "/object-count",
        data={
            "threshold": "0.5",
            "file": (image_file2, "boy.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response2.status_code == 200
    body2 = json.loads(response2.data)

    total1 = sum(body1["total_objects"].values())
    total2 = sum(body2["total_objects"].values())

    assert total2 >= total1