"""
PERMISOS.PY - Sistema de Control de Acceso Basado en Roles (RBAC)
==================================================================

Este módulo proporciona:
1. Verificación de permisos por rol
2. Verificación de permisos específicos por usuario
3. Decoradores para proteger rutas
4. Helpers para templates Jinja2
5. API endpoints para gestión de permisos

Sistema híbrido: Rol base + permisos específicos por usuario

Author: Sistema Loansi
Date: 2025-12-31
Version: 1.1 - Mejorado 2025-01-06 (validación permisos protegidos)
"""

from functools import wraps
from flask import session, abort, jsonify, request, redirect, url_for
import sqlite3
import json
import time
from pathlib import Path

# Ruta de la base de datos
DB_PATH = Path(__file__).parent / 'loansi.db'


# ============================================================================
# CONSTANTES GLOBALES
# ============================================================================

# Permisos que NUNCA se pueden quitar a usuarios con rol admin
# Estos permisos son críticos para evitar bloqueo del sistema
PERMISOS_PROTEGIDOS_ADMIN = {
    'usr_permisos',   # Gestionar permisos (evita bloqueo total)
    'usr_ver',        # Ver usuarios
    'usr_crear',      # Crear usuarios
    'usr_editar',     # Editar usuarios
    'usr_eliminar',   # Eliminar usuarios
    'usr_password',   # Cambiar contraseñas
    # Permisos de configuración de scoring (críticos para admin panel)
    'cfg_sco_ver',    # Ver configuración de scoring
    'cfg_sco_editar'  # Editar configuración de scoring
}


# ============================================================================
# CONEXIÓN A BASE DE DATOS
# ============================================================================

def _conectar_db():
    """Conecta a la base de datos SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================================
# CACHE DE PERMISOS (Optimización de performance)
# ============================================================================

_PERMISOS_CACHE = {}
_CACHE_TTL = 300  # 5 minutos


def invalidar_cache_permisos(usuario_id=None):
    """
    Invalida el cache de permisos.

    Args:
        usuario_id: Si se especifica, solo invalida el cache de ese usuario.
                   Si es None, invalida todo el cache.
    """
    global _PERMISOS_CACHE

    if usuario_id:
        # Invalidar solo permisos del usuario específico
        keys_to_remove = [k for k in _PERMISOS_CACHE if k.startswith(f"user_{usuario_id}_")]
        for key in keys_to_remove:
            del _PERMISOS_CACHE[key]
        print(f"🔄 Cache de permisos invalidado para usuario {usuario_id}")
    else:
        # Invalidar todo el cache
        _PERMISOS_CACHE = {}
        print("🔄 Cache de permisos completamente invalidado")


def _obtener_permisos_rol(rol):
    """
    Obtiene los permisos de un rol desde la base de datos.
    Usa cache para optimizar consultas repetidas.

    Args:
        rol (str): Nombre del rol

    Returns:
        list: Lista de códigos de permisos
    """
    cache_key = f"rol_{rol}"
    now = time.time()

    # Verificar cache
    if cache_key in _PERMISOS_CACHE:
        cached_data, timestamp = _PERMISOS_CACHE[cache_key]
        if now - timestamp < _CACHE_TTL:
            return cached_data

    # Consultar base de datos
    conn = _conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.codigo
        FROM permisos p
        INNER JOIN rol_permisos rp ON p.id = rp.permiso_id
        WHERE rp.rol = ? AND p.activo = 1
    """, (rol,))

    permisos = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Guardar en cache
    _PERMISOS_CACHE[cache_key] = (permisos, now)

    return permisos


