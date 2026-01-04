import psycopg2
import sys

print("=== MÉTODO ALTERNATIVO ===")
print("Conectando primero a 'postgres' database...\n")

try:
    # PASO 1: Conectar a la database 'postgres' (siempre existe)
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='12345678',
        host='localhost',
        port='5432'
    )
    
    print("✅ Conexión a 'postgres' exitosa")
    conn.autocommit = True
    cursor = conn.cursor()
    
    # PASO 2: Verificar que nuestra database existe
    cursor.execute(
        """SELECT 1 FROM pg_database WHERE datname = 'financial_dashboard';"""
    )
    exists = cursor.fetchone()
    
    if exists:
        print("✅ Database 'financial_dashboard' existe")
    else:
        print("❌ Database no existe")
        sys.exit(1)
    
    cursor.close()
    conn.close()
    
    # PASO 3: Conectar a nuestra database
    print("\nConectando a 'financial_dashboard'...")
    conn2 = psycopg2.connect(
        dbname='financial_dashboard',
        user='postgres',
        password='12345678',
        host='localhost',
        port='5432',
        client_encoding='utf8'
    )
    
    print("✅ ¡CONEXIÓN EXITOSA!")
    print("\n=== INFORMACIÓN ===")
    cursor2 = conn2.cursor()
    cursor2.execute('SELECT version();')
    print(f"PostgreSQL: {cursor2.fetchone()[0][:50]}...")
    
    cursor2.execute('SHOW server_encoding;')
    print(f"Server encoding: {cursor2.fetchone()[0]}")
    
    cursor2.execute('SHOW client_encoding;')
    print(f"Client encoding: {cursor2.fetchone()[0]}")
    
    cursor2.close()
    conn2.close()
    
    print("\n🎉 TODO LISTO PARA DJANGO")
    sys.exit(0)
    
except UnicodeDecodeError as e:
    print(f"\n❌ Error de codificación persiste: {e}")
    print(f"Byte: 0x{e.object[e.start]:02x} en posición {e.start}")
    print("\n⚠️ SOLUCIÓN: Necesitas reinstalar PostgreSQL con locale en inglés")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"Tipo: {type(e).__name__}")
    sys.exit(1)
EOF

