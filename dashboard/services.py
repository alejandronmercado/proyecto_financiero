import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from datetime import datetime, timedelta
from .models import Cotizacion, IndiceEconomico

class DolarAPIService:
    BASE_URL = 'https://dolarapi.com/v1'

    def __init__(self):
        self.timeout = 10
        self.headers = {
            'User-Agent': 'DashboardFinanciero/1.0',
            'Accept': 'application/json'
        }

    def obtener_cotizaciones(self):
        tipos = {
            'blue': 'dolares/blue',
            'mep': 'dolares/bolsa', 
            'ccl': 'dolares/contadoconliqui'
        }

        cotizaciones_guardadas = []
        fecha_hoy = datetime.now().date()

        for tipo, endpoint in tipos.items():
            try:
                url = f'{self.BASE_URL}/{endpoint}'
                response = requests.get(url, timeout=self.timeout, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    cotizacion, created = Cotizacion.objects.update_or_create(
                        tipo=tipo,
                        fecha=fecha_hoy,
                        defaults={
                            'compra': data['compra'],
                            'venta': data['venta']
                        }
                    )
                    cotizaciones_guardadas.append(cotizacion)
                    accion = 'creada' if created else 'actualizada'
                    print(f'Cotización {tipo} {accion}: ${cotizacion.venta}')
                else:
                    print(f'Error al obtener {tipo}: HTTP {response.status_code}')
            
            except requests.exceptions.Timeout:
                print(f'Timeout al obtener {tipo}')
            except requests.exceptions.ConnectionError:
                print(f'Sin conexión al obtener {tipo}')
            except Exception as e:
                print(f'Error inesperado al obtener {tipo}: {e}')
        
        return cotizaciones_guardadas

    def obtener_cotizacion_especifica(self, tipo):
        endpoints = {
            'blue': 'dolares/blue',
            'mep': 'dolares/bolsa',
            'ccl': 'dolares/contadoconliqui'
        }

        if tipo not in endpoints:
            print(f'Tipo inválido: {tipo}')
            return None
        
        try:
            url = f'{self.BASE_URL}/{endpoints[tipo]}'
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                cotizacion, created = Cotizacion.objects.update_or_create(
                    tipo=tipo,
                    fecha=datetime.now().date(),
                    defaults={
                        'compra': data['compra'],
                        'venta': data['venta']
                    }
                )
                return cotizacion
        except Exception as e:
            print(f'Error: {e}')
            return None


class BCRACambiarioService:
    """Dólar oficial de Estadísticas Cambiarias v1.0 - Sin token"""
    BASE_URL = 'https://api.bcra.gob.ar/estadisticascambiarias/v1.0'

    def __init__(self):
        self.timeout = 15
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'DashboardFinanciero/1.0',
            'Accept': 'application/json'
        })

    def obtener_dolar_oficial(self):
        """Obtiene la cotización del dólar oficial del día actual"""
        try:
            # Método 1: Endpoint general de cotizaciones del día
            url = f'{self.BASE_URL}/Cotizaciones'
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                
                # Según el Swagger: data['results'] tiene fecha y detalle
                if 'results' in data and data['results']:
                    resultados = data['results']
                    fecha_str = resultados.get('fecha')
                    
                    if resultados.get('detalle'):
                        # Buscar USD en los detalles
                        for detalle in resultados['detalle']:
                            if detalle.get('codigoMoneda') == 'USD':
                                cotizacion_valor = detalle.get('tipoCotizacion')
                                
                                if fecha_str and cotizacion_valor is not None:
                                    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                                    
                                    cotizacion, created = Cotizacion.objects.update_or_create(
                                        tipo='oficial',
                                        fecha=fecha,
                                        defaults={
                                            'compra': cotizacion_valor,
                                            'venta': cotizacion_valor
                                        }
                                    )
                                    accion = 'creada' if created else 'actualizada'
                                    print(f'Cotización oficial (BCRA) {accion}: ${cotizacion.venta}')
                                    return cotizacion
                    
                    print("No se encontró USD en los detalles de la respuesta")
                    return None
                else:
                    print("La respuesta no contiene 'results'")
                    return None
            else:
                print(f'Error HTTP al obtener dólar oficial: {response.status_code}')
                return None
                
        except Exception as e:
            print(f'Error al obtener dólar oficial: {e}')
            return None


