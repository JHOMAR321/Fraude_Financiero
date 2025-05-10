# Sistema de Detección de Fraude Financiero

Este proyecto implementa una solución tecnológica para la detección de fraude financiero utilizando Inteligencia Artificial e Inteligencia de Negocios.

## Estructura del Proyecto

```
Dev/
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
└── backend/
    ├── app.py
    └── requirements.txt
```

## Requisitos Previos

- Python 3.8 o superior
- Node.js (para servir el frontend)
- Visual Studio Code (para el ETL)
- Power BI Desktop

## Instalación

### Backend

1. Crear un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:

```bash
cd backend
pip install -r requirements.txt
```

### Frontend

El frontend es una aplicación web estática que puede ser servida por cualquier servidor web. Para desarrollo, puedes usar:

# Usando Python
python -m http.server 8000

# O usando Node.js
npx serve frontend

## Uso

1. Ejecutar el backend:

```bash
cd backend
python app.py
```

2. Abrir el frontend en el navegador:

```
http://localhost:8000
```

## Flujo de Trabajo

1. Realizar el ETL de los datos en Visual Studio Code
2. Cargar los datos limpios en el backend
3. Entrenar los modelos de Machine Learning
4. Visualizar los resultados en el dashboard
5. Integrar el reporte de Power BI

## Modelos de Machine Learning Implementados

- Random Forest
- Árbol de Decisión
- Red Neuronal
- Gradient Boosting

## Métricas de Evaluación

- Accuracy
- Precision
- Recall
- F1 Score
- ROC AUC

## Contribución

Para contribuir al proyecto, por favor sigue estos pasos:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