def _obtener_permisos_usuario_especificos(usuario_id):
    """
    Obtiene los permisos específicos (agregados/quitados) de un usuario.

    Args:
        usuario_id (int): ID del usuario

    Returns:
        dict: {'agregar': [...], 'quitar': [...]}
    """
    cache_key = f"user_{usuario_id}_especificos"
    now = time.time()

    # Verificar cache
    if cache_key in _PERMISOS_CACHE:
        cached_data, timestamp = _PERMISOS_CACHE[cache_key]
        if now - timestamp < _CACHE_TTL:
            return cached_data

    conn = _conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.codigo, up.tipo
        FROM usuario_permisos up
        INNER JOIN permisos p ON up.permiso_id = p.id
        WHERE up.usuario_id = ? AND p.activo = 1
    """, (usuario_id,))

    resultado = {'agregar': [], 'quitar': []}
    for row in cursor.fetchall():
        if row[1] == 'agregar':
            resultado['agregar'].append(row[0])
        else:
            resultado['quitar'].append(row[0])

    conn.close()

    # Guardar en cache
    _PERMISOS_CACHE[cache_key] = (resultado, now)

    return resultado


def obtener_permisos_usuario_completos(username):
    """
    Obtiene todos los permisos efectivos de un usuario.
    Combina: permisos del rol + permisos agregados - permisos quitados

    NOTA: Algunos permisos son PROTEGIDOS y no se pueden quitar a admin.

    Args:
        username (str): Username del usuario

    Returns:
        list: Lista de códigos de permisos efectivos
    """
    conn = _conectar_db()
    cursor = conn.cursor()

    # Obtener rol e id del usuario
    cursor.execute("""
        SELECT id, rol FROM usuarios
        WHERE username = ? AND activo = 1
    """, (username,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return []

    usuario_id, rol = row[0], row[1]
    conn.close()

    # Para admin: obtener TODOS los permisos como base
    if rol == 'admin':
        conn = _conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo FROM permisos WHERE activo = 1")
        permisos_base = set(r[0] for r in cursor.fetchall())
        conn.close()
    else:
        # Para otros roles: obtener permisos del rol
        permisos_base = set(_obtener_permisos_rol(rol))

    # Obtener permisos específicos del usuario
    especificos = _obtener_permisos_usuario_especificos(usuario_id)

    # Combinar: base + agregados - quitados
    permisos_finales = permisos_base.copy()
    permisos_finales.update(especificos['agregar'])
    permisos_finales -= set(especificos['quitar'])

    # IMPORTANTE: Para admin, restaurar permisos protegidos
    if rol == 'admin':
        permisos_finales.update(PERMISOS_PROTEGIDOS_ADMIN)

    return list(permisos_finales)


# ============================================================================
# FUNCIONES DE VERIFICACIÓN
# ============================================================================

def tiene_permiso(permiso_requerido):
    """
    Verifica si el usuario actual tiene un permiso específico.

    Args:
        permiso_requerido (str): Código del permiso (ej: 'com_aprobar')

    Returns:
        bool: True si tiene el permiso
    """
    if not session.get('autorizado'):
        return False

    username = session.get('username')
    if not username:
        return False

    # Verificar permisos completos (incluye protegidos para admin)
    permisos = obtener_permisos_usuario_completos(username)
    return permiso_requerido in permisos

def tiene_alguno_de(permisos_requeridos):
    """
    Verifica si el usuario tiene AL MENOS UNO de los permisos.

    Args:
        permisos_requeridos (list): Lista de códigos de permisos

    Returns:
        bool: True si tiene al menos uno
    """
    if not session.get('autorizado'):
        return False

    username = session.get('username')
    if not username:
        return False

    permisos_usuario = obtener_permisos_usuario_completos(username)
    return any(p in permisos_usuario for p in permisos_requeridos)


def tiene_todos(permisos_requeridos):
    """
    Verifica si el usuario tiene TODOS los permisos.

    Args:
        permisos_requeridos (list): Lista de códigos de permisos

    Returns:
        bool: True si tiene todos
    """
    if not session.get('autorizado'):
        return False

    username = session.get('username')
    if not username:
        return False

    permisos_usuario = obtener_permisos_usuario_completos(username)
    return all(p in permisos_usuario for p in permisos_requeridos)

def obtener_permisos_usuario_actual():
    """
    Obtiene todos los permisos del usuario actual.

    Returns:
        list: Lista de códigos de permisos
    """
    if not session.get('autorizado'):
        return []

    username = session.get('username')
    if not username:
        return []

    return obtener_permisos_usuario_completos(username)


def es_permiso_protegido(permiso_codigo, rol_usuario):
    """
    Verifica si un permiso es protegido para un rol específico.

    Args:
        permiso_codigo (str): Código del permiso
        rol_usuario (str): Rol del usuario

    Returns:
        bool: True si el permiso es protegido para ese rol
    """
    if rol_usuario == 'admin':
        return permiso_codigo in PERMISOS_PROTEGIDOS_ADMIN
    return False


# ============================================================================
# DECORADORES PARA RUTAS
# ============================================================================

def requiere_permiso(permiso):
    """
    Decorador que protege una ruta requiriendo un permiso específico.

    Uso:
        @app.route('/admin/scoring')
        @requiere_permiso('cfg_sco_editar')
        def editar_scoring():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('autorizado'):
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'No autorizado', 'code': 'AUTH_REQUIRED'}), 401
                return redirect(url_for('login'))

            if not tiene_permiso(permiso):
                _registrar_acceso_denegado(permiso)
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'Permiso denegado',
                        'code': 'PERMISSION_DENIED',
                        'required': permiso
                    }), 403
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def requiere_alguno_de(*permisos):
    """
    Decorador que requiere AL MENOS UNO de los permisos listados.

    Uso:
        @app.route('/reportes')
        @requiere_alguno_de('rep_metricas_propio', 'rep_metricas_equipo', 'rep_metricas_global')
        def ver_reportes():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('autorizado'):
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'No autorizado'}), 401
                return redirect(url_for('login'))

            if not tiene_alguno_de(permisos):
                _registrar_acceso_denegado(list(permisos))
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'Permiso denegado',
                        'code': 'PERMISSION_DENIED',
                        'required_any': permisos
                    }), 403
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def requiere_todos(*permisos):
    """
    Decorador que requiere TODOS los permisos listados.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('autorizado'):
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({'error': 'No autorizado'}), 401
                return redirect(url_for('login'))

            if not tiene_todos(permisos):
                _registrar_acceso_denegado(list(permisos))
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'Permiso denegado',
                        'code': 'PERMISSION_DENIED',
                        'required_all': permisos
                    }), 403
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def requiere_rol(*roles_permitidos):
    """
    Decorador que requiere uno de los roles específicos.

    Uso:
        @app.route('/comite')
        @requiere_rol('comite_credito', 'admin')
        def panel_comite():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('autorizado'):
                if request.is_json:
                    return jsonify({'error': 'No autorizado'}), 401
                return redirect(url_for('login'))

            rol_actual = session.get('rol', 'asesor')
            if rol_actual not in roles_permitidos:
                _registrar_acceso_denegado(f"rol:{list(roles_permitidos)}")
                if request.is_json:
                    return jsonify({
                        'error': 'Rol no autorizado',
                        'required_roles': roles_permitidos
                    }), 403
                abort(403)

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# AUDITORÍA DE ACCESOS
# ============================================================================

def _registrar_acceso_denegado(permiso_requerido):
    """Registra intentos de acceso denegado para auditoría"""
    try:
        conn = _conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO auditoria (usuario, accion, tabla_afectada, datos_nuevos, ip_address)
            VALUES (?, 'ACCESO_DENEGADO', 'permisos', ?, ?)
        """, (
            session.get('username', 'anónimo'),
            json.dumps({
                'permiso_requerido': str(permiso_requerido),
                'ruta': request.path,
                'metodo': request.method,
                'rol_usuario': session.get('rol', 'sin_rol')
            }),
            request.remote_addr
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error registrando acceso denegado: {e}")


def registrar_accion_permiso(accion, detalles):
    """Registra acciones relacionadas con permisos para auditoría"""
    try:
        conn = _conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO auditoria (usuario, accion, tabla_afectada, datos_nuevos, ip_address)
            VALUES (?, ?, 'permisos', ?, ?)
        """, (
            session.get('username', 'sistema'),
            accion,
            json.dumps(detalles),
            request.remote_addr if request else None
        ))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Error registrando acción: {e}")


# ============================================================================
# GESTIÓN DE PERMISOS POR USUARIO
# ============================================================================

def agregar_permiso_usuario(usuario_id, permiso_codigo, motivo=None):
    """
     Agrega un permiso específico a un usuario.

    IMPORTANTE: Incluye control anti-auto-permisos para evitar que un usuario
    modifique sus propios permisos.

    Args:
        usuario_id (int): ID del usuario
        permiso_codigo (str): Código del permiso
        motivo (str): Razón de la asignación

    Returns:
        dict: {'success': bool, 'message': str}
    """
    # ═══════════════════════════════════════════════════════════════════════
    # CONTROL ANTI-AUTO-PERMISOS: Verificar que no se edite a sí mismo
    # ═══════════════════════════════════════════════════════════════════════
    current_username = session.get('username')
    if current_username:
        conn_check = _conectar_db()
        cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT id FROM usuarios WHERE username = ?", (current_username,))
        current_user_row = cursor_check.fetchone()
        conn_check.close()

        if current_user_row and current_user_row[0] == usuario_id:
            print(f"🚫 BLOQUEADO: Usuario {current_username} intentó agregar permiso a sí mismo")
            return {
                'success': False,
                'message': 'No puedes modificar tus propios permisos. Solicita a otro administrador.',
                'auto_permiso_bloqueado': True
            }
    # ═══════════════════════════════════════════════════════════════════════
    conn = _conectar_db()
    cursor = conn.cursor()

    try:
        # Obtener ID del permiso
        # Obtener ID del permiso
        cursor.execute("SELECT id FROM permisos WHERE codigo = ? AND activo = 1", (permiso_codigo,))
        permiso = cursor.fetchone()

        if not permiso:
            return {'success': False, 'message': f'Permiso "{permiso_codigo}" no existe'}

        permiso_id = permiso[0]

        # Verificar si ya tiene el permiso asignado
        cursor.execute("""
            SELECT id, tipo FROM usuario_permisos
            WHERE usuario_id = ? AND permiso_id = ?
        """, (usuario_id, permiso_id))

        existente = cursor.fetchone()

        if existente:
            if existente[1] == 'agregar':
                return {'success': False, 'message': 'El usuario ya tiene este permiso'}
            else:
                # Cambiar de 'quitar' a 'agregar'
                cursor.execute("""
                    UPDATE usuario_permisos
                    SET tipo = 'agregar',
                        asignado_por = ?,
                        motivo = ?,
                        fecha_asignacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (session.get('username'), motivo, existente[0]))
        else:
            cursor.execute("""
                INSERT INTO usuario_permisos (usuario_id, permiso_id, tipo, asignado_por, motivo)
                VALUES (?, ?, 'agregar', ?, ?)
            """, (usuario_id, permiso_id, session.get('username'), motivo))

        conn.commit()

        # Invalidar cache
        invalidar_cache_permisos(usuario_id)

        # Registrar en auditoría
        registrar_accion_permiso('PERMISO_AGREGADO', {
            'usuario_id': usuario_id,
            'permiso': permiso_codigo,
            'motivo': motivo
        })

        return {'success': True, 'message': 'Permiso agregado correctamente'}

    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        conn.close()


