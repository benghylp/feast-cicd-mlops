#!/usr/bin/env python3
"""
🧪 Validador Local de Feast Config
Prueba que tu configuración funciona ANTES de hacer push a GitHub

Uso:
    python validate_local.py --help
    python validate_local.py --test-postgres
    python validate_local.py --test-redis
    python validate_local.py --test-all
"""

import os
import sys
import argparse
from pathlib import Path


def print_header(title):
    """Imprime un header formateado"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def check_env_var(var_name, required=True):
    """Verifica si una variable de entorno existe"""
    value = os.getenv(var_name)
    
    if not value:
        if required:
            print(f"  ❌ {var_name:<30} NO CONFIGURADO")
            return False
        else:
            print(f"  ⚠️  {var_name:<30} (opcional, sin configurar)")
            return True
    
    # Oculta valores sensibles
    masked_value = value[:10] + "..." if len(value) > 10 else value
    print(f"  ✅ {var_name:<30} {masked_value}")
    return True


def validate_env_vars():
    """Valida que todas las variables de entorno estén configuradas"""
    print_header("1️⃣  Validar Variables de Entorno")
    
    required_vars = [
        'POSTGRES_HOST',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_PORT',
        'POSTGRES_DB',
        'FEAST_REDIS_HOST',
        'FEAST_REDIS_KEY',
        'AZURE_STORAGE_ACCOUNT_NAME',
        'AZURE_STORAGE_ACCOUNT_KEY',
    ]
    
    all_ok = True
    for var in required_vars:
        if not check_env_var(var):
            all_ok = False
    
    if all_ok:
        print("\n✅ Todas las variables están configuradas\n")
    else:
        print("\n❌ Faltan variables de entorno")
        print("   Configura: export VAR_NAME=value\n")
    
    return all_ok


def test_postgres_connection():
    """Prueba conexión a PostgreSQL"""
    print_header("2️⃣  Probar Conexión PostgreSQL")
    
    try:
        import psycopg2
    except ImportError:
        print("❌ psycopg2 no instalado")
        print("   pip install psycopg2-binary\n")
        return False
    
    try:
        host = os.getenv('POSTGRES_HOST')
        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DB')
        
        print(f"  Conectando a {user}@{host}:{port}/{database}...\n")
        
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"  ✅ Conectado exitosamente")
        print(f"  ✅ PostgreSQL version: {version[0][:50]}...\n")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)}\n")
        print("  💡 Troubleshooting:")
        print("     - Verifica que PostgreSQL está corriendo")
        print("     - Verifica host, user, password, port")
        print("     - Verifica que la database existe\n")
        return False


def test_redis_connection():
    """Prueba conexión a Redis"""
    print_header("3️⃣  Probar Conexión Redis")
    
    try:
        import redis
    except ImportError:
        print("❌ redis no instalado")
        print("   pip install redis\n")
        return False
    
    try:
        redis_host = os.getenv('FEAST_REDIS_HOST')  # formato: host:port
        redis_key = os.getenv('FEAST_REDIS_KEY')
        
        if ':' in redis_host:
            host, port = redis_host.rsplit(':', 1)
            port = int(port)
        else:
            host = redis_host
            port = 6379
        
        print(f"  Conectando a {host}:{port}...\n")
        
        client = redis.Redis(
            host=host,
            port=port,
            password=redis_key,
            ssl=True,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Prueba la conexión
        client.ping()
        
        print(f"  ✅ Conectado exitosamente")
        print(f"  ✅ Redis respondió a PING\n")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {type(e).__name__}: {str(e)}\n")
        print("  💡 Troubleshooting:")
        print("     - Verifica que Redis está corriendo")
        print("     - Verifica host, puerto, contraseña")
        print("     - Verifica conexión SSL si es requerida\n")
        return False


def validate_yaml():
    """Valida feature_store.yaml"""
    print_header("4️⃣  Validar feature_store.yaml")
    
    try:
        import yaml
    except ImportError:
        print("❌ pyyaml no instalado")
        print("   pip install pyyaml\n")
        return False
    
    yaml_path = Path("feast_repo/feature_store.yaml")
    
    if not yaml_path.exists():
        print(f"❌ {yaml_path} no encontrado\n")
        return False
    
    try:
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
        
        print(f"  ✅ YAML válido")
        print(f"  ✅ Project: {config.get('project', 'N/A')}")
        print(f"  ✅ Provider: {config.get('provider', 'N/A')}")
        print(f"  ✅ Registry: {config.get('registry', {}).get('registry_type', 'N/A')}\n")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error parsing YAML: {str(e)}\n")
        return False


def validate_feast_imports():
    """Valida que se pueden importar los módulos Feast"""
    print_header("5️⃣  Validar Imports de Feast")
    
    try:
        from feast import FeatureStore
        print("  ✅ Importó feast.FeatureStore")
    except ImportError as e:
        print(f"  ❌ No se puede importar FeatureStore: {e}\n")
        print("  pip install 'feast[redis,postgres]'\n")
        return False
    
    feast_repo = Path("feast_repo")
    if not feast_repo.exists():
        print(f"  ❌ Carpeta {feast_repo} no encontrada\n")
        return False
    
    try:
        # Verifica que existen los módulos principales
        required_files = [
            'feature_store.yaml',
            'entities.py',
            'feature_views.py',
            'feature_services.py'
        ]
        
        for file in required_files:
            path = feast_repo / file
            if path.exists():
                print(f"  ✅ {file:<25} Existe")
            else:
                print(f"  ❌ {file:<25} NO EXISTE")
                return False
        
        print()
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}\n")
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validador local de Feast config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python validate_local.py --all      # Todas las validaciones
  python validate_local.py --postgres # Solo PostgreSQL
  python validate_local.py --redis    # Solo Redis
        """
    )
    
    parser.add_argument('--all', action='store_true', help='Todas las validaciones')
    parser.add_argument('--env', action='store_true', help='Validar variables de entorno')
    parser.add_argument('--postgres', action='store_true', help='Probar PostgreSQL')
    parser.add_argument('--redis', action='store_true', help='Probar Redis')
    parser.add_argument('--yaml', action='store_true', help='Validar YAML')
    parser.add_argument('--feast', action='store_true', help='Validar imports Feast')
    
    args = parser.parse_args()
    
    # Si no hay opciones específicas, hace --all
    if not any([args.all, args.env, args.postgres, args.redis, args.yaml, args.feast]):
        args.all = True
    
    results = {}
    
    print_header("🧪 Validador de Configuración Feast")
    
    if args.all or args.env:
        results['env'] = validate_env_vars()
    
    if args.all or args.postgres:
        results['postgres'] = test_postgres_connection()
    
    if args.all or args.redis:
        results['redis'] = test_redis_connection()
    
    if args.all or args.yaml:
        results['yaml'] = validate_yaml()
    
    if args.all or args.feast:
        results['feast'] = validate_feast_imports()
    
    # Resumen final
    print_header("📊 Resumen Final")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"  {test_name:<20} {status}")
    
    print()
    
    if all_passed:
        print("🎉 ¡TODO OK! Puedes hacer push a GitHub\n")
        return 0
    else:
        print("❌ Hay errores. Soluciona antes de hacer push\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
