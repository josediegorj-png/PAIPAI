import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session as flask_session
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, Patient, SessionRecord
from forms import validate_patient_form, validate_session_form
import csv
from io import StringIO, BytesIO

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cmr_pai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

# Inicializa DB
with app.app_context():
    db.init_app(app)
    db.create_all()

# ---------- Utilidades ----------

def logged_in():
    return flask_session.get('logged_in', False)

def require_login():
    if not logged_in():
        return redirect(url_for('login'))

# ---------- Rutas de autenticación ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == os.environ.get('ADMIN_PASSWORD', 'admin'):
            flask_session['logged_in'] = True
            flash('Ingreso exitoso', 'success')
            return redirect(url_for('dashboard'))
        flash('Contraseña incorrecta', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    flask_session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

# ---------- Vistas principales ----------
@app.route('/')
def index():
    if not logged_in():
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if not logged_in():
        return redirect(url_for('login'))
    total_patients = Patient.query.count()
    active_patients = Patient.query.filter_by(status='activo').count()
    waiting_patients = Patient.query.filter_by(status='lista_espera').count()
    total_sessions = SessionRecord.query.count()
    last_sessions = SessionRecord.query.order_by(SessionRecord.date.desc()).limit(8).all()
    return render_template('dashboard.html',
                           total_patients=total_patients,
                           active_patients=active_patients,
                           waiting_patients=waiting_patients,
                           total_sessions=total_sessions,
                           last_sessions=last_sessions)

# ---------- Pacientes ----------
@app.route('/patients')
def patients_list():
    if not logged_in():
        return redirect(url_for('login'))
    q = request.args.get('q', '').strip()
    status = request.args.get('status', '').strip()
    query = Patient.query
    if q:
        like = f"%{q}%"
        query = query.filter((Patient.first_name.ilike(like)) |
                             (Patient.last_name.ilike(like)) |
                             (Patient.rut.ilike(like)))
    if status:
        query = query.filter_by(status=status)
    patients = query.order_by(Patient.created_at.desc()).all()
    return render_template('patients_list.html', patients=patients, q=q, status=status)

@app.route('/patients/new', methods=['GET', 'POST'])
@app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
def patient_form(patient_id=None):
    if not logged_in():
        return redirect(url_for('login'))
    patient = Patient.query.get(patient_id) if patient_id else None
    if request.method == 'POST':
        ok, data, errors = validate_patient_form(request.form)
        if not ok:
            for e in errors:
                flash(e, 'danger')
            return render_template('patient_form.html', patient=patient)
        if patient:
            for k, v in data.items():
                setattr(patient, k, v)
            flash('Usuario actualizado', 'success')
        else:
            patient = Patient(**data)
            db.session.add(patient)
            flash('Usuario creado', 'success')
        db.session.commit()
        return redirect(url_for('patient_detail', patient_id=patient.id))
    return render_template('patient_form.html', patient=patient)

@app.route('/patients/<int:patient_id>')
def patient_detail(patient_id):
    if not logged_in():
        return redirect(url_for('login'))
    patient = Patient.query.get_or_404(patient_id)
    sessions = SessionRecord.query.filter_by(patient_id=patient.id).order_by(SessionRecord.date.desc()).all()
    return render_template('patient_detail.html', patient=patient, sessions=sessions)

# ---------- Sesiones ----------
@app.route('/sessions')
def sessions_list():
    if not logged_in():
        return redirect(url_for('login'))
    q = request.args.get('q', '').strip()
    query = SessionRecord.query
    if q:
        like = f"%{q}%"
        query = query.filter((SessionRecord.professional.ilike(like)) | (SessionRecord.focus.ilike(like)))
    sessions = query.order_by(SessionRecord.date.desc()).limit(200).all()
    return render_template('sessions_list.html', sessions=sessions, q=q)

@app.route('/patients/<int:patient_id>/sessions/new', methods=['GET', 'POST'])
@app.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
def session_form(patient_id=None, session_id=None):
    if not logged_in():
        return redirect(url_for('login'))
    record = SessionRecord.query.get(session_id) if session_id else None
    patient = Patient.query.get(patient_id) if patient_id else (Patient.query.get(record.patient_id) if record else None)
    if not patient:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('patients_list'))

    if request.method == 'POST':
        ok, data, errors = validate_session_form(request.form)
        if not ok:
            for e in errors:
                flash(e, 'danger')
            return render_template('session_form.html', record=record, patient=patient)
        if record:
            for k, v in data.items():
                setattr(record, k, v)
            flash('Registro actualizado', 'success')
        else:
            record = SessionRecord(patient_id=patient.id, **data)
            db.session.add(record)
            flash('Registro creado', 'success')
        db.session.commit()
        return redirect(url_for('patient_detail', patient_id=patient.id))

    return render_template('session_form.html', record=record, patient=patient)

# ---------- Estadísticas ----------
@app.route('/stats')
def stats():
    if not logged_in():
        return redirect(url_for('login'))
    # Totales
    total_users = Patient.query.count()
    active_users = Patient.query.filter_by(status='activo').count()
    wait_users = Patient.query.filter_by(status='lista_espera').count()
    total_sessions = SessionRecord.query.count()

    # Sesiones por mes del año actual (SQLite)
    yr = date.today().year
    rows = db.session.execute(
        db.text('''
            SELECT strftime('%Y-%m', date) as ym, COUNT(*) as c
            FROM session_record
            WHERE strftime('%Y', date) = :yr
            GROUP BY ym
            ORDER BY ym ASC
        '''), {"yr": str(yr)}
    ).mappings().all()
    monthly = [{"month": r['ym'], "count": r['c']} for r in rows]

    return render_template('stats.html',
                           total_users=total_users,
                           active_users=active_users,
                           wait_users=wait_users,
                           total_sessions=total_sessions,
                           monthly=monthly,
                           year=yr)

# ---------- Exportaciones ----------
@app.route('/export/patients.csv')
def export_patients_csv():
    if not logged_in():
        return redirect(url_for('login'))
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','rut','nombres','apellidos','fecha_nac','curso','establecimiento','telefono','apoderado','estado','creado'])
    for p in Patient.query.order_by(Patient.id.asc()).all():
        cw.writerow([p.id, p.rut, p.first_name, p.last_name, p.birthdate or '', p.grade or '', p.school or '', p.phone or '', p.guardian or '', p.status, p.created_at])
    bio = BytesIO(si.getvalue().encode('utf-8'))
    bio.seek(0)
    return send_file(bio, mimetype='text/csv', as_attachment=True, download_name='patients.csv')

@app.route('/export/sessions.csv')
def export_sessions_csv():
    if not logged_in():
        return redirect(url_for('login'))
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['id','patient_id','fecha','profesional','modalidad','duracion_min','motivo','foco','intervenciones','resultados','riesgo','derivaciones','proximos_pasos'])
    for s in SessionRecord.query.order_by(SessionRecord.id.asc()).all():
        cw.writerow([s.id, s.patient_id, s.date, s.professional, s.mode, s.duration_min, s.reason, s.focus, s.interventions, s.outcomes, s.risk_level, s.referrals, s.next_steps])
    bio = BytesIO(si.getvalue().encode('utf-8'))
    bio.seek(0)
    return send_file(bio, mimetype='text/csv', as_attachment=True, download_name='sessions.csv')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
