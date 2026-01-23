---
trigger: always_on
---

## Reglas de Desarrollo Flask

## Contexto del Proyecto
- Python 3.10
- Flask 3.x con Flask-WTF (CSRF activo)
- SQLite como base de datos
- Bootstrap 5.3.2 via CDN
- Despliegue: PythonAnywhere Free tier

##ESTRUCTURA DEL PROYECTO:
```
/simulador-loansi-antigravity/
├── app/
│   ├── __init__.py              # Factory create_app() 
│   ├── config.py                # Configuración por entorno
│   ├── extensions.py            # CSRF y extensiones Flask
│   └── routes/
│       ├── __init__.py          # register_blueprints()
│       ├── auth.py              # Login/logout/sesiones
│       ├── main.py              # Home/dashboard
│       ├── admin_routes.py      # Panel administración
│       ├── scoring_routes.py    # Sistema puntuación
│       ├── comite_routes.py     # Comité de crédito
│       ├── api_routes.py        # Endpoints REST/AJAX
│       └── asesor_routes.py     # Gestión asesores
│   └── services/                # Lógica de negocio
│   └── models/                  # Acceso a datos
│   └── utils/                   # Utilidades
├── templates/
│   ├── admin/
│   ├── asesor/
│   ├── cliente/
│   ├── dashboards/
│   └── partials/
├── static/
│   ├── css/
│   │   ├── theme.css            # Variables CSS, tema claro/oscuro
│   │   └── components.css       # Estilos componentes
│   └── js/
├── run.py                       # Punto de entrada
├── loansi.db                    # Base de datos SQLite
├── db_helpers.py                # Helpers BD
└── requirements.txt
```
## Reglas de Código Flask

### CSRF - Obligatorio en Todos los Formularios
```html
<form method="POST">
    {{ form.hidden_tag() }}
    <!-- O para formularios sin FlaskForm: -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
</form>
```

### AJAX con CSRF Token
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

### SQLite - SIEMPRE Queries Parametrizados
```python
# CORRECTO
cursor.execute("SELECT * FROM users WHERE id = ?", [user_id])

# INCORRECTO - SQL Injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Templates - Herencia Obligatoria
Todos los templates DEBEN extender base.html:
```html
{% extends 'base.html' %}
{% block title %}Título{% endblock %}
{% block content %}
<!-- Contenido -->
{% endblock %}
```

## Reglas de Estilo
- PEP 8 para todo el código Python
- Nombres descriptivos: is_active, has_permission
- snake_case para archivos: user_routes.py
- Type hints en funciones públicas