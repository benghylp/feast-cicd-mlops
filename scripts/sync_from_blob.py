"""Sincroniza parquets desde Azure Blob Storage a feast_repo/data/"""
import os

def sync():
    account = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
    if not account or not key:
        print("  ⚠ Storage no configurado, saltando sync")
        return
    from azure.storage.blob import BlobServiceClient
    conn = (f"DefaultEndpointsProtocol=https;AccountName={account};"
            f"AccountKey={key};EndpointSuffix=core.windows.net")
    client = BlobServiceClient.from_connection_string(conn)
    container = client.get_container_client("features")
    local_dir = os.path.join("feast_repo", "data")
    os.makedirs(local_dir, exist_ok=True)
    for blob in container.list_blobs(name_starts_with="interferencia_4g/"):
        filename = blob.name.split("/")[-1]
        local_path = os.path.join(local_dir, filename)
        if os.path.exists(local_path) and os.path.getsize(local_path) == blob.size:
            print(f"  → {filename} ya sincronizado")
            continue
        with open(local_path, "wb") as f:
            f.write(container.get_blob_client(blob.name).download_blob().readall())
        print(f"  ✓ {filename} ({blob.size/1024/1024:.2f} MB)")

if __name__ == "__main__":
    sync()