from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time

app = Flask(__name__)
CORS(app)

fallos = {
    "usuarios": 0,
    "catalogo": 0,
    "reservas": 0
}

fallos_circuit = {
    "usuarios": 0,
    "catalogo": 0,
    "reservas": 0
}

circuito_abierto = {
    "usuarios": False,
    "catalogo": False,
    "reservas": False
}

tiempo_ultimo_fallo = {
    "usuarios": 0.0,
    "catalogo": 0.0,
    "reservas": 0.0
}     

fallos_maximos = 3
TIEMPO_RECUPERACION = 10 

URL_USUARIOS = "http://tourfer-users:5000"
URL_CATALOGO = "http://tourfer-catalogo:5000"
URL_RESERVAS = "http://tourfer-reservas:5000"

def reenviar_headers():
    """Filtra y envía solo las cabeceras estrictamente necesarias a los microservicios"""
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    if 'Content-Type' in request.headers:
        headers['Content-Type'] = request.headers['Content-Type']
    return headers

# RUTAS DE USUARIOS

@app.route("/register", methods=['POST'])
def register():
    print("[Gateway] Accediendo a usuarios (Registro)", flush=True)
    
    if circuito_abierto["usuarios"]:
        tiempo_pasado = time.time() - tiempo_ultimo_fallo["usuarios"]
        if tiempo_pasado >= TIEMPO_RECUPERACION:
            print("[Gateway] Estado HALF-OPEN en usuarios: Intentando recuperar conexión...", flush=True)
        else:
            tiempo_restante = int(TIEMPO_RECUPERACION - tiempo_pasado)
            return jsonify({"error": f"Servicio bloqueado. Reintento en {tiempo_restante}s"}), 503
    
    try:
        body = request.get_json(silent=True)
        response = requests.post(f"{URL_USUARIOS}/register", json=body, headers=reenviar_headers(), timeout=5)
        
        if circuito_abierto["usuarios"]:
            print("[Gateway] Recuperación exitosa. Circuito de usuarios CERRADO.", flush=True)
            
        fallos_circuit["usuarios"] = 0
        circuito_abierto["usuarios"] = False
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        fallos_circuit["usuarios"] += 1
        fallos["usuarios"] += 1
        tiempo_ultimo_fallo["usuarios"] = time.time() 
        print(f"[Gateway] Fallo en usuarios número {fallos_circuit['usuarios']}. Detalles: {e}", flush=True)

        if fallos_circuit["usuarios"] >= fallos_maximos or circuito_abierto["usuarios"]:
            circuito_abierto["usuarios"] = True
            print("[Gateway] Circuito de usuarios ABIERTO.", flush=True)

        return jsonify({"error": "Servicio de usuarios caido"}), 503

@app.route("/login", methods=['POST'])
def login():
    print("[Gateway] Accediendo a usuarios (Login)", flush=True)
    
    if circuito_abierto["usuarios"]:
        tiempo_pasado = time.time() - tiempo_ultimo_fallo["usuarios"]
        if tiempo_pasado >= TIEMPO_RECUPERACION:
            print("[Gateway] Estado HALF-OPEN en usuarios: Intentando recuperar conexión...", flush=True)
        else:
            tiempo_restante = int(TIEMPO_RECUPERACION - tiempo_pasado)
            return jsonify({"error": f"Servicio bloqueado. Reintento en {tiempo_restante}s"}), 503
    
    try:
        body = request.get_json(silent=True)
        response = requests.post(f"{URL_USUARIOS}/login", json=body, headers=reenviar_headers(), timeout=5)
        
        if circuito_abierto["usuarios"]:
            print("[Gateway] Recuperación exitosa. Circuito de usuarios CERRADO.", flush=True)
            
        fallos_circuit["usuarios"] = 0
        circuito_abierto["usuarios"] = False
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException as e:
        fallos_circuit["usuarios"] += 1
        fallos["usuarios"] += 1
        tiempo_ultimo_fallo["usuarios"] = time.time() 
        print(f"[Gateway] Fallo en usuarios número {fallos_circuit['usuarios']}", flush=True)

        if fallos_circuit["usuarios"] >= fallos_maximos or circuito_abierto["usuarios"]:
            circuito_abierto["usuarios"] = True
            print("[Gateway] Circuito de usuarios ABIERTO.", flush=True)

        return jsonify({"error": "Servicio de usuarios caido"}), 503

# RUTAS DE CATÁLOGO

