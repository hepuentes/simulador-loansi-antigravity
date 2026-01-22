"""
API_ROUTES.PY - Rutas de la API REST
=====================================
CORREGIDO: 2026-01-18 - Agregado success:true a endpoints que lo necesitan
"""

from flask import request, jsonify, session
from functools import wraps
import json
import traceback

from . import api_bp


def api_login_required(f):
    """Decorador que requiere autenticación para API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("autorizado"):
            return jsonify({
                'error': 'No autorizado',
                'code': 'AUTH_REQUIRED'
            }), 401
        return f(*args, **kwargs)
    return decorated_function


def api_requiere_permiso(permiso):
    """Decorador que requiere un permiso específico para API"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("autorizado"):
                return jsonify({
                    'error': 'No autorizado',
                    'code': 'AUTH_REQUIRED'
                }), 401
            
            import sys
            from pathlib import Path
            BASE_DIR = Path(__file__).parent.parent.parent.resolve()
            if str(BASE_DIR) not in sys.path:
                sys.path.insert(0, str(BASE_DIR))
            
            from permisos import tiene_permiso
            
            if not tiene_permiso(permiso):
                return jsonify({
                    'error': 'Permiso denegado',
                    'code': 'PERMISSION_DENIED',
                    'required': permiso
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ============================================================================
# API DE SESIÓN Y CSRF
# ============================================================================

@api_bp.route("/csrf-token", methods=["GET"])
def api_csrf_token():
    """Obtener token CSRF"""
    from flask_wtf.csrf import generate_csrf
    
    return jsonify({
        "csrf_token": generate_csrf()
    })


@api_bp.route("/session-status", methods=["GET"])
def api_session_status():
    """Verificar estado de sesión"""
    if session.get("autorizado"):
        return jsonify({
            "authenticated": True,
            "username": session.get("username"),
            "rol": session.get("rol"),
            "nombre_completo": session.get("nombre_completo")
        })
    return jsonify({"authenticated": False})


# ============================================================================
# API DE CONFIGURACIÓN
# ============================================================================

@api_bp.route("/lineas-config", methods=["GET"])
@api_login_required
def api_lineas_config():
    """Obtener configuración de líneas de crédito"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers import cargar_configuracion
    
    config = cargar_configuracion()
    
    return jsonify({
        "lineas_credito": config.get("LINEAS_CREDITO", {}),
        "costos_asociados": config.get("COSTOS_ASOCIADOS", {})
    })


@api_bp.route("/capacidad-config", methods=["GET"])
@api_login_required
def api_capacidad_config():
    """Obtener configuración de capacidad de pago"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers import cargar_configuracion
    
    config = cargar_configuracion()
    
    return jsonify(config.get("PARAMETROS_CAPACIDAD_PAGO", {}))


# ============================================================================
# API DE COMITÉ
# ============================================================================

@api_bp.route("/comite/pendientes", methods=["GET"])
@api_login_required
@api_requiere_permiso("com_ver_todos")
def api_comite_pendientes():
    """Obtener casos pendientes del comité"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers import obtener_casos_comite
    
    casos = obtener_casos_comite({"estado_comite": "pending"})
    
    return jsonify({
        "success": True,
        "casos": casos,
        "total": len(casos)
    })


@api_bp.route("/detalle_evaluacion/<timestamp>", methods=["GET"])
@api_login_required
def api_detalle_evaluacion(timestamp):
    """Obtener detalle de una evaluación"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers import obtener_evaluacion_por_timestamp
    
    try:
        evaluacion = obtener_evaluacion_por_timestamp(timestamp)
        
        if not evaluacion:
            return jsonify({
                "success": False,
                "error": "Evaluación no encontrada"
            }), 404
        
        # Asegurar que los campos críticos existen
        if 'monto_solicitado' not in evaluacion:
            evaluacion['monto_solicitado'] = 0
        if 'resultado' not in evaluacion:
            evaluacion['resultado'] = {}
        
        return jsonify({
            "success": True,
            "evaluacion": evaluacion
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@api_bp.route("/badge-count", methods=["GET"])
@api_login_required
def api_badge_count():
    """Obtener contadores para badges del navbar"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers import contar_casos_nuevos_asesor, obtener_casos_comite
    
    username = session.get("username")
    rol = session.get("rol")
    
    response = {
        "casos_nuevos": 0,
        "pendientes_comite": 0
    }
    
    # Casos nuevos para el asesor
    if username:
        try:
            response["casos_nuevos"] = contar_casos_nuevos_asesor(username)
        except:
            response["casos_nuevos"] = 0
    
    # Pendientes de comité (para admin y comité)
    if rol in ["admin", "admin_tecnico", "comite_credito"]:
        try:
            casos_pendientes = obtener_casos_comite({"estado_comite": "pending"})
            response["pendientes_comite"] = len(casos_pendientes)
        except:
            response["pendientes_comite"] = 0
    
    return jsonify(response)


# ============================================================================
# API DE USUARIOS
# ============================================================================

@api_bp.route("/usuarios/lista", methods=["GET"])
@api_login_required
@api_requiere_permiso("usr_ver")
def api_usuarios_lista():
    """Obtener lista de usuarios"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers import obtener_usuarios_completos
    
    usuarios = obtener_usuarios_completos()
    
    return jsonify({
        "success": True,
        "usuarios": usuarios,
        "total": len(usuarios)
    })


@api_bp.route("/usuarios/<username>/id", methods=["GET"])
@api_login_required
def api_usuario_id(username):
    """Obtener ID de un usuario por username"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from database import conectar_db
    
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE username = ? AND activo = 1", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify({
                "success": True,
                "id": row[0],
                "username": username
            })
        
        return jsonify({
            "success": False,
            "error": "Usuario no encontrado"
        }), 404
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ============================================================================
# API DE SCORING POR LÍNEA
# ============================================================================

@api_bp.route("/scoring/lineas-credito", methods=["GET"])
@api_login_required
def api_scoring_lineas():
    """Obtener líneas de crédito con info de scoring"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    # from app.utils.decorators import no_cache_and_check_session, admin_required, requiere_permiso (ERROR: Module not found)
    
    # from db_helpers import (
    #     obtener_parametros_capacidad, guardar_parametros_capacidad
    # )
    from db_helpers_scoring_linea import (
        obtener_config_scoring_linea, 
        guardar_config_scoring_linea,
        guardar_niveles_riesgo_linea,
        obtener_lineas_credito_scoring,
        guardar_factores_rechazo_linea,
        guardar_criterios_completos_linea,
        copiar_config_scoring
    )
    # from db_helpers_comite import obtener_casos_pendientes_comite (Check if used? It is not used in this function)
    
    try:
        lineas = obtener_lineas_credito_scoring()
        
        # CORRECCIÓN: El JavaScript espera success: true
        return jsonify({
            "success": True,
            "lineas": lineas,
            "total": len(lineas)
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "lineas": []
        })


@api_bp.route("/scoring/linea/<int:linea_id>/config", methods=["GET"])
@api_login_required
def api_scoring_linea_config(linea_id):
    """Obtener configuración de scoring para una línea"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from db_helpers_scoring_linea import obtener_config_scoring_linea
        
        config = obtener_config_scoring_linea(linea_id)
        
        return jsonify({
            "success": True,
            "config": config
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        })


@api_bp.route("/scoring/linea/<int:linea_id>/config", methods=["POST"])
@api_login_required
@api_requiere_permiso("cfg_sco_editar")
def api_scoring_linea_guardar(linea_id):
    """Guardar configuración de scoring para una línea"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers_scoring_linea import guardar_config_scoring_linea
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"}), 400
        
        if guardar_config_scoring_linea(linea_id, data):
            return jsonify({
                "success": True,
                "message": "Configuración guardada"
            })
        else:
            return jsonify({"success": False, "error": "Error al guardar configuración"}), 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/scoring/linea/<int:linea_id>/niveles-riesgo", methods=["GET"])
@api_login_required
def api_scoring_niveles_riesgo(linea_id):
    """Obtener niveles de riesgo para una línea"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from db_helpers_scoring_linea import obtener_niveles_riesgo_linea
        
        niveles = obtener_niveles_riesgo_linea(linea_id)
        
        return jsonify({
            "success": True,
            "niveles": niveles,
            "total": len(niveles)
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "niveles": []
        })


@api_bp.route("/scoring/linea/<int:linea_id>/niveles-riesgo", methods=["POST"])
@api_login_required
@api_requiere_permiso("cfg_sco_editar")
def api_scoring_niveles_guardar(linea_id):
    """Guardar niveles de riesgo para una línea"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers_scoring_linea import guardar_niveles_riesgo_linea
    
    try:
        data = request.get_json()
        
        if not data or 'niveles' not in data:
            return jsonify({"success": False, "error": "Datos de niveles no especificados"}), 400
        
        if guardar_niveles_riesgo_linea(linea_id, data['niveles']):
            return jsonify({
                "success": True,
                "message": "Niveles de riesgo guardados"
            })
        else:
            return jsonify({"success": False, "error": "Error al guardar niveles"}), 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# API DE ESTADOS DE CRÉDITO
# ============================================================================

@api_bp.route("/credito/marcar-desembolsado", methods=["POST"])
@api_login_required
@api_requiere_permiso("com_marcar_desembolso")
def api_marcar_desembolsado():
    """Marcar un crédito como desembolsado"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from db_helpers_estados import marcar_desembolsado
    except ImportError:
        return jsonify({"success": False, "error": "Módulo de estados no disponible"}), 500
    
    try:
        data = request.get_json()
        
        timestamp = data.get("timestamp")
        comentario = data.get("comentario")
        
        if not timestamp:
            return jsonify({"success": False, "error": "Timestamp no especificado"}), 400
        
        resultado = marcar_desembolsado(
            timestamp, 
            session.get("username"),
            comentario
        )
        
        if resultado['success']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/credito/marcar-desistido", methods=["POST"])
@api_login_required
@api_requiere_permiso("com_marcar_desistido")
def api_marcar_desistido():
    """Marcar un crédito como desistido"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from db_helpers_estados import marcar_desistido
    except ImportError:
        return jsonify({"success": False, "error": "Módulo de estados no disponible"}), 500
    
    try:
        data = request.get_json()
        
        timestamp = data.get("timestamp")
        motivo = data.get("motivo")
        
        if not timestamp:
            return jsonify({"success": False, "error": "Timestamp no especificado"}), 400
        
        resultado = marcar_desistido(
            timestamp,
            session.get("username"),
            motivo
        )
        
        if resultado['success']:
            return jsonify(resultado)
        else:
            return jsonify(resultado), 400
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/credito/estadisticas-estados", methods=["GET"])
@api_login_required
def api_estadisticas_estados():
    """Obtener estadísticas de estados de crédito"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from db_helpers_estados import obtener_estadisticas_estados
        
        estadisticas = obtener_estadisticas_estados()
        
        return jsonify({
            "success": True,
            "estadisticas": estadisticas
        })
        
    except ImportError:
        return jsonify({
            "success": False,
            "error": "Módulo de estados no disponible"
        }), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500





@api_bp.route("/scoring/linea/<int:linea_id>/criterios", methods=["POST"])
@api_login_required
@api_requiere_permiso("admin_panel_acceso")
def guardar_criterios_linea(linea_id):
    """Guarda los criterios de scoring para una línea específica"""
    from db_helpers_scoring_linea import guardar_criterios_completos_linea
    
    try:
        data = request.get_json()
        # El frontend puede mandar 'criterios' o ser una lista directa
        criterios = data.get("criterios", data) if isinstance(data, dict) else data
        
        if guardar_criterios_completos_linea(linea_id, criterios):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Error al guardar criterios"}), 500
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/scoring/invalidar-cache", methods=["POST"])
@api_login_required
@api_requiere_permiso("admin_panel_acceso")
def api_invalidar_cache():
    """Invalida el caché de configuración de scoring"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from db_helpers_scoring_linea import invalidar_cache_scoring_linea
        from db_helpers import cargar_configuracion # To force reload if needed
        
        # Invalidar cache de scoring
        invalidar_cache_scoring_linea()
        
        return jsonify({
            "success": True, 
            "message": "Caché invalidado correctamente"
        })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/scoring/copiar-config", methods=["POST"])
@api_login_required
@api_requiere_permiso("admin_panel_acceso")
def copiar_configuracion_scoring():
    """Copia la configuración de scoring de una línea a otra"""
    try:
        data = request.get_json()
        linea_origen_id = data.get("linea_origen_id")
        linea_destino_id = data.get("linea_destino_id")
        incluir_criterios = data.get("incluir_criterios", True)
        
        if not linea_origen_id or not linea_destino_id:
            return jsonify({"success": False, "error": "IDs de línea requeridos"}), 400
            
        if copiar_config_scoring(linea_origen_id, linea_destino_id, incluir_criterios):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Error al copiar configuración"}), 500
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/scoring/linea/<int:linea_id>/factores-rechazo", methods=["POST"])
@api_login_required
@api_requiere_permiso("admin_panel_acceso")
def guardar_factores_rechazo(linea_id):
    """Guarda los factores de rechazo para una línea específica"""
    try:
        data = request.get_json()
        # El frontend manda {factores: [...]} o [...]
        factores = data.get("factores", data) if isinstance(data, dict) else data
        
        from db_helpers_scoring_linea import guardar_factores_rechazo_linea
        
        if guardar_factores_rechazo_linea(linea_id, factores):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Error al guardar factores de rechazo"}), 500
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/debug/session", methods=["GET"])
@api_login_required
@api_requiere_permiso("aud_ver_todos")
def api_debug_session():
    """Endpoint temporal para debugging de sesión"""
    return jsonify(
        {
            "session_keys": list(session.keys()),
            "username": session.get("username"),
            "rol": session.get("rol"),
            "session_id": session.get("_id", "N/A"),
            "permanent": session.permanent,
            "all_session": dict(session),
        }
    )


@api_bp.route("/db_diagnostics", methods=["GET"])
@api_login_required
@api_requiere_permiso("aud_ver_todos")
def api_db_diagnostics():
    """
    Endpoint de diagnóstico para verificar estado de SQLite.
    Solo accesible por admin.
    """
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
        
    try:
        from database import (
            conectar_db,
            verificar_integridad_db,
            listar_tablas,
            contar_registros_tabla
        )
        import sqlite3

        # 1. Verificar conexión
        conn = conectar_db()
        conn.close()

        # 2. Verificar integridad (usando función existente)
        tablas_ok = verificar_integridad_db()

        # 3. Obtener estadísticas de tablas (manual loop)
        tablas = listar_tablas()
        stats = {}
        for tabla in tablas:
            stats[tabla] = contar_registros_tabla(tabla)

        # 4. Verificar WAL mode
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]
        conn.close()

        return jsonify(
            {
                "status": "ok",
                "database_connection": "success",
                "tables_integrity": tablas_ok,
                "table_stats": stats,
                "journal_mode": journal_mode,
                "python_sqlite_version": sqlite3.version,
                "sqlite_lib_version": sqlite3.sqlite_version,
            }
        )

    except Exception as e:
        traceback.print_exc()
        return jsonify(
            {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
        ), 500


# ============================================================================
# API DE PERMISOS
# ============================================================================

@api_bp.route("/permisos/cache/invalidar", methods=["POST"])
@api_login_required
@api_requiere_permiso("usr_permisos")
def api_permisos_cache_invalidar():
    """Invalidar cache de permisos"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from permisos import invalidar_cache_permisos
        invalidar_cache_permisos()
        
        print("🔄 [API] Cache de permisos invalidado")
        
        return jsonify({
            "success": True,
            "message": "Cache de permisos invalidado correctamente"
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/permisos/matriz", methods=["GET"])
@api_login_required
@api_requiere_permiso("usr_permisos")
def api_permisos_matriz():
    """Obtener matriz de permisos por rol"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from permisos import obtener_matriz_permisos, obtener_todos_permisos
        
        matriz = obtener_matriz_permisos()
        permisos = obtener_todos_permisos()
        roles = ["asesor", "supervisor", "gerente", "admin"]
        
        return jsonify({
            "success": True,
            "matriz": matriz,
            "permisos": permisos,
            "roles": roles
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/permisos/protegidos", methods=["GET"])
@api_login_required
@api_requiere_permiso("usr_permisos")
def api_permisos_protegidos():
    """Obtener lista de permisos protegidos"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from permisos import obtener_permisos_protegidos
        
        protegidos = obtener_permisos_protegidos()
        
        return jsonify({
            "success": True,
            "protegidos": protegidos
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/permisos/usuario/<int:user_id>", methods=["GET"])
@api_login_required
@api_requiere_permiso("usr_permisos")
def api_permisos_usuario(user_id):
    """Obtener permisos detallados de un usuario"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from permisos import obtener_permisos_usuario_detallados
        
        permisos = obtener_permisos_usuario_detallados(user_id)
        
        return jsonify({
            "success": True,
            "permisos": permisos
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/permisos/limpiar-overrides", methods=["POST"])
@api_login_required
@api_requiere_permiso("usr_permisos")
def api_permisos_limpiar_overrides():
    """Limpiar overrides de permisos sin efecto"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    try:
        from permisos import limpiar_overrides_sin_efecto
        
        eliminados = limpiar_overrides_sin_efecto()
        
        print(f"🧹 [API] Overrides limpiados: {eliminados}")
        
        return jsonify({
            "success": True,
            "eliminados": eliminados
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
