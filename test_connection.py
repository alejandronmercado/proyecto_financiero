import psycopg2
import sys

try:
    # Intentar conexión con parámetros explícitos
    print("Intentando conectar a PostgreSQL...")
    
    conn = psycopg2.connect(
        dbname='financial_dashboard',
        user='postgres',
        password='falcor2018',
        host='localhost',
        port='5432'
    )
    
    print("✅ ¡Conexión exitosa!")
    print(f"Versión de PostgreSQL: {conn.server_version}")
    
    # Probar una consulta simple
    cursor = conn.cursor()
    cursor.execute('SELECT version();')
    version = cursor.fetchone()
    print(f"Versión completa: {version[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ TODO FUNCIONA CORRECTAMENTE")
    
except psycopg2.OperationalError as e:
    print(f"❌ Error de conexión: {e}")
    print("\nPosibles causas:")
    print("- PostgreSQL no está corriendo")
    print("- Contraseña incorrecta")
    print("- Base de datos no existe")
    sys.exit(1)
    
except UnicodeDecodeError as e:
    print(f"❌ Error de codificación: {e}")
    print(f"Byte problemático: 0x{e.object[e.start]:02x} en posición {e.start}")
    print("\nPosibles causas:")
    print("- Problema con la instalación de PostgreSQL")
    print("- Archivo pg_hba.conf con codificación incorrecta")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    print(f"Tipo: {type(e).__name__}")
    sys.exit(1)
