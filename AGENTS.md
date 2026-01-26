# Configuración de Agentes AI - Proyecto LOANSI

## Información del Proyecto
- **Nombre**: Simulador LOANSI
- **Stack**: Python 3.10, Flask 3.x, Flask-WTF, SQLite
- **Frontend**: Bootstrap 5.3.2 (CDN)
- **Sistema**: Windows 11
- **IDE**: Google Antigravity Desktop

## Credenciales de Prueba
```
URL: http://127.0.0.1:5000/login
Usuario: hpsupersu
Contraseña: loanaP25@
```

## Skills Disponibles (se activan automáticamente)

| Skill | Función | Cuándo se activa |
|-------|---------|------------------|
| **flask-developer** | Corrige bugs, crea código | "corrige", "arregla", "crea", "modifica" |
| **code-auditor** | Revisa calidad de código | "revisa", "audita", "analiza" |
| **security-analyzer** | Detecta vulnerabilidades | "seguridad", "vulnerabilidades" |
| **qa-tester** | Prueba y verifica | "prueba", "test", "verifica" |

## Workflows Disponibles (activar con /nombre)

| Comando | Función |
|---------|---------|
| `/fix-bug` | Flujo completo para corregir un bug |
| `/run-tests` | Ejecutar pruebas del sistema |

## Flujo de Trabajo Recomendado

### Para corregir un bug:
1. Describe el problema al agente (se activa flask-developer)
2. El agente propone solución y la aplica
3. Pide verificación (se activa qa-tester)
4. El agente prueba y reporta

### Para auditoría:
1. Pide revisar el código (se activa code-auditor)
2. El agente genera reporte con problemas
3. Para cada problema, pide corrección (se activa flask-developer)

### Para seguridad:
1. Pide análisis de seguridad (se activa security-analyzer)
2. El agente reporta vulnerabilidades
3. Para cada una, pide corrección (se activa flask-developer)

## Separación de Roles

| Skill | Puede hacer | NO puede hacer |
|-------|-------------|----------------|
| flask-developer | Modificar código | - |
| code-auditor | Analizar y reportar | Modificar código |
| security-analyzer | Detectar vulnerabilidades | Modificar código |
| qa-tester | Probar y reportar | Modificar código |

## Estructura de Archivos
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

## Patrones de Código Obligatorios

### CSRF en formularios
```html
<form method="POST">
    {{ form.csrf_token }}
</form>
```

### SQL seguro
```python
cursor.execute("SELECT * FROM tabla WHERE id = ?", (valor,))
```