def quitar_permiso_usuario(usuario_id, permiso_codigo, motivo=None):
    """
    Quita un permiso específico a un usuario (override del rol).

    IMPORTANTE:
    1. Incluye control anti-auto-permisos
    2. Valida permisos protegidos antes de guardar

    Args:
        usuario_id (int): ID del usuario
        permiso_codigo (str): Código del permiso
        motivo (str): Razón de la revocación

    Returns:
        dict: {'success': bool, 'message': str, 'protegido': bool (opcional)}
    """
    # ═══════════════════════════════════════════════════════════════════════
    # CONTROL ANTI-AUTO-PERMISOS: Verificar que no se edite a sí mismo
    # ═══════════════════════════════════════════════════════════════════════
    current_username = session.get('username')
    if current_username:
        conn_check = _conectar_db()
        cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT id FROM usuarios WHERE username = ?", (current_username,))
        current_user_row = cursor_check.fetchone()
        conn_check.close()

        if current_user_row and current_user_row[0] == usuario_id:
            print(f"🚫 BLOQUEADO: Usuario {current_username} intentó quitar permiso a sí mismo")
            return {
                'success': False,
                'message': 'No puedes modificar tus propios permisos. Solicita a otro administrador.',
                'auto_permiso_bloqueado': True
            }
    # ═══════════════════════════════════════════════════════════════════════
    conn = _conectar_db()
    cursor = conn.cursor()

    try:
        # Verificar si el usuario es admin y el permiso es protegido
        cursor.execute("SELECT rol FROM usuarios WHERE id = ?", (usuario_id,))
        user_row = cursor.fetchone()

        if not user_row:
            return {'success': False, 'message': 'Usuario no encontrado'}

        rol_usuario = user_row[0]

        # Validar permisos protegidos ANTES de guardar
        if rol_usuario == 'admin' and permiso_codigo in PERMISOS_PROTEGIDOS_ADMIN:
            return {
                'success': False,
                'message': f'El permiso "{permiso_codigo}" es PROTEGIDO y no se puede quitar a usuarios admin. '
                           f'Esto evita bloqueos del sistema.',
                'protegido': True
            }

        # Obtener ID del permiso
        cursor.execute("SELECT id FROM permisos WHERE codigo = ? AND activo = 1", (permiso_codigo,))
        permiso = cursor.fetchone()

        if not permiso:
            return {'success': False, 'message': f'Permiso "{permiso_codigo}" no existe'}

        permiso_id = permiso[0]

        # Verificar si ya tiene registro
        cursor.execute("""
            SELECT id, tipo FROM usuario_permisos
            WHERE usuario_id = ? AND permiso_id = ?
        """, (usuario_id, permiso_id))

        existente = cursor.fetchone()

        if existente:
            if existente[1] == 'quitar':
                return {'success': False, 'message': 'El permiso ya está quitado'}
            else:
                # Cambiar de 'agregar' a 'quitar'
                cursor.execute("""
                    UPDATE usuario_permisos
                    SET tipo = 'quitar',
                        asignado_por = ?,
                        motivo = ?,
                        fecha_asignacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (session.get('username'), motivo, existente[0]))
        else:
            cursor.execute("""
                INSERT INTO usuario_permisos (usuario_id, permiso_id, tipo, asignado_por, motivo)
                VALUES (?, ?, 'quitar', ?, ?)
            """, (usuario_id, permiso_id, session.get('username'), motivo))

        conn.commit()

        # Invalidar cache
        invalidar_cache_permisos(usuario_id)

        # Registrar en auditoría
        registrar_accion_permiso('PERMISO_QUITADO', {
            'usuario_id': usuario_id,
            'permiso': permiso_codigo,
            'motivo': motivo
        })

        return {'success': True, 'message': 'Permiso quitado correctamente'}

    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        conn.close()


def restaurar_permiso_usuario(usuario_id, permiso_codigo):
    """
    Elimina un override específico, restaurando el permiso por defecto del rol.

    Args:
        usuario_id (int): ID del usuario
        permiso_codigo (str): Código del permiso

    Returns:
        dict: {'success': bool, 'message': str}
    """
    # ═══════════════════════════════════════════════════════════════════════
    # CONTROL ANTI-AUTO-PERMISOS
    # ═══════════════════════════════════════════════════════════════════════
    current_username = session.get('username')
    if current_username:
        conn_check = _conectar_db()
        cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT id FROM usuarios WHERE username = ?", (current_username,))
        current_user_row = cursor_check.fetchone()
        conn_check.close()

        if current_user_row and current_user_row[0] == usuario_id:
            print(f"🚫 BLOQUEADO: Usuario {current_username} intentó restaurar permiso propio")
            return {
                'success': False,
                'message': 'No puedes modificar tus propios permisos. Solicita a otro administrador.',
                'auto_permiso_bloqueado': True
            }
    # ═══════════════════════════════════════════════════════════════════════
    conn = _conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM usuario_permisos
            WHERE usuario_id = ?
            AND permiso_id = (SELECT id FROM permisos WHERE codigo = ?)
        """, (usuario_id, permiso_codigo))

        if cursor.rowcount == 0:
            return {'success': False, 'message': 'No hay override para restaurar'}

        conn.commit()

        # Invalidar cache
        invalidar_cache_permisos(usuario_id)

        # Registrar en auditoría
        registrar_accion_permiso('PERMISO_RESTAURADO', {
            'usuario_id': usuario_id,
            'permiso': permiso_codigo
        })

        return {'success': True, 'message': 'Permiso restaurado a valor del rol'}

    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        conn.close()


