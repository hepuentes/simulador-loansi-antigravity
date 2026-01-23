---
trigger: always_on
---

# Reglas de Gestión de Archivos

## CRÍTICO: Prevención de Duplicados

### Antes de Editar CUALQUIER Archivo
1. Busca archivos similares primero
2. Verifica cuál archivo está siendo usado en render_template()
3. Si existen duplicados, PREGUNTA al usuario cuál editar

### Archivos a NUNCA Modificar
- Cualquier archivo con sufijo: _fixed, _backup, _old, _bak, _copy
- Archivos en directorios: /archive/, /backup/, /old/
- Archivos .pyc, __pycache__/

### Template Activo de Admin
El template admin activo es: templates/admin/admin.html
NUNCA editar archivos con nombres similares si existen

## Verificación de Persistencia de Cambios (Windows PowerShell)

### Después de CADA modificación:
1. Verificar que el archivo existe:
```powershell
   Test-Path "ruta/al/archivo.html"
```

2. Ver contenido del archivo para confirmar cambios:
```powershell
   Get-Content "ruta/al/archivo.html" | Select-String "texto_nuevo"
```

3. Ver fecha de modificación:
```powershell
   Get-Item "ruta/al/archivo.html" | Select-Object LastWriteTime
```

## Credenciales de Prueba
Para pruebas que requieran login, usar las credenciales definidas en:
`.agent/rules/test-credentials.md`

## Rutas del Proyecto
- templates/admin/admin.html
- app/routes/admin_routes.py
- static/css/theme.css