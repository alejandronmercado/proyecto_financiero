# dashboard/views.py
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.utils import timezone
from datetime import date, timedelta
from .models import Cotizacion, IndiceEconomico
from .services import actualizar_todos_los_datos
from .analytics import (AnalizadorMercadoInternacional, obtener_resumen_mercado, generar_grafico_heatmap_rendimientos)
from .models import AccionInternacional
import plotly.express as px
import pandas as pd
from django.db.models import Count


class DashboardView(TemplateView):
    """Vista principal del dashboard con resumen de datos"""
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        
        # Cotizaciones de hoy
        cotizaciones_hoy = Cotizacion.objects.filter(fecha=hoy)
        
        # Cotizaciones de ayer para comparar
        cotizaciones_ayer = Cotizacion.objects.filter(fecha=ayer)
        
        # Índices económicos de hoy
        indices_hoy = IndiceEconomico.objects.filter(fecha=hoy)
        
        # Calcular cambios porcentuales
        context['cotizaciones'] = []
        for tipo in ['oficial', 'blue', 'mep', 'ccl']:
            try:
                cot_hoy = cotizaciones_hoy.get(tipo=tipo)
                cot_ayer = cotizaciones_ayer.get(tipo=tipo)
                
                # Calcular variación
                variacion = ((cot_hoy.venta - cot_ayer.venta) / cot_ayer.venta) * 100
                
                context['cotizaciones'].append({
                    'tipo': cot_hoy.get_tipo_display(),
                    'codigo': tipo,
                    'compra': cot_hoy.compra,
                    'venta': cot_hoy.venta,
                    'diferencia': cot_hoy.diferencia_precio(),
                    'spread': cot_hoy.spread_porcentual(),
                    'variacion': variacion,
                    'actualizado': cot_hoy.actualizado,
                })
            except Cotizacion.DoesNotExist:
                pass
        
        # Índices económicos
        context['indices'] = []
        for indice in indices_hoy:
            context['indices'].append({
                'nombre': indice.get_tipo_display(),
                'valor': indice.valor,
                'unidad': indice.unidad,
                'actualizado': indice.actualizado,
            })
        
        # Calcular brecha cambiaria
        try:
            oficial = cotizaciones_hoy.get(tipo='oficial')
            blue = cotizaciones_hoy.get(tipo='blue')
            context['brecha_cambiaria'] = ((blue.venta - oficial.venta) / oficial.venta) * 100
        except Cotizacion.DoesNotExist:
            context['brecha_cambiaria'] = None
        
        # Estadísticas generales
        context['total_cotizaciones'] = Cotizacion.objects.count()
        context['total_indices'] = IndiceEconomico.objects.count()
        context['hoy'] = hoy
        
        return context


class CotizacionesListView(ListView):
    """Lista de todas las cotizaciones históricas"""
    model = Cotizacion
    template_name = 'dashboard/cotizaciones_list.html'
    context_object_name = 'cotizaciones'
    paginate_by = 50
    ordering = ['-fecha', 'tipo']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        tipo = self.request.GET.get('tipo')
        fecha = self.request.GET.get('fecha')
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
            
        return queryset


class IndicesListView(ListView):
    """Lista de todos los índices económicos históricos"""
    model = IndiceEconomico
    template_name = 'dashboard/indices_list.html'
    context_object_name = 'indices'
    paginate_by = 50
    ordering = ['-fecha', 'tipo']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        tipo = self.request.GET.get('tipo')
        fecha = self.request.GET.get('fecha')
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
            
        return queryset


def actualizar_datos_manual(request):
    """Vista para actualizar datos manualmente"""
    if request.method == 'POST':
        resultado = actualizar_todos_los_datos()
        
        return render(request, 'dashboard/actualizacion_completada.html', {
            'resultado': resultado
        })
    
    return render(request, 'dashboard/actualizar_datos.html')

class MercadoInternacionalView(TemplateView):
    """Vista para el mercado internacional"""
    template_name = 'dashboard/mercado_internacional.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analizador = AnalizadorMercadoInternacional()
        
        # Obtener todos los símbolos activos
        simbolos = list(AccionInternacional.objects.filter(activo=True).values_list('simbolo', flat=True))
        
        # Obtener métricas para todos los símbolos
        metricas = analizador.generar_tabla_metricas(simbolos, dias=30)
        
        # Generar gráficos
        simbolos_principales = ['AAPL', 'MSFT', 'SPY', 'QQQ']
        
        # Gráfico comparativo
        context['grafico_comparativo'] = analizador.generar_grafico_comparativo(
            simbolos_principales, dias=30
        )
        
        # Heatmap de rendimientos
        context['heatmap_rendimientos'] = generar_grafico_heatmap_rendimientos(
            simbolos_principales, dias=5
        )
        
        # Gráficos individuales
        context['graficos_individuales'] = {}
        for simbolo in simbolos_principales[:3]:  # Primeros 3
            context['graficos_individuales'][simbolo] = analizador.generar_grafico_linea(
                simbolo, dias=30
            )
        
        # Tabla de métricas
        context['metricas_acciones'] = metricas
        
        # Resumen rápido
        context['resumen_mercado'] = obtener_resumen_mercado(dias=7)
        
        # Estadísticas
        context['total_acciones'] = AccionInternacional.objects.count()
        context['total_precios'] = sum(
            AccionInternacional.objects.get(simbolo=s).precios.count() 
            for s in simbolos if AccionInternacional.objects.filter(simbolo=s).exists()
        )
        
        # Agrupar por tipo
        context['acciones_por_tipo'] = AccionInternacional.objects.values('tipo').annotate(
            total=Count('id')
        )
        
        return context



class DashboardView(TemplateView):
    """Vista principal del dashboard con resumen de datos"""
    template_name = 'dashboard/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoy = date.today()
        ayer = hoy - timedelta(days=1)
        
        # Resumen mercado internacional
        try:
            analizador = AnalizadorMercadoInternacional()
            
            # Obtener métricas para símbolos principales
            simbolos_principales = ['AAPL', 'MSFT', 'SPY']
            metricas_internacionales = []
            
            for simbolo in simbolos_principales:
                metricas = analizador.calcular_metricas_basicas(simbolo, dias=7)
                if metricas:
                    metricas_internacionales.append(metricas)
            
            context['metricas_internacionales'] = metricas_internacionales
            
            # Calcular correlación dólar blue vs acciones (ejemplo)
            if metricas_internacionales:
                context['correlacion_aapl_blue'] = analizador.calcular_correlacion_dolar_blue('AAPL', 30)
            
            # Gráfico mini comparativo
            context['grafico_mini_internacional'] = analizador.generar_grafico_comparativo(
                ['AAPL', 'SPY'], dias=7
            )
            
        except Exception as e:
            print(f"Error cargando datos internacionales: {e}")
            context['metricas_internacionales'] = []
        
        return context