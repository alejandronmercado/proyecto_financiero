from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('cotizaciones/', views.CotizacionesListView.as_view(), name='cotizaciones'),
    path('indices/', views.IndicesListView.as_view(), name='indices'),
    path('actualizar/', views.actualizar_datos_manual, name='actualizar'),
    path('mercado-internacional/', views.MercadoInternacionalView.as_view(), name='mercado_internacional'),
]