from datetime import datetime

def validate_patient_form(form):
    errors=[]
    data = {
        'rut': form.get('rut','').strip() or None,
        'first_name': form.get('first_name','').strip(),
        'last_name': form.get('last_name','').strip(),
        'school': form.get('school','').strip() or None,
        'grade': form.get('grade','').strip() or None,
        'birthdate': form.get('birthdate','').strip() or None,
        'phone': form.get('phone','').strip() or None,
        'guardian': form.get('guardian','').strip() or None,
        'relation': form.get('relation','').strip() or None,
        'address': form.get('address','').strip() or None,
        'zone': form.get('zone','').strip() or None,
        'status': form.get('status','activo').strip() or 'activo',
        'frequency': form.get('frequency','').strip() or None,
        'intervention_plan': form.get('intervention_plan','').strip() or None,
        'doc_link': form.get('doc_link','').strip() or None,
    }
    if not data['first_name']: errors.append('Nombres es obligatorio')
    if not data['last_name']: errors.append('Apellidos es obligatorio')
    return (len(errors)==0, data, errors)

def validate_session_form(form):
    errors=[]
    try:
        d = datetime.strptime(form.get('date',''), '%Y-%m-%d').date()
    except Exception:
        d=None; errors.append('Fecha inválida (AAAA-MM-DD)')
    data = {
        'date': d,
        'professional': form.get('professional','').strip(),
        'mode': form.get('mode','presencial').strip() or 'presencial',
        'duration_min': int(form.get('duration_min',50) or 50),
        'reason': form.get('reason','').strip() or None,
        'focus': form.get('focus','').strip() or None,
        'interventions': form.get('interventions','').strip() or None,
        'outcomes': form.get('outcomes','').strip() or None,
        'risk_level': form.get('risk_level','').strip() or None,
        'referrals': form.get('referrals','').strip() or None,
        'next_steps': form.get('next_steps','').strip() or None,
        'doc_link': form.get('doc_link','').strip() or None,
    }
    if not data['professional']: errors.append('Profesional es obligatorio')
    return (len(errors)==0 and d is not None, data, errors)