def limpiar_overrides_invalidos():
    """
    Elimina overrides de permisos protegidos que no tienen efecto.
    Esto limpia la BD de registros inútiles que causan confusión.

    Returns:
        dict: {'success': bool, 'eliminados': int, 'detalles': list}
    """
    conn = _conectar_db()
    cursor = conn.cursor()

    try:
        # Buscar overrides inválidos (permisos protegidos quitados a admins)
        cursor.execute("""
            SELECT up.id, u.username, p.codigo
            FROM usuario_permisos up
            JOIN usuarios u ON up.usuario_id = u.id
            JOIN permisos p ON up.permiso_id = p.id
            WHERE u.rol = 'admin'
            AND up.tipo = 'quitar'
            AND p.codigo IN (?, ?, ?, ?, ?, ?)
        """, tuple(PERMISOS_PROTEGIDOS_ADMIN))

        invalidos = cursor.fetchall()
        detalles = []

        for row in invalidos:
            detalles.append({
                'id': row[0],
                'username': row[1],
                'permiso': row[2]
            })

        if invalidos:
            # Eliminar los registros inválidos
            ids_eliminar = [row[0] for row in invalidos]
            placeholders = ','.join('?' * len(ids_eliminar))
            cursor.execute(f"DELETE FROM usuario_permisos WHERE id IN ({placeholders})", ids_eliminar)
            conn.commit()

            # Invalidar cache completo
            invalidar_cache_permisos()

            # Registrar en auditoría
            registrar_accion_permiso('LIMPIEZA_OVERRIDES', {
                'eliminados': len(invalidos),
                'detalles': detalles
            })

            print(f"🧹 Limpieza completada: {len(invalidos)} overrides inválidos eliminados")

        return {
            'success': True,
            'eliminados': len(invalidos),
            'detalles': detalles
        }

    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e), 'eliminados': 0}
    finally:
        conn.close()


