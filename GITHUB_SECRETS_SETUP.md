# 🔐 Configuración de GitHub Secrets para Feast CI/CD

Este documento explica cómo configurar todos los secretos necesarios para que el workflow `feast-apply.yml` funcione correctamente.

## ⚠️ El Error que Tenías

```
ValueError: invalid literal for int() with base 10: ''
```

**Causa:** `FEAST_POSTGRES_PORT` estaba vacío → el puerto PostgreSQL no se pudo convertir a número.

---

## 🚀 Solución: Configurar Secretos en GitHub

### Paso 1: Ir a GitHub → Settings

1. Abre tu repositorio en GitHub
2. Ve a **Settings** (⚙️ en la barra superior)
3. En el menú izquierdo: **Secrets and variables** → **Actions**

![GitHub Settings Path](https://docs.github.com/assets/cb-34314/mw-1440/images/help/settings/actions-org-secrets.webp)

---

### Paso 2: Agregar Secretos (Copiar & Pegar)

**Haz clic en "New repository secret"** y agrega EXACTAMENTE lo siguiente:

#### **PostgreSQL Registry (REQUERIDO)**

| Secreto | Valor | Ejemplo |
|---------|-------|---------|
| `FEAST_POSTGRES_HOST` | IP o hostname del servidor | `postgres.database.azure.com` |
| `FEAST_POSTGRES_USER` | Usuario PostgreSQL | `feast_user@postgres` |
| `FEAST_POSTGRES_PASSWORD` | Contraseña PostgreSQL | `Secure!P@ssw0rd123` |
| `FEAST_POSTGRES_PORT` | Puerto PostgreSQL | `5432` |
| `FEAST_POSTGRES_DB` | Nombre de la base de datos | `feast_registry` |

#### **Redis Online Store (REQUERIDO)**

| Secreto | Valor | Ejemplo |
|---------|-------|---------|
| `FEAST_REDIS_HOST` | Host:Puerto de Redis | `redis.cache.windows.net:6380` |
| `FEAST_REDIS_KEY` | Contraseña/API Key de Redis | `YourRedisPassword123` |

#### **Azure Storage (REQUERIDO)**

| Secreto | Valor | Ejemplo |
|---------|-------|---------|
| `AZURE_STORAGE_ACCOUNT_NAME` | Nombre de la Storage Account | `mystorageaccount` |
| `AZURE_STORAGE_ACCOUNT_KEY` | Clave de acceso primaria | `DefaultEndpointsProtocol=https;...` |

---

## ✅ Checklist de Verificación

```bash
# Después de configurar los secretos, verifica en el workflow:

□ FEAST_POSTGRES_HOST        → NO ESTÁ VACÍO
□ FEAST_POSTGRES_USER        → NO ESTÁ VACÍO
□ FEAST_POSTGRES_PASSWORD    → NO ESTÁ VACÍO
□ FEAST_POSTGRES_PORT        → TIENE UN NÚMERO (ej: 5432)
□ FEAST_POSTGRES_DB          → NO ESTÁ VACÍO
□ FEAST_REDIS_HOST           → NO ESTÁ VACÍO
□ FEAST_REDIS_KEY            → NO ESTÁ VACÍO
□ AZURE_STORAGE_ACCOUNT_NAME → NO ESTÁ VACÍO
□ AZURE_STORAGE_ACCOUNT_KEY  → NO ESTÁ VACÍO
```

---

## 🔍 Cómo Obtener los Valores

### PostgreSQL en Azure

```bash
# En Azure Portal → Database for PostgreSQL
1. Ve a tu servidor PostgreSQL
2. Copia: Server name (host)
3. Copia: Admin username
4. Copia: Password (o resetea)
5. Copia: Port (usualmente 5432)
6. Copia: Database name
```

### Redis en Azure

```bash
# En Azure Portal → Cache for Redis
1. Ve a tu Redis cache
2. Copia: Primary Endpoint (host:port)
3. Copia: Primary access key
```

### Azure Storage

```bash
# En Azure Portal → Storage Account
1. Ve a tu Storage Account
2. Access Keys → Copia: Key1 o Key2
```

---

## 🧪 Test: Validar Secretos Antes de Mergear

El workflow **automáticamente valida** que todos los secretos estén configurados.

Si ves este error al hacer push:

```
❌ ERROR: FEAST_POSTGRES_PORT no configurado
```

Significa que **falta configurar ese secreto en GitHub**.

---

## 🛠️ Troubleshooting

### "Connection refused" en PostgreSQL

✅ **Soluciones:**
1. Verifica que PostgreSQL está corriendo
2. Confirma el host/puerto son correctos
3. Verifica firewall permite conexión desde GitHub Actions (IP: `0.0.0.0/0` o específica)

### "Redis timeout"

✅ **Soluciones:**
1. Verifica que Redis está corriendo
2. Confirma que la contraseña/key es correcta
3. Verifica que el formato es: `host:puerto`

### "403 Unauthorized" en Azure Storage

✅ **Soluciones:**
1. Verifica que la Storage Account Key es correcta
2. Prueba con la otra key (Key2)
3. Regenera las keys en Azure Portal si es necesario

---

## 📋 Template: Script para Probar Localmente

```bash
# Para probar que tus secretos funcionan ANTES de pushear

# 1. Crea un .env local (NO commitear)
cat > .env.local << 'EOF'
POSTGRES_HOST=your-postgres.database.azure.com
POSTGRES_USER=feast_user@postgres
POSTGRES_PASSWORD=your_password
POSTGRES_PORT=5432
POSTGRES_DB=feast_registry
FEAST_REDIS_HOST=your-redis.redis.cache.windows.net:6380
FEAST_REDIS_KEY=your_redis_key
AZURE_STORAGE_ACCOUNT_NAME=yourstorageaccount
AZURE_STORAGE_ACCOUNT_KEY=your_storage_key
EOF

# 2. Carga las variables
source .env.local

# 3. Prueba la conexión PostgreSQL
python << 'PYTHON'
import os
from sqlalchemy import create_engine

postgres_url = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
try:
    engine = create_engine(postgres_url)
    with engine.connect() as conn:
        print("✅ PostgreSQL conectado exitosamente")
except Exception as e:
    print(f"❌ Error PostgreSQL: {e}")
PYTHON

# 4. Limpia el archivo de prueba
rm .env.local
```

---

## 🔒 Seguridad

**❌ NUNCA hagas esto:**
- ❌ Commitear secretos en código
- ❌ Poner contraseñas en `feature_store.yaml`
- ❌ Compartir secretos por Slack/Email

**✅ SIEMPRE haz esto:**
- ✅ Usa GitHub Secrets
- ✅ Usa variables de entorno
- ✅ Rota secretos regularmente
- ✅ Usa managed identities (Azure)

---

## 📞 Referencia Rápida

| Componente | Puerto | Host |
|----------|--------|------|
| PostgreSQL | 5432 | `*.database.azure.com` |
| Redis | 6380 | `*.redis.cache.windows.net` |
| Azure Storage | - | Usar Storage Key |

---

## ✨ Una Vez Configurado

Simplemente haz un **push a main** que toque `feast_repo/`:

```bash
# El workflow se ejecutará automáticamente
git add .
git commit -m "feat: add new feature"
git push origin main

# Workflow se ejecuta:
# 1. ✅ Valida secretos
# 2. ✅ Verifica YAML
# 3. ✅ Corre tests
# 4. ✅ Sincroniza datos desde Blob
# 5. ✅ Registra features en Feast
```

---

## 🎯 Checklist Final

- [ ] Configuraste FEAST_POSTGRES_HOST
- [ ] Configuraste FEAST_POSTGRES_USER
- [ ] Configuraste FEAST_POSTGRES_PASSWORD
- [ ] Configuraste FEAST_POSTGRES_PORT (número válido, ej: 5432)
- [ ] Configuraste FEAST_POSTGRES_DB
- [ ] Configuraste FEAST_REDIS_HOST
- [ ] Configuraste FEAST_REDIS_KEY
- [ ] Configuraste AZURE_STORAGE_ACCOUNT_NAME
- [ ] Configuraste AZURE_STORAGE_ACCOUNT_KEY
- [ ] Hiciste un push de prueba
- [ ] El workflow pasó sin errores ✅
