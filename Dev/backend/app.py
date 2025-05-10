from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session
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

app = Flask(__name__)
app.config.from_object(Config)

# Configurar CORS para permitir credenciales
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:8000"],
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Inicialización de extensiones
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'
mail = Mail(app)

# Clase de Usuario
class User(UserMixin):
    def __init__(self, id, username, password, email, role, area):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.role = role
        self.area = area

    def is_area_manager(self):
        return self.role == 'area_manager'

# Decorador para verificar permisos
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return jsonify({'status': 'error', 'message': 'No tiene permisos para realizar esta acción'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Cargar usuarios desde JSON
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return []

# Cargar foro desde JSON
def load_forum():
    if os.path.exists('forum.json'):
        with open('forum.json', 'r') as f:
            return json.load(f)
    return []

# Guardar foro en JSON
def save_forum(forum_data):
    with open('forum.json', 'w') as f:
        json.dump(forum_data, f)

# Crear usuario inicial si no existe
if not os.path.exists('users.json'):
    initial_users = [
        {
            "id": 1,
            "username": "admin",
            "password": "admin123",
            "email": "admin@ejemplo.com",
            "role": "area_manager",
            "area": "Gerencia"
        }
    ]
    save_users(initial_users)

# Crear foro inicial si no existe
if not os.path.exists('forum.json'):
    initial_forum = []
    save_forum(initial_forum)

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    user_data = next((user for user in users if user['id'] == int(user_id)), None)
    if user_data:
        return User(**user_data)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                print("No se recibieron datos JSON")
                return jsonify({'status': 'error', 'message': 'No se recibieron datos'}), 400
                
            username = data.get('username')
            password = data.get('password')
            
            print(f"Intento de login - Usuario: {username}")
            
            if not username or not password:
                print("Faltan credenciales")
                return jsonify({'status': 'error', 'message': 'Faltan credenciales'}), 400
            
            users = load_users()
            user_data = next((user for user in users if user['username'] == username and user['password'] == password), None)
            
            if user_data:
                user = User(**user_data)
                login_user(user, remember=True)
                session.permanent = True
                print(f"Login exitoso para usuario: {username}")
                return jsonify({'status': 'success'})
            
            print(f"Credenciales inválidas para usuario: {username}")
            return jsonify({'status': 'error', 'message': 'Credenciales inválidas'}), 401
            
        except Exception as e:
            print(f"Error en login: {str(e)}")
            return jsonify({'status': 'error', 'message': f'Error en el servidor: {str(e)}'}), 500
    
    return render_template('login.html')

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
            'role': current_user.role
        }
    })

# Ruta para enviar correos
@app.route('/api/send-email', methods=['POST'])
@login_required
def send_email():
    # Simulación: no se envía correo real
    return jsonify({
        'status': 'success',
        'message': 'Correo enviado exitosamente (simulado)'
    })

# Rutas protegidas
@app.route('/api/metrics', methods=['GET'])
@login_required
def get_metrics():
    metrics = {
        'accuracy': 0.95,
        'precision': 0.92,
        'recall': 0.94,
        'f1': 0.93
    }
    return jsonify(metrics)

@app.route('/api/detect-fraud', methods=['POST'])
@login_required
def detect_fraud():
    return jsonify({
        'is_fraud': True,
        'confidence': 0.95,
        'message': 'Se ha detectado un posible fraude financiero'
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
            "id": len(users) + 1,
            "username": username,
            "password": password,
            "email": email,
            "role": "user",
            "area": area
        }

        users.append(new_user)
        save_users(users)

        return jsonify({'status': 'success', 'message': 'Usuario registrado exitosamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/forum', methods=['GET'])
@login_required
def get_forum_posts():
    forum_data = load_forum()
    # Convertir 'responses' a 'answers' y 'username' a 'user' para el frontend, asegurando valores por defecto
    for post in forum_data:
        # Asegura que responses exista
        if 'responses' not in post or not isinstance(post['responses'], list):
            post['responses'] = []
        post['answers'] = post.get('responses', [])
        # Asegura que user exista
        post['user'] = post.get('username', 'Usuario')
        # Limpia el campo username para evitar confusión
        if 'username' in post:
            del post['username']
        # Para cada respuesta
        for ans in post['answers']:
            ans['user'] = ans.get('username', 'Usuario')
            if 'username' in ans:
                del ans['username']
    return jsonify(forum_data)

@app.route('/api/forum', methods=['POST'])
@login_required
def create_forum_post():
    try:
        data = request.get_json()
        # Aceptar tanto 'question' como 'content'
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

        forum_data.append(new_post)
        save_forum(forum_data)
        return jsonify({'status': 'success', 'message': 'Post creado exitosamente'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/forum/<int:post_id>/answer', methods=['POST'])
@login_required
def add_forum_response(post_id):
    try:
        data = request.get_json()
        # Aceptar tanto 'answer' como 'content'
        content = data.get('answer') or data.get('content')
        if not content:
            return jsonify({'status': 'error', 'message': 'Contenido requerido'}), 400

        forum_data = load_forum()
        post = next((p for p in forum_data if p['id'] == post_id), None)
        if not post:
            return jsonify({'status': 'error', 'message': 'Post no encontrado'}), 404

        response = {
            'id': len(post['responses']) + 1,
            'user_id': current_user.id,
            'username': current_user.username,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }

        post['responses'].append(response)
        save_forum(forum_data)
        return jsonify({'status': 'success', 'message': 'Respuesta agregada exitosamente'})
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
        post['responses'] = [r for r in post['responses'] if r['id'] != answer_id]
        save_forum(forum_data)
        return jsonify({'status': 'success', 'message': 'Respuesta eliminada exitosamente'})
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

if __name__ == '__main__':
    app.run(debug=True) 