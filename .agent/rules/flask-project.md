---
trigger: always_on
---

# Reglas del Proyecto Flask LOANSI - SIEMPRE ACTIVAS

## Información del Proyecto
- Nombre: Simulador LOANSI
- Stack: Python 3.10, Flask 3.x, Flask-WTF, SQLite
- Frontend: Bootstrap 5.3.2 (CDN)
- Sistema: Windows 11
- Despliegue: PythonAnywhere

## Credenciales de Prueba (Solo Desarrollo Local)
```
URL: http://127.0.0.1:5000/login
Usuario: hpsupersu
Contraseña: loanaP25@
```

## Estructura del Proyecto
```
simulador-loansi-antigravity/
├── run.py                      # Punto de entrada
├── app/
│   ├── __init__.py            # App factory
│   ├── config.py              # Configuración
│   ├── routes/                # Blueprints
│   │   ├── admin_routes.py
│   │   ├── asesor_routes.py
│   │   ├── auth.py            # Login/logout
│   │   └── ...
│   ├── services/
│   └── utils/
├── templates/
│   ├── admin/
│   │   └── admin.html
│   ├── asesor/
│   ├── cliente/
│   ├── dashboards/
│   └── login.html             # Página de login
├── static/
│   ├── css/
│   └── js/
└── .agent/
    ├── rules/
    │   ├── flask-development.md
    │   ├── file-management.md
    │   ├── security-standards.md
    │   └── test-credentials.md    # Credenciales
    └── workflows/
        ├── developer.md
        ├── auditor.md
        ├── security.md
        └── qa-tester.md           # Login automático
```

## Reglas de Código OBLIGATORIAS

### CSRF - En TODOS los formularios POST
```html
<form method="POST">
    {{ form.csrf_token }}
    <!-- o -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
</form>
```

### SQL - SIEMPRE usar parámetros
```python
# CORRECTO
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# PROHIBIDO - SQL Injection
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Templates - Herencia obligatoria
```html
{% extends 'dashboards/_base_dashboard.html' %}
{% block content %}
<!-- contenido -->
{% endblock %}
```

## Prevención de Duplicados de Archivos

### Antes de editar CUALQUIER archivo:
1. Verificar que es el archivo correcto
2. Buscar si hay duplicados con nombres similares
3. Confirmar cuál usa render_template() en las rutas

### Archivos a NUNCA modificar:
- Cualquier archivo con sufijo: _fixed, _backup, _old, _bak
- Archivos en carpeta /archive/
- Archivos .pyc, __pycache__/

## Verificación de Cambios (Windows PowerShell)

### Después de CADA modificación:
```powershell
# Verificar sintaxis
python -m py_compile archivo_modificado.py

# Verificar que el cambio se guardó
Get-Content "ruta/archivo" | Select-String "contenido_nuevo"

# Verificar que servidor arranca
python -c "from app import create_app; create_app()"
```

## Comportamiento del Agente

### OBLIGATORIO:
- Si falta información: PREGUNTAR, no asumir
- Si un archivo no existe: REPORTAR, no inventar
- Si una importación falla: VERIFICAR requirements.txt
- Nunca modificar archivos fuera del proyecto

### Antes de reportar "tarea completada":
1. Verificar que el archivo se modificó realmente
2. Ejecutar verificación de sintaxis
3. Si hay tests relacionados, ejecutarlos
4. Solo entonces reportar como completado