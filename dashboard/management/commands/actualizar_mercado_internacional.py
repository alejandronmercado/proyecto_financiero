from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.services.alpha_vantage_service import AlphaVantageService
from dashboard.models import AccionInternacional
import time
from datetime import datetime
from django.conf import settings



class Command(BaseCommand):
    help = 'Actualiza los precios del mercado internacional desde Alpha Vantage'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--simbolos',
            type=str,
            help='Símbolos específicos a actualizar (separados por comas)'
        )
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['accion', 'etf', 'indice', 'todos'],
            default='todos',
            help='Tipo de activos a actualizar'
        )
        parser.add_argument(
            '--full',
            action='store_true',
            help='Obtener historial completo (20+ años) en lugar de solo 100 días'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('ACTUALIZACIÓN DE MERCADO INTERNACIONAL')
        self.stdout.write('=' * 60)
        
        service = AlphaVantageService()

        # Obtener la API Key desde settings
        api_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', '')
        
        self.stdout.write(f"API Key configurada: {'SÍ' if api_key else 'NO'}")
        if api_key:
            self.stdout.write(f"API Key (primeros 5): {api_key[:5]}...")
            
        # Obtener símbolos según parámetros
        simbolos_filtrados = self._obtener_simbolos_filtrados(options)
        
        if not simbolos_filtrados:
            self.stdout.write(self.style.ERROR('No se encontraron símbolos para actualizar'))
            return
        
        self.stdout.write(f"Símbolos a actualizar: {', '.join(simbolos_filtrados)}")
        self.stdout.write(f"Total: {len(simbolos_filtrados)} símbolos")
        
        # Configurar servicio
        service = AlphaVantageService()
        
        # Determinar outputsize
        outputsize = 'full' if options['full'] else 'compact'
        
        if options['full']:
            self.stdout.write(self.style.WARNING(
                '⚠️  Modo FULL: Se descargará historial completo (puede tardar mucho)'
            ))
        
        # Obtener precios
        self.stdout.write('\n[1/1] Obteniendo precios diarios...')
        
        resultados = service.obtener_multiple_precios_diarios(
            simbolos_filtrados,
            outputsize=outputsize
        )
        
        # Mostrar resumen
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('RESUMEN DE ACTUALIZACIÓN')
        self.stdout.write('=' * 60)
        
        total_precios = 0
        simbolos_exitosos = 0
        
        for simbolo, count in resultados.items():
            if count > 0:
                self.stdout.write(self.style.SUCCESS(f'✓ {simbolo}: {count} precios actualizados'))
                simbolos_exitosos += 1
                total_precios += count
            else:
                self.stdout.write(self.style.ERROR(f'✗ {simbolo}: No se pudieron obtener datos'))
        
        self.stdout.write('\n' + '-' * 40)
        self.stdout.write(f"Total símbolos exitosos: {simbolos_exitosos}/{len(simbolos_filtrados)}")
        self.stdout.write(f"Total precios obtenidos: {total_precios}")
        
        # Estadísticas generales
        total_acciones = AccionInternacional.objects.count()
        total_precios_db = sum(
            AccionInternacional.objects.get(simbolo=s).precios.count() 
            for s in simbolos_filtrados 
            if AccionInternacional.objects.filter(simbolo=s).exists()
        )
        
        self.stdout.write(f"\n📊 Estadísticas generales:")
        self.stdout.write(f"   • Acciones/ETFs en BD: {total_acciones}")
        self.stdout.write(f"   • Precios almacenados: {total_precios_db}")
        
        self.stdout.write(self.style.SUCCESS('\n✅ Actualización completada'))
    
    def _obtener_simbolos_filtrados(self, options):
        """Obtiene lista de símbolos según filtros"""
        queryset = AccionInternacional.objects.filter(activo=True)
        
        # Filtrar por tipo
        if options['tipo'] != 'todos':
            queryset = queryset.filter(tipo=options['tipo'])
        
        # Filtrar por símbolos específicos
        if options['simbolos']:
            simbolos_lista = [s.strip().upper() for s in options['simbolos'].split(',')]
            queryset = queryset.filter(simbolo__in=simbolos_lista)
        
        return list(queryset.values_list('simbolo', flat=True))