// Función para verificar la autenticación
async function checkAuth() {
    try {
        const response = await fetch('http://localhost:5000/api/check-auth', {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            window.location.href = '/';
            return false;
        }
        return true;
    } catch (error) {
        console.error('Error checking auth:', error);
        window.location.href = '/';
        return false;
    }
}

// Verificar autenticación cada 30 segundos
setInterval(checkAuth, 30000);

// Verificar autenticación al cargar la página
// (No agregar lógica de correo aquí, solo autenticación y funciones generales)
document.addEventListener('DOMContentLoaded', async () => {
    const isAuthenticated = await checkAuth();
    if (!isAuthenticated) return;
    // Aquí solo lógica general, no de correo
});

// URL del reporte de Power BI
const POWER_BI_URL = 'https://app.powerbi.com/view?r=eyJrIjoiMzhkOGM3NjgtZGZhZC00NTNkLTgzZjgtYTU4ZDFiNjQzODI1IiwidCI6IjBjZGQyMmVkLTQxZjAtNGYxYi05YzI1LTRiZGIwZDBmNmZkYSIsImMiOjR9&pageName=13325b94c17c5aca1803';

// Valores de ejemplo para las métricas
const EXAMPLE_METRICS = {
    accuracy: 0.95,
    precision: 0.92,
    recall: 0.94,
    f1: 0.93
};

// Función para mostrar/ocultar alerta de fraude
function toggleFraudAlert(show) {
    const alert = document.getElementById('fraud-alert');
    if (show) {
        alert.classList.remove('hidden');
    } else {
        alert.classList.add('hidden');
    }
}

// Función para cargar el reporte de Power BI
function loadPowerBIReport() {
    const iframe = document.getElementById('power-bi-frame');
    if (POWER_BI_URL) {
        iframe.src = POWER_BI_URL;
    }
}

// Función para verificar si hay fraude basado en las métricas
function checkForFraud(metrics) {
    const threshold = 0.90;
    const hasFraud = Object.values(metrics).every(value => value >= threshold);
    toggleFraudAlert(hasFraud);
}

// Función para obtener las métricas del backend
async function fetchMetrics() {
    try {
        // const response = await fetch('/api/metrics');
        // const data = await response.json();
        // updateMetrics(data);
        // checkForFraud(data);
    } catch (error) {
        console.error('Error al obtener métricas:', error);
        // Usar valores de ejemplo si hay error de conexión
        // updateMetrics(EXAMPLE_METRICS);
        // checkForFraud(EXAMPLE_METRICS);
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    loadPowerBIReport();
    // Mostrar valores de ejemplo inmediatamente
    // updateMetrics(EXAMPLE_METRICS);
    // checkForFraud(EXAMPLE_METRICS);
    // Intentar obtener valores reales del backend
    // fetchMetrics();
    // No agregar lógica de correo aquí
    // Actualizar métricas cada 5 minutos
    // setInterval(fetchMetrics, 300000);
}); 