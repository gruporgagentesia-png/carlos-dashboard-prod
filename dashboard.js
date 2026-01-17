// Dashboard Carlos AI - JavaScript Functionality

// Variables globales para gráficos
let conversacionesChart, rangosIngresosChart;

// Configuración global de Chart.js
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;

/**
 * Inicializa el dashboard cargando todos los datos y gráficos
 */
function initializeDashboard() {
    console.log('🚀 Inicializando Dashboard Carlos AI...');
    
    // Mostrar indicador de carga
    showLoadingState();
    
    // Cargar datos iniciales
    Promise.all([
        cargarConversacionesPorDia(),
        cargarRangosIngresos(),
        cargarEstadoHipoteca(),
        cargarEmbudoEstados()
    ]).then(() => {
        console.log('✅ Dashboard inicializado correctamente');
        hideLoadingState();
        mostrarMensaje('Dashboard cargado correctamente', 'success');
    }).catch((error) => {
        console.error('❌ Error inicializando dashboard:', error);
        hideLoadingState();
        mostrarMensaje('Error cargando el dashboard', 'danger');
    });
    
    // Configurar actualización automática cada 5 minutos
    setInterval(actualizarDashboard, 300000);
}

/**
 * Carga datos de conversaciones por día y crea el gráfico de líneas
 */
async function cargarConversacionesPorDia() {
    try {
        const response = await fetch('/api/conversaciones-dia/');
        if (!response.ok) throw new Error('Error cargando conversaciones por día');
        
        const data = await response.json();
        
        // Destruir gráfico existente si existe
        if (conversacionesChart) {
            conversacionesChart.destroy();
        }
        
        // Crear nuevo gráfico
        const ctx = document.getElementById('conversacionesChart').getContext('2d');
        conversacionesChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Conversaciones',
                    data: data.data,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#667eea',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#667eea',
                        borderWidth: 1
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
        
        console.log('📈 Gráfico de conversaciones por día cargado');
        
    } catch (error) {
        console.error('Error cargando conversaciones por día:', error);
        throw error;
    }
}

/**
 * Carga datos de rangos de ingresos y crea el gráfico circular
 */
async function cargarRangosIngresos() {
    try {
        const response = await fetch('/api/rangos-ingresos/');
        if (!response.ok) throw new Error('Error cargando rangos de ingresos');
        
        const data = await response.json();
        
        // Destruir gráfico existente si existe
        if (rangosIngresosChart) {
            rangosIngresosChart.destroy();
        }
        
        // Crear nuevo gráfico
        const ctx = document.getElementById('rangosIngresosChart').getContext('2d');
        rangosIngresosChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#f5576c',
                        '#4facfe',
                        '#00f2fe',
                        '#43e97b'
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#667eea',
                        borderWidth: 1
                    }
                }
            }
        });
        
        console.log('🍩 Gráfico de rangos de ingresos cargado');
        
    } catch (error) {
        console.error('Error cargando rangos de ingresos:', error);
        throw error;
    }
}

/**
 * Carga datos del estado de hipotecas y actualiza la tabla
 */
async function cargarEstadoHipoteca() {
    try {
        const response = await fetch('/api/hipoteca-estado/');
        if (!response.ok) throw new Error('Error cargando estado de hipotecas');
        
        const data = await response.json();
        
        // Actualizar tabla
        document.getElementById('hipotecaSi').textContent = data.con_hipoteca;
        document.getElementById('hipotecaNo').textContent = data.sin_hipoteca;
        
        console.log('🏠 Estado de hipotecas cargado');
        
    } catch (error) {
        console.error('Error cargando estado de hipotecas:', error);
        throw error;
    }
}

/**
 * Carga datos del embudo de estados y crea la visualización
 */
async function cargarEmbudoEstados() {
    try {
        const response = await fetch('/api/embudo-estados/');
        if (!response.ok) throw new Error('Error cargando embudo de estados');
        
        const data = await response.json();
        const container = document.getElementById('embudoContainer');
        
        // Limpiar contenedor
        container.innerHTML = '';
        
        // Crear elementos del embudo
        data.embudo.forEach((item, index) => {
            const embudoItem = document.createElement('div');
            embudoItem.className = 'embudo-item fade-in';
            embudoItem.style.animationDelay = `${index * 0.1}s`;
            
            embudoItem.innerHTML = `
                <span class="embudo-estado">${formatearEstado(item.estado)}</span>
                <span class="embudo-cantidad">${item.cantidad}</span>
            `;
            
            container.appendChild(embudoItem);
        });
        
        console.log('🎯 Embudo de estados cargado');
        
    } catch (error) {
        console.error('Error cargando embudo de estados:', error);
        throw error;
    }
}