# ============================================================================
# GESTIÓN DE PERMISOS POR ROL
# ============================================================================

def obtener_permisos_rol(rol):
    """
    Obtiene los permisos asignados a un rol.

    Returns:
        list: Lista de diccionarios con info de permisos
    """
    conn = _conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, p.codigo, p.nombre, p.descripcion, p.modulo
        FROM permisos p
        INNER JOIN rol_permisos rp ON p.id = rp.permiso_id
        WHERE rp.rol = ? AND p.activo = 1
        ORDER BY p.modulo, p.nombre
    """, (rol,))

    permisos = []
    for row in cursor.fetchall():
        permisos.append({
            'id': row[0],
            'codigo': row[1],
            'nombre': row[2],
            'descripcion': row[3],
            'modulo': row[4]
        })

    conn.close()
    return permisos


def agregar_permiso_rol(rol, permiso_codigo):
    """
    Agrega un permiso a un rol.

    Returns:
        dict: {'success': bool, 'message': str}
    """
    conn = _conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO rol_permisos (rol, permiso_id, asignado_por)
            SELECT ?, id, ? FROM permisos WHERE codigo = ? AND activo = 1
        """, (rol, session.get('username'), permiso_codigo))

        if cursor.rowcount == 0:
            return {'success': False, 'message': 'Permiso no encontrado'}

        conn.commit()

        # Invalidar cache de este rol
        cache_key = f"rol_{rol}"
        if cache_key in _PERMISOS_CACHE:
            del _PERMISOS_CACHE[cache_key]

        registrar_accion_permiso('PERMISO_ROL_AGREGADO', {
            'rol': rol,
            'permiso': permiso_codigo
        })

        return {'success': True, 'message': f'Permiso agregado al rol {rol}'}

    except sqlite3.IntegrityError:
        return {'success': False, 'message': 'El rol ya tiene este permiso'}
    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        conn.close()


def quitar_permiso_rol(rol, permiso_codigo):
    """
    Quita un permiso de un rol.

    Returns:
        dict: {'success': bool, 'message': str}
    """
    if rol == 'admin':
        return {'success': False, 'message': 'No se pueden modificar permisos del rol admin'}

    conn = _conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM rol_permisos
            WHERE rol = ?
            AND permiso_id = (SELECT id FROM permisos WHERE codigo = ?)
        """, (rol, permiso_codigo))

        if cursor.rowcount == 0:
            return {'success': False, 'message': 'El rol no tiene este permiso'}

        conn.commit()

        # Invalidar cache
        cache_key = f"rol_{rol}"
        if cache_key in _PERMISOS_CACHE:
            del _PERMISOS_CACHE[cache_key]

        registrar_accion_permiso('PERMISO_ROL_QUITADO', {
            'rol': rol,
            'permiso': permiso_codigo
        })

        return {'success': True, 'message': f'Permiso quitado del rol {rol}'}

    except Exception as e:
        conn.rollback()
        return {'success': False, 'message': str(e)}
    finally:
        conn.close()


# ============================================================================
# FUNCIONES DE CONSULTA
# ============================================================================

def obtener_todos_permisos():
    """
    Obtiene todos los permisos del sistema agrupados por módulo.

    Returns:
        dict: Permisos agrupados por módulo
    """
    conn = _conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, codigo, nombre, descripcion, modulo, activo
        FROM permisos
        ORDER BY modulo, nombre
    """)

    permisos_por_modulo = {}
    for row in cursor.fetchall():
        modulo = row[4]
        if modulo not in permisos_por_modulo:
            permisos_por_modulo[modulo] = []

        permisos_por_modulo[modulo].append({
            'id': row[0],
            'codigo': row[1],
            'nombre': row[2],
            'descripcion': row[3],
            'activo': bool(row[5])
        })

    conn.close()
    return permisos_por_modulo


