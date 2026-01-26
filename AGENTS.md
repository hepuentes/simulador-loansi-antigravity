# Configuración de Agentes - Proyecto LOANSI

## Información del Proyecto
- **Nombre**: Simulador LOANSI
- **Ubicación**: C:\Users\Admin\loansi antig\simulador-loansi-antigravity
- **Stack**: Python 3.10, Flask 3.x, Flask-WTF, SQLite
- **Frontend**: Bootstrap 5.3.2 (CDN)
- **Sistema**: Windows 11
- **Antigravity**: 1.15.8

## Entorno de Ejecución
- NO se usa entorno virtual (venv)
- Python se ejecuta directamente: `python run.py`
- Las dependencias están instaladas globalmente
- Terminal: PowerShell integrado de Antigravity

## Credenciales de Prueba
```
URL: http://127.0.0.1:5000/login
Usuario: hpsupersu
Contraseña: loanaP25@
```

## Skills Disponibles

| Skill | Función | Palabras que lo activan |
|-------|---------|-------------------------|
| flask-developer | Crear y corregir código | "corrige", "arregla", "modifica", "crea", "cambia" |
| code-auditor | Revisar calidad | "revisa", "audita", "analiza código" |
| security-analyzer | Detectar vulnerabilidades | "seguridad", "vulnerabilidades", "OWASP" |

## Workflows Disponibles

| Comando | Función |
|---------|---------|
| /fix-bug | Corregir un bug paso a paso |
| /verify | Verificar que cambios se aplicaron |

## Reglas Críticas para el Agente

### Sobre Cambios de Código
1. SIEMPRE leer el archivo ANTES de modificarlo
2. SIEMPRE verificar que el cambio se guardó DESPUÉS
3. NUNCA decir "listo" sin haber verificado
4. Si hay errores, corregirlos sin preguntar

### Sobre Verificación de Cambios
Después de modificar un archivo, OBLIGATORIO ejecutar:
```powershell
Get-Content "ruta/archivo" | Select-String "texto_nuevo"
```
Si el texto NO aparece, el cambio NO se guardó.

### Sobre el Servidor Flask
- Iniciar: `python run.py`
- Detener: Ctrl+C en la terminal
- NO intentar abrir navegador automáticamente
- El usuario probará manualmente en http://127.0.0.1:5000

### Sobre Dependencias
- NO activar venv (no existe)
- Si falta un paquete: `pip install nombre-paquete`
- Verificar con: `pip show nombre-paquete`

## Estructura del Proyecto
```
simulador-loansi-antigravity/
├── .agent/
│   ├── rules/
│   │   └── flask-project.md
│   ├── skills/
│   │   ├── flask-developer/SKILL.md
│   │   ├── code-auditor/SKILL.md
│   │   └── security-analyzer/SKILL.md
│   └── workflows/
│       ├── fix-bug.md
│       └── verify.md
├── app/
│   ├── __init__.py
│   ├── routes/
│   └── services/
├── templates/
├── static/
├── run.py
└── requirements.txt
```

## Patrones de Código Obligatorios

### CSRF en formularios
```html
<form method="POST">
    {{ form.csrf_token }}
    <!-- o -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
</form>
```

### SQL seguro
```python
cursor.execute("SELECT * FROM tabla WHERE id = ?", (valor,))
```

### Imports en rutas Flask
```python
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
```
