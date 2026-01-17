from django.db import models
from django.utils import timezone

class CarlosChat(models.Model):
    """
    Modelo para almacenar las conversaciones de Carlos AI
    """
    # Campos del lead
    nombre = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Información financiera
    ingreso_bruto = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    hipoteca_vigente = models.BooleanField(default=False)
    segmento_laboral = models.CharField(max_length=50, blank=True)
    
    # Estados del proceso
    estado_lead = models.CharField(max_length=50, default='CONTACTO_INICIAL')
    tipo_lead = models.CharField(max_length=20, default='FRIO', choices=[
        ('FRIO', 'Frío'),
        ('TIBIO', 'Tibio'),
        ('CALIENTE', 'Caliente'),
    ])
    
    # Métricas de conversación
    numero_interacciones = models.IntegerField(default=0)
    fecha_hilo = models.DateTimeField(default=timezone.now)
    fecha_ultima_interaccion = models.DateTimeField(auto_now=True)
    
    # Recomendación final
    banco_recomendado = models.CharField(max_length=100, blank=True)
    monto_recomendado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conversación Carlos'
        verbose_name_plural = 'Conversaciones Carlos'
        ordering = ['-fecha_ultima_interaccion']
    
    def __str__(self):
        return f"{self.nombre or 'Sin nombre'} - {self.estado_lead}"
    
    @property
    def duracion_conversacion(self):
        """Calcula la duración de la conversación en minutos"""
        if self.fecha_ultima_interaccion and self.fecha_hilo:
            delta = self.fecha_ultima_interaccion - self.fecha_hilo
            return delta.total_seconds() / 60
        return 0

class MetricasDiarias(models.Model):
    """
    Modelo para almacenar métricas diarias agregadas
    """
    fecha = models.DateField(unique=True)
    total_conversaciones = models.IntegerField(default=0)
    conversaciones_completadas = models.IntegerField(default=0)
    tiempo_promedio = models.FloatField(default=0.0)
    tasa_conversion = models.FloatField(default=0.0)
    
    # Contadores por tipo de lead
    leads_frios = models.IntegerField(default=0)
    leads_tibios = models.IntegerField(default=0)
    leads_calientes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Métrica Diaria'
        verbose_name_plural = 'Métricas Diarias'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Métricas {self.fecha}"
