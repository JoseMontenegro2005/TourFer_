from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token
from flask_cors import CORS
from config import Config
from db import get_db_connection

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')
    password = data.get('password')

    print(f"[LOG] Solicitud POST /register recibida para el email: {email}", flush=True)

    if not email or not password:
        print(f"[WARNING] Registro rechazado: Faltan datos obligatorios.", flush=True)
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    conn = None
    cur = None
    try:
        print(f"[LOG] Generando hash de seguridad para la contraseña...", flush=True)
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        print(f"[LOG] Intentando conectar a usuarios_db...", flush=True)
        conn = get_db_connection(Config)
        cur = conn.cursor()
        
        print(f"[LOG] Insertando nuevo usuario '{nombre}' en la base de datos...", flush=True)
        cur.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, pw_hash)
        )
        conn.commit()
        
        print(f"[EVENTO SUCCESS] Usuario {email} registrado exitosamente.", flush=True)
        return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201

    except Exception as e:
        if conn: conn.rollback()
        print(f"[ERROR] No se pudo completar el registro de {email}: {str(e)}", flush=True)
        return jsonify({"error": "El usuario ya existe o hubo un error en la base de datos"}), 409
    
    finally:
        if cur: cur.close()
        if conn: conn.close()
        print(f"[LOG] Conexiones cerradas tras proceso de registro.", flush=True)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    print(f"[LOG] Intento de inicio de sesión para: {email}", flush=True)

    conn = None
    cur = None
    try:
        print(f"[LOG] Buscando credenciales en usuarios_db...", flush=True)
        conn = get_db_connection(Config)
        cur = conn.cursor()
        
        cur.execute("SELECT id, nombre, password, rol_id FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user:
            print(f"[LOG] Usuario {email} localizado. Validando contraseña...", flush=True)
            if bcrypt.check_password_hash(user['password'], password):
                print(f"[LOG] Contraseña válida. Configurando payload del JWT autocontenido...", flush=True)
                
                claims = {
                    "rol_id": user['rol_id'],
                    "user_id": user['id']
                }
                
                access_token = create_access_token(identity=str(email), additional_claims=claims)
                
                print(f"[EVENTO SUCCESS] Login exitoso para {email}. Token entregado de forma autónoma.", flush=True)
                return jsonify({
                    "access_token": access_token,
                    "user_name": user['nombre']
                }), 200
            else:
                print(f"[WARNING] Contraseña incorrecta para el usuario {email}.", flush=True)
        else:
            print(f"[WARNING] El email {email} no se encuentra registrado.", flush=True)

        return jsonify({"error": "Credenciales inválidas"}), 401

    except Exception as e:
        print(f"[ERROR] Error crítico durante el login de {email}: {str(e)}", flush=True)
        return jsonify({"error": "Error interno durante la autenticación"}), 500
    
    finally:
        if cur: cur.close()
        if conn: conn.close()
        print(f"[LOG] Flujo de login finalizado.", flush=True)

@app.route('/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection(Config)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify({"status": "UP", "database": "Connected"}), 200
    except Exception as e:
        return jsonify({"status": "DOWN", "database": "Disconnected", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)