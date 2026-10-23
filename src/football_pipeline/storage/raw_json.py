import json
import os
from datetime import date, datetime
from pathlib import Path

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient, ContentSettings

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _upload_raw_payload_to_azure(payload: dict, local_path: Path) -> None:
    if os.getenv("AZURE_STORAGE_ENABLED", "false").lower() != "true":
        return

    account_url = os.environ["AZURE_STORAGE_ACCOUNT_URL"]
    container_name = os.environ["AZURE_STORAGE_CONTAINER"]
    auth_mode = os.getenv("AZURE_STORAGE_AUTH_MODE", "sas").strip().lower()

    if auth_mode == "managed_identity":
        credential = ManagedIdentityCredential()
    elif auth_mode == "default_azure_credential":
        credential = DefaultAzureCredential()
    elif auth_mode == "sas":
        credential = os.environ["AZURE_STORAGE_SAS_TOKEN"].lstrip("?")
    else:
        raise ValueError(
            "AZURE_STORAGE_AUTH_MODE must be "
            "'managed_identity', 'default_azure_credential', or 'sas'"
        )

    raw_folder = PROJECT_ROOT / "data" / "raw"
    blob_name = local_path.relative_to(raw_folder).as_posix()

    blob_service = BlobServiceClient(
        account_url=account_url,
        credential=credential,
    )
    blob_client = blob_service.get_blob_client(
        container=container_name,
        blob=blob_name,
    )
    try:
        blob_client.upload_blob(
            json.dumps(payload, ensure_ascii=False, indent=4).encode("utf-8"),
            overwrite=False,
            content_settings=ContentSettings(content_type="application/json"),
        )
    finally:
        blob_service.close()


def save_raw_payload(payload: dict, fixture_date: date, fetched_at: datetime) -> None:
    folder = (
        PROJECT_ROOT
        / "data"
        / "raw"
        / "api_football"
        / "fixtures"
        / f"ingestion_date={fetched_at.date().isoformat()}"
    )
    folder.mkdir(parents=True, exist_ok=True)

    timestamp = fetched_at.strftime("%Y%m%dT%H%M%SZ")

    path = folder / f"fixtures_{fixture_date.isoformat()}_{timestamp}.json"

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )

    _upload_raw_payload_to_azure(payload, path)

    return str(path)


def read_raw_payload(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
