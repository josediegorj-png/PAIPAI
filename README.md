# CMR PAI Pucón (mini)

## 1) Uso local
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # ajusta ADMIN_PASSWORD y SECRET_KEY
python app.py
```
Abre http://localhost:5000 y entra con la contraseña.

## 2) Despliegue en Render (gratis)
1. Sube esta carpeta a un repositorio en GitHub.
2. En Render → New + → Web Service → conecta tu repo.
3. **Runtime:** Python.  
   **Build Command:** `pip install -r requirements.txt`  
   **Start Command:** `gunicorn app:app`
4. En *Environment Variables* agrega: `ADMIN_PASSWORD`, `SECRET_KEY`.  
5. Deploy. Listo.

## 3) Campos de sesión (formulario tipo Medilink)
- Fecha (AAAA-MM-DD)  
- Profesional (Psicólogo/a, TO, TS, etc.)  
- Modalidad (presencial/teleconsulta/domicilio)  
- Duración (minutos)  
- Motivo/Derivación  
- Foco/Objetivo  
- Intervenciones (técnicas/actividades)  
- Resultados/Observaciones  
- Nivel de riesgo (bajo/medio/alto)  
- Derivaciones (OLN/Salud/otros)  
- Próximos pasos/tareas

## 4) Exportaciones
- /export/patients.csv  
- /export/sessions.csv

## 5) Notas
- Este sistema NO almacena archivos adjuntos ni historiales clínicos extensos; es un registro liviano.  
- Para multiusuario con permisos por rol, agregar tabla `User` y decoradores @login_required por rol.  
- Para gráficos, se puede integrar Chart.js en `stats.html`.
