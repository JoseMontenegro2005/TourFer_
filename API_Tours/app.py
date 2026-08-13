from flask import Flask, jsonify, request
from functools import wraps
from config import Config
from db import get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key == Config.CATALOGO_API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Acceso no autorizado: API Key inválida"}), 401
    return decorated_function

@app.route('/tours', methods=['GET'])
def get_all_tours():
    print("[LOG] Solicitud GET /tours recibida.", flush=True)
    conn = None
    cur = None
    try:
        print("[LOG] Iniciando conexión con la base de datos de catálogo...", flush=True)
        conn = get_db_connection(Config)
        cur = conn.cursor()
        cur.execute("SELECT * FROM tours")
        tours = cur.fetchall()
        print(f"[LOG] Consulta exitosa. Se retornaron {len(tours)} tours.", flush=True)
        return jsonify(tours), 200
    except Exception as e:
        print(f"[ERROR] Error al obtener tours: {str(e)}", flush=True)
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/tours/<int:id>', methods=['GET'])
def get_tour_by_id(id):
    print(f"[LOG] Solicitud GET /tours/{id} recibida.", flush=True)
    conn = None
    cur = None
    try:
        print("[LOG] Iniciando conexión con la base de datos de catálogo...", flush=True)
        conn = get_db_connection(Config)
        cur = conn.cursor()
        cur.execute("SELECT * FROM tours WHERE id = %s", (id,))
        tour = cur.fetchone()
        
        if tour:
            print(f"[LOG] Tour ID {id} encontrado.", flush=True)
            return jsonify(tour), 200
        
        print(f"[WARNING] Tour ID {id} no existe en la base de datos.", flush=True)
        return jsonify({"error": "Tour no encontrado"}), 404
    except Exception as e:
        print(f"[ERROR] Error al buscar tour {id}: {str(e)}", flush=True)
        return jsonify({"error": "Error en la consulta"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/guias', methods=['GET'])
def get_all_guias():
    print("[LOG] Solicitud GET /guias recibida.", flush=True)
    conn = None
    cur = None
    try:
        print("[LOG] Iniciando conexión con la base de datos de catálogo...", flush=True)
        conn = get_db_connection(Config)
        cur = conn.cursor()
        
        print("[LOG] Consultando información de los guías registrados...", flush=True)
        cur.execute("SELECT id, nombre, email, biografia FROM guias")
        guias = cur.fetchall()
        
        print(f"[LOG] Consulta exitosa. Total de guías recuperados: {len(guias)}", flush=True)
        return jsonify(guias), 200

    except Exception as e:
        print(f"[ERROR] No se pudo obtener la lista de guías: {str(e)}", flush=True)
        return jsonify({"error": "Error interno del servidor al consultar guías"}), 500
    
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/tours', methods=['POST'])
@require_api_key
def create_tour():
    data = request.get_json()
    print(f"[LOG] Intentando crear nuevo tour: {data.get('nombre')}", flush=True)
    
    conn = None
    cur = None
    try:
        conn = get_db_connection(Config)
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO tours (nombre, destino, descripcion, duracion_horas, precio, cupos_disponibles, guia_id) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (data['nombre'], data['destino'], data['descripcion'], data['duracion_horas'], 
             data['precio'], data['cupos_disponibles'], data.get('guia_id'))
        )
        new_id = cur.lastrowid
        conn.commit()
        print(f"[EVENTO] Tour '{data['nombre']}' creado exitosamente con ID: {new_id}", flush=True)
        return jsonify({"mensaje": "Tour creado", "id": new_id}), 201
    except Exception as e:
        if conn: conn.rollback()
        print(f"[ERROR] No se pudo crear el tour: {str(e)}", flush=True)
        return jsonify({"error": "Error al insertar el tour"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/tours/<int:id>/cupos', methods=['PATCH'])
@require_api_key
def update_tour_cupos(id):
    data = request.get_json()
    cantidad = data.get('cantidad')
    accion = data.get('accion')
    
    print(f"[LOG] Solicitud PATCH /cupos para Tour ID {id}. Acción: {accion}, Cantidad: {cantidad}", flush=True)
    
    conn = None
    cur = None
    try:
        conn = get_db_connection(Config)
        cur = conn.cursor()
        
        cur.execute("SELECT nombre, cupos_disponibles, precio FROM tours WHERE id = %s", (id,))
        tour = cur.fetchone()
        
        if not tour:
            print(f"[WARNING] Intento de actualizar cupos en Tour ID {id} inexistente.", flush=True)
            return jsonify({"error": "Tour no encontrado"}), 404

        if accion == 'decrementar':
            nuevos_cupos = tour['cupos_disponibles'] - cantidad
        else:
            nuevos_cupos = tour['cupos_disponibles'] + cantidad
        
        if nuevos_cupos < 0:
            print(f"[WARNING] Stock insuficiente para Tour '{tour['nombre']}'. Disponibles: {tour['cupos_disponibles']}", flush=True)
            return jsonify({"error": "Cupos insuficientes para realizar la operación"}), 409

        cur.execute("UPDATE tours SET cupos_disponibles = %s WHERE id = %s", (nuevos_cupos, id))
        conn.commit()
        
        print(f"[EVENTO] Cupos actualizados para '{tour['nombre']}'. Nuevo total: {nuevos_cupos}", flush=True)
        return jsonify({
            "mensaje": "Cupos actualizados correctamente", 
            "nuevo_total": nuevos_cupos,
            "precio": float(tour['precio'])
        }), 200

    except Exception as e:
        if conn: conn.rollback()
        print(f"[CRÍTICO] Fallo al actualizar cupos del tour {id}: {str(e)}", flush=True)
        return jsonify({"error": "Error interno al actualizar cupos"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

@app.route('/tours/<int:id>', methods=['DELETE'])
@require_api_key
def delete_tour(id):
    print(f"[LOG] Solicitud DELETE para Tour ID {id}", flush=True)
    conn = None
    cur = None
    try:
        conn = get_db_connection(Config)
        cur = conn.cursor()
        cur.execute("DELETE FROM tours WHERE id = %s", (id,))
        affected = cur.rowcount
        conn.commit()
        
        if affected > 0:
            print(f"[EVENTO] Tour ID {id} eliminado físicamente de la DB.", flush=True)
            return jsonify({"mensaje": "Tour eliminado exitosamente"}), 200
        
        print(f"[WARNING] Intento de eliminar Tour ID {id} que no existe.", flush=True)
        return jsonify({"error": "Tour no encontrado"}), 404
    except Exception as e:
        if conn: conn.rollback()
        print(f"[ERROR] Error al intentar eliminar tour {id}: {str(e)}", flush=True)
        return jsonify({"error": "Error en la operación de eliminación"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

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