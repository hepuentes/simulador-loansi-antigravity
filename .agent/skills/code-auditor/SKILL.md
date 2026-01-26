---
name: code-auditor
description: Audita código Python Flask para detectar bugs, code smells, violaciones de estilo y problemas de mantenibilidad. Usa cuando necesites revisar calidad de código o encontrar problemas potenciales. NO modifica código, solo REPORTA.
---

# Code Auditor Skill

## Cuándo se activa este skill
- Usuario pide revisar o auditar código
- Usuario dice "revisa", "analiza", "encuentra problemas"
- Antes de hacer merge de cambios grandes
- Comportamiento inesperado sin error claro

## ROL IMPORTANTE
Este skill SOLO analiza y reporta. NO hace modificaciones.
Si el usuario quiere que se corrijan los problemas, debe usar el skill flask-developer.

## Proceso de Auditoría

### Paso 1: Identificar archivos a revisar
```powershell
# Listar archivos Python
Get-ChildItem -Path "app" -Recurse -Filter "*.py" | Select-Object FullName
```

### Paso 2: Análisis por categorías

#### CRÍTICOS (bloquean funcionamiento):
- [ ] Variables usadas antes de definir
- [ ] Imports que no existen
- [ ] Sintaxis inválida
- [ ] Archivos referenciados que no existen

#### ALTOS (bugs probables):
- [ ] Excepciones silenciadas (except: pass)
- [ ] Queries SQL sin parámetros (SQL Injection)
- [ ] Formularios sin CSRF
- [ ] Archivos abiertos sin cerrar

#### MEDIOS (code smells):
- [ ] Funciones muy largas (>50 líneas)
- [ ] Código duplicado
- [ ] Nombres poco descriptivos
- [ ] Imports no utilizados

## Formato de Reporte OBLIGATORIO

Para CADA problema encontrado usar este formato exacto:

```
📍 UBICACIÓN: archivo.py:número_de_línea

🔴 SEVERIDAD: CRÍTICA | ALTA | MEDIA

📝 PROBLEMA: 
Descripción clara de qué está mal.
Código actual:
[mostrar línea problemática]

💡 SOLUCIÓN PROPUESTA:
Código corregido:
[mostrar cómo debería quedar]

✅ VERIFICACIÓN:
Comando o pasos para confirmar que se arregló
```

## Ejemplo de Reporte Completo

```
═══════════════════════════════════════════════════════════
              REPORTE DE AUDITORÍA DE CÓDIGO
═══════════════════════════════════════════════════════════

📊 RESUMEN
- Archivos analizados: 5
- Problemas críticos: 1
- Problemas altos: 2
- Problemas medios: 3

═══════════════════════════════════════════════════════════
                    PROBLEMAS CRÍTICOS
═══════════════════════════════════════════════════════════

📍 UBICACIÓN: app/routes/admin_routes.py:47

🔴 SEVERIDAD: CRÍTICA

📝 PROBLEMA: SQL Injection - Query concatenada con f-string
Código actual:
    cursor.execute(f"SELECT * FROM usuarios WHERE id = {user_id}")

💡 SOLUCIÓN PROPUESTA:
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))

✅ VERIFICACIÓN:
1. Abrir app/routes/admin_routes.py línea 47
2. Confirmar que usa parámetros (?)
3. Ejecutar: python -m py_compile app/routes/admin_routes.py

═══════════════════════════════════════════════════════════
                    PROBLEMAS ALTOS
═══════════════════════════════════════════════════════════

[Continuar con el mismo formato...]

═══════════════════════════════════════════════════════════
                    SIGUIENTE PASO
═══════════════════════════════════════════════════════════

Para corregir estos problemas, ejecutar:
"Corrige el problema de SQL Injection en admin_routes.py:47"

El skill flask-developer aplicará las correcciones.
```

## Checklist Específico para Flask

### Seguridad
- [ ] Todos los forms POST tienen csrf_token
- [ ] No hay SQL con f-strings o concatenación
- [ ] SECRET_KEY viene de variable de entorno
- [ ] Debug mode desactivado en config de producción

### Estructura
- [ ] Blueprints separados por funcionalidad
- [ ] Templates en carpeta correcta según blueprint
- [ ] Static files organizados (css/, js/)

### Errores
- [ ] Existe manejador para error 404
- [ ] Existe manejador para error 500
- [ ] Flash messages para feedback al usuario

## Restricciones

- NO modificar ningún archivo
- NO ejecutar correcciones
- SOLO analizar y reportar
- Proveer ubicación EXACTA (archivo:línea)
- Proveer código de solución COPIABLE
