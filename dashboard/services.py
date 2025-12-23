import requests
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
            'oficial': 'dolares/oficiales',
            'blue': 'dolares/blue',
            'mep': 'dolares/bolsa',
            'ccl': 'dolares/contadoconliqui'
        }

        cotizaciones_guardadas = []
        fecha_hoy = datetime.now().date()

        for tipo, endpoint in tipos.items():
            try:
                url = f'{self.BASE_URL}/{endpoint}'
                response = requests.get(
                    url,
                    timeout=self.timeout,
                    headers=self.headers
                )

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
        'oficial': 'dolares/oficial',
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
    
class BCRAService:
    BASE_URL = 'https://api.bcra.gob.ar/estadisticas/v2.0'

    def __init__(self):
        self.timeout = 15
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DashboardFincaciero/1.0',
            'Accept': 'application/json'
        })

    def obtener_reservas(self):
        try:
            url = f'{self.BASE_URL}/DatosVariable/1'
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data= response.json()
                if data.get('Results'):
                        ultimo = data['Results'][0]
                        fecha = datetime.strptime(
                            ultimo['fecha'],
                            '%Y-%m-%d'
                        ).date()    
                
            indice, created = IndiceEconomico.objects.update_or_create(
                tipo='reservas',
                fecha=fecha,
                defaults={
                    'valor': ultimo['valor'],
                    'unidad': 'Millones USD'
                }
            )

            print(f'Reservas guardadas:${indice.valor} millones')
            return indice
        
        except Exception as e:
            print(f'Error al obtener reservas BCRA: {e}')
            return None

    def obtener_tasa_politica(self):
        try:
            url = f'{self.BASE_URL}/DatosVariables/7'
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data=response.json()

                if data.get('Results'):
                    ultimo = data['Results'][0]
                    fecha = datetime.strptime(ultimo['fecha'], '%Y-%m-%d').date()

                    indice, created = IndiceEconomico.objects.update_or_create(
                        tipo='tasa',
                        fecha=fecha,
                        defaults={
                            'valor': ultimo['valor'],
                            'unidad': '%'
                        }
                    )

                    print(f'Tasa guardada: {indice.valor}%')
                    return indice
    
        except Exception as e:
            print(f'Error al obtener tasa BCRA: {e}')
            return None

def actualizar_todos_los_datos():
    print('='*60)
    print('INICIANDO ACTUALIZACION DE DATOS')
    print('='*60)

    dolar_service = DolarAPIService()
    bcra_service = BCRAService()

    print('\n[2/3] Obteniendo reservas del BCRA...')
    reservas = bcra_service.obtener_reservas() 
    if reservas:
        print(f' Reservas actualizadas: ${reservas.valor} millones')
    else:
        print(' No se pudieron obtener las reservas')

    print("\n[3/3] Obteniendo tasa del BCRA...")
    tasa = bcra_service.obtener_tasa_politica()
    if tasa:
        print(f" Tasa actualizada: {tasa.valor}%")
    else:
        print(" Nose pudo obtener la tasa")
    
    print("\n" + "=" * 60)
    print("ACTUALIZACIÓN COMPLETADA")
    print("=" * 60)

    return {
        'cotizaciones': len(cotizaciones),
        'reservas': reservas,
        'tasa': tasa,
        'timestamp': datetime.now()
    }

def limpiar_datos_antiguos(dias=90):
    fecha_limite = datetime.now().date() - timedelta(days=dias)

    print(f"Eliminando datos anteriores a {fecha_limite}...")

    cotizaciones_viejas = Cotizacion.objects.filter(fecha__lt=fecha_limite)
    cantidad_cot = cotizaciones_viejas.count()
    cotizaciones_viejas.delete()

    indices_viejos = IndiceEconomico.objects.filter(fecha__lt=fecha_limite)
    cantidad_ind = indices_viejos.count()
    indices_viejos.delete()
    
    print(f"✓ Eliminadas {cantidad_cot} cotizaciones")
    print(f"✓ Eliminados {cantidad_ind} índices económicos")
    
    return {
        'cotizaciones': cantidad_cot,
        'indices': cantidad_ind
    }

    