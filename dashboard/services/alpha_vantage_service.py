import requests
import time
import json
from datetime import datetime, date, timedelta
from django.conf import settings
from django.utils import timezone
from dashboard.models import AccionInternacional, PrecioAccion


class AlphaVantageService:
    """Servicio para interactuar con la API de Alpha Vantage"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(settings, 'ALPHA_VANTAGE_API_KEY', '')
        self.base_url = getattr(settings, 'ALPHA_VANTAGE_BASE_URL', 'https://www.alphavantage.co/query')
        self.timeout = 30
        self.session = requests.Session()
        
        # Headers para evitar bloqueos
        self.session.headers.update({
            'User-Agent': 'DashboardFinanciero/1.0',
            'Accept': 'application/json'
        })
    
    def _make_request(self, params):
        """Método base para hacer requests con manejo de errores"""
        try:
            params['apikey'] = self.api_key
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar si hay error en la respuesta de Alpha Vantage
                if 'Error Message' in data:
                    error_msg = data.get('Error Message', 'Error desconocido')
                    print(f"  ✗ Error Alpha Vantage: {error_msg[:100]}")
                    return None
                
                # Verificar rate limit
                if 'Note' in data and 'call frequency' in data['Note']:
                    print(f"  ⚠️ Rate limit alcanzado: {data['Note'][:100]}")
                    return None
                
                return data
            else:
                print(f"  ✗ Error HTTP {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("  ✗ Timeout al conectar con Alpha Vantage")
            return None
        except requests.exceptions.ConnectionError:
            print("  ✗ Error de conexión con Alpha Vantage")
            return None
        except Exception as e:
            print(f"  ✗ Error inesperado: {e}")
            return None
    
    def obtener_precio_diario(self, simbolo, outputsize='compact'):
        """Obtiene datos diarios históricos (compact=100 días, full=20+ años)"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': simbolo,
            'outputsize': outputsize
        }
        
        print(f"  Obteniendo datos diarios para {simbolo}...")
        data = self._make_request(params)
        
        if not data:
            print(f"    ✗ No se pudieron obtener datos para {simbolo}")
            return None
        
        # Debug info
        print(f"    Response keys: {list(data.keys())[:3]}...")
        
        if 'Time Series (Daily)' not in data:
            print(f"    ✗ No hay 'Time Series (Daily)' en la respuesta")
            return None
        
        return self._procesar_datos_diarios(data, simbolo)
    
    def _procesar_datos_diarios(self, data, simbolo):
        """Procesa datos diarios históricos y los guarda en la base de datos"""
        time_series = data.get('Time Series (Daily)', {})
        precios_guardados = []
        
        try:
            accion = AccionInternacional.objects.get(simbolo=simbolo)
        except AccionInternacional.DoesNotExist:
            print(f"    ✗ Acción {simbolo} no encontrada en la base de datos")
            return []
        
        count = 0
        today = date.today()
        
        for fecha_str, valores in time_series.items():
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                
                # FILTRAR FECHAS FUTURAS
                if fecha > today:
                    print(f"      ⚠️ Saltando fecha futura: {fecha_str}")
                    continue
                
                # Crear o actualizar precio
                precio, created = PrecioAccion.objects.update_or_create(
                    accion=accion,
                    fecha=fecha,
                    defaults={
                        'apertura': float(valores.get('1. open', 0)),
                        'maximo': float(valores.get('2. high', 0)),
                        'minimo': float(valores.get('3. low', 0)),
                        'cierre': float(valores.get('4. close', 0)),
                        'cierre_ajustado': float(valores.get('5. adjusted close', valores.get('4. close', 0))),
                        'volumen': int(float(valores.get('6. volume', 0))),
                        'dividendo': float(valores.get('7. dividend amount', 0)),
                        'split': float(valores.get('8. split coefficient', 1))
                    }
                )
                
                precios_guardados.append(precio)
                count += 1
                
                # Limitar para no sobrecargar en la primera ejecución
                if count >= 30:  # Solo primeros 30 días
                    break
                    
            except Exception as e:
                print(f"      Error procesando {fecha_str}: {e}")
                continue
        
        print(f"    ✓ {simbolo}: {count} precios procesados")
        return precios_guardados
    
    def obtener_multiple_precios_diarios(self, simbolos, outputsize='compact'):
        """Obtiene precios diarios para múltiples símbolos con delay"""
        resultados = {}
        
        for i, simbolo in enumerate(simbolos):
            print(f"  Procesando {i+1}/{len(simbolos)}: {simbolo}")
            
            # Obtener datos
            precios = self.obtener_precio_diario(simbolo, outputsize)
            resultados[simbolo] = len(precios) if precios else 0
            
            # Esperar 15 segundos entre llamadas para no exceder límite
            if i < len(simbolos) - 1:
                print(f"    Esperando 12 segundos por rate limit...")
                time.sleep(12)
        
        return resultados


# Función helper para uso rápido
def obtener_ultimos_precios(simbolo, dias=30):
    """Obtiene los últimos N días de precios para un símbolo"""
    try:
        accion = AccionInternacional.objects.get(simbolo=simbolo)
        fecha_limite = timezone.now().date() - timedelta(days=dias)
        
        precios = PrecioAccion.objects.filter(
            accion=accion,
            fecha__gte=fecha_limite
        ).order_by('fecha')
        
        return precios
    except Exception as e:
        print(f"Error obteniendo precios para {simbolo}: {e}")
        return []