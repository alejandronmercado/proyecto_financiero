# cargar_datos_prueba.py
import yfinance as yf
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_dashboard.settings')
django.setup()

from dashboard.models import AccionInternacional, PrecioAccion
from datetime import datetime, timedelta

# Símbolos de prueba
simbolos = ['AAPL', 'MSFT', 'SPY']

for simbolo in simbolos:
    print(f"\nProcesando {simbolo}...")
    
    try:
        # Descargar datos
        ticker = yf.Ticker(simbolo)
        df = ticker.history(period="30d")
        
        if df.empty:
            print(f"  ✗ Sin datos")
            continue
        
        # Obtener o crear acción
        accion, created = AccionInternacional.objects.get_or_create(
            simbolo=simbolo,
            defaults={
                'nombre': simbolo,
                'tipo': 'accion' if len(simbolo) <= 5 else 'etf',
                'pais': 'USA',
                'moneda': 'USD',
                'activo': True
            }
        )
        
        # Guardar precios
        count = 0
        for fecha, row in df.iterrows():
            precio, _ = PrecioAccion.objects.update_or_create(
                accion=accion,
                fecha=fecha.date(),
                defaults={
                    'apertura': float(row['Open']),
                    'maximo': float(row['High']),
                    'minimo': float(row['Low']),
                    'cierre': float(row['Close']),
                    'cierre_ajustado': float(row['Close']),
                    'volumen': int(row['Volume']),
                    'dividendo': 0,
                    'split': 1
                }
            )
            count += 1
        
        print(f"  ✓ {count} precios guardados")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n✅ ¡Datos de prueba cargados!")