# Configuración de Agentes AI - Proyecto LOANSI

## Información del Proyecto
- **Nombre**: Simulador LOANSI
- **Stack**: Python 3.10, Flask 3.x, Flask-WTF, SQLite
- **Frontend**: Bootstrap 5.3.2 (CDN)
- **Sistema**: Windows 11
- **IDE**: Google Antigravity Desktop
- **Despliegue**: PythonAnywhere (al finalizar desarrollo)

## Credenciales de Prueba (Desarrollo Local)
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

## Archivos Activos (ÚNICOS a editar)
| Función | Archivo Correcto |
|---------|------------------|
| Dashboard Admin | templates/admin/admin.html |
| Rutas Admin | app/routes/admin_routes.py |
| Login | templates/login.html |
| Auth | app/routes/auth.py |

## Agentes Disponibles
Usar en el chat del editor:
- `/developer` - Implementar cambios (pide aprobación)
- `/auditor` - Revisar calidad de código
- `/security` - Análisis de seguridad
- `/qa-tester` - Probar cambios con login automático

## Flujo de Trabajo Recomendado

### Para corregir un bug:
1. `/developer` - Describe el bug, él crea plan, tú apruebas, él corrige
2. `/qa-tester` - Él automáticamente: verifica archivos, inicia app, hace login, prueba rutas, reporta

### Para auditoría:
1. `/auditor` - Analiza código y genera reporte
2. `/security` - Analiza vulnerabilidades

## Patrones Obligatorios

### CSRF en Formularios
```html
<form method="POST">
    {{ form.hidden_tag() }}
</form>
```

### Queries SQLite Seguros
```python
cursor.execute("SELECT * FROM tabla WHERE id = ?", [valor])
```
```

---
