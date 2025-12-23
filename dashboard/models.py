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

'''calcula la diferencia entre precio de venta y compra 
   returns: decimal: diferencia en pesos'''
def diferencia_precio(self):
    return self.venta - self.compra

def spread_porcentual(self):
    if self.compra > 0:
            return float((self.venta - self.compra) / self.compra * 100)
    return 0

"""
    Modelo para almacenar indicadores económicos del BCRA.
    
    Tabla en BD: dashboard_indiceeconomico
    
    Ejemplo de registro:
    - tipo: 'reservas'
    - fecha: 2024-01-15
    - valor: 25000.00
    - unidad: 'Millones USD'
"""
class IndiceEconomico(models.Model):
     TIPOS_INDICE = [
        ('inflacion', 'Inflación Mensual'),
        ('tasa', 'Tasa de Interés BCRA'),
        ('reservas', 'Reservas Internacionales'),
        ('riesgo_pais', 'Riesgo País'),
        ('merval', 'Índice Merval'),

     ]