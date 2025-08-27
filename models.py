from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Identificación básica (Chile)
    rut = db.Column(db.String(20), unique=True, nullable=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)

    # Datos escolares
    school = db.Column(db.String(200))
    grade = db.Column(db.String(50))  # 5° básico, 2° medio, etc.

    # Contacto
    phone = db.Column(db.String(50))
    guardian = db.Column(db.String(200))

    # Otros
    birthdate = db.Column(db.String(20))
    status = db.Column(db.String(50), default='activo')  # activo, egresado, lista_espera

class SessionRecord(db.Model):
    __tablename__ = 'session_record'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)

    # Registro de intervención por sesión (tipo Medilink)
    date = db.Column(db.Date, nullable=False)
    professional = db.Column(db.String(120), nullable=False)  # Psicólogo, TO, TS, etc.
    mode = db.Column(db.String(50), default='presencial')      # presencial/teleconsulta/domicilio
    duration_min = db.Column(db.Integer, default=50)

    reason = db.Column(db.Text)            # motivo consulta/derivación
    focus = db.Column(db.Text)             # foco/objetivo de la sesión
    interventions = db.Column(db.Text)     # técnicas, instrumentos, actividades
    outcomes = db.Column(db.Text)          # resultados, observaciones clínicas

    risk_level = db.Column(db.String(50))  # bajo/medio/alto + banderas
    referrals = db.Column(db.Text)         # derivaciones (OLN, salud, OPD, etc.)
    next_steps = db.Column(db.Text)        # tareas, acuerdos, próxima cita