@app.route("/tours", methods=['GET', 'POST'])
def tours():
    print(f"[Gateway] Accediendo a catálogo (Tours - {request.method})", flush=True)
    
    if circuito_abierto["catalogo"]:
        tiempo_pasado = time.time() - tiempo_ultimo_fallo["catalogo"]
        if tiempo_pasado >= TIEMPO_RECUPERACION:
            print("[Gateway] Estado HALF-OPEN en catálogo: Intentando recuperar...", flush=True)
        else:
            tiempo_restante = int(TIEMPO_RECUPERACION - tiempo_pasado)
            return jsonify({"error": f"Servicio bloqueado. Reintento en {tiempo_restante}s"}), 503
    
    try:
        if request.method == 'GET':
            response = requests.get(f"{URL_CATALOGO}/tours", headers=reenviar_headers(), timeout=5)
        else:
            body = request.get_json(silent=True)
            response = requests.post(f"{URL_CATALOGO}/tours", json=body, headers=reenviar_headers(), timeout=5)
        
        if circuito_abierto["catalogo"]:
            print("[Gateway] Recuperación exitosa. Circuito de catálogo CERRADO.", flush=True)
            
        fallos_circuit["catalogo"] = 0
        circuito_abierto["catalogo"] = False
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException:
        fallos_circuit["catalogo"] += 1
        fallos["catalogo"] += 1
        tiempo_ultimo_fallo["catalogo"] = time.time()
        print(f"[Gateway] Fallo en catálogo número {fallos_circuit['catalogo']}", flush=True)

        if fallos_circuit["catalogo"] >= fallos_maximos or circuito_abierto["catalogo"]:
            circuito_abierto["catalogo"] = True
            print("[Gateway] Circuito de catálogo ABIERTO.", flush=True)

        return jsonify({"error": "Servicio de catálogo no disponible"}), 503

@app.route("/tours/<int:id>", methods=['GET', 'DELETE'])
def tour_by_id(id):
    print(f"[Gateway] Accediendo a catálogo (Tour ID {id} - {request.method})", flush=True)
    
    if circuito_abierto["catalogo"]:
        tiempo_pasado = time.time() - tiempo_ultimo_fallo["catalogo"]
        if tiempo_pasado >= TIEMPO_RECUPERACION:
            print("[Gateway] Estado HALF-OPEN en catálogo: Intentando recuperar...", flush=True)
        else:
            return jsonify({"error": "Servicio bloqueado. Circuito abierto."}), 503
            
    try:
        if request.method == 'GET':
            response = requests.get(f"{URL_CATALOGO}/tours/{id}", headers=reenviar_headers(), timeout=5)
        else:
            response = requests.delete(f"{URL_CATALOGO}/tours/{id}", headers=reenviar_headers(), timeout=5)
        
        if circuito_abierto["catalogo"]:
            print("[Gateway] Recuperación exitosa. Circuito CERRADO.", flush=True)
            
        fallos_circuit["catalogo"] = 0
        circuito_abierto["catalogo"] = False
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException:
        fallos_circuit["catalogo"] += 1
        fallos["catalogo"] += 1
        tiempo_ultimo_fallo["catalogo"] = time.time()
        print(f"[Gateway] Fallo en catálogo por ID número {fallos_circuit['catalogo']}", flush=True)
        
        if fallos_circuit["catalogo"] >= fallos_maximos or circuito_abierto["catalogo"]:
            circuito_abierto["catalogo"] = True
            print("[Gateway] Circuito de catálogo ABIERTO.", flush=True)
            
        return jsonify({"error": "Servicio de catálogo por id caido"}), 503

@app.route("/tours/<int:id>/cupos", methods=['PATCH'])
def tour_cupos(id):
    print(f"[Gateway] Accediendo a catálogo (Actualizar Cupos Tour ID {id})", flush=True)
    
    if circuito_abierto["catalogo"]:
        tiempo_pasado = time.time() - tiempo_ultimo_fallo["catalogo"]
        if tiempo_pasado >= TIEMPO_RECUPERACION:
            print("[Gateway] Estado HALF-OPEN en catálogo: Intentando recuperar...", flush=True)
        else:
            return jsonify({"error": "Servicio bloqueado. Circuito abierto."}), 503
            
    try:
        body = request.get_json(silent=True)
        response = requests.patch(f"{URL_CATALOGO}/tours/{id}/cupos", json=body, headers=reenviar_headers(), timeout=5)
        
        fallos_circuit["catalogo"] = 0
        circuito_abierto["catalogo"] = False
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException:
        fallos_circuit["catalogo"] += 1
        fallos["catalogo"] += 1
        tiempo_ultimo_fallo["catalogo"] = time.time()
        
        if fallos_circuit["catalogo"] >= fallos_maximos or circuito_abierto["catalogo"]:
            circuito_abierto["catalogo"] = True
            print("[Gateway] Circuito de catálogo ABIERTO.", flush=True)
            
        return jsonify({"error": "Servicio de catálogo caido"}), 503

