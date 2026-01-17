from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import CarlosChat, MetricasDiarias
import json
import gspread
from google.auth import service_account
from django.conf import settings
import pandas as pd
from datetime import datetime, timedelta

def dashboard_view(request):
    """
    Vista principal del dashboard que renderiza la página principal
    con todas las métricas y gráficos de Carlos AI
    """
    # Obtener métricas básicas
    total_conversaciones = CarlosChat.objects.count()
    
    # Calcular tiempo promedio de conversación
    chats_con_duracion = CarlosChat.objects.exclude(
        Q(fecha_hilo__isnull=True) | Q(fecha_ultima_interaccion__isnull=True)
    )
    
    tiempo_promedio = 0
    if chats_con_duracion.exists():
        duraciones = [chat.duracion_conversacion for chat in chats_con_duracion]
        tiempo_promedio = sum(duraciones) / len(duraciones) if duraciones else 0
    
    # Calcular interacciones promedio
    interacciones_promedio = CarlosChat.objects.aggregate(
        promedio=Avg('numero_interacciones')
    )['promedio'] or 0
    
    # Calcular eficiencia (% que llegan a ACEPTA_DERIVACION)
    total_chats = CarlosChat.objects.count()
    chats_exitosos = CarlosChat.objects.filter(
        estado_lead='ACEPTA_DERIVACION'
    ).count()
    
    eficiencia = (chats_exitosos / total_chats * 100) if total_chats > 0 else 0
    
    # Preparar contexto para el template
    context = {
        'metricas': {
            'total_conversaciones': total_conversaciones,
            'tiempo_promedio': round(tiempo_promedio, 1),
            'interacciones_promedio': round(interacciones_promedio, 1),
            'eficiencia': round(eficiencia, 1),
        }
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def api_conversaciones_dia(request):
    """
    API que devuelve datos de conversaciones generadas por día
    para el gráfico de líneas
    """
    # Obtener datos de los últimos 30 días
    fecha_inicio = timezone.now().date() - timedelta(days=30)
    
    conversaciones_por_dia = CarlosChat.objects.filter(
        fecha_hilo__date__gte=fecha_inicio
    ).extra({
        'fecha_creacion': 'date(fecha_hilo)'
    }).values('fecha_creacion').annotate(
        total=Count('id')
    ).order_by('fecha_creacion')
    
    # Convertir a formato para Chart.js
    labels = []
    datos = []
    
    for item in conversaciones_por_dia:
        labels.append(item['fecha_creacion'].strftime('%d/%m'))
        datos.append(item['total'])
    
    return JsonResponse({
        'labels': labels,
        'data': datos
    })

def api_rangos_ingresos(request):
    """
    API que devuelve la distribución por rangos de ingresos
    para el gráfico circular
    """
    # Definir rangos de ingresos
    rangos = [
        ('0-500', 0, 500),
        ('500-700', 500, 700),
        ('700-1000', 700, 1000),
        ('1000-1200', 1000, 1200),
        ('1200-1500', 1200, 1500),
        ('1500-2000', 1500, 2000),
        ('2000+', 2000, float('inf'))
    ]
    
    labels = []
    datos = []
    
    for etiqueta, min_val, max_val in rangos:
        if max_val == float('inf'):
            count = CarlosChat.objects.filter(
                ingreso_bruto__gte=min_val,
                ingreso_bruto__isnull=False
            ).count()
        else:
            count = CarlosChat.objects.filter(
                ingreso_bruto__gte=min_val,
                ingreso_bruto__lt=max_val,
                ingreso_bruto__isnull=False
            ).count()
        
        labels.append(etiqueta)
        datos.append(count)
    
    return JsonResponse({
        'labels': labels,
        'data': datos
    })

def api_hipoteca_estado(request):
    """
    API que devuelve el estado de hipotecas (SI/NO)
    """
    con_hipoteca = CarlosChat.objects.filter(hipoteca_vigente=True).count()
    sin_hipoteca = CarlosChat.objects.filter(hipoteca_vigente=False).count()
    
    return JsonResponse({
        'con_hipoteca': con_hipoteca,
        'sin_hipoteca': sin_hipoteca
    })

def api_embudo_estados(request):
    """
    API que devuelve datos para el embudo de estados de lead
    """
    estados_orden = [
        'CONTACTO_INICIAL',
        'RECOPILANDO_PERSONAL',
        'RECOPILANDO_FINANCIERA',
        'RECOMENDACION_HECHA',
        'ACEPTA_DERIVACION',
        'MANEJA_OBJECIONES',
        'FINALIZADO'
    ]
    
    embudo_datos = []
    
    for estado in estados_orden:
        count = CarlosChat.objects.filter(estado_lead=estado).count()
        embudo_datos.append({
            'estado': estado,
            'cantidad': count
        })
    
    return JsonResponse({
        'embudo': embudo_datos
    })

@csrf_exempt
@require_http_methods(["POST"])
def webhook_make_automation(request):
    """
    Webhook para recibir datos de Make Automation
    Actualiza o crea registros de conversaciones
    """
    try:
        data = json.loads(request.body)
        
        # Extraer datos del webhook
        telefono = data.get('telefono', '')
        nombre = data.get('nombre', '')
        email = data.get('email', '')
        ingreso_bruto = data.get('ingreso_bruto')
        hipoteca_vigente = data.get('hipoteca_vigente', False)
        segmento_laboral = data.get('segmento_laboral', '')
        estado_lead = data.get('estado_lead', 'CONTACTO_INICIAL')
        numero_interacciones = data.get('numero_interacciones', 0)
        
        # Buscar o crear conversación
        chat, created = CarlosChat.objects.get_or_create(
            telefono=telefono,
            defaults={
                'nombre': nombre,
                'email': email,
                'ingreso_bruto': ingreso_bruto,
                'hipoteca_vigente': hipoteca_vigente,
                'segmento_laboral': segmento_laboral,
                'estado_lead': estado_lead,
                'numero_interacciones': numero_interacciones,
            }
        )
        
        # Si ya existe, actualizar
        if not created:
            chat.nombre = nombre or chat.nombre
            chat.email = email or chat.email
            if ingreso_bruto:
                chat.ingreso_bruto = ingreso_bruto
            chat.hipoteca_vigente = hipoteca_vigente
            chat.segmento_laboral = segmento_laboral or chat.segmento_laboral
            chat.estado_lead = estado_lead
            chat.numero_interacciones = numero_interacciones
            chat.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Datos actualizados correctamente',
            'created': created
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def sincronizar_google_sheets(request):
    """
    Vista para sincronizar datos con Google Sheets
    """
    try:
        if not settings.GOOGLE_SHEETS_SERVICE_ACCOUNT_FILE or not settings.GOOGLE_SHEETS_SPREADSHEET_ID:
            return JsonResponse({
                'status': 'error',
                'message': 'Configuración de Google Sheets no encontrada'
            })
        
        # Configurar conexión a Google Sheets
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SHEETS_SERVICE_ACCOUNT_FILE,
            scopes=scopes
        )
        
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(settings.GOOGLE_SHEETS_SPREADSHEET_ID)
        worksheet = sheet.get_worksheet(0)
        
        # Obtener todos los datos
        records = worksheet.get_all_records()
        
        # Procesar y guardar en base de datos
        registros_procesados = 0
        for record in records:
            try:
                telefono = record.get('Telefono', '')
                if not telefono:
                    continue
                    
                chat, created = CarlosChat.objects.get_or_create(
                    telefono=telefono,
                    defaults={
                        'nombre': record.get('Nombre', ''),
                        'email': record.get('Email', ''),
                        'ingreso_bruto': record.get('Ingreso_Bruto') if record.get('Ingreso_Bruto') else None,
                        'hipoteca_vigente': record.get('Hipoteca_Vigente', '').upper() == 'SI',
                        'segmento_laboral': record.get('Segmento_Laboral', ''),
                        'estado_lead': record.get('Estado_Lead', 'CONTACTO_INICIAL'),
                        'numero_interacciones': record.get('Numero_Interacciones', 0),
                    }
                )
                registros_procesados += 1
                
            except Exception as e:
                print(f"Error procesando registro {record}: {e}")
                continue
        
        return JsonResponse({
            'status': 'success',
            'message': f'Sincronización completada. {registros_procesados} registros procesados.'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
