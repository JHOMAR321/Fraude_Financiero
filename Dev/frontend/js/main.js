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
document.addEventListener('DOMContentLoaded', async () => {
    const isAuthenticated = await checkAuth();
    if (!isAuthenticated) return;

    // Cargar métricas
    // const response = await fetch('http://localhost:5000/api/metrics', {
    // const metrics = await response.json();
    // document.getElementById('accuracy-metric').textContent = metrics.accuracy.toFixed(2);
    // document.getElementById('precision-metric').textContent = metrics.precision.toFixed(2);
    // document.getElementById('recall-metric').textContent = metrics.recall.toFixed(2);
    // document.getElementById('f1-metric').textContent = metrics.f1.toFixed(2);

    // Configurar el formulario de correo
    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const recipients = document.getElementById('recipients').value.split(',').map(email => email.trim());
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;
            
            try {
                const response = await fetch('http://localhost:5000/api/send-email', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ recipients, subject, message })
                });
                
                const result = await response.json();
                const statusDiv = document.getElementById('email-status');
                
                if (response.ok) {
                    statusDiv.textContent = 'Correo enviado exitosamente';
                    statusDiv.style.color = 'green';
                    emailForm.reset();
                } else {
                    statusDiv.textContent = `Error: ${result.message}`;
                    statusDiv.style.color = 'red';
                }
            } catch (error) {
                console.error('Error sending email:', error);
                const statusDiv = document.getElementById('email-status');
                statusDiv.textContent = 'Error al enviar el correo';
                statusDiv.style.color = 'red';
            }
        });
    }
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

// Función para enviar correo
async function sendEmail(event) {
    event.preventDefault();
    
    const recipients = document.getElementById('recipients').value.split(',').map(email => email.trim());
    const subject = document.getElementById('subject').value;
    const message = document.getElementById('message').value;
    
    try {
        const response = await fetch('/api/send-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                recipients,
                subject,
                message
            })
        });
        
        const data = await response.json();
        const statusDiv = document.getElementById('email-status');
        
        if (data.status === 'success') {
            statusDiv.textContent = 'Correo enviado exitosamente';
            statusDiv.className = 'email-status success';
            document.getElementById('email-form').reset();
        } else {
            statusDiv.textContent = 'Error al enviar el correo: ' + data.message;
            statusDiv.className = 'email-status error';
        }
    } catch (error) {
        const statusDiv = document.getElementById('email-status');
        statusDiv.textContent = 'Error al enviar el correo: ' + error.message;
        statusDiv.className = 'email-status error';
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
    
    // Agregar manejador de eventos para el formulario de correo
    document.getElementById('email-form').addEventListener('submit', sendEmail);
    
    // Actualizar métricas cada 5 minutos
    // setInterval(fetchMetrics, 300000);
}); 