@app.route("/guias", methods=['GET'])
def guias():
    print("[Gateway] Accediendo a catálogo (Guías)", flush=True)
    
    if circuito_abierto["catalogo"]:
        tiempo_pasado = time.time() - tiempo_ultimo_fallo["catalogo"]
        if tiempo_pasado >= TIEMPO_RECUPERACION:
            print("[Gateway] Estado HALF-OPEN en catálogo: Intentando recuperar...", flush=True)
        else:
            return jsonify({"error": "Servicio bloqueado. Circuito abierto."}), 503
            
    try:
        response = requests.get(f"{URL_CATALOGO}/guias", headers=reenviar_headers(), timeout=5)
        fallos_circuit["catalogo"] = 0
        circuito_abierto["catalogo"] = False
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException:
        fallos_circuit["catalogo"] += 1
        fallos["catalogo"] += 1
        tiempo_ultimo_fallo["catalogo"] = time.time()
        
        if fallos_circuit["catalogo"] >= fallos_maximos or circuito_abierto["catalogo"]:
            circuito_abierto["catalogo"] = True
        return jsonify({"error": "Servicio de catálogo caido"}), 503

# RUTAS DE RESERVAS

@app.route("/reservas", methods=['POST'])
def reservas():
    print("[Gateway] Accediendo a reservas (Crear Reserva)", flush=True)
    
    if circuito_abierto["reservas"]:
        tiempo_pasado = time.time() - tiempo_ultimo_fallo["reservas"]
        if tiempo_pasado >= TIEMPO_RECUPERACION:
            print("[Gateway] Estado HALF-OPEN en reservas: Intentando recuperar...", flush=True)
        else:
            tiempo_restante = int(TIEMPO_RECUPERACION - tiempo_pasado)
            return jsonify({"error": f"Servicio bloqueado. Reintento en {tiempo_restante}s"}), 503
    
    try:
        body = request.get_json(silent=True)
        response = requests.post(f"{URL_RESERVAS}/reservas", json=body, headers=reenviar_headers(), timeout=15)
        
        if circuito_abierto["reservas"]:
            print("[Gateway] Recuperación exitosa. Circuito de reservas CERRADO.", flush=True)
            
        fallos_circuit["reservas"] = 0
        circuito_abierto["reservas"] = False
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException:
        fallos_circuit["reservas"] += 1
        fallos["reservas"] += 1
        tiempo_ultimo_fallo["reservas"] = time.time()
        print(f"[Gateway] Fallo en reservas número {fallos_circuit['reservas']}", flush=True)

        if fallos_circuit["reservas"] >= fallos_maximos or circuito_abierto["reservas"]:
            circuito_abierto["reservas"] = True
            print("[Gateway] Circuito de reservas ABIERTO.", flush=True)

        return jsonify({"error": "Servicio de reservas no disponible"}), 503

@app.route("/mis-reservas", methods=['GET'])
def mis_reservas():
    print("[Gateway] Accediendo a reservas (Mis Reservas)", flush=True)
    
    if circuito_abierto["reservas"]:
        tiempo_pasado = time.time() - tiempo_ultimo_fallo["reservas"]
        if tiempo_pasado >= TIEMPO_RECUPERACION:
            print("[Gateway] Estado HALF-OPEN en reservas: Intentando recuperar...", flush=True)
        else:
            return jsonify({"error": "Servicio bloqueado. Circuito abierto."}), 503
            
    try:
        response = requests.get(f"{URL_RESERVAS}/mis-reservas", headers=reenviar_headers(), timeout=5)
        
        fallos_circuit["reservas"] = 0
        circuito_abierto["reservas"] = False
        return jsonify(response.json()), response.status_code
    
    except requests.exceptions.RequestException:
        fallos_circuit["reservas"] += 1
        fallos["reservas"] += 1
        tiempo_ultimo_fallo["reservas"] = time.time()
        
        if fallos_circuit["reservas"] >= fallos_maximos or circuito_abierto["reservas"]:
            circuito_abierto["reservas"] = True
            print("[Gateway] Circuito de reservas ABIERTO.", flush=True)
            
        return jsonify({"error": "Servicio de reservas caido"}), 503

# RUTAS DE MONITOREO DEL GATEWAY

@app.route('/health', methods=['GET'])
def global_health():
    print("[Gateway] Generando reporte de salud global...", flush=True)
    return jsonify({
        "gateway_status": "UP",
        "circuit_breakers": {
            "usuarios": "OPEN" if circuito_abierto["usuarios"] else "CLOSED",
            "catalogo": "OPEN" if circuito_abierto["catalogo"] else "CLOSED",
            "reservas": "OPEN" if circuito_abierto["reservas"] else "CLOSED"
        },
        "fallos_actuales": fallos,
        "fallos_circuit": fallos_circuit
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)