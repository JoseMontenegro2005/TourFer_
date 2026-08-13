from flask import Flask, jsonify, request
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/notify', methods=['POST'])
def send_notification():
    data = request.get_json(silent=True) or {}
    email_destino = data.get('email')
    asunto = data.get('asunto', 'Confirmación de Reserva - TourFer')
    mensaje_html = data.get('mensaje', 'Su reserva ha sido procesada con éxito.')
    
    print(f"[LOG] Solicitud de correo recibida para: {email_destino}", flush=True)

    if not email_destino:
        return jsonify({"error": "El campo 'email' es obligatorio"}), 400

    REMITENTE = os.environ.get('SMTP_EMAIL')
    PASSWORD = os.environ.get('SMTP_PASSWORD')
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com') 
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))

    if not REMITENTE or not PASSWORD:
        print("[WARNING] Credenciales SMTP no configuradas. SIMULANDO envío...", flush=True)
        return jsonify({"status": "Simulado", "detalle": "Configura SMTP_EMAIL y SMTP_PASSWORD"}), 200

    try:
        msg = MIMEMultipart()
        msg['From'] = REMITENTE
        msg['To'] = email_destino
        msg['Subject'] = asunto
        
        msg.attach(MIMEText(mensaje_html, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(REMITENTE, PASSWORD)
        
        server.sendmail(REMITENTE, email_destino, msg.as_string())
        server.quit()
        
        print(f"[SUCCESS] Correo enviado exitosamente vía SMTP a {email_destino}", flush=True)
        return jsonify({"status": "Notificación enviada con éxito reales por SMTP"}), 200

    except Exception as e:
        print(f"[ERROR CRÍTICO SMTP] Falló el envío: {str(e)}", flush=True)
        return jsonify({"error": "No se pudo enviar el correo por SMTP", "detalle": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP", "mode": "SMTP"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)