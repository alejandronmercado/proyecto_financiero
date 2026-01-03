# dashboard/management/commands/cargar_acciones_internacionales.py
from django.core.management.base import BaseCommand
from dashboard.models import AccionInternacional


class Command(BaseCommand):
    help = 'Carga las acciones y ETFs internacionales iniciales'
    
    def handle(self, *args, **options):
        simbolos = [
            # Acciones
            ('AAPL', 'Apple Inc.', 'accion', 'Tecnología'),
            ('MSFT', 'Microsoft Corporation', 'accion', 'Tecnología'),
            ('TSLA', 'Tesla Inc.', 'accion', 'Automotriz'),
            ('GOOGL', 'Alphabet Inc. (Google)', 'accion', 'Tecnología'),
            ('META', 'Meta Platforms Inc. (Facebook)', 'accion', 'Tecnología'),
            ('NVDA', 'NVIDIA Corporation', 'accion', 'Tecnología'),
            
            # ETFs Principales
            ('SPY', 'SPDR S&P 500 ETF', 'etf', 'Índice'),
            ('QQQ', 'Invesco QQQ Trust (NASDAQ 100)', 'etf', 'Índice'),
            ('VTI', 'Vanguard Total Stock Market ETF', 'etf', 'Total Market'),
            ('VOO', 'Vanguard S&P 500 ETF', 'etf', 'Índice'),
            ('GLD', 'SPDR Gold Shares', 'etf', 'Commodities'),
            ('IWM', 'iShares Russell 2000 ETF', 'etf', 'Small Cap'),
            ('EEM', 'iShares MSCI Emerging Markets ETF', 'etf', 'Emerging Markets'),
        ]
        
        count_creados = 0
        count_actualizados = 0
        
        for simbolo, nombre, tipo, sector in simbolos:
            try:
                obj, created = AccionInternacional.objects.update_or_create(
                    simbolo=simbolo,
                    defaults={
                        'nombre': nombre,
                        'tipo': tipo,
                        'sector': sector,
                        'pais': 'USA',
                        'moneda': 'USD',
                        'activo': True
                    }
                )
                
                if created:
                    count_creados += 1
                    self.stdout.write(self.style.SUCCESS(f'✓ Creado: {simbolo} - {nombre}'))
                else:
                    count_actualizados += 1
                    self.stdout.write(self.style.WARNING(f'↻ Actualizado: {simbolo}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error con {simbolo}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Carga completada: {count_creados} creados, {count_actualizados} actualizados'
        ))
        
        # Mostrar resumen
        total = AccionInternacional.objects.count()
        self.stdout.write(f'Total de acciones en base de datos: {total}')