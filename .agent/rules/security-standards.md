---
trigger: always_on
---

# Estándares de Seguridad Flask

## CSRF - Obligatorio SIEMPRE

### En TODOS los formularios HTML
```html
<form method="POST">
    {{ form.hidden_tag() }}
    <!-- campos del formulario -->
</form>
```

### Para formularios sin FlaskForm
```html
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <!-- campos -->
</form>
```

### En peticiones AJAX/Fetch
```javascript
const csrfToken = document.querySelector('input[name="csrf_token"]').value;
fetch('/api/endpoint', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(data)
});
```

## SQL Injection - Prevención

### SIEMPRE usar queries parametrizados
```python
# CORRECTO
cursor.execute("SELECT * FROM users WHERE id = ?", [user_id])
db.execute("INSERT INTO tabla (col1, col2) VALUES (?, ?)", [val1, val2])

# INCORRECTO - NUNCA hacer esto
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
```

## XSS - Prevención

### Jinja2 escapa automáticamente, pero cuidado con:
```html
<!-- PELIGROSO - revisar cada uso -->
{{ variable|safe }}

<!-- SEGURO - escape automático -->
{{ variable }}
```

## Configuración Segura Flask

### Archivo config.py debe tener:
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-temporal-solo-desarrollo'
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
```

## Contraseñas

### SIEMPRE hashear con werkzeug
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Guardar
hashed = generate_password_hash(password)

# Verificar
if check_password_hash(stored_hash, password):
    # Login exitoso
```