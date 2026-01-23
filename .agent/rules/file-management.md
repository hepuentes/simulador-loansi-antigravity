---
trigger: always_on
---

# Reglas de Gestión de Archivos

## CRÍTICO: Prevención de Duplicados

### Antes de Editar CUALQUIER Archivo
1. Ejecuta `find . -name "filename*" -type f` para identificar duplicados
2. Verifica cuál archivo está siendo usado buscando:
   - render_template() en rutas Python
   - import statements
   - {% extends %} y {% include %}
3. Si existen duplicados, PREGUNTA al usuario cuál editar

### Archivos a NUNCA Modificar
- Cualquier archivo con sufijo: _fixed, _backup, _old, _bak, _copy
- Archivos en directorios: /archive/, /backup/, /old/
- Archivos .pyc, __pycache__/

### Template Activo de Admin
El template admin activo es: `templates/admin.html`
NUNCA editar: admin_fixed.html, admin_backup.html, o similares

### Verificación de Rutas Flask
Antes de modificar un template, confirma su uso:
```python
# Buscar en routes/views:
grep -r "render_template.*admin" *.py
```

### Persistencia de Cambios
Después de CADA modificación:
1. Guarda explícitamente (Ctrl+S)
2. Verifica con: git status
3. Confirma contenido: git diff <archivo>
4. Si git no muestra cambios, los cambios NO se guardaron

### Rutas Absolutas Obligatorias
SIEMPRE usa rutas completas al referenciar archivos:
- ✅ templates/admin.html
- ❌ admin.html