def obtener_permisos_usuario_detalle(usuario_id):
    """
    Obtiene detalle completo de permisos de un usuario.
    Incluye información sobre permisos protegidos.

    Returns:
        dict: {
            'rol': str,
            'permisos_rol': [...],
            'permisos_agregados': [...],
            'permisos_quitados': [...],
            'permisos_quitados_sin_efecto': [...],  # NUEVO
            'permisos_efectivos': [...],
            'permisos_protegidos': [...]  # NUEVO
        }
    """
    conn = _conectar_db()
    cursor = conn.cursor()

    # Obtener info del usuario
    cursor.execute("SELECT username, rol FROM usuarios WHERE id = ?", (usuario_id,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return None

    username, rol = user[0], user[1]

    # Permisos del rol
    permisos_rol = obtener_permisos_rol(rol)

    # Permisos específicos
    especificos = _obtener_permisos_usuario_especificos(usuario_id)

    # Permisos efectivos
    efectivos = obtener_permisos_usuario_completos(username)

    # NUEVO: Identificar permisos quitados que no tienen efecto (protegidos)
    permisos_quitados_sin_efecto = []
    permisos_quitados_efectivos = []

    for p in especificos['quitar']:
        if rol == 'admin' and p in PERMISOS_PROTEGIDOS_ADMIN:
            permisos_quitados_sin_efecto.append(p)
        else:
            permisos_quitados_efectivos.append(p)

    conn.close()

    return {
        'usuario_id': usuario_id,
        'username': username,
        'rol': rol,
        'permisos_rol': permisos_rol,
        'permisos_agregados': especificos['agregar'],
        'permisos_quitados': permisos_quitados_efectivos,
        'permisos_quitados_sin_efecto': permisos_quitados_sin_efecto,  # NUEVO
        'permisos_efectivos': efectivos,
        'permisos_protegidos': list(PERMISOS_PROTEGIDOS_ADMIN) if rol == 'admin' else []  # NUEVO
    }


def obtener_matriz_permisos():
    """
    Obtiene la matriz completa de permisos por rol.

    Returns:
        dict: {
            'permisos': [...],
            'roles': [...],
            'matriz': {rol: {permiso: bool}},
            'permisos_protegidos': [...]  # NUEVO
        }
    """
    conn = _conectar_db()
    cursor = conn.cursor()

    # Todos los permisos
    cursor.execute("SELECT codigo, nombre, modulo FROM permisos WHERE activo = 1 ORDER BY modulo, nombre")
    permisos = [{'codigo': r[0], 'nombre': r[1], 'modulo': r[2]} for r in cursor.fetchall()]

    # Todos los roles
    roles = ['asesor', 'supervisor', 'auditor', 'gerente', 'admin_tecnico', 'comite_credito', 'admin']

    # Construir matriz
    matriz = {}
    for rol in roles:
        permisos_rol = set(_obtener_permisos_rol(rol))
        matriz[rol] = {p['codigo']: p['codigo'] in permisos_rol for p in permisos}

    conn.close()

    return {
        'permisos': permisos,
        'roles': roles,
        'matriz': matriz,
        'permisos_protegidos': list(PERMISOS_PROTEGIDOS_ADMIN)  # NUEVO
    }


# ============================================================================
# HELPERS PARA TEMPLATES JINJA2
# ============================================================================

def registrar_helpers_permisos(app):
    """
    Registra funciones helper para usar en templates Jinja2.

    Uso en template:
        {% if tiene_permiso('com_aprobar') %}
            <button>Aprobar</button>
        {% endif %}
    """
    @app.context_processor
    def inject_permisos():
        permisos_usuario = []
        if session.get('autorizado') and session.get('username'):
            permisos_usuario = obtener_permisos_usuario_actual()

        return {
            'tiene_permiso': tiene_permiso,
            'tiene_alguno_de': tiene_alguno_de,
            'tiene_todos': tiene_todos,
            'permisos_usuario': permisos_usuario,
            'PERMISOS_PROTEGIDOS_ADMIN': PERMISOS_PROTEGIDOS_ADMIN  # NUEVO: disponible en templates
        }


# ============================================================================
# RUTAS API PARA GESTIÓN DE PERMISOS
# ============================================================================

def registrar_rutas_permisos(app):
    """Registra rutas API para gestión de permisos"""
    from flask_wtf.csrf import validate_csrf

    @app.route('/api/permisos/mis-permisos')
    def api_mis_permisos():
        """Obtiene los permisos del usuario actual"""
        if not session.get('autorizado'):
            return jsonify({'error': 'No autorizado'}), 401

        permisos = obtener_permisos_usuario_actual()
        return jsonify({
            'username': session.get('username'),
            'rol': session.get('rol'),
            'permisos': permisos,
            'total': len(permisos)
        })

    @app.route('/api/permisos/verificar/<permiso>')
    def api_verificar_permiso(permiso):
        """Verifica si el usuario tiene un permiso específico"""
        if not session.get('autorizado'):
            return jsonify({'error': 'No autorizado'}), 401

        return jsonify({
            'permiso': permiso,
            'tiene': tiene_permiso(permiso)
        })

    @app.route('/api/permisos/todos')
    @requiere_permiso('usr_permisos')
    def api_todos_permisos():
        """Obtiene todos los permisos del sistema"""
        return jsonify(obtener_todos_permisos())

    @app.route('/api/permisos/matriz')
    @requiere_permiso('usr_permisos')
    def api_matriz_permisos():
        """Obtiene la matriz de permisos por rol"""
        return jsonify(obtener_matriz_permisos())

    @app.route('/api/permisos/protegidos')
    @requiere_permiso('usr_permisos')
    def api_permisos_protegidos():
        """Obtiene la lista de permisos protegidos"""
        return jsonify({
            'permisos_protegidos': list(PERMISOS_PROTEGIDOS_ADMIN),
            'descripcion': 'Estos permisos no se pueden quitar a usuarios con rol admin'
        })

    @app.route('/api/permisos/usuario/<int:usuario_id>')
    @requiere_permiso('usr_permisos')
    def api_permisos_usuario(usuario_id):
        """Obtiene los permisos de un usuario específico"""
        detalle = obtener_permisos_usuario_detalle(usuario_id)
        if not detalle:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        return jsonify(detalle)

    @app.route('/api/permisos/usuario/<int:usuario_id>/agregar', methods=['POST'])
    @requiere_permiso('usr_permisos')
    def api_agregar_permiso_usuario(usuario_id):
        """Agrega un permiso específico a un usuario"""
        try:
            # Validar CSRF
            csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if csrf_token:
                validate_csrf(csrf_token)
        except:
            return jsonify({'error': 'Token CSRF inválido'}), 400

        data = request.get_json()
        if not data or 'permiso' not in data:
            return jsonify({'error': 'Permiso no especificado'}), 400

        resultado = agregar_permiso_usuario(
            usuario_id,
            data['permiso'],
            data.get('motivo')
        )

        status = 200 if resultado['success'] else 400
        return jsonify(resultado), status

    @app.route('/api/permisos/usuario/<int:usuario_id>/quitar', methods=['POST'])
    @requiere_permiso('usr_permisos')
    def api_quitar_permiso_usuario(usuario_id):
        """Quita un permiso específico a un usuario"""
        try:
            csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if csrf_token:
                validate_csrf(csrf_token)
        except:
            return jsonify({'error': 'Token CSRF inválido'}), 400

        data = request.get_json()
        if not data or 'permiso' not in data:
            return jsonify({'error': 'Permiso no especificado'}), 400

        resultado = quitar_permiso_usuario(
            usuario_id,
            data['permiso'],
            data.get('motivo')
        )

        status = 200 if resultado['success'] else 400
        return jsonify(resultado), status

    @app.route('/api/permisos/usuario/<int:usuario_id>/restaurar', methods=['POST'])
    @requiere_permiso('usr_permisos')
    def api_restaurar_permiso_usuario(usuario_id):
        """Restaura un permiso al valor por defecto del rol"""
        try:
            csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if csrf_token:
                validate_csrf(csrf_token)
        except:
            return jsonify({'error': 'Token CSRF inválido'}), 400

        data = request.get_json()
        if not data or 'permiso' not in data:
            return jsonify({'error': 'Permiso no especificado'}), 400

        resultado = restaurar_permiso_usuario(usuario_id, data['permiso'])

        status = 200 if resultado['success'] else 400
        return jsonify(resultado), status

    @app.route('/api/permisos/rol/<rol>/agregar', methods=['POST'])
    @requiere_permiso('usr_permisos')
    def api_agregar_permiso_rol(rol):
        """Agrega un permiso a un rol"""
        try:
            csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if csrf_token:
                validate_csrf(csrf_token)
        except:
            return jsonify({'error': 'Token CSRF inválido'}), 400

        data = request.get_json()
        if not data or 'permiso' not in data:
            return jsonify({'error': 'Permiso no especificado'}), 400

        resultado = agregar_permiso_rol(rol, data['permiso'])

        status = 200 if resultado['success'] else 400
        return jsonify(resultado), status

    @app.route('/api/permisos/rol/<rol>/quitar', methods=['POST'])
    @requiere_permiso('usr_permisos')
    def api_quitar_permiso_rol(rol):
        """Quita un permiso de un rol"""
        try:
            csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if csrf_token:
                validate_csrf(csrf_token)
        except:
            return jsonify({'error': 'Token CSRF inválido'}), 400

        data = request.get_json()
        if not data or 'permiso' not in data:
            return jsonify({'error': 'Permiso no especificado'}), 400

        resultado = quitar_permiso_rol(rol, data['permiso'])

        status = 200 if resultado['success'] else 400
        return jsonify(resultado), status

    @app.route('/api/permisos/cache/invalidar', methods=['POST'])
    @requiere_permiso('usr_permisos')
    def api_invalidar_cache():
        """Invalida el cache de permisos (usuarios con permiso usr_permisos)"""
        try:
            csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if csrf_token:
                validate_csrf(csrf_token)
        except:
            return jsonify({'error': 'Token CSRF inválido'}), 400

        invalidar_cache_permisos()
        return jsonify({'success': True, 'message': 'Cache invalidado'})

    @app.route('/api/permisos/limpiar-overrides', methods=['POST'])
    @requiere_permiso('usr_permisos')
    def api_limpiar_overrides():
        """
        Limpia overrides de permisos protegidos que no tienen efecto.
        Solo usuarios con permiso usr_permisos pueden ejecutar esto.
        """
        try:
            csrf_token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if csrf_token:
                validate_csrf(csrf_token)
        except:
            return jsonify({'error': 'Token CSRF inválido'}), 400

        resultado = limpiar_overrides_invalidos()

        status = 200 if resultado['success'] else 500
        return jsonify(resultado), status


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def ensure_permisos_minimos():
    try:
        conn = _conectar_db()
        cursor = conn.cursor()

        nuevos = [
            ('admin_panel_acceso', 'Acceso al Panel Admin',
             'Permite entrar al panel /admin', 'admin'),
            ('usr_asignaciones_equipo', 'Gestionar asignaciones de equipo',
             'Permite acceder a /admin/asignaciones-equipo', 'usuarios'),
            ('cap_usar', 'Usar capacidad de pago',
             'Permite acceder a /capacidad_pago', 'simulador'),
            ('cfg_comite_ver', 'Ver configuración comité',
             'Permite ver la configuración del comité de crédito', 'config'),
            ('cfg_comite_editar', 'Editar configuración comité',
             'Permite editar la configuración del comité de crédito', 'config'),
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO permisos (codigo, nombre, descripcion, modulo, activo)
            VALUES (?, ?, ?, ?, 1)
        """, nuevos)

        cursor.execute("SELECT id FROM permisos WHERE codigo='sim_usar'")
        row_sim = cursor.fetchone()
        cursor.execute("SELECT id FROM permisos WHERE codigo='cap_usar'")
        row_cap = cursor.fetchone()

        if row_sim and row_cap:
            sim_id = row_sim[0]
            cap_id = row_cap[0]

            cursor.execute("""
                SELECT DISTINCT rol
                FROM rol_permisos
                WHERE permiso_id = ? AND rol <> 'admin'
            """, (sim_id,))
            roles = [r[0] for r in cursor.fetchall()]

            for rol in roles:
                cursor.execute("""
                    INSERT OR IGNORE INTO rol_permisos (rol, permiso_id, asignado_por)
                    VALUES (?, ?, 'system')
                """, (rol, cap_id))

            cursor.execute("""
                SELECT usuario_id, tipo, asignado_por, motivo
                FROM usuario_permisos
                WHERE permiso_id = ?
            """, (sim_id,))
            for r in cursor.fetchall():
                cursor.execute("""
                    INSERT OR IGNORE INTO usuario_permisos (usuario_id, permiso_id, tipo, asignado_por, motivo)
                    VALUES (?, ?, ?, ?, ?)
                """, (r[0], cap_id, r[1], r[2] or 'system', r[3] or 'Clonado desde sim_usar'))

        conn.commit()
        conn.close()

        invalidar_cache_permisos()
        return True
    except Exception as e:
        print(f"⚠️ ensure_permisos_minimos(): {e}")
        return False


def inicializar_permisos(app):
    """
    Inicializa el sistema de permisos en la aplicación Flask.

    Uso en flask_app.py:
        from permisos import inicializar_permisos
        inicializar_permisos(app)
    """
    registrar_helpers_permisos(app)
    registrar_rutas_permisos(app)
    ensure_permisos_minimos()
    print("✅ Sistema de permisos inicializado")
    print(f"   Permisos protegidos (admin): {', '.join(PERMISOS_PROTEGIDOS_ADMIN)}")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                 LOANSI - MÓDULO DE PERMISOS                          ║
║                      Testing básico                                  ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    # Verificar que las tablas existen
    conn = _conectar_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='permisos'")
    if cursor.fetchone():
        print("✅ Tabla 'permisos' existe")

        cursor.execute("SELECT COUNT(*) FROM permisos")
        print(f"   Total permisos: {cursor.fetchone()[0]}")

        cursor.execute("SELECT COUNT(*) FROM rol_permisos")
        print(f"   Total asignaciones: {cursor.fetchone()[0]}")

        # NUEVO: Mostrar permisos protegidos
        print(f"\n🛡️  Permisos protegidos (admin):")
        for p in PERMISOS_PROTEGIDOS_ADMIN:
            print(f"   - {p}")

        # NUEVO: Verificar overrides inválidos
        cursor.execute("""
            SELECT COUNT(*)
            FROM usuario_permisos up
            JOIN usuarios u ON up.usuario_id = u.id
            JOIN permisos p ON up.permiso_id = p.id
            WHERE u.rol = 'admin' AND up.tipo = 'quitar'
            AND p.codigo IN (?, ?, ?, ?, ?, ?)
        """, tuple(PERMISOS_PROTEGIDOS_ADMIN))

        invalidos = cursor.fetchone()[0]
        if invalidos > 0:
            print(f"\n⚠️  Hay {invalidos} override(s) inválidos en la BD")
            print("   Ejecuta limpiar_overrides_invalidos() para limpiar")
        else:
            print("\n✅ Sin overrides inválidos")

    else:
        print("❌ Tabla 'permisos' no existe")
        print("   Ejecuta primero: python migracion_permisos.py")

    conn.close()