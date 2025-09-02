# Sistema de Detección de Fraude Financiero

![Python](https://img.shields.io/badge/python-3.9-blue.svg) ![Flask](https://img.shields.io/badge/flask-2.0-blue.svg) ![scikit-learn](https://img.shields.io/badge/scikit--learn-1.0-blue.svg)

## Descripción General

Este proyecto es una aplicación web diseñada para la detección de fraude en transacciones financieras. Utiliza un backend de Flask en Python para servir un modelo de machine learning y una API RESTful, junto con un frontend interactivo para la visualización de datos y la interacción del usuario. El sistema está diseñado para ser utilizado por analistas de fraude y administradores, con diferentes niveles de acceso y funcionalidad basados en roles.

## Estructura del Proyecto

```
Fraude_Financiero/
├── Dev/
│   ├── backend/
│   │   ├── models/         # Modelos de ML, escalador y features
│   │   ├── __pycache__/
│   │   ├── app.py          # Aplicación principal de Flask (backend)
│   │   ├── config.py       # Configuración de la aplicación
│   │   ├── admin.json      # Credenciales de administrador
│   │   ├── users.json      # Credenciales de usuarios
│   │   └── requirements.txt  # Dependencias de Python
│   └── frontend/
│       ├── css/            # Hojas de estilo
│       ├── js/             # Scripts de JavaScript
│       ├── index.html      # Página de inicio/login
│       ├── dashboard.html  # Dashboard principal
│       └── server.py       # Servidor HTTP para el frontend
└── README.md
```

## Características Clave

-   **API Segura y Basada en Roles:** Acceso seguro a los endpoints de la API con autenticación basada en sesión y roles de usuario.
-   **Carga y Procesamiento de Datos:** Los administradores pueden subir archivos de transacciones en formato `.xlsx` para su análisis.
-   **Modelo de Machine Learning:** Utiliza un modelo de Redes Neuronales (MLPClassifier) para predecir la probabilidad de fraude.
-   **Dashboard de Visualización:**
    -   Gráficos interactivos para visualizar la distribución del riesgo, la evolución mensual del fraude y las señales de riesgo más comunes.
    -   Previsualización de los datos cargados.
-   **Gestión de Usuarios:** Sistema de registro y login para usuarios y administradores.
-   **Foro de Colaboración:** Un espacio para que los usuarios discutan y compartan información.

## Tecnologías Utilizadas

-   **Backend:**
    -   Python 3.9
    -   Flask
    -   Pandas & NumPy para la manipulación de datos
    -   Scikit-learn para el modelo de machine learning
-   **Frontend:**
    -   HTML5, CSS3, JavaScript (ES6)
    -   Chart.js para la visualización de gráficos
-   **Servidor:**
    -   Servidor de desarrollo de Flask para el backend.
    -   Servidor HTTP simple de Python para el frontend.

## Instalación y Configuración

Sigue estos pasos para configurar el entorno de desarrollo en tu máquina local.

### Prerrequisitos

-   Python 3.7+
-   `pip` (manejador de paquetes de Python)

### 1. Configuración del Backend

```bash
# 1. Navega al directorio del backend
cd Dev/backend

# 2. (Recomendado) Crea y activa un entorno virtual
# En macOS/Linux
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
.\venv\Scripts\activate

# 3. Instala las dependencias de Python
pip install -r requirements.txt
```

### 2. Configuración del Frontend

El frontend es una aplicación web estática que no requiere un proceso de build o instalación de dependencias. Se sirve directamente a través de un servidor web simple.

## Cómo Ejecutar la Aplicación

Para que la aplicación funcione correctamente, tanto el servidor del backend como el del frontend deben estar en ejecución simultáneamente.

### 1. Iniciar el Servidor del Backend (API)

-   **Directorio:** `Dev/backend`
-   **Comando:**
    ```bash
    python app.py
    ```
-   El servidor del backend se ejecutará en `http://localhost:5000`.

### 2. Iniciar el Servidor del Frontend

-   Abre una **nueva terminal**.
-   **Directorio:** `Dev/frontend`
-   **Comando:**
    ```bash
    python server.py
    ```
-   El servidor del frontend se ejecutará en `http://localhost:8000`.

### 3. Acceder a la Aplicación

Una vez que ambos servidores estén en funcionamiento, abre tu navegador web y navega a:

**`http://localhost:8000`**

## Uso de la Aplicación

### Roles y Credenciales

-   **Administrador:**
    -   **Usuario:** `admin`
    -   **Contraseña:** `admin123`
    -   **Permisos:** Cargar y procesar archivos, ver dashboard, descargar reportes, y gestionar el foro.
-   **Usuario Estándar:**
    -   Puede registrarse a través de la página de inicio.
    -   **Permisos:** Ver el dashboard con los últimos datos procesados y participar en el foro.

### Flujo de Trabajo Típico

1.  Un **administrador** inicia sesión.
2.  Sube un archivo `.xlsx` con datos de transacciones.
3.  Procesa el archivo para que el modelo de IA genere las predicciones de fraude.
4.  El dashboard se actualiza con los nuevos resultados.
5.  Un **usuario estándar** inicia sesión y puede ver el dashboard actualizado y el foro.

## Documentación de la API

La API RESTful proporciona los siguientes endpoints:

| Método | Endpoint                      | Descripción                                                                 | Rol Requerido      |
| :----- | :---------------------------- | :-------------------------------------------------------------------------- | :----------------- |
| `POST` | `/login`                      | Autentica a un usuario y crea una sesión.                                   | Público            |
| `GET`  | `/logout`                     | Cierra la sesión del usuario actual.                                        | Autenticado        |
| `GET`  | `/api/check-auth`             | Verifica el estado de autenticación del usuario.                            | Autenticado        |
| `POST` | `/api/register`               | Registra un nuevo usuario estándar.                                         | Público            |
| `POST` | `/api/upload-excel`           | Sube un archivo Excel para análisis.                                        | Administrador      |
| `POST` | `/api/process-data`           | Procesa el archivo previamente subido para detectar fraudes.                | Administrador      |
| `GET`  | `/api/latest-stats`           | Obtiene las estadísticas del último análisis de fraude.                     | Usuario Estándar   |
| `GET`  | `/api/download-report`        | Descarga el reporte completo del análisis en formato Excel.                 | Administrador      |
| `GET`  | `/api/forum`                  | Obtiene todas las publicaciones del foro.                                   | Autenticado        |
| `POST` | `/api/forum`                  | Crea una nueva publicación en el foro.                                      | Autenticado        |
| `POST` | `/api/forum/<id>/answer`      | Publica una respuesta a una pregunta existente.                             | Autenticado        |
| `DELETE`| `/api/forum/<id>`             | Elimina una publicación del foro.                                           | Administrador      |
| `DELETE`| `/api/forum/<id>/answer/<id>` | Elimina una respuesta de una publicación.                                   | Administrador      |

---

_Este README fue generado y actualizado para reflejar el estado actual del proyecto._
