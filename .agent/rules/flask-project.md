---
trigger: always_on
---

## Reglas de Contexto para Proyecto Flask LOANSI

**Activación:** Siempre Activa (Always On)

### 1. Protocolo de Verificación de Cambios (VDO)

**MANDATORIO:** Después de cualquier modificación en cualquier archivo, **DEBES** ejecutar el flujo de trabajo de verificación:

```
/verify <ruta_del_archivo> <snippet_de_codigo_nuevo>
```
*El `<snippet_de_codigo_nuevo>` debe ser una cadena de texto corta y única que se haya añadido o modificado.*

### 2. Comandos de Terminal (Windows PowerShell)

**DEBES** usar la siguiente sintaxis para la interacción con el sistema de archivos y la ejecución de código:

| Tarea | Comando PowerShell |
| :--- | :--- |
| **Verificar Sintaxis Python** | `python -m py_compile <ruta_del_archivo>` |
| **Verificar Contenido (VDO)** | `Get-Content <ruta_del_archivo> | Select-String "<snippet_de_codigo_nuevo>"` |
| **Leer Contenido Completo** | `Get-Content <ruta_del_archivo>` |
| **Escribir/Sobrescribir** | `Set-Content <ruta_del_archivo> -Value "<contenido>"` |

### 3. Reglas de Código Obligatorias

1.  **CSRF:** Todos los formularios `POST` en templates HTML **DEBEN** incluir `{{ form.csrf_token }}`.
2.  **SQL Seguro:** **PROHIBIDO** usar f-strings o concatenación para construir consultas SQL. **SIEMPRE** usar parámetros: `cursor.execute("SELECT * FROM tabla WHERE id = ?", (valor,))`.
3.  **Estructura:** El punto de entrada es `run.py`. Las rutas están en `app/routes/`.
4.  **Templates:** Se espera herencia de templates (ej. `{% extends 'base.html' %}`).