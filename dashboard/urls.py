# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('cotizaciones/', views.CotizacionesListView.as_view(), name='cotizaciones_list'),
    path('indices/', views.IndicesListView.as_view(), name='indices_list'),
    path('actualizar/', views.actualizar_datos_manual, name='actualizar_datos'),
]