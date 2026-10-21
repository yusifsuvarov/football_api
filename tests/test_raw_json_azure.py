from unittest.mock import MagicMock

import pytest

from football_pipeline.storage import raw_json


def test_azure_upload_failure_closes_client_and_propagates(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ENABLED", "true")
    monkeypatch.setenv(
        "AZURE_STORAGE_ACCOUNT_URL",
        "https://example.blob.core.windows.net",
    )
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "raw-football-data")
    monkeypatch.setenv("AZURE_STORAGE_SAS_TOKEN", "fake-token")

    blob_service = MagicMock()
    blob_client = MagicMock()
    blob_service.get_blob_client.return_value = blob_client
    blob_client.upload_blob.side_effect = RuntimeError("simulated upload failure")

    monkeypatch.setattr(
        raw_json,
        "BlobServiceClient",
        lambda **kwargs: blob_service,
    )

    local_path = (
        raw_json.PROJECT_ROOT
        / "data"
        / "raw"
        / "api_football"
        / "fixtures"
        / "ingestion_date=2026-10-21"
        / "fixtures_test.json"
    )

    with pytest.raises(RuntimeError, match="simulated upload failure"):
        raw_json._upload_raw_payload_to_azure({"response": []}, local_path)

    blob_service.close.assert_called_once()