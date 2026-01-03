from django.db import models

class Cotizacion(models.Model):
    TIPOS_DOLAR = [
        ('oficial', 'Dólar Oficial'),
        ('blue', 'Dólar Blue'),
        ('mep', 'Dólar MEP'),
        ('ccl', 'Dólar CCL'),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_DOLAR,
        help_text='Tipo de cotización del dólar'
    )

    fecha = models.DateField(
        help_text='Fecha de la cotización'
    )

    compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio de compra en ARS'
    )

    venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio de venta en ARS'
    )

    actualizado = models.DateTimeField(
        auto_now=True,
        help_text='Fecha y hora de última actualización'
    )

    class Meta:
        unique_together = ['tipo', 'fecha']
        ordering = ['-fecha', 'tipo']
        verbose_name_plural = 'Cotizaciones'
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['tipo', 'fecha']),
        ]
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.fecha}'
    
    def diferencia_precio(self):
        """Calcula la diferencia entre precio de venta y compra"""
        return self.venta - self.compra
    
    def spread_porcentual(self):
        """Calcula el porcentaje de diferencia entre compra y venta"""
        if self.compra > 0:
            return float((self.venta - self.compra) / self.compra * 100)
        return 0.0


class IndiceEconomico(models.Model):
    """
    Modelo para almacenar indicadores económicos del BCRA.
    
    Ejemplo de registro:
    - tipo: 'reservas'
    - fecha: 2024-01-15
    - valor: 25000.00
    - unidad: 'Millones USD'
    """
    
    TIPOS_INDICE = [
        ('inflacion', 'Inflación Mensual'),
        ('tasa', 'Tasa de Interés BCRA'),
        ('reservas', 'Reservas Internacionales'),
        ('riesgo_pais', 'Riesgo País'),
        ('merval', 'Índice Merval'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_INDICE,
        help_text='Tipo de índice económico'
    )
    
    fecha = models.DateField(
        help_text='Fecha del índice'
    )
    
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Valor del índice'
    )
    
    unidad = models.CharField(
        max_length=50,
        help_text='Unidad de medida (ej: %, Millones USD, puntos)'
    )
    
    actualizado = models.DateTimeField(
        auto_now=True,
        help_text='Fecha y hora de última actualización'
    )
    
    class Meta:
        unique_together = ['tipo', 'fecha']
        ordering = ['-fecha', 'tipo']
        verbose_name_plural = 'Índices Económicos'
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['tipo', 'fecha']),
        ]
    
    def __str__(self):
        return f'{self.get_tipo_display()} - {self.fecha}: {self.valor} {self.unidad}'

class AccionInternacional(models.Model):
    """
    Modelo para almacenar acciones internacionales
    """
    TIPO_ACTIVO = [
        ('accion', 'Acción'),
        ('etf', 'ETF'),
        ('indice', 'Índice'),
    ]
    
    simbolo = models.CharField(
        max_length=10,
        unique=True,
        help_text='Símbolo de la acción (ej: AAPL, MSFT)'
    )
    
    nombre = models.CharField(
        max_length=200,
        help_text='Nombre completo de la empresa/fondo'
    )
    
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_ACTIVO,
        default='accion'
    )
    
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción del activo'
    )
    
    pais = models.CharField(
        max_length=50,
        default='USA',
        help_text='País de origen'
    )
    
    sector = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Sector económico'
    )
    
    moneda = models.CharField(
        max_length=10,
        default='USD',
        help_text='Moneda de cotización'
    )
    
    activo = models.BooleanField(
        default=True,
        help_text='Indica si sigue activo en el mercado'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        ordering = ['simbolo']
        verbose_name = 'Acción Internacional'
        verbose_name_plural = 'Acciones Internacionales'
        indexes = [
            models.Index(fields=['simbolo']),
            models.Index(fields=['tipo', 'activo']),
        ]
    
    def __str__(self):
        return f'{self.simbolo} - {self.nombre}'


class PrecioAccion(models.Model):
    """
    Precios históricos de acciones internacionales
    """
    accion = models.ForeignKey(
        AccionInternacional,
        on_delete=models.CASCADE,
        related_name='precios'
    )
    
    fecha = models.DateField(
        help_text='Fecha del precio'
    )
    
    apertura = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text='Precio de apertura'
    )
    
    maximo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text='Precio máximo del día'
    )
    
    minimo = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text='Precio mínimo del día'
    )
    
    cierre = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text='Precio de cierre'
    )
    
    cierre_ajustado = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text='Precio de cierre ajustado por splits/dividendos'
    )
    
    volumen = models.BigIntegerField(
        help_text='Volumen negociado'
    )
    
    dividendo = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        help_text='Dividendo pagado'
    )
    
    split = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1,
        help_text='Coeficiente de split'
    )
    
    actualizado = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        unique_together = ['accion', 'fecha']
        ordering = ['-fecha']
        verbose_name = 'Precio de Acción'
        verbose_name_plural = 'Precios de Acciones'
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['accion', 'fecha']),
        ]
    
    def __str__(self):
        return f'{self.accion.simbolo} - {self.fecha}: ${self.cierre}'
    
    def retorno_diario(self):
        """Calcula el retorno diario en porcentaje"""
        if self.apertura > 0:
            return ((self.cierre - self.apertura) / self.apertura * 100)
        return 0
    
    def rango_diario(self):
        """Calcula el rango entre máximo y mínimo"""
        return self.maximo - self.mino


class MetricaAccion(models.Model):
    """
    Métricas calculadas para análisis técnico
    """
    PERIODO_CHOICES = [
        ('D', 'Diario'),
        ('W', 'Semanal'),
        ('M', 'Mensual'),
    ]
    
    accion = models.ForeignKey(
        AccionInternacional,
        on_delete=models.CASCADE,
        related_name='metricas'
    )
    
    fecha = models.DateField(
        help_text='Fecha de cálculo'
    )
    
    periodo = models.CharField(
        max_length=1,
        choices=PERIODO_CHOICES,
        default='D'
    )
    
    # Métricas básicas
    retorno = models.FloatField(
        help_text='Retorno porcentual'
    )
    
    volatilidad = models.FloatField(
        help_text='Volatilidad (desviación estándar)'
    )
    
    volumen_promedio = models.FloatField(
        help_text='Volumen promedio'
    )
    
    # Análisis técnico básico
    rsi = models.FloatField(
        null=True,
        blank=True,
        help_text='Relative Strength Index (14 periodos)'
    )
    
    media_movil_20 = models.FloatField(
        null=True,
        blank=True,
        help_text='Media móvil 20 días'
    )
    
    media_movil_50 = models.FloatField(
        null=True,
        blank=True,
        help_text='Media móvil 50 días'
    )
    
    maximo_52_semanas = models.FloatField(
        null=True,
        blank=True
    )
    
    minimo_52_semanas = models.FloatField(
        null=True,
        blank=True
    )
    
    # Relación con mercado argentino
    correlacion_dolar_blue = models.FloatField(
        null=True,
        blank=True,
        help_text='Correlación con dólar blue'
    )
    
    calculado = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        unique_together = ['accion', 'fecha', 'periodo']
        ordering = ['-fecha', 'accion']
        verbose_name = 'Métrica de Acción'
        verbose_name_plural = 'Métricas de Acciones'
    
    def __str__(self):
        return f'{self.accion.simbolo} - {self.fecha} ({self.get_periodo_display()}): {self.retorno:.2f}%'