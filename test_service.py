import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financial_dashboard.settings')
django.setup()

from dashboard.services.alpha_vantage_service import AlphaVantageService
from django.conf import settings

print("=" * 60)
print("PRUEBA DEL SERVICIO ALPHA VANTAGE")
print("=" * 60)

# Verificar settings
print(f"API Key en settings: {getattr(settings, 'ALPHA_VANTAGE_API_KEY', 'NO DEFINIDA')}")

# Crear servicio
service = AlphaVantageService()
print(f"API Key en servicio: {service.api_key[:5] if service.api_key else 'VACÍA'}")

# Probar un request simple
print("\nProbando request simple...")
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': 'AAPL',
    'outputsize': 'compact'
}

# Usar el método interno del servicio
data = service._make_request(params)
if data:
    print("✅ Servicio funcionando correctamente")
    print(f"Datos obtenidos: {list(data.keys())}")
else:
    print("❌ El servicio no pudo obtener datos")