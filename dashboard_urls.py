from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Vista principal del dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # APIs para datos de gráficos
    path('api/conversaciones-dia/', views.api_conversaciones_dia, name='api_conversaciones_dia'),
    path('api/rangos-ingresos/', views.api_rangos_ingresos, name='api_rangos_ingresos'),
    path('api/hipoteca-estado/', views.api_hipoteca_estado, name='api_hipoteca_estado'),
    path('api/embudo-estados/', views.api_embudo_estados, name='api_embudo_estados'),
    
    # Webhook para Make Automation
    path('webhook/make/', views.webhook_make_automation, name='webhook_make'),
    
    # Sincronización con Google Sheets
    path('sincronizar/', views.sincronizar_google_sheets, name='sincronizar_sheets'),
]
