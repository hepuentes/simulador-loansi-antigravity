---
name: security-analyzer
description: Analiza vulnerabilidades de seguridad en aplicaciones Flask incluyendo SQL injection, XSS, CSRF bypass y configuraciones inseguras. Usa para auditoría de seguridad. SOLO reporta, NO modifica código.
---

# Security Analyzer Skill

## Cuándo se activa
- Usuario dice: "seguridad", "vulnerabilidades", "OWASP", "analiza seguridad"
- Antes de deploy a producción
- Después de agregar autenticación

## Rol Importante
Este skill SOLO detecta y reporta vulnerabilidades.
NO hace correcciones automáticas.
Para corregir, el usuario debe pedir al flask-developer.

## Análisis de Seguridad

### 1. SQL Injection
```powershell
# Buscar queries inseguras
Select-String -Path "app\*.py" -Pattern "execute.*f[`"']" -Recurse
Select-String -Path "app\*.py" -Pattern "execute.*\+" -Recurse
Select-String -Path "app\*.py" -Pattern "execute.*%" -Recurse
```

**Vulnerable:**
```python
db.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

**Seguro:**
```python
db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### 2. Cross-Site Scripting (XSS)
```powershell
# Buscar bypass de autoescape
Select-String -Path "templates\*.html" -Pattern "\|safe" -Recurse
Select-String -Path "app\*.py" -Pattern "Markup\(" -Recurse
```

**Regla:** Solo usar `|safe` con contenido controlado, NUNCA con input de usuario.

### 3. CSRF Protection
```powershell
# Verificar forms POST tienen token
Select-String -Path "templates\*.html" -Pattern "method=.POST" -Recurse
# Comparar con
Select-String -Path "templates\*.html" -Pattern "csrf_token" -Recurse
```

### 4. Secretos Expuestos
```powershell
Select-String -Path "*.py" -Pattern "SECRET_KEY.*=.*[`"'][^`"']+[`"']" -Recurse
Select-String -Path "*.py" -Pattern "PASSWORD.*=.*[`"']" -Recurse
```

### 5. Debug Mode
```powershell
Select-String -Path "*.py" -Pattern "debug.*=.*True" -Recurse
```

## Formato de Reporte de Seguridad

```
═══════════════════════════════════════════════════════
           REPORTE DE SEGURIDAD - LOANSI
═══════════════════════════════════════════════════════

🛡️ RESUMEN
- Vulnerabilidades CRÍTICAS: X
- Vulnerabilidades ALTAS: X
- Vulnerabilidades MEDIAS: X

═══════════════════════════════════════════════════════
              VULNERABILIDADES CRÍTICAS
═══════════════════════════════════════════════════════

🔴 VULNERABILIDAD: SQL Injection
📍 UBICACIÓN: app/routes/admin_routes.py:47
⚠️  RIESGO: Atacante puede ejecutar queries arbitrarios

📝 CÓDIGO VULNERABLE:
    cursor.execute(f"SELECT * FROM usuarios WHERE id = {user_id}")

🔧 REMEDIACIÓN:
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))

✅ VERIFICACIÓN:
    Select-String -Path "app\routes\admin_routes.py" -Pattern "execute.*\?"

═══════════════════════════════════════════════════════
                  CSRF PROTECTION
═══════════════════════════════════════════════════════

| Template | Tiene CSRF | Estado |
|----------|------------|--------|
| login.html | ✅ SÍ | OK |
| admin.html | ❌ NO | VULNERABLE |

═══════════════════════════════════════════════════════
                   SIGUIENTE PASO
═══════════════════════════════════════════════════════

Para corregir, decir:
"Corrige la vulnerabilidad de SQL Injection en admin_routes.py:47"
```

## Restricciones
- NO modificar ningún archivo
- SOLO detectar y reportar
- Clasificar por severidad OWASP
- Proveer código de remediación COPIABLE
