---
description: Flujo de trabajo estructurado para la corrección de errores, asegurando la Verificación Determinista Obligatoria (VDO).
---

## Flujo de Trabajo: Corregir un Error (/fix-bug)

**Descripción:** Flujo de trabajo estructurado para la corrección de errores, asegurando la Verificación Determinista Obligatoria (VDO).

**Pasos:**

1.  **Análisis:** Analiza el error reportado y el código fuente. Determina la línea o bloque de código que necesita ser modificado.
2.  **Plan de Corrección:** Genera un plan de acción detallado, especificando el archivo (`<ruta_del_archivo>`), el cambio exacto a realizar y el **`<snippet_de_codigo_nuevo>`** para la verificación.
3.  **Ejecución:** Aplica el cambio al archivo.
4.  **Verificación:** **MANDATORIAMENTE**, invoca el flujo de trabajo de verificación:
    ```
    /verify <ruta_del_archivo> "<snippet_de_codigo_nuevo>"
    ```
5.  **Reporte:** Si `/verify` es exitoso, reporta la corrección del error, incluyendo la salida de la verificación. Si falla, regresa al paso 1.