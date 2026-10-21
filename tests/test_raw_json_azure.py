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


def test_upload_uses_managed_identity_when_configured(monkeypatch):
    monkeypatch.setenv("AZURE_STORAGE_ENABLED", "true")
    monkeypatch.setenv(
        "AZURE_STORAGE_ACCOUNT_URL",
        "https://example.blob.core.windows.net",
    )
    monkeypatch.setenv("AZURE_STORAGE_CONTAINER", "raw-football-data")
    monkeypatch.setenv("AZURE_STORAGE_AUTH_MODE", "managed_identity")

    credential = MagicMock()
    credential_factory = MagicMock(return_value=credential)
    monkeypatch.setattr(
        raw_json,
        "ManagedIdentityCredential",
        credential_factory,
    )

    blob_service = MagicMock()
    blob_service_factory = MagicMock(return_value=blob_service)
    monkeypatch.setattr(raw_json, "BlobServiceClient", blob_service_factory)

    local_path = (
        raw_json.PROJECT_ROOT
        / "data"
        / "raw"
        / "api_football"
        / "fixtures"
        / "ingestion_date=2026-10-21"
        / "fixtures_test.json"
    )

    raw_json._upload_raw_payload_to_azure({"response": []}, local_path)

    credential_factory.assert_called_once_with()
    blob_service_factory.assert_called_once_with(
        account_url="https://example.blob.core.windows.net",
        credential=credential,
    )
    blob_service.get_blob_client.assert_called_once_with(
        container="raw-football-data",
        blob="api_football/fixtures/ingestion_date=2026-10-21/fixtures_test.json",
    )
    blob_service.get_blob_client.return_value.upload_blob.assert_called_once()
    blob_service.close.assert_called_once()
