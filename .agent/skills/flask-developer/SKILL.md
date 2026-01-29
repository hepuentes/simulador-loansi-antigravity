---
name: flask-developer
description: Experto en desarrollo Flask en Windows/PowerShell. Su proceso incluye la Verificación Determinista Obligatoria (VDO) para garantizar la aplicación real de los cambios.
license: MIT
metadata:
  version: "2.0"
---

# Flask Developer Skill - Protocolo de Ejecución (VDO)

## 1. Protocolo de Modificación de Archivos (VDO)

Cuando se te solicite implementar una nueva característica o modificar el código, **DEBES** seguir este flujo estricto:

1.  **Análisis:** Lee el archivo completo (`Get-Content`) para entender el contexto.
2.  **Planificación:** Crea un plan de implementación detallado, identificando el archivo, el cambio exacto y el **`snippet_de_codigo_nuevo`** que servirá como prueba de verificación.
3.  **Modificación:** Aplica el cambio.
4.  **Verificación Obligatoria:** **INMEDIATAMENTE** después de la modificación, invoca el flujo de trabajo de verificación:
    ```
    /verify <ruta_del_archivo> "<snippet_de_codigo_nuevo>"
    ```
5.  **Reporte Final:** **SOLO** si el flujo `/verify` es exitoso, reporta la tarea como completada. Tu reporte **DEBE** incluir la salida de `Get-Content | Select-String` proporcionada por `/verify`.

## 2. Patrones de Código OBLIGATORIOS

*   **CSRF:** Asegúrate de que todos los formularios POST tengan protección CSRF.
*   **SQL:** **SIEMPRE** usa consultas parametrizadas para prevenir inyección SQL.

## 3. Formato de Reporte de Éxito

Tu reporte final al usuario **DEBE** incluir la siguiente estructura para demostrar la VDO:

```markdown
## Tarea Completada: [Descripción de la Tarea]

📍 **ARCHIVO MODIFICADO:** `<ruta_del_archivo>`
📝 **CAMBIO APLICADO:** [Descripción del cambio]

### ✅ PRUEBA DE VERIFICACIÓN (VDO)

**Resultado de `/verify <ruta_del_archivo> "<snippet_de_codigo_nuevo>"`:**

```powershell
# Salida de python -m py_compile (si es .py)
# Salida de Get-Content <ruta_del_archivo> | Select-String "<snippet_de_codigo_nuevo>"
```
*La salida anterior confirma que el código fue escrito correctamente en el archivo.*

**Instrucciones para el Usuario:**
1. Detener el servidor (Ctrl+C) e iniciar con `python run.py`.
2. Probar manualmente en `http://127.0.0.1:5000`.
```