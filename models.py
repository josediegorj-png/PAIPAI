from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

def _calc_age(birth_str):
    try:
        y,m,d = map(int, birth_str.split("-"))
        b = date(y,m,d); t = date.today()
        return t.year - b.year - ((t.month, t.day) < (b.month, b.day))
    except Exception:
        return None

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Identificación / contacto
    rut = db.Column(db.String(20), unique=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    birthdate = db.Column(db.String(20))  # AAAA-MM-DD

    school = db.Column(db.String(200))
    grade = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    guardian = db.Column(db.String(200))
    relation = db.Column(db.String(50))
    address = db.Column(db.String(250))
    zone = db.Column(db.String(30))

    status = db.Column(db.String(50), default='activo')   # activo, lista_espera, egresado, evaluacion
    frequency = db.Column(db.String(50))

    # PAI
    intervention_plan = db.Column(db.Text)        # plan de intervención
    doc_link = db.Column(db.String(300))          # link a Drive/One/etc

    @property
    def age(self): return _calc_age(self.birthdate) if self.birthdate else None

class SessionRecord(db.Model):
    __tablename__ = 'session_record'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    professional = db.Column(db.String(120), nullable=False)
    mode = db.Column(db.String(50), default='presencial')   # presencial / teleconsulta / domicilio
    duration_min = db.Column(db.Integer, default=50)

    reason = db.Column(db.Text)
    focus = db.Column(db.Text)
    interventions = db.Column(db.Text)
    outcomes = db.Column(db.Text)

    risk_level = db.Column(db.String(50))  # bajo/medio/alto
    referrals = db.Column(db.Text)
    next_steps = db.Column(db.Text)

    created_by = db.Column(db.String(120))
    doc_link = db.Column(db.String(300))

