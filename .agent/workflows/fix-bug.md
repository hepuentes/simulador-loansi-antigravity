---
description: Flujo completo para corregir un bug con verificación paso a paso
---

---
name: fix-bug
description: Flujo completo para corregir un bug con verificación paso a paso
---

# Workflow: Corregir Bug

## Paso 1: Entender el Bug
Antes de tocar código, responder:
- ¿Cuál es el comportamiento actual?
- ¿Cuál es el comportamiento esperado?
- ¿Cómo se reproduce?
- ¿En qué archivo/línea está el problema?

## Paso 2: Localizar el Código
```powershell
# Buscar archivos relacionados
Select-String -Path "app\*.py" -Pattern "texto_relacionado" -Recurse
Select-String -Path "templates\*.html" -Pattern "texto_relacionado" -Recurse
```

## Paso 3: Leer el Archivo
Antes de modificar, leer el archivo completo para entender el contexto.

## Paso 4: Aplicar el Fix
- Modificar SOLO lo necesario
- NO cambiar código no relacionado
- Mantener el estilo existente

## Paso 5: Verificar Sintaxis
```powershell
python -m py_compile archivo_modificado.py
```
Si hay error, corregir antes de continuar.

## Paso 6: Verificar que el Cambio se Guardó
```powershell
Get-Content "archivo_modificado.py" | Select-String "codigo_nuevo"
```
Si no aparece, el cambio NO se guardó.

## Paso 7: Probar
```powershell
python run.py
```
Verificar que el servidor arranca sin errores.

## Paso 8: Reportar
Solo cuando TODO esté verificado:
```
## Bug Corregido

📍 Archivo: ruta/archivo.py:línea
📝 Problema: [descripción]
🔧 Solución: [qué se cambió]

### Verificaciones:
✅ Sintaxis OK
✅ Servidor arranca
✅ Cambio guardado en archivo
```
