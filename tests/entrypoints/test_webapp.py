import io
import json

TEST_BOY_IMAGE = "boy.jpg"


def test_object_count_returns_expected_fields(client, image_file_factory):
    """
    Verifies that /object-count returns a successful response
    with the expected response structure.
    """

    image_file = image_file_factory(TEST_BOY_IMAGE)

    data = {
        "threshold": "0.9",
        "model_name": "ssd_mobilenet_v2",
        "file": (image_file, TEST_BOY_IMAGE),
    }

    response = client.post(
        "/object-count",
        data=data,
        content_type="multipart/form-data",
        buffered=True,
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)

    assert "current_objects" in response_json
    assert "total_objects" in response_json


def test_list_predictions_returns_valid_structure(client, image_file_factory):
    """
    Verifies that /list-predictions returns a list of predictions
    with the expected schema.
    """

    image_file = image_file_factory(TEST_BOY_IMAGE)

    data = {
        "threshold": "0.5",
        "file": (image_file, TEST_BOY_IMAGE),
    }

    response = client.post(
        "/list-predictions",
        data=data,
        content_type="multipart/form-data",
        buffered=True,
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)
    assert isinstance(response_json, list)

    if response_json:
        first_item = response_json[0]

        assert isinstance(first_item, dict)

        expected_keys = {"class_name", "score", "box"}
        assert expected_keys.issubset(first_item.keys())

        assert isinstance(first_item["class_name"], str)
        assert isinstance(first_item["score"], float)


def test_list_predictions_missing_file_returns_400(client):
    """
    Missing file should return 400.
    """

    response = client.post(
        "/list-predictions",
        data={"threshold": "0.5"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_list_predictions_invalid_threshold_returns_400(client, image_file_factory):
    """
    Non-numeric threshold should return 400.
    """

    image_file = image_file_factory(TEST_BOY_IMAGE)

    data = {
        "threshold": "invalid",
        "file": (image_file, TEST_BOY_IMAGE),
    }

    response = client.post(
        "/list-predictions",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_list_predictions_invalid_file_type_returns_400(client):
    """
    Non-image file should return 400.
    """

    fake_file = io.BytesIO(b"not an image")

    data = {
        "threshold": "0.5",
        "file": (fake_file, "test.txt"),
    }

    response = client.post(
        "/list-predictions",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 400