---
name: flask-developer
description: Desarrolla y corrige código Python Flask. Usa cuando el usuario pida crear endpoints, corregir bugs, modificar templates, trabajar con formularios, cambiar estilos CSS, o modificar JavaScript. SIEMPRE verifica que los cambios se aplicaron antes de reportar.
---

# Flask Developer Skill

## Cuándo se activa
- Usuario dice: "corrige", "arregla", "modifica", "crea", "cambia", "agrega", "elimina"
- Errores 400, 403, 404, 500 en la aplicación
- Cambios en templates HTML, CSS, JavaScript
- Cambios en rutas Flask o lógica Python

## Entorno de Trabajo
- Windows 11 con PowerShell
- Python 3.10 instalado globalmente (SIN venv)
- Flask 3.x con Flask-WTF
- Servidor: `python run.py` en puerto 5000

## PROTOCOLO OBLIGATORIO

### ANTES de modificar:
1. LEER el archivo completo para entender el contexto
2. IDENTIFICAR la línea o sección exacta a cambiar
3. VERIFICAR que no hay archivos duplicados con nombres similares

### DESPUÉS de modificar:
1. VERIFICAR que el cambio se guardó:
```powershell
Get-Content "ruta/archivo" | Select-String "codigo_nuevo"
```

2. Si es archivo Python, verificar sintaxis:
```powershell
python -m py_compile ruta/archivo.py
```

3. Si hay error, CORREGIR inmediatamente

### ANTES de decir "listo":
- Confirmar que Get-Content muestra el código nuevo
- Confirmar que py_compile no dio errores
- Si modificaste varios archivos, verificar TODOS

## Patrones de Código Flask

### Ruta con Formulario
```python
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

bp = Blueprint('nombre', __name__)

@bp.route('/ruta', methods=['GET', 'POST'])
def mi_funcion():
    form = MiForm()
    if form.validate_on_submit():
        # Procesar
        flash('Éxito', 'success')
        return redirect(url_for('nombre.mi_funcion'))
    return render_template('template.html', form=form)
```

### Template con CSRF y Bootstrap
```html
{% extends 'base.html' %}
{% block content %}
<div class="container">
    <form method="POST">
        {{ form.csrf_token }}
        <div class="mb-3">
            {{ form.campo.label(class="form-label") }}
            {{ form.campo(class="form-control") }}
        </div>
        <button type="submit" class="btn btn-primary">Enviar</button>
    </form>
</div>
{% endblock %}
```

### Query SQLite Segura
```python
def get_item(item_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM items WHERE id = ?", 
        (item_id,)
    ).fetchone()
```

### JavaScript en archivo separado
```javascript
// static/js/mi-script.js
document.addEventListener('DOMContentLoaded', function() {
    // código aquí
});
```

## Modificación de Estilos CSS

### En archivo CSS:
```css
/* static/css/custom.css */
.mi-clase {
    border: 2px solid #color;
    background-color: #color;
}
```

### Inline en template (evitar si es posible):
```html
<div style="border: 2px solid {{ nivel.color }};">
```

### En JavaScript dinámico:
```javascript
element.style.border = `2px solid ${color}`;
element.style.borderColor = color;
```

## Formato de Reporte al Completar

```
## Cambio Realizado

📍 ARCHIVO: ruta/completa/archivo.ext
📝 CAMBIO: Descripción breve
🔧 LÍNEAS: XX-YY (aproximado)

### Verificación:
✅ Sintaxis: OK (python -m py_compile)
✅ Contenido guardado: OK (Get-Content confirmó)

### Para probar:
1. Detener servidor si está corriendo (Ctrl+C)
2. Iniciar servidor: python run.py
3. Abrir en navegador: http://127.0.0.1:5000/ruta
4. Refrescar con Ctrl+Shift+R (limpiar caché)
```

## Si el Cambio NO se Aplica

1. Verificar que hiciste clic en "Accept All" en Antigravity
2. Verificar con Get-Content que el archivo tiene el código nuevo
3. Si no lo tiene, volver a aplicar el cambio
4. Si sigue sin aplicarse, reportar el problema
