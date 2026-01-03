import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Max, Min, StdDev, Count
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from .models import PrecioAccion, AccionInternacional, Cotizacion


class AnalizadorMercadoInternacional:
    """Clase para análisis y visualización de datos del mercado internacional"""
    
    def __init__(self):
        self.hoy = timezone.now().date()
    
    def obtener_datos_dataframe(self, simbolo, dias=30):
        """Convierte datos de la base de datos a DataFrame de pandas"""
        try:
            accion = AccionInternacional.objects.get(simbolo=simbolo)
            fecha_limite = self.hoy - timedelta(days=dias)
            
            precios = PrecioAccion.objects.filter(
                accion=accion,
                fecha__gte=fecha_limite
            ).order_by('fecha')
            
            if not precios.exists():
                return None
            
            # Convertir a DataFrame
            data = []
            for precio in precios:
                data.append({
                    'fecha': precio.fecha,
                    'apertura': float(precio.apertura),
                    'maximo': float(precio.maximo),
                    'minimo': float(precio.minimo),
                    'cierre': float(precio.cierre),
                    'cierre_ajustado': float(precio.cierre_ajustado),
                    'volumen': float(precio.volumen),
                    'retorno_diario': float(precio.retorno_diario()),
                })
            
            df = pd.DataFrame(data)
            df.set_index('fecha', inplace=True)
            return df
            
        except AccionInternacional.DoesNotExist:
            return None
    
    def calcular_metricas_basicas(self, simbolo, dias=30):
        """Calcula métricas básicas para un símbolo"""
        df = self.obtener_datos_dataframe(simbolo, dias)
        
        if df is None or df.empty:
            return None
        
        # Calcular métricas
        ultimo_precio = df['cierre'].iloc[-1]
        primer_precio = df['cierre'].iloc[0]
        
        retorno_total = ((ultimo_precio - primer_precio) / primer_precio * 100)
        volatilidad = df['retorno_diario'].std() * np.sqrt(252)  # Anualizada
        
        maximo = df['maximo'].max()
        minimo = df['minimo'].min()
        volumen_promedio = df['volumen'].mean()
        
        # Media móvil 20 días
        if len(df) >= 20:
            media_movil_20 = df['cierre'].rolling(window=20).mean().iloc[-1]
        else:
            media_movil_20 = None
        
        return {
            'simbolo': simbolo,
            'ultimo_precio': round(ultimo_precio, 2),
            'retorno_periodo': round(retorno_total, 2),
            'volatilidad_anual': round(volatilidad, 2),
            'maximo_periodo': round(maximo, 2),
            'minimo_periodo': round(minimo, 2),
            'volumen_promedio': f"{volumen_promedio:,.0f}",
            'media_movil_20': round(media_movil_20, 2) if media_movil_20 else None,
            'dias_analizados': len(df)
        }
    
    def generar_grafico_linea(self, simbolo, dias=30):
        """Genera gráfico de línea para un símbolo"""
        df = self.obtener_datos_dataframe(simbolo, dias)
        
        if df is None or df.empty:
            return None
        
        fig = go.Figure()
        
        # Agregar línea de precios
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['cierre'],
            mode='lines',
            name='Precio de Cierre',
            line=dict(color='#1f77b4', width=2)
        ))
        
        # Agregar media móvil 20 días si hay suficientes datos
        if len(df) >= 20:
            df['MA20'] = df['cierre'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['MA20'],
                mode='lines',
                name='Media Móvil 20 días',
                line=dict(color='#ff7f0e', width=1, dash='dash')
            ))
        
        # Configurar layout
        accion = AccionInternacional.objects.get(simbolo=simbolo)
        fig.update_layout(
            title=f'{simbolo} - {accion.nombre} (Últimos {dias} días)',
            xaxis_title='Fecha',
            yaxis_title='Precio (USD)',
            template='plotly_white',
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def generar_grafico_comparativo(self, simbolos, dias=30):
        """Genera gráfico comparativo de múltiples símbolos (normalizado)"""
        datos = {}
        
        # Obtener datos para cada símbolo
        for simbolo in simbolos:
            df = self.obtener_datos_dataframe(simbolo, dias)
            if df is not None and not df.empty:
                # Normalizar a 100 para comparación
                primer_precio = df['cierre'].iloc[0]
                datos[simbolo] = (df['cierre'] / primer_precio * 100).tolist()
        
        if not datos:
            return None
        
        # Crear figura
        fig = go.Figure()
        
        # Agregar cada símbolo
        for simbolo, valores in datos.items():
            accion = AccionInternacional.objects.get(simbolo=simbolo)
            
            fig.add_trace(go.Scatter(
                x=list(range(len(valores))),
                y=valores,
                mode='lines',
                name=f'{simbolo}',
                hovertemplate=f'{simbolo}: %{{y:.1f}}<extra></extra>'
            ))
        
        # Configurar layout
        fig.update_layout(
            title=f'Comparativa Normalizada (Base 100) - Últimos {dias} días',
            xaxis_title='Días',
            yaxis_title='Rendimiento (%)',
            template='plotly_white',
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        return fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    def generar_tabla_metricas(self, simbolos, dias=30):
        """Genera tabla con métricas para múltiples símbolos"""
        metricas = []
        
        for simbolo in simbolos:
            datos = self.calcular_metricas_basicas(simbolo, dias)
            if datos:
                metricas.append(datos)
        
        return metricas
    
    def calcular_correlacion_dolar_blue(self, simbolo, dias=30):
        """Calcula correlación entre una acción y el dólar blue"""
        try:
            # Obtener datos de la acción
            df_accion = self.obtener_datos_dataframe(simbolo, dias)
            if df_accion is None or df_accion.empty:
                return None
            
            # Obtener datos del dólar blue
            fecha_limite = self.hoy - timedelta(days=dias)
            cotizaciones = Cotizacion.objects.filter(
                tipo='blue',
                fecha__gte=fecha_limite
            ).order_by('fecha')
            
            # Convertir a Series
            precios_accion = df_accion['cierre']
            precios_dolar = pd.Series({
                c.fecha: float(c.venta)
                for c in cotizaciones
            })
            
            # Alinear fechas
            fechas_comunes = set(precios_accion.index) & set(precios_dolar.index)
            if len(fechas_comunes) < 5:
                return None
            
            # Calcular correlación
            correlacion = np.corrcoef(
                precios_accion.loc[list(fechas_comunes)].values,
                precios_dolar.loc[list(fechas_comunes)].values
            )[0, 1]
            
            return round(correlacion, 3)
            
        except Exception as e:
            print(f"Error calculando correlación para {simbolo}: {e}")
            return None


# Funciones helper rápidas
def obtener_resumen_mercado(dias=7):
    """Obtiene resumen rápido del mercado internacional"""
    analizador = AnalizadorMercadoInternacional()
    
    # Símbolos principales
    simbolos_principales = ['AAPL', 'MSFT', 'SPY', 'QQQ']
    
    resumen = []
    for simbolo in simbolos_principales:
        metricas = analizador.calcular_metricas_basicas(simbolo, dias)
        if metricas:
            resumen.append(metricas)
    
    return resumen


def generar_grafico_heatmap_rendimientos(simbolos, dias=5):
    """Genera heatmap de rendimientos diarios"""
    datos_heatmap = []
    fechas = []
    
    for simbolo in simbolos:
        df = AnalizadorMercadoInternacional().obtener_datos_dataframe(simbolo, dias)
        if df is not None and not df.empty:
            # Calcular rendimientos diarios
            rendimientos = df['cierre'].pct_change().dropna() * 100
            
            if not fechas:
                fechas = [f.strftime('%d/%m') for f in rendimientos.index]
            
            datos_heatmap.append({
                'simbolo': simbolo,
                'rendimientos': rendimientos.values.tolist()
            })
    
    if not datos_heatmap:
        return None
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[d['rendimientos'] for d in datos_heatmap],
        x=fechas,
        y=[d['simbolo'] for d in datos_heatmap],
        colorscale='RdYlGn',
        zmid=0,
        text=[[f"{v:.1f}%" for v in d['rendimientos']] for d in datos_heatmap],
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title=f'Heatmap de Rendimientos Diarios (Últimos {dias} días)',
        xaxis_title='Fecha',
        yaxis_title='Símbolo',
        height=300,
        template='plotly_white'
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')