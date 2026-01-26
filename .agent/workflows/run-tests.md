---
description: Ejecutar pruebas completas del sistema Flask
---

---
name: run-tests
description: Ejecutar pruebas completas del sistema Flask
---

# Workflow: Ejecutar Tests

## Pruebas Automáticas

### 1. Verificar Sintaxis de Todos los Archivos Python
```powershell
Get-ChildItem -Path "app" -Recurse -Filter "*.py" | ForEach-Object {
    python -m py_compile $_.FullName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: $($_.Name)"
    } else {
        Write-Host "ERROR: $($_.Name)"
    }
}
```

### 2. Verificar que el Servidor Arranca
```powershell
python -c "from app import create_app; app = create_app(); print('OK: App factory funciona')"
```

### 3. Iniciar Servidor y Probar Rutas
```powershell
# Iniciar
Start-Process python -ArgumentList "run.py" -PassThru
Start-Sleep -Seconds 5

# Probar rutas básicas
$rutas = @("/", "/login")
foreach ($ruta in $rutas) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:5000$ruta" -UseBasicParsing -TimeoutSec 5
        Write-Host "OK: $ruta - Status $($r.StatusCode)"
    } catch {
        Write-Host "ERROR: $ruta - $_"
    }
}

# Detener
Get-Process python | Stop-Process -Force
```

### 4. Si hay pytest instalado
```powershell
python -m pytest tests/ -v --tb=short
```

## Reporte de Resultados

```
## Resultados de Tests

| Test | Resultado |
|------|-----------|
| Sintaxis Python | ✅ OK / ❌ X errores |
| App Factory | ✅ OK / ❌ Error |
| Servidor inicia | ✅ OK / ❌ Error |
| Ruta / | ✅ 200 / ❌ Error |
| Ruta /login | ✅ 200 / ❌ Error |

### Errores encontrados:
[Lista de errores si hay]

### Siguiente paso:
[Qué hacer con los resultados]
```
