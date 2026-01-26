---
name: code-auditor
description: Audita código Python Flask para detectar bugs, code smells y problemas de calidad. Usa cuando el usuario pida revisar código, analizar calidad, o encontrar problemas. SOLO reporta, NO modifica código.
---

# Code Auditor Skill

## Cuándo se activa
- Usuario dice: "revisa", "audita", "analiza", "encuentra problemas", "revisa calidad"
- Revisión antes de deploy
- Comportamiento extraño sin error claro

## Rol Importante
Este skill SOLO analiza y reporta.
NO hace modificaciones al código.
Para corregir, el usuario debe pedir al flask-developer.

## Proceso de Auditoría

### Paso 1: Listar archivos a revisar
```powershell
Get-ChildItem -Path "app" -Recurse -Filter "*.py" | Select-Object FullName
```

### Paso 2: Buscar problemas comunes

#### SQL Injection (CRÍTICO)
```powershell
Select-String -Path "app\*.py" -Pattern "execute.*f[`"']" -Recurse
Select-String -Path "app\*.py" -Pattern "execute.*\+" -Recurse
```

#### CSRF faltante (CRÍTICO)
```powershell
Select-String -Path "templates\*.html" -Pattern "method=.POST" -Recurse
Select-String -Path "templates\*.html" -Pattern "csrf_token" -Recurse
```

#### Excepciones silenciadas (ALTO)
```powershell
Select-String -Path "app\*.py" -Pattern "except:[\s]*pass" -Recurse
```

#### Imports no usados (MEDIO)
Revisar manualmente los imports vs uso en el código.

### Paso 3: Generar Reporte

## Formato de Reporte OBLIGATORIO

```
═══════════════════════════════════════════════════════
              REPORTE DE AUDITORÍA
═══════════════════════════════════════════════════════

📊 RESUMEN
- Archivos analizados: X
- Problemas CRÍTICOS: X
- Problemas ALTOS: X
- Problemas MEDIOS: X

═══════════════════════════════════════════════════════
                 PROBLEMAS ENCONTRADOS
═══════════════════════════════════════════════════════

📍 UBICACIÓN: archivo.py:número_línea

🔴 SEVERIDAD: CRÍTICA | ALTA | MEDIA

📝 PROBLEMA: 
Descripción clara del problema.
Código actual:
    [código problemático]

💡 SOLUCIÓN:
Código corregido:
    [código correcto]

✅ VERIFICACIÓN:
Cómo confirmar que se arregló.

═══════════════════════════════════════════════════════
                    SIGUIENTE PASO
═══════════════════════════════════════════════════════

Para corregir estos problemas, decir:
"Corrige el problema de [descripción] en [archivo:línea]"
```

## Categorías de Severidad

### CRÍTICA (bloquea funcionamiento o seguridad)
- SQL Injection
- CSRF faltante en formularios POST
- Credenciales hardcodeadas
- Errores de sintaxis

### ALTA (bugs probables)
- Excepciones silenciadas
- Variables no definidas
- Imports que fallan
- Archivos referenciados que no existen

### MEDIA (code smells)
- Funciones muy largas (>50 líneas)
- Código duplicado
- Nombres poco descriptivos
- Imports no utilizados

## Restricciones
- NO modificar ningún archivo
- SOLO analizar y reportar
- Proveer ubicación EXACTA (archivo:línea)
- Proveer código de solución COPIABLE
