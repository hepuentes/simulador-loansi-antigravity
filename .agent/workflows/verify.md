---
description: Flujo de trabajo esencial para la Verificación Determinista Obligatoria (VDO) post-modificación.
---

## Flujo de Trabajo: Verificación Obligatoria (/verify)

**Descripción:** Flujo de trabajo esencial para la Verificación Determinista Obligatoria (VDO) post-modificación.

**Uso:**
```
/verify <ruta_del_archivo> "<snippet_de_codigo_nuevo>"
```

**Pasos:**

1.  **Activación del Auditor:** Invoca la skill `code-auditor` con la ruta del archivo y el snippet de código.
    *   **Instrucción al Auditor:** "Audita el archivo `<ruta_del_archivo>` con el snippet de prueba `<snippet_de_codigo_nuevo>` siguiendo tus instrucciones de verificación de sintaxis y contenido."
2.  **Captura de Resultado:** Captura la salida completa de la ejecución de `code-auditor`.
3.  **Evaluación:**
    *   Si la salida del auditor indica un error de sintaxis o no contiene el snippet de código, reporta el fallo y **DETÉN** el flujo de trabajo.
    *   Si la salida del auditor es exitosa y contiene la prueba de `Select-String`, reporta el éxito de la verificación.
4.  **Prueba de Éxito:** La salida de este flujo de trabajo **DEBE** ser la salida completa generada por el `code-auditor`.