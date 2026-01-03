# test_alpha_vantage_corregido.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_dashboard.settings')
django.setup()

from django.conf import settings
import requests

# Verificar configuración
print("=" * 60)
print("CONFIGURACIÓN ALPHA VANTAGE")
print("=" * 60)

# Verificar si la configuración existe
if hasattr(settings, 'ALPHA_VANTAGE_API_KEY'):
    api_key = settings.ALPHA_VANTAGE_API_KEY
    print(f"API Key configurada: SÍ")
    print(f"API Key (primeros 5 chars): {api_key[:5]}...")
    print(f"Longitud API Key: {len(api_key)} caracteres")
else:
    print("API Key configurada: NO - No hay atributo ALPHA_VANTAGE_API_KEY en settings")
    api_key = None

# Solo probar la API si tenemos API Key
if api_key:
    print("\n" + "=" * 60)
    print("PRUEBA DIRECTA A API")
    print("=" * 60)

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": "AAPL",
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "Error Message" in data:
                print(f"Error de API: {data['Error Message'][:100]}")
            elif "Note" in data:
                print(f"Nota (rate limit): {data['Note'][:100]}")
            elif "Time Series (Daily)" in data:
                print("✅ ¡API funcionando correctamente!")
                fechas = list(data["Time Series (Daily)"].keys())[:3]
                print(f"Primeras fechas disponibles: {fechas}")
            else:
                print(f"Respuesta inesperada: {list(data.keys())}")
        else:
            print(f"Error HTTP: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error en la prueba: {type(e).__name__}: {e}")
else:
    print("\nNo se puede probar la API porque no hay API Key configurada.")