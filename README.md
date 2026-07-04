# Feast CI/CD — GitHub Actions

## Estructura

```
.github/
└── workflows/
    ├── feast-ci.yml          # PR → valida features
    └── feast-apply.yml       # Merge → registra en registry
CODEOWNERS                    # MLOps team aprueba feast_repo/
feast_repo/
├── feature_store.yaml
├── entities.py
├── sources.py
├── feature_views.py
└── feature_services.py
scripts/
└── sync_from_blob.py
tests/
└── test_features.py
```

## Setup en GitHub

### 1. Crear repo y subir código

```bash
git init
git add .
git commit -m "feat: feast CI/CD pipeline"
git remote add origin https://github.com/TU_USUARIO/mlops-feast.git
git branch -M main
git push -u origin main
```

### 2. Agregar secrets

Settings → Secrets and variables → Actions:

- FEAST_POSTGRES_HOST
- FEAST_POSTGRES_USER
- FEAST_POSTGRES_PASSWORD
- FEAST_REDIS_HOST
- FEAST_REDIS_KEY
- AZURE_STORAGE_ACCOUNT_NAME
- AZURE_STORAGE_ACCOUNT_KEY

### 3. Proteger rama main

Settings → Branches → Add rule → main:

- Require pull request before merging
- Require status checks: Feast CI / Validar features
- Require review from CODEOWNERS

### 4. Mover CODEOWNERS

```bash
mkdir -p .github
mv CODEOWNERS .github/CODEOWNERS
git add . && git commit -m "chore: move CODEOWNERS" && git push
```

## Probar el flujo

### Simular un DS que agrega un feature

```bash
git checkout -b feat/add-rssi-feature

# Editar feast_repo/feature_views.py
# Agregar un nuevo Field al metricas_rf_fv:
#   Field(name="rssi_dbm", dtype=Float32, description="RSSI (dBm)"),

git add . && git commit -m "feat: add rssi_dbm to metricas_rf"
git push -u origin feat/add-rssi-feature

# Abrir PR en GitHub → feast-ci.yml corre automáticamente
# Si CI pasa → MLOps engineer aprueba → merge → feast-apply.yml corre
```

### Simular un DS que rompe convenciones (CI debe fallar)

```bash
git checkout -b feat/bad-feature

# Editar feast_repo/feature_views.py
# Agregar un FeatureView sin TTL:
#   bad_fv = FeatureView(name="bad", entities=[celda], ttl=None, ...)

git add . && git commit -m "feat: bad feature view"
git push -u origin feat/bad-feature

# PR → feast-ci.yml corre → test_features.py falla → PR bloqueado
```