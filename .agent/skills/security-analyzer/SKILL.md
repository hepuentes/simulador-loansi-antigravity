---
name: security-analyzer
description: Analiza vulnerabilidades de seguridad en aplicaciones Flask incluyendo SQL injection, XSS, CSRF bypass, exposición de secretos y configuraciones inseguras. Usa para auditoría de seguridad. NO modifica código, solo REPORTA.
---

# Security Analyzer Skill

## Cuándo se activa este skill
- Usuario pide análisis de seguridad
- Usuario dice "vulnerabilidades", "seguridad", "OWASP"
- Antes de deploy a producción
- Después de agregar autenticación o manejo de usuarios

## ROL IMPORTANTE
Este skill SOLO analiza y reporta vulnerabilidades. NO hace modificaciones.
Para corregir, el usuario debe usar el skill flask-developer.

## OWASP Top 10 - Checklist para Flask

### 1. SQL Injection
Buscar queries inseguras:
```powershell
Select-String -Path "app\*.py" -Pattern "execute.*f[`"']" -Recurse
Select-String -Path "app\*.py" -Pattern "execute.*\+" -Recurse
Select-String -Path "app\*.py" -Pattern "execute.*%" -Recurse
```

**Vulnerable:**
```python
db.execute(f"SELECT * FROM users WHERE name = '{name}'")
db.execute("SELECT * FROM users WHERE name = '" + name + "'")
```

**Seguro:**
```python
db.execute("SELECT * FROM users WHERE name = ?", (name,))
```

### 2. Cross-Site Scripting (XSS)
Buscar bypass de autoescape:
```powershell
Select-String -Path "templates\*.html" -Pattern "\|safe" -Recurse
Select-String -Path "app\*.py" -Pattern "Markup\(" -Recurse
```

**Regla:** Solo usar `|safe` con contenido 100% controlado, NUNCA con input de usuario.

### 3. CSRF (Cross-Site Request Forgery)
Verificar que todos los forms POST tienen token:
```powershell
# Buscar forms POST
Select-String -Path "templates\*.html" -Pattern "method=.POST" -Recurse

# Verificar CSRF en cada uno
Select-String -Path "templates\*.html" -Pattern "csrf_token" -Recurse
```

**Cada form POST debe tener:**
```html
<form method="POST">
    {{ form.csrf_token }}
    <!-- o -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

### 4. Exposición de Secretos
```powershell
Select-String -Path "app\*.py" -Pattern "SECRET_KEY.*=.*[`"']" -Recurse
Select-String -Path "*.py" -Pattern "PASSWORD.*=.*[`"']" -Recurse
```

**Vulnerable:**
```python
app.config['SECRET_KEY'] = 'mi-clave-secreta-123'
```

**Seguro:**
```python
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-only-key')
```

### 5. Debug Mode en Producción
```powershell
Select-String -Path "app\*.py" -Pattern "debug.*=.*True" -Recurse
Select-String -Path "*.py" -Pattern "DEBUG.*=.*True" -Recurse
```

## Formato de Reporte de Seguridad

```
═══════════════════════════════════════════════════════════
              REPORTE DE SEGURIDAD - LOANSI
═══════════════════════════════════════════════════════════

🛡️ RESUMEN DE SEGURIDAD
- Vulnerabilidades CRÍTICAS: X
- Vulnerabilidades ALTAS: X
- Vulnerabilidades MEDIAS: X
- Configuraciones inseguras: X

═══════════════════════════════════════════════════════════
                 VULNERABILIDADES CRÍTICAS
═══════════════════════════════════════════════════════════

🔴 VULNERABILIDAD: SQL Injection
📍 UBICACIÓN: app/routes/admin_routes.py:47
⚠️  RIESGO: Un atacante puede ejecutar queries arbitrarios en la base de datos
📝 CÓDIGO VULNERABLE:
    cursor.execute(f"SELECT * FROM usuarios WHERE id = {user_id}")

🔧 REMEDIACIÓN:
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))

✅ VERIFICACIÓN:
    1. Buscar el archivo y línea
    2. Confirmar que usa parámetros (?)
    3. No debe haber f-strings ni concatenación en queries

═══════════════════════════════════════════════════════════
                    CSRF PROTECTION
═══════════════════════════════════════════════════════════

| Template | Tiene CSRF | Estado |
|----------|------------|--------|
| login.html | ✅ SÍ | OK |
| admin.html | ❌ NO | VULNERABLE |

═══════════════════════════════════════════════════════════
                 CONFIGURACIÓN DE SEGURIDAD
═══════════════════════════════════════════════════════════

| Setting | Estado | Recomendación |
|---------|--------|---------------|
| SECRET_KEY | ⚠️ Hardcoded | Usar variable de entorno |
| DEBUG | ✅ False | OK |
| CSRF_ENABLED | ✅ True | OK |

═══════════════════════════════════════════════════════════
                    SIGUIENTE PASO
═══════════════════════════════════════════════════════════

Para corregir las vulnerabilidades encontradas:
"Corrige la vulnerabilidad de SQL Injection en admin_routes.py:47"

El skill flask-developer aplicará las correcciones.
```

## Restricciones

- NO modificar ningún archivo
- NO ejecutar correcciones automáticamente
- SOLO analizar y reportar
- Proveer ubicación EXACTA
- Proveer código de remediación COPIABLE
- Clasificar por severidad según OWASP
