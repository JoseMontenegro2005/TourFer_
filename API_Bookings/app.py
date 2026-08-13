from flask import Flask, jsonify, request
import requests
from config import Config
from db import get_db_connection
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
jwt = JWTManager(app)

@app.route('/mis-reservas', methods=['GET'])
@jwt_required()
def get_mis_reservas():
    jwt_claims = get_jwt()
    user_id = jwt_claims.get("user_id") 
    print(f"[LOG] Solicitud GET /mis-reservas recibida para el usuario ID: {user_id}", flush=True)
    try:
        conn = get_db_connection(Config)
        cur = conn.cursor()
        cur.execute("SELECT * FROM reservas WHERE usuario_id = %s", (user_id,))
        reservas = cur.fetchall()
        cur.close()
        conn.close()
        print(f"[LOG] Consulta exitosa. Reservas encontradas: {len(reservas)}", flush=True)
        return jsonify(reservas), 200
    
    except Exception as e:
        print(f"[ERROR] Falló la obtención de reservas para el usuario {user_id}: {str(e)}", flush=True)
        return jsonify({"error": "Error interno al obtener el historial de reserva"})

@app.route('/reservas', methods=['POST'])
@jwt_required() 
def create_reserva():
    user_email = get_jwt_identity()
    
    jwt_claims = get_jwt()
    user_id = jwt_claims.get("user_id") 
    
    data = request.get_json()
    tour_id = data.get('tour_id')
    cantidad = data.get('cantidad_personas')
    
    precio_unidad = data.get('precio_unidad', data.get('precio', 0))

    print(f"[LOG] Inicio de proceso de reserva: Usuario ID {user_id} ({user_email}) | Tour {tour_id} | Cantidad {cantidad}", flush=True)

    try:
        print(f"[LOG] Enviando petición PATCH a Catálogo para descontar {cantidad} cupos...", flush=True)
        headers = {'X-API-Key': Config.CATALOGO_API_KEY}
        payload = {"cantidad": cantidad, "accion": "decrementar"}
        
        patch_resp = requests.patch(
            f"{Config.CATALOGO_API_URL}/tours/{tour_id}/cupos",
            json=payload,
            headers=headers,
            timeout=10 
        )

        if patch_resp.status_code != 200:
            error_msg = patch_resp.json().get('error', 'Error desconocido')
            print(f"[WARNING] El Catálogo rechazó la operación: {error_msg} (Status: {patch_resp.status_code})", flush=True)
            return jsonify({"error": f"Catálogo rechazó la operación: {error_msg}"}), patch_resp.status_code

        print(f"[LOG] Cupos descontados exitosamente en el servicio de Catálogo.", flush=True)
        
        tour_data = patch_resp.json() 
        if tour_data and 'precio' in tour_data:
            precio_unidad = float(tour_data.get('precio'))
            print(f"[LOG] Precio de unidad validado de forma interna por Catálogo: {precio_unidad}", flush=True)

    except requests.exceptions.Timeout:
        print(f"[ERROR] Timeout al conectar con Catálogo para el tour {tour_id}.", flush=True)
        return jsonify({"error": "El Catálogo tardó demasiado en responder. Intenta de nuevo."}), 504
    except Exception as e:
        print(f"[ERROR] Error de conexión con el servicio de Catálogo: {str(e)}", flush=True)
        return jsonify({"error": f"No se pudo conectar con el Catálogo: {str(e)}"}), 503

    total = float(precio_unidad) * int(cantidad)
    print(f"[LOG] Intentando guardar la reserva en la base de datos local con Total: {total}...", flush=True)
    
    conn = get_db_connection(Config)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO reservas (tour_id, usuario_id, cantidad_personas, costo_total, estado) VALUES (%s, %s, %s, %s, %s)",
            (tour_id, user_id, cantidad, total, 'Confirmada')
        )
        reserva_id = cur.lastrowid
        conn.commit()
        print(f"[EVENTO]: Reserva {reserva_id} guardada exitosamente en la base de datos con costo {total}.", flush=True)

        try:
            print(f"[LOG NOTIFICACIÓN] Destinatario resuelto directamente desde JWT de forma óptima: {user_email}", flush=True)

            payload_notificacion = {
                "email": user_email,
                "asunto": f"Confirmación de Reserva N° {reserva_id} - TourFer",
                "mensaje": f"""
                    <h2>¡Tu reserva está lista!</h2>
                    <p>Hemos procesado tu registro para el tour de manera exitosa en nuestro ecosistema.</p>
                    <ul>
                        <li><strong>Código de Reserva:</strong> {reserva_id}</li>
                        <li><strong>Cantidad de Cupos:</strong> {cantidad}</li>
                        <li><strong>Costo Total:</strong> ${total:,.2f} COP</li>
                        <li><strong>Mecanismo de red:</strong> Autenticación por Token Autónomo (JWT)</li>
                    </ul>
                    <p>Gracias por viajar con TourFer Colombia.</p>
                """
            }

            notif_resp = requests.post("http://notificaciones:5000/notify", json=payload_notificacion, timeout=4)
            print(f"[LOG NOTIFICACIÓN] Servicio de notificaciones respondió con status: {notif_resp.status_code}", flush=True)

        except Exception as notif_err:
            print(f"[WARNING NO CRÍTICO] Reserva almacenada, fallo en despacho de correo: {str(notif_err)}", flush=True)

        return jsonify({"mensaje": "Reserva creada", "id": reserva_id}), 201

    except Exception as e:
        print(f"[CRÍTICO] Error al insertar en DB: {str(e)}. Iniciando compensación de cupos...", flush=True)
        if conn: conn.rollback()
        
        try:
            requests.patch(
                f"{Config.CATALOGO_API_URL}/tours/{tour_id}/cupos",
                json={"cantidad": cantidad, "accion": "incrementar"},
                headers={'X-API-Key': Config.CATALOGO_API_KEY},
                timeout=5
            )
            print(f"[LOG COMPENSACIÓN]: Cupos devueltos correctamente al tour {tour_id}.", flush=True)
        except Exception as comp_err:
            print(f"[ALERTA]: No se pudo realizar la compensación automática: {str(comp_err)}", flush=True)
        
        return jsonify({"error": "Error al procesar la reserva. Se ha revertido el cambio en cupos."}), 500
    finally:
        cur.close()
        conn.close()

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