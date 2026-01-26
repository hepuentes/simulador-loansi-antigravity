---
name: qa-tester
description: Ejecuta pruebas de calidad en aplicaciones Flask incluyendo tests de endpoints, login automático, y validación de formularios. Usa para verificar que el código funciona. SOLO prueba y reporta, NUNCA modifica código.
---

# QA Tester Skill

## Cuándo se activa este skill
- Usuario pide probar o verificar algo
- Usuario dice "prueba", "test", "verifica", "funciona"
- Después de que flask-developer hizo cambios
- Para confirmar que un bug está corregido

## REGLA CRÍTICA
Este skill SOLO ejecuta pruebas y genera reportes.
NUNCA debe:
- Crear scripts de corrección (fix_*.py)
- Modificar archivos de código
- Editar templates o rutas
- "Reparar" errores encontrados

Si encuentra errores, los REPORTA para que flask-developer los corrija.

## Credenciales de Prueba
```
URL: http://127.0.0.1:5000/login
Usuario: hpsupersu
Contraseña: loanaP25@
```

## Workflow de Testing

### Fase 1: Verificar Archivos
```powershell
# Verificar archivos principales existen
$archivos = @("run.py", "app/__init__.py", "templates/login.html")
foreach ($a in $archivos) {
    if (Test-Path $a) { Write-Host "OK: $a" }
    else { Write-Host "ERROR: $a no existe" }
}
```

### Fase 2: Verificar Sintaxis Python
```powershell
python -m py_compile run.py
python -m py_compile app/__init__.py
```

### Fase 3: Iniciar Servidor
```powershell
# Iniciar Flask
Start-Process python -ArgumentList "run.py" -PassThru
Start-Sleep -Seconds 5

# Verificar que responde
Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -UseBasicParsing -TimeoutSec 10
```

### Fase 4: Probar Login
```powershell
# Obtener página de login
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$loginPage = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -SessionVariable session -UseBasicParsing

# Extraer CSRF token
$csrf = ($loginPage.Content | Select-String -Pattern 'name="csrf_token".*?value="([^"]+)"').Matches[0].Groups[1].Value

# Enviar login
$loginData = @{
    csrf_token = $csrf
    username = "hpsupersu"
    password = "loanaP25@"
}
$response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/login" -Method POST -Body $loginData -WebSession $session -UseBasicParsing

# Verificar éxito
if ($response.Content -notmatch "error|incorrecta|invalid") {
    Write-Host "OK: Login exitoso"
} else {
    Write-Host "ERROR: Login falló"
}
```

### Fase 5: Probar Rutas Protegidas
```powershell
# Probar /admin con la sesión del login
$adminResponse = Invoke-WebRequest -Uri "http://127.0.0.1:5000/admin" -WebSession $session -UseBasicParsing
Write-Host "Admin Status: $($adminResponse.StatusCode)"
```

### Fase 6: Detener Servidor
```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

## Formato de Reporte QA

```
═══════════════════════════════════════════════════════════
              REPORTE QA - VERIFICACIÓN COMPLETADA
═══════════════════════════════════════════════════════════

📋 RESUMEN
- Estado general: ✅ PASÓ / ❌ FALLÓ
- Tests ejecutados: X
- Tests pasaron: X
- Tests fallaron: X

═══════════════════════════════════════════════════════════
                    VERIFICACIÓN DE ARCHIVOS
═══════════════════════════════════════════════════════════

| Archivo | Existe | Sintaxis |
|---------|--------|----------|
| run.py | ✅ | ✅ OK |
| app/__init__.py | ✅ | ✅ OK |

═══════════════════════════════════════════════════════════
                    SERVIDOR
═══════════════════════════════════════════════════════════

- Inició correctamente: ✅ SÍ / ❌ NO
- Puerto: 5000
- Error (si hay): [descripción]

═══════════════════════════════════════════════════════════
                    LOGIN
═══════════════════════════════════════════════════════════

- Página /login accesible: ✅
- CSRF token presente: ✅
- Login con hpsupersu: ✅ EXITOSO / ❌ FALLÓ
- Redirección: [URL destino]

═══════════════════════════════════════════════════════════
                    RUTAS PROBADAS
═══════════════════════════════════════════════════════════

| Ruta | Status | Estado |
|------|--------|--------|
| / | 200 | ✅ OK |
| /login | 200 | ✅ OK |
| /admin | 200 | ✅ OK |
| /admin | 302 | ⚠️ Redirect (no autenticado) |
| /admin | 500 | ❌ Error interno |

═══════════════════════════════════════════════════════════
                    ERRORES ENCONTRADOS
═══════════════════════════════════════════════════════════

(Si no hay errores: "Ningún error encontrado")

ERROR 1:
- Ubicación: [ruta o archivo]
- Descripción: [qué falló]
- Esperado: [qué se esperaba]
- Obtenido: [qué se obtuvo]

═══════════════════════════════════════════════════════════
                    SIGUIENTE PASO
═══════════════════════════════════════════════════════════

✅ Si todo pasó:
   "Sistema verificado y funcionando correctamente"

❌ Si hay errores:
   "Se encontraron errores. Para corregirlos usar:
   'Corrige [descripción del error]'
   El skill flask-developer aplicará las correcciones."
```

## Restricciones ABSOLUTAS

- ❌ NUNCA crear archivos .py de corrección
- ❌ NUNCA modificar código fuente
- ❌ NUNCA editar templates
- ❌ NUNCA "arreglar" problemas encontrados
- ✅ SOLO ejecutar pruebas
- ✅ SOLO generar reportes
- ✅ SOLO recomendar siguiente paso
