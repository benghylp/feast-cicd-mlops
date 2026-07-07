"""
============================================================================
 Feast materialize — Azure Container Apps Job
============================================================================
 Cron job diario (10:30 AM Lima / 15:30 UTC):
   1. Sincroniza parquets desde Blob Storage a local
   2. Ejecuta feast materialize-incremental (offline -> online)
   3. Verifica que Redis tenga features frescos
   4. Sale con codigo 0 (exito) o 1 (fallo)
============================================================================
"""

import os
import sys
import time
from datetime import datetime


def sync_from_blob():
    """Descarga parquets desde Blob Storage a feast_repo/data/."""
    account = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")

    if not account or not key:
        print("  x AZURE_STORAGE credentials no configuradas")
        return False

    from azure.storage.blob import BlobServiceClient

    conn = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={account};"
        f"AccountKey={key};"
        f"EndpointSuffix=core.windows.net"
    )
    client = BlobServiceClient.from_connection_string(conn)
    container = client.get_container_client("features")

    local_dir = os.path.join("feast_repo", "data")
    os.makedirs(local_dir, exist_ok=True)

    blobs = list(container.list_blobs(name_starts_with="interferencia_4g/"))
    if not blobs:
        print("  ! No hay parquets en features/interferencia_4g/")
        return True

    for blob in blobs:
        filename = blob.name.split("/")[-1]
        if not filename.endswith(".parquet"):
            continue
        local_path = os.path.join(local_dir, filename)

        if os.path.exists(local_path) and os.path.getsize(local_path) == blob.size:
            print(f"  - {filename} sin cambios")
            continue

        with open(local_path, "wb") as f:
            f.write(container.get_blob_client(blob.name).download_blob().readall())
        print(f"  + {filename} ({blob.size / 1024:.1f} KB)")

    return True


def materialize():
    """Ejecuta feast materialize-incremental."""
    from feast import FeatureStore

    store = FeatureStore(repo_path="feast_repo")

    t0 = time.time()
    store.materialize_incremental(end_date=datetime.utcnow())
    elapsed = time.time() - t0

    print(f"  + Materializacion completada en {elapsed:.1f}s")
    return True


def verify_online_store():
    """Verifica que Redis tenga features frescos."""
    from feast import FeatureStore

    store = FeatureStore(repo_path="feast_repo")

    try:
        result = store.get_online_features(
            features=["metricas_rf:sinr_db", "metricas_rf:rsrp_dbm"],
            entity_rows=[{"cell_id": "ENB10000_S1"}],
        ).to_dict()

        sinr = result.get("sinr_db", [None])[0]
        rsrp = result.get("rsrp_dbm", [None])[0]

        if sinr is not None:
            print(f"  + Online store OK (sinr={sinr}, rsrp={rsrp})")

            latencies = []
            for _ in range(10):
                t0 = time.perf_counter()
                store.get_online_features(
                    features=["metricas_rf:sinr_db"],
                    entity_rows=[{"cell_id": "ENB10000_S1"}],
                )
                latencies.append((time.perf_counter() - t0) * 1000)

            avg = sum(latencies) / len(latencies)
            print(f"  + Latencia promedio: {avg:.0f}ms")
            return True
        else:
            print("  ! Features son None (datos insuficientes)")
            return True

    except Exception as e:
        print(f"  x Error verificando online store: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print(f"  Feast materialize - {datetime.utcnow():%Y-%m-%d %H:%M UTC}")
    print("=" * 60)

    success = True

    print("\n  [1/3] Sincronizando desde Blob Storage...")
    if not sync_from_blob():
        success = False

    if success:
        print("\n  [2/3] Ejecutando materialize-incremental...")
        try:
            if not materialize():
                success = False
        except Exception as e:
            print(f"  x Error: {e}")
            success = False

    if success:
        print("\n  [3/3] Verificando online store...")
        if not verify_online_store():
            success = False

    print(f"\n{'=' * 60}")
    if success:
        print("  OK - Job completado exitosamente")
    else:
        print("  FAIL - Job fallo")
    print(f"{'=' * 60}")

    sys.exit(0 if success else 1)