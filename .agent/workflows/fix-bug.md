---
name: fix-bug
description: Flujo paso a paso para corregir un bug con verificación
---

# Workflow: Corregir Bug

## Paso 1: Entender el Problema
Antes de tocar código:
- ¿Qué debería pasar?
- ¿Qué está pasando?
- ¿En qué archivo está el problema?

## Paso 2: Localizar el Código
```powershell
# Buscar texto relacionado
Select-String -Path "app\*.py" -Pattern "texto_relacionado" -Recurse
Select-String -Path "templates\*.html" -Pattern "texto_relacionado" -Recurse
Select-String -Path "static\js\*.js" -Pattern "texto_relacionado" -Recurse
```

## Paso 3: Leer el Archivo
Leer el archivo completo antes de modificar.

## Paso 4: Aplicar el Fix
Modificar SOLO lo necesario.

## Paso 5: Verificar Sintaxis (si es Python)
```powershell
python -m py_compile archivo.py
```

## Paso 6: Verificar que se Guardó
```powershell
Get-Content "archivo" | Select-String "codigo_nuevo"
```

## Paso 7: Instrucciones para el Usuario
```
## Bug Corregido

📍 Archivo: ruta/archivo
📝 Cambio: descripción

### Para probar:
1. Detener servidor: Ctrl+C
2. Iniciar servidor: python run.py
3. Abrir: http://127.0.0.1:5000/ruta
4. Refrescar: Ctrl+Shift+R
```
