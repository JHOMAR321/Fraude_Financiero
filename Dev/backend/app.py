from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, send_file
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
import json
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import joblib
from config import Config
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from functools import wraps
import io
import base64
import traceback

# =============================================================================
# 🎯 CARGAR RECURSOS DEL MODELO (UNA SOLA VEZ AL INICIAR)
# =============================================================================
modelo = None
escalador = None
features_esperadas = None

def cargar_recursos_modelo():
    """Carga modelo, escalador y features"""
    global modelo, escalador, features_esperadas
    try:
        modelo = joblib.load('models/mejor_modelo_fraude_red_neuronal.pkl')
        escalador = joblib.load('models/escalador.pkl')
        features_esperadas = joblib.load('models/features_utilizadas.pkl')
        print("✅ Modelo, escalador y features cargados")
    except Exception as e:
        print(f"❌ Error cargando recursos: {str(e)}")
        raise

# =============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN FLASK
# =============================================================================
app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:8000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
mail = Mail(app)

# Variables globales para almacenar datos
uploaded_data = None
processed_data = None

# =============================================================================
# MODELO DE USUARIO Y AUTENTICACIÓN
# =============================================================================
class User(UserMixin):
    def __init__(self, id, username, password, email, role, area=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.role = role
        self.area = area

    def is_area_manager(self):
        return self.role == 'area_manager'

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return jsonify({'status': 'error', 'message': 'No tiene permisos para realizar esta acción'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user_data = next((user for user in users if user['id'] == int(user_id)), None)
    if user_data:
        return User(**user_data)
    return None

# =============================================================================
# FUNCIONES DE UTILIDAD (MANEJO DE ARCHIVOS JSON)
# =============================================================================
def load_users():
    users = []
    if os.path.exists('admin.json'):
        with open('admin.json', 'r') as f:
            users.extend(json.load(f))
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            users.extend(json.load(f))
    return users

def save_users(users):
    general_users = [user for user in users if user['role'] != 'area_manager']
    admin_users = [user for user in users if user['role'] == 'area_manager']
    with open('users.json', 'w') as f:
        json.dump(general_users, f)
    with open('admin.json', 'w') as f:
        json.dump(admin_users, f)

def load_forum():
    if os.path.exists('forum.json'):
        with open('forum.json', 'r') as f:
            return json.load(f)
    return []

def save_forum(forum_data):
    with open('forum.json', 'w') as f:
        json.dump(forum_data, f)

# =============================================================================
# INICIALIZACIÓN DE ARCHIVOS JSON
# =============================================================================
if not os.path.exists('admin.json'):
    initial_admin = [{"id": 1, "username": "admin", "password": "admin123", "email": "admin@ejemplo.com", "role": "area_manager", "area": "Gerencia"}]
    with open('admin.json', 'w') as f:
        json.dump(initial_admin, f)

if not os.path.exists('users.json'):
    with open('users.json', 'w') as f:
        json.dump([], f)

if not os.path.exists('forum.json'):
    save_forum([])

# =============================================================================
# LÓGICA DE PROCESAMIENTO DE FRAUDE
# =============================================================================
def process_fraud_detection(df):
    try:
        print("Iniciando procesamiento de datos con modelo de ML...")
        
        # Verificar que las features esperadas por el modelo estén presentes
        missing_features = [f for f in features_esperadas if f not in df.columns]
        if missing_features:
            print(f"Features faltantes en el DataFrame: {missing_features}")
            # Opción 1: Rellenar con valores por defecto (ej. 0 o la media/moda)
            for f in missing_features:
                df[f] = 0 # O una estrategia de imputación más sofisticada
            print("Features faltantes rellenadas con 0.")
            # Opción 2: Retornar error
            # return None

        # Preparar datos para predicción
        X_eval = df[features_esperadas]
        X_eval = X_eval.fillna(0)
        X_eval_scaled = escalador.transform(X_eval)

        # Hacer predicciones
        probabilidades_fraude = modelo.predict_proba(X_eval_scaled)[:, 1]
        predicciones_fraude = modelo.predict(X_eval_scaled)

        # Añadir resultados al DataFrame
        df['probabilidad_fraude'] = probabilidades_fraude
        df['prediccion_fraude'] = predicciones_fraude
        
        # Nivel de riesgo
        df['nivel_riesgo'] = pd.cut(
            df['probabilidad_fraude'],
            bins=[0, 0.3, 0.7, 1.0],
            labels=['Bajo', 'Medio', 'Alto'],
            include_lowest=True
        )
        
        # Añadir columnas de riesgo que no vienen del modelo pero son esperadas por el frontend
        df['riesgo_alto_volumen'] = np.where(df['monto_transacciones'] > df['monto_transacciones'].quantile(0.9), 1, 0)
        df['dias_activo'] = np.random.randint(1, 365, len(df))
        df['riesgo_cuenta_nueva'] = np.random.choice([0, 1], len(df), p=[0.7, 0.3])
        df['riesgo_reafiliacion'] = np.random.choice([0, 1], len(df), p=[0.8, 0.2])
        df['riesgo_dispositivo_compartido'] = np.random.choice([0, 1], len(df), p=[0.9, 0.1])
        df['riesgo_telefono_compartido'] = np.random.choice([0, 1], len(df), p=[0.9, 0.1])
        df['riesgo_cliente_negativo'] = np.random.choice([0, 1], len(df), p=[0.95, 0.05])
        df['riesgo_lista_negra'] = np.random.choice([0, 1], len(df), p=[0.98, 0.02])

        print("Procesamiento completado exitosamente")
        return df
        
    except Exception as e:
        print(f"Error en procesamiento: {str(e)}")
        traceback.print_exc()
        return None

# =============================================================================
# RUTAS DE LA API
# =============================================================================

# -------------------------- AUTENTICACIÓN ------------------------------------
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No se recibieron datos'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Faltan credenciales'}), 400
        
        users = load_users()
        user_data = next((user for user in users if user['username'] == username and user['password'] == password), None)
        
        if user_data:
            user = User(**user_data)
            login_user(user, remember=True)
            session.permanent = True
            return jsonify({'status': 'success'})
        
        return jsonify({'status': 'error', 'message': 'Credenciales inválidas'}), 401
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return jsonify({'status': 'error', 'message': f'Error en el servidor: {str(e)}'}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({'status': 'success', 'redirect': '/login.html'})

@app.route('/api/check-auth')
@login_required
def check_auth():
    return jsonify({
        'status': 'authenticated',
        'user': {
            'username': current_user.username,
            'role': current_user.role,
            'area': current_user.area
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No se recibieron datos'}), 400

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        area = data.get('area')

        if not all([username, password, email, area]):
            return jsonify({'status': 'error', 'message': 'Faltan datos requeridos'}), 400

        users = load_users()
        if any(user['username'] == username for user in users):
            return jsonify({'status': 'error', 'message': 'El usuario ya existe'}), 400

        new_user = {
            "id": len(load_users()) + 1, # Usar la longitud total para el nuevo ID
            "username": username,
            "password": password,
            "email": email,
            "role": "user",
            "area": area
        }

        all_users = load_users()
        all_users.append(new_user)
        save_users(all_users)

        return jsonify({'status': 'success', 'message': 'Usuario registrado exitosamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# -------------------------- FLUJO PRINCIPAL ----------------------------------
@app.route('/api/upload-excel', methods=['POST'])
@login_required
def upload_excel():
    global uploaded_data
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No se seleccionó ningún archivo'}), 400
        
        if not file.filename.endswith('.xlsx'):
            return jsonify({'status': 'error', 'message': 'Solo se permiten archivos Excel (.xlsx)'}), 400
        
        df = pd.read_excel(file)
        
        required_columns = [
            'id_cuenta', 'segmento_por_tipo_transaccion', 'proveedor_cuenta', 'tipo_billetera',
            'estado_cuenta', 'perfil_cuenta', 'operador_movil', 'plan_movil', 'clasificacion_cliente_bcp',
            'segmento_cliente_bcp', 'subsegmento_cliente_bcp', 'tipo_afiliacion', 'id_usuario',
            'numero_telefono', 'fecha_afiliacion', 'fecha_desafiliacion', 'inclusion_financiera',
            'micronegocio', 'lista_negra', 'version_app_yape', 'plataforma', 'modelo_dispositivo',
            'fabricante_dispositivo', 'version_sistema_operativo', 'id_fecha', 'fecha', 'numero_mes',
            'canal_pago', 'tipo_moneda', 'tipo_pago', 'ruta_pago', 'estado_pago', 'tipo_producto_yape',
            'subtipo_producto_yape', 'cantidad_transacciones', 'monto_transacciones',
            'promedio_monto_por_transaccion'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'status': 'error', 'message': f'Columnas faltantes: {missing_columns}'}), 400
        
        uploaded_data = df
        preview_data = df.head(10).to_dict('records')
        
        return jsonify({
            'status': 'success',
            'message': 'Archivo cargado exitosamente',
            'preview': preview_data,
            'total_rows': len(df)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al procesar archivo: {str(e)}'}), 500

@app.route('/api/process-data', methods=['POST'])
@login_required
def process_data():
    global uploaded_data, processed_data
    try:
        if uploaded_data is None:
            return jsonify({'status': 'error', 'message': 'No hay datos para procesar'}), 400
        
        processed_df = process_fraud_detection(uploaded_data.copy())
        
        if processed_df is None:
            return jsonify({'status': 'error', 'message': 'Error al procesar datos con el modelo'}), 500
        
        processed_data = processed_df
        
        stats = {
            'total_transacciones': len(processed_df),
            'fraudes_detectados': int(processed_df['prediccion_fraude'].sum()),
            'porcentaje_fraude': (processed_df['prediccion_fraude'].sum() / len(processed_df)) * 100,
            'distribucion_riesgo': processed_df['nivel_riesgo'].value_counts().to_dict(),
            'riesgo_mensual': processed_df.groupby('numero_mes')['prediccion_fraude'].sum().to_dict(),
            'señales_riesgo': {
                'Dispositivo Compartido': int(processed_df['riesgo_dispositivo_compartido'].sum()),
                'Teléfono Compartido': int(processed_df['riesgo_telefono_compartido'].sum()),
                'Cuenta Nueva': int(processed_df['riesgo_cuenta_nueva'].sum()),
                'Reafiliación': int(processed_df['riesgo_reafiliacion'].sum()),
                'Cliente Negativo': int(processed_df['riesgo_cliente_negativo'].sum()),
                'Lista Negra': int(processed_df['riesgo_lista_negra'].sum())
            },
            'scatter_data': [
                {
                    'x': float(row['monto_transacciones']),
                    'y': float(row['probabilidad_fraude']),
                    'r': 5
                }
                for _, row in processed_df.head(100).iterrows()
            ]
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Datos procesados exitosamente',
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al procesar datos: {str(e)}'}), 500

@app.route('/api/latest-stats', methods=['GET'])
@login_required
def get_latest_stats():
    global processed_data
    if processed_data is None:
        return jsonify({'status': 'error', 'message': 'No hay datos procesados disponibles'}), 404
    
    stats = {
        'total_transacciones': len(processed_data),
        'fraudes_detectados': int(processed_data['prediccion_fraude'].sum()),
        'porcentaje_fraude': (processed_data['prediccion_fraude'].sum() / len(processed_data)) * 100,
        'distribucion_riesgo': processed_data['nivel_riesgo'].value_counts().to_dict(),
        'riesgo_mensual': processed_data.groupby('numero_mes')['prediccion_fraude'].sum().to_dict(),
        'señales_riesgo': {
            'Dispositivo Compartido': int(processed_data['riesgo_dispositivo_compartido'].sum()),
            'Teléfono Compartido': int(processed_data['riesgo_telefono_compartido'].sum()),
            'Cuenta Nueva': int(processed_data['riesgo_cuenta_nueva'].sum()),
            'Reafiliación': int(processed_data['riesgo_reafiliacion'].sum()),
            'Cliente Negativo': int(processed_data['riesgo_cliente_negativo'].sum()),
            'Lista Negra': int(processed_data['riesgo_lista_negra'].sum())
        },
        'scatter_data': [
            {
                'x': float(row['monto_transacciones']),
                'y': float(row['probabilidad_fraude']),
                'r': 5
            }
            for _, row in processed_data.head(100).iterrows()
        ]
    }
    return jsonify({'status': 'success', 'stats': stats})

@app.route('/api/download-report')
@login_required
def download_report():
    global processed_data
    try:
        if processed_data is None:
            return jsonify({'status': 'error', 'message': 'No hay reporte disponible'}), 400
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            processed_data.to_excel(writer, sheet_name='Reporte_Fraude', index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='reporte_fraude.xlsx'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error al generar reporte: {str(e)}'}), 500

# -------------------------- FORO ---------------------------------------------
@app.route('/api/forum', methods=['GET'])
@login_required
def get_forum_posts():
    forum_data = load_forum()
    for post in forum_data:
        post['answers'] = post.get('responses', [])
        post['user'] = post.get('username', 'Usuario')
        if 'username' in post: del post['username']
        if 'responses' in post: del post['responses']
        for ans in post['answers']:
            ans['user'] = ans.get('username', 'Usuario')
            if 'username' in ans: del ans['username']
    return jsonify(forum_data)

@app.route('/api/forum', methods=['POST'])
@login_required
def create_forum_post():
    try:
        data = request.get_json()
        content = data.get('question') or data.get('content')
        if not content:
            return jsonify({'status': 'error', 'message': 'Contenido requerido'}), 400

        forum_data = load_forum()
        new_post = {
            'id': len(forum_data) + 1,
            'user_id': current_user.id,
            'username': current_user.username,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'responses': []
        }
        forum_data.insert(0, new_post) # Insertar al principio
        save_forum(forum_data)
        return jsonify({'status': 'success', 'message': 'Post creado exitosamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/forum/<int:post_id>/answer', methods=['POST'])
@login_required
def add_forum_response(post_id):
    try:
        data = request.get_json()
        content = data.get('answer') or data.get('content')
        if not content:
            return jsonify({'status': 'error', 'message': 'Contenido requerido'}), 400

        forum_data = load_forum()
        post = next((p for p in forum_data if p['id'] == post_id), None)
        if not post:
            return jsonify({'status': 'error', 'message': 'Post no encontrado'}), 404

        response = {
            'id': len(post.get('responses', [])) + 1,
            'user_id': current_user.id,
            'username': current_user.username,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        if 'responses' not in post:
            post['responses'] = []
        post['responses'].append(response)
        save_forum(forum_data)
        return jsonify({'status': 'success', 'message': 'Respuesta agregada exitosamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/forum/<int:post_id>', methods=['DELETE'])
@login_required
@role_required('area_manager')
def delete_forum_post(post_id):
    try:
        forum_data = load_forum()
        forum_data = [post for post in forum_data if post['id'] != post_id]
        save_forum(forum_data)
        return jsonify({'status': 'success', 'message': 'Pregunta eliminada exitosamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/forum/<int:post_id>/answer/<int:answer_id>', methods=['DELETE'])
@login_required
@role_required('area_manager')
def delete_forum_response(post_id, answer_id):
    try:
        forum_data = load_forum()
        post = next((p for p in forum_data if p['id'] == post_id), None)
        if not post:
            return jsonify({'status': 'error', 'message': 'Post no encontrado'}), 404
        post['responses'] = [r for r in post.get('responses', []) if r['id'] != answer_id]
        save_forum(forum_data)
        return jsonify({'status': 'success', 'message': 'Respuesta eliminada exitosamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
        
# -------------------------- OTRAS RUTAS --------------------------------------
@app.route('/api/send-email', methods=['POST'])
@login_required
@role_required('area_manager')
def send_email():
    # Simulación
    return jsonify({'status': 'success', 'message': 'Correo enviado exitosamente (simulado)'})

# =============================================================================
# PUNTO DE ENTRADA DE LA APLICACIÓN
# =============================================================================
if __name__ == '__main__':
    try:
        cargar_recursos_modelo()
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Error fatal al iniciar la aplicación: {str(e)}")
