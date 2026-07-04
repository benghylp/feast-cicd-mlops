# 🐛 Troubleshooting: Feast Apply Workflow

## 🔴 Error: `ValueError: invalid literal for int() with base 10: ''`

### ¿Qué significa?

```
ValueError: invalid literal for int() with base 10: ''
```

**Traducción:** El workflow intenta convertir el puerto PostgreSQL a número, pero está vacío.

### 🎯 Root Cause

El secret `FEAST_POSTGRES_PORT` no está configurado en GitHub → SQLAlchemy no puede crear la URL de conexión.

---

## ✅ Solución Paso a Paso

### Paso 1: Ir a GitHub Secrets

1. **Abre tu repositorio** en GitHub
2. **Settings** (⚙️ icon)
3. **Secrets and variables** → **Actions** (en el menú izquierdo)

### Paso 2: Agregar el Secret Faltante

Haz clic en **"New repository secret"** y crea:

```
Name:  FEAST_POSTGRES_PORT
Value: 5432
```

> ⚠️ **IMPORTANTE:** El valor debe ser un **número** (5432), no texto ("5432")

### Paso 3: Agregar Todos los Secretos Requeridos

| Secreto | Obligatorio | Valor Ejemplo |
|---------|-----------|----------|
| FEAST_POSTGRES_HOST | ✅ SÍ | `postgres.database.azure.com` |
| FEAST_POSTGRES_USER | ✅ SÍ | `feast_user` |
| FEAST_POSTGRES_PASSWORD | ✅ SÍ | `MyPassword123!` |
| FEAST_POSTGRES_PORT | ✅ SÍ | `5432` |
| FEAST_POSTGRES_DB | ✅ SÍ | `feast_registry` |
| FEAST_REDIS_HOST | ✅ SÍ | `redis.cache.windows.net:6380` |
| FEAST_REDIS_PORT | ❌ NO | (se calcula del HOST) |
| FEAST_REDIS_KEY | ✅ SÍ | `your_redis_key` |
| AZURE_STORAGE_ACCOUNT_NAME | ✅ SÍ | `mystorageaccount` |
| AZURE_STORAGE_ACCOUNT_KEY | ✅ SÍ | `DefaultEndpointsProtocol=...` |

### Paso 4: Validar Configuración

El workflow ahora valida automáticamente todos los secretos.

Si ves:

```
✅ Todos los secretos PostgreSQL están configurados
✅ Todos los secretos Redis están configurados
✅ Todos los secretos Azure están configurados
```

**¡Estás listo!** ✨

---

## 🧪 Otros Errores Comunes

### Error 1: Connection Refused

```
psycopg2.OperationalError: could not connect to server
```

**Causas:**
- PostgreSQL no está corriendo
- Host/puerto incorrectos
- Firewall bloqueando conexión

**Solución:**
```bash
# Verifica conectividad desde tu máquina
psql -h <host> -U <user> -d <database>

# Si falla, verifica:
# 1. HOST está correcto
# 2. Puerto está abierto (telnet <host> 5432)
# 3. Usuario/contraseña correctos
# 4. Database existe
```

---

### Error 2: Invalid Syntax en feature_store.yaml

```
yaml.parser.ParserError: expected '<document start>'
```

**Causa:** Indentación incorrecta en `feature_store.yaml`

**Solución:**
```yaml
# ❌ INCORRECTO (espacios inconsistentes)
project: my_project
provider: local
registry:
  registry_type: sql

# ✅ CORRECTO (2 espacios de indentación)
project: my_project
provider: local
registry:
  registry_type: sql
  path: postgresql+psycopg2://...
```

---

### Error 3: Module Not Found

```
ModuleNotFoundError: No module named 'feast'
```

**Causa:** Dependencias no instaladas

**Solución:** El workflow instala automáticamente, pero si lo ejecutas localmente:

```bash
pip install -r requirements.txt
# o
pip install "feast[redis,postgres]" psycopg2-binary
```

