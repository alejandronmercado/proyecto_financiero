from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px 
from .models import Cotizacion, IndiceEconomico
from .services import DolarAPIService, BCRAService, actualizar_todos_los_datos


# Create your views here.