/**
 * Formatea los nombres de estados para mostrar de forma legible
 */
function formatearEstado(estado) {
    const estados = {
        'CONTACTO_INICIAL': 'Contacto Inicial',
        'RECOPILANDO_PERSONAL': 'Datos Personales',
        'RECOPILANDO_FINANCIERA': 'Datos Financieros',
        'RECOMENDACION_HECHA': 'Recomendación',
        'ACEPTA_DERIVACION': 'Acepta Derivación',
        'MANEJA_OBJECIONES': 'Manejo Objeciones',
        'FINALIZADO': 'Finalizado'
    };
    
    return estados[estado] || estado;
}

/**
 * Actualiza todos los datos del dashboard
 */
async function actualizarDashboard() {
    console.log('🔄 Actualizando dashboard...');
    showLoadingState();
    
    try {
        // Recargar página para obtener nuevas métricas del servidor
        location.reload();
        
    } catch (error) {
        console.error('Error actualizando dashboard:', error);
        hideLoadingState();
        mostrarMensaje('Error actualizando el dashboard', 'danger');
    }
}

/**
 * Sincroniza datos con Google Sheets
 */
async function sincronizarGoogleSheets() {
    console.log('📊 Sincronizando con Google Sheets...');
    
    const btn = document.querySelector('button[onclick="sincronizarGoogleSheets()"]');
    const originalText = btn.innerHTML;
    
    // Mostrar estado de carga en el botón
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sincronizando...';
    btn.disabled = true;
    
    try {
        const response = await fetch('/sincronizar/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            mostrarMensaje(result.message, 'success');
            // Actualizar dashboard después de sincronizar
            setTimeout(() => actualizarDashboard(), 2000);
        } else {
            mostrarMensaje(result.message, 'danger');
        }
        
    } catch (error) {
        console.error('Error sincronizando Google Sheets:', error);
        mostrarMensaje('Error en la sincronización con Google Sheets', 'danger');
        
    } finally {
        // Restaurar botón
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

/**
 * Muestra el estado de carga en todo el dashboard
 */
function showLoadingState() {
    const containers = document.querySelectorAll('.metric-card, .chart-container, .table-container, .embudo-container');
    containers.forEach(container => {
        container.classList.add('loading');
    });
}

/**
 * Oculta el estado de carga del dashboard
 */
function hideLoadingState() {
    const containers = document.querySelectorAll('.metric-card, .chart-container, .table-container, .embudo-container');
    containers.forEach(container => {
        container.classList.remove('loading');
    });
    
    // Actualizar timestamp de última actualización
    const now = new Date();
    const timestamp = now.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    const ultimaActualizacion = document.getElementById('ultimaActualizacion');
    if (ultimaActualizacion) {
        ultimaActualizacion.textContent = timestamp;
    }
}

/**
 * Muestra mensajes de estado al usuario
 */
function mostrarMensaje(mensaje, tipo = 'info') {
    // Crear elemento del mensaje
    const alert = document.createElement('div');
    alert.className = `alert alert-${tipo} alert-dismissible fade show`;
    alert.style.position = 'fixed';
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    alert.style.minWidth = '300px';
    alert.style.maxWidth = '400px';
    
    alert.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Añadir al body
    document.body.appendChild(alert);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

/**
 * Obtiene el valor de una cookie (necesario para CSRF token)
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Manejo de errores globales
 */
window.addEventListener('error', function(e) {
    console.error('Error global capturado:', e.error);
    mostrarMensaje('Se ha producido un error inesperado', 'danger');
});

/**
 * Manejo de errores de promesas no capturadas
 */
window.addEventListener('unhandledrejection', function(e) {
    console.error('Promesa rechazada no capturada:', e.reason);
    mostrarMensaje('Error en la comunicación con el servidor', 'danger');
});

// Funciones de utilidad para exportar datos
function exportarDatos(formato = 'json') {
    console.log(`📤 Exportando datos en formato ${formato}...`);
    mostrarMensaje('Función de exportación en desarrollo', 'info');
}

// Debug mode - solo en desarrollo
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.dashboardDebug = {
        conversacionesChart,
        rangosIngresosChart,
        actualizarDashboard,
        sincronizarGoogleSheets,
        cargarConversacionesPorDia,
        cargarRangosIngresos,
        cargarEstadoHipoteca,
        cargarEmbudoEstados
    };
    console.log('🔧 Modo debug activado. Funciones disponibles en window.dashboardDebug');
}

console.log('📜 Dashboard JavaScript cargado correctamente');
