---
trigger: always_on
---

# Credenciales de Prueba - Desarrollo Local

## IMPORTANTE
Este archivo contiene credenciales SOLO para pruebas en desarrollo local.
NUNCA subir a producción con estas credenciales.

## Acceso al Sistema

### URL Base
```
http://127.0.0.1:5000
```

### Página de Login
```
http://127.0.0.1:5000/login
```

### Credenciales de Superusuario (Acceso Total)
```
Usuario: hpsupersu
Contraseña: loanaP25@
```

## Campos del Formulario de Login
- Campo usuario: name="username" o name="usuario"
- Campo contraseña: name="password" o name="contrasena"
- Botón submit: type="submit"

## Rutas Principales Post-Login
Después de login exitoso, según el rol se redirige a:
- Admin: /admin o /dashboard/admin
- Asesor: /asesor o /dashboard/asesor
- Otros roles: verificar en app/routes/auth.py

## Verificación de Login Exitoso
- Status code 200 o 302 (redirect)
- NO aparece mensaje "error" o "incorrecta" en la respuesta
- Aparece contenido del dashboard o navbar del usuario