class BCRAMonetarioService:
    """Reservas y tasa de interés de Estadísticas v4.0 - Sin token"""
    BASE_URL = 'https://api.bcra.gob.ar/estadisticas/v4.0'
    
    # IDs según documentación previa
    RESERVAS_ID = 1      # Reservas Internacionales
    TASA_POLITICA_ID = 7 # Tasa de Política Monetaria

    def __init__(self):
        self.timeout = 15
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'DashboardFinanciero/1.0',
            'Accept': 'application/json'
        })

    def _obtener_dato_variable(self, variable_id, nombre_variable, unidad):
        """Método genérico para obtener cualquier variable monetaria"""
        try:
            url = f'{self.BASE_URL}/Monetarias/{variable_id}'
            
            # Parámetros para el último dato
            hoy = datetime.now().date()
            params = {
                'Limit': 1,
                'Hasta': hoy.strftime('%Y-%m-%d')
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Estructura: data['results'][0]['detalle'][0]
                if data.get('results') and len(data['results']) > 0:
                    variable_data = data['results'][0]
                    
                    if variable_data.get('detalle') and len(variable_data['detalle']) > 0:
                        ultimo_dato = variable_data['detalle'][0]
                        fecha_str = ultimo_dato.get('fecha')
                        valor = ultimo_dato.get('valor')
                        
                        if fecha_str and valor is not None:
                            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                            
                            indice, created = IndiceEconomico.objects.update_or_create(
                                tipo=nombre_variable,
                                fecha=fecha,
                                defaults={
                                    'valor': valor,
                                    'unidad': unidad
                                }
                            )
                            print(f'{nombre_variable.capitalize()} guardadas: {valor:,.2f} {unidad}')
                            return indice
                    else:
                        print(f"No hay datos en 'detalle' para {nombre_variable}")
                else:
                    print(f"No hay 'results' en la respuesta para {nombre_variable}")
                    
            else:
                print(f'Error HTTP {response.status_code} al obtener {nombre_variable}')
                
        except Exception as e:
            print(f'Error al obtener {nombre_variable}: {e}')
        
        return None

    def obtener_reservas(self):
        """Obtiene las Reservas Internacionales"""
        return self._obtener_dato_variable(
            variable_id=self.RESERVAS_ID,
            nombre_variable='reservas',
            unidad='Millones USD'
        )

    def obtener_tasa_politica(self):
        """Obtiene la Tasa de Política Monetaria"""
        return self._obtener_dato_variable(
            variable_id=self.TASA_POLITICA_ID,
            nombre_variable='tasa',
            unidad='%'
        )


def actualizar_todos_los_datos():
    print('='*60)
    print('INICIANDO ACTUALIZACIÓN DE DATOS')
    print('='*60)

    dolar_service = DolarAPIService()
    bcra_cambiario = BCRACambiarioService()  # Dólar oficial
    bcra_monetario = BCRAMonetarioService()  # Reservas y tasa

    print('\n[1/4] Obteniendo dólar oficial del BCRA...')
    dolar_oficial = bcra_cambiario.obtener_dolar_oficial()
    if dolar_oficial:
        print(f' Dólar oficial obtenido: ${dolar_oficial.venta}')
    else:
        print(' No se pudo obtener el dólar oficial')

    print('\n[2/4] Obteniendo cotizaciones de mercado (blue, mep, ccl)...')
    cotizaciones_mercado = dolar_service.obtener_cotizaciones()
    if cotizaciones_mercado:
        print(f' Cotizaciones obtenidas: {len(cotizaciones_mercado)}')
    else:
        print(' No se pudieron obtener las cotizaciones')

    print('\n[3/4] Obteniendo reservas del BCRA...')
    reservas = bcra_monetario.obtener_reservas()
    if not reservas:
        print(' No se pudieron obtener las reservas')

    print('\n[4/4] Obteniendo tasa del BCRA...')
    tasa = bcra_monetario.obtener_tasa_politica()
    if not tasa:
        print(' No se pudo obtener la tasa')
    
    print('\n' + '='*60)
    print('ACTUALIZACIÓN COMPLETADA')
    print('='*60)

    # Combinar todas las cotizaciones
    todas_cotizaciones = []
    if dolar_oficial:
        todas_cotizaciones.append(dolar_oficial)
    if cotizaciones_mercado:
        todas_cotizaciones.extend(cotizaciones_mercado)

    return {
        'cotizaciones': len(todas_cotizaciones),
        'dolar_oficial': dolar_oficial,
        'cotizaciones_mercado': cotizaciones_mercado,
        'reservas': reservas,
        'tasa': tasa,
        'timestamp': datetime.now()
    }


def limpiar_datos_antiguos(dias=90):
    fecha_limite = datetime.now().date() - timedelta(days=dias)
    print(f'Eliminando datos anteriores a {fecha_limite}...')

    cotizaciones_viejas = Cotizacion.objects.filter(fecha__lt=fecha_limite)
    cantidad_cot = cotizaciones_viejas.count()
    cotizaciones_viejas.delete()

    indices_viejos = IndiceEconomico.objects.filter(fecha__lt=fecha_limite)
    cantidad_ind = indices_viejos.count()
    indices_viejos.delete()
    
    print(f'✓ Eliminadas {cantidad_cot} cotizaciones')
    print(f'✓ Eliminados {cantidad_ind} índices económicos')
    
    return {
        'cotizaciones': cantidad_cot,
        'indices': cantidad_ind
    }
