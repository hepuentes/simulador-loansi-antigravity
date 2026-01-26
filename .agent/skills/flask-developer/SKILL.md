---
name: flask-developer
description: Desarrolla y corrige código Python Flask con Flask-WTF, SQLite y Jinja2. Usa cuando el usuario pida crear endpoints, corregir bugs, modificar templates, o trabajar con formularios. VERIFICA que los cambios se apliquen realmente antes de reportar.
---

# Flask Developer Skill

## Cuándo se activa este skill
- Usuario pide crear o modificar rutas/endpoints Flask
- Usuario reporta errores en formularios o CSRF
- Usuario necesita queries SQLite
- Usuario pide modificar templates Jinja2
- Hay errores 400, 403, 404, 500 en la aplicación
- Usuario dice "corrige", "arregla", "fix", "bug"

## PROTOCOLO ANTI-ALUCINACIÓN (OBLIGATORIO)

### Antes de modificar cualquier archivo:
1. LEER el archivo completo primero
2. IDENTIFICAR la línea exacta del problema
3. PLANIFICAR el cambio mínimo necesario

### Después de cada modificación:
1. RELEER el archivo para confirmar que el cambio se guardó
2. EJECUTAR verificación de sintaxis:
```powershell
python -m py_compile archivo_modificado.py
```
3. Si hay error de sintaxis, CORREGIR antes de continuar

### Antes de reportar "completado":
1. Verificar que el archivo cambió realmente
2. Ejecutar el servidor de prueba:
```powershell
python run.py
```
3. Si hay error al iniciar, NO reportar como completado

## Patrones de Código Flask

### Ruta con Formulario (Flask-WTF)
```python
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

bp = Blueprint('main', __name__)

class MiForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    submit = SubmitField('Enviar')

@bp.route('/ruta', methods=['GET', 'POST'])
def mi_funcion():
    form = MiForm()
    if form.validate_on_submit():
        # Procesar datos
        flash('Operación exitosa', 'success')
        return redirect(url_for('main.mi_funcion'))
    return render_template('template.html', form=form)
```

### Template con CSRF
```html
{% extends 'base.html' %}
{% block content %}
<form method="POST">
    {{ form.csrf_token }}
    {{ form.nombre.label }} {{ form.nombre(class="form-control") }}
    {% for error in form.nombre.errors %}
        <span class="text-danger">{{ error }}</span>
    {% endfor %}
    {{ form.submit(class="btn btn-primary") }}
</form>
{% endblock %}
```

### Query SQLite Segura
```python
def get_user(user_id):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", 
        (user_id,)
    ).fetchone()
    return user

def insert_user(nombre, email):
    db = get_db()
    db.execute(
        "INSERT INTO users (nombre, email) VALUES (?, ?)",
        (nombre, email)
    )
    db.commit()
```

## Formato de Reporte al Completar

```
## Cambios Realizados

📍 ARCHIVO: ruta/al/archivo.py
📝 CAMBIO: Descripción breve del cambio
🔧 LÍNEAS: XX-YY

### Código modificado:
[mostrar el código nuevo]

### Verificación:
✅ Sintaxis verificada: python -m py_compile OK
✅ Servidor inicia: python run.py OK
✅ Cambio confirmado en archivo: SÍ
```

## Si el Error Persiste Después del Fix

1. Verificar que guardaste el archivo correcto (ruta completa)
2. Verificar que Flask recargó (modo debug muestra "Restarting")
3. Limpiar caché del navegador (Ctrl+Shift+R)
4. Revisar logs de Flask en terminal
5. Si nada funciona: REPORTAR el problema, no inventar solución
