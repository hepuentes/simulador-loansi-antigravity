# Reglas del Proyecto Flask LOANSI

## Stack Técnico
- Python 3.10 (instalación global, SIN venv)
- Flask 3.x con Flask-WTF
- SQLite como base de datos
- Bootstrap 5.3.2 (CDN)
- Windows 11 con PowerShell

## Comandos de Terminal (Windows PowerShell)

### Ejecutar servidor
```powershell
python run.py
```

### Verificar sintaxis Python
```powershell
python -m py_compile archivo.py
```

### Instalar dependencia (si falta)
```powershell
pip install nombre-paquete
```

### Verificar que un cambio se guardó
```powershell
Get-Content "ruta/archivo.py" | Select-String "texto_esperado"
```

### Ver contenido de archivo
```powershell
Get-Content "ruta/archivo.py"
```

## Reglas de Código OBLIGATORIAS

### CSRF - En TODOS los formularios POST
```html
<form method="POST">
    {{ form.csrf_token }}
</form>
```

### SQL - SIEMPRE usar parámetros
```python
# CORRECTO
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# PROHIBIDO
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### Templates - Herencia obligatoria
```html
{% extends 'dashboards/_base_dashboard.html' %}
{% block content %}
<!-- contenido -->
{% endblock %}
```

## Estructura de Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| run.py | Punto de entrada de la aplicación |
| app/__init__.py | Factory de la aplicación Flask |
| app/routes/ | Blueprints con las rutas |
| templates/ | Plantillas HTML (Jinja2) |
| static/js/ | JavaScript del frontend |
| static/css/ | Estilos CSS |

## Prevención de Errores

### Antes de modificar un archivo:
1. Leer el archivo completo
2. Identificar la sección exacta a modificar
3. Verificar que no hay otros archivos con nombres similares

### Después de modificar:
1. Ejecutar verificación de sintaxis
2. Confirmar que el cambio se guardó (Get-Content)
3. Si es Python, verificar que no hay errores de import

### Archivos a NUNCA modificar:
- Archivos con sufijo _backup, _old, _fixed
- Archivos en carpeta /archive/
- Archivos __pycache__/

## Credenciales de Prueba
```
URL: http://127.0.0.1:5000/login
Usuario: hpsupersu
Contraseña: loanaP25@
```

## Navegador y Pruebas
- El navegador integrado de Antigravity NO funciona en v1.15.8
- Las pruebas de UI se hacen manualmente
- El agente puede probar endpoints con Invoke-WebRequest en PowerShell
- El usuario abre http://127.0.0.1:5000 en su navegador normal
