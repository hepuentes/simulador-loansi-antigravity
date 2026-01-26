---
name: verify
description: Verificar que los cambios se aplicaron correctamente
---

# Workflow: Verificar Cambios

## Paso 1: Listar Archivos Modificados
Identificar qué archivos deberían haber cambiado.

## Paso 2: Verificar Cada Archivo

Para cada archivo modificado:

### Si es Python:
```powershell
# Verificar sintaxis
python -m py_compile ruta/archivo.py

# Verificar contenido
Get-Content "ruta/archivo.py" | Select-String "codigo_esperado"
```

### Si es HTML:
```powershell
Get-Content "templates/archivo.html" | Select-String "codigo_esperado"
```

### Si es JavaScript:
```powershell
Get-Content "static/js/archivo.js" | Select-String "codigo_esperado"
```

### Si es CSS:
```powershell
Get-Content "static/css/archivo.css" | Select-String "codigo_esperado"
```

## Paso 3: Reportar Estado

```
## Verificación de Cambios

| Archivo | Sintaxis | Contenido Guardado |
|---------|----------|-------------------|
| archivo1.py | ✅ OK | ✅ SÍ |
| archivo2.html | N/A | ✅ SÍ |
| archivo3.js | N/A | ❌ NO |

### Problemas Encontrados:
- archivo3.js: El cambio NO se guardó

### Acción Requerida:
1. Hacer clic en "Accept All" si no lo hiciste
2. Volver a aplicar el cambio en archivo3.js
```

## Paso 4: Si Hay Problemas

Si algún archivo NO tiene los cambios:
1. Verificar que el usuario hizo clic en "Accept All"
2. Volver a aplicar el cambio
3. Verificar de nuevo