---

### Error 4: Features Not Found

```
ImportError: cannot import name 'metricas_rf_fv'
```

**Causa:** El archivo `feature_views.py` no existe o no exporta el objeto

**Solución:**
1. Verifica que `feast_repo/feature_views.py` existe
2. Verifica que `metricas_rf_fv` está definido
3. Verifica la sintaxis de Python

```python
# ✅ Correcto
from feast import FeatureView, Field

metricas_rf_fv = FeatureView(
    name="metricas_rf",
    # ...
)
```

---

## 🔍 Debug: Ver Logs del Workflow

### En GitHub Actions

1. Ve a **Actions** en tu repositorio
2. Busca el workflow que falló: **"Feast Apply"**
3. Haz clic en el run
4. Expande el step que falló
5. Mira los logs detallados

### Tipos de Logs

```
Step 1: ✅ Validar secretos requeridos     ← Secretos ok
Step 2: ✅ Sincronizar datos desde Blob   ← Azure Storage ok
Step 3: ❌ Feast apply                      ← Error aquí
Step 4: ✅ Crear Issue si falla            ← Auto-crea Issue
```

---

## 💡 Tips para Debugging Local

### Setup Local para Probar

```bash
# 1. Crea archivo .env.local (NO commitear)
cat > .env.local << 'EOF'
POSTGRES_HOST=localhost
POSTGRES_USER=feast_user
POSTGRES_PASSWORD=feast_pass
POSTGRES_PORT=5432
POSTGRES_DB=feast_registry
FEAST_REDIS_HOST=localhost:6379
FEAST_REDIS_KEY=
EOF

# 2. Carga variables
source .env.local

# 3. Prueba el comando localmente
cd feast_repo
python -c "
from feast import FeatureStore
store = FeatureStore('.')
print('✅ Feature Store conectado')
"
```

### Docker para Simular el Environment

```bash
# Usa Docker para simular Ubuntu (igual que CI/CD)
docker run -it --rm \
  -v $(pwd):/work \
  -w /work \
  python:3.11 bash

# Dentro del container
pip install "feast[redis,postgres]"
cd feast_repo
python test_features.py
```

---

## 📊 Estado del Workflow

Después de configurar todo, deberías ver:

```
┌─────────────────────────────────────────┐
│ Feast Apply Workflow                    │
├─────────────────────────────────────────┤
│ validate-secrets       ✅ PASSED        │
│ apply                  ✅ PASSED        │
│ validate-config        ✅ PASSED        │
└─────────────────────────────────────────┘

🎉 All jobs passed! Features registrados.
```

---

## 🚀 Próximos Pasos

1. ✅ Configura todos los secretos en GitHub
2. ✅ Haz un push a `main` que toque `feast_repo/`
3. ✅ Verifica que el workflow pasa
4. ✅ Revisa los logs para confirmar que features se registraron

---

## 📞 Contacto y Preguntas

Si el problema persiste:

1. **Copia los logs exactos** del workflow
2. **Verifica que TODOS los secretos** están configurados
3. **Confirma que tu BD PostgreSQL** es accesible
4. **Crea un Issue** en el repositorio con los detalles

---

## 🎓 Apéndice: Anatomía del Workflow

```yaml
jobs:
  validate-secrets:     ← Paso 1: Valida que existen secrets
    name: ...

  apply:                ← Paso 2: Ejecuta feast apply
    needs: validate-secrets  ← Espera a que Paso 1 pase
    steps:
      - checkout        ← Descarga código
      - setup-python    ← Prepara Python 3.11
      - install         ← pip install dependencias
      - sync            ← Sincroniza datos desde Azure
      - apply           ← Ejecuta "feast apply"

  validate-config:      ← Paso 3: Valida YAML
    steps:
      - checkout
      - validate yaml
```

**Importante:** El workflow **falla en el primer error**. Necesitas pasar todos los steps.

---
