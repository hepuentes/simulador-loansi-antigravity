"""
SCORING_ROUTES.PY - Rutas de scoring de crédito
================================================
"""

from flask import render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
import json
import traceback

from . import scoring_bp


def login_required(f):
    """Decorador que requiere autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("autorizado"):
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def requiere_permiso(permiso):
    """Decorador que requiere un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("autorizado"):
                return redirect(url_for("auth.login"))
            
            import sys
            from pathlib import Path
            BASE_DIR = Path(__file__).parent.parent.parent.resolve()
            if str(BASE_DIR) not in sys.path:
                sys.path.insert(0, str(BASE_DIR))
            
            from permisos import tiene_permiso
            
            if not tiene_permiso(permiso):
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'Permiso denegado',
                        'code': 'PERMISSION_DENIED'
                    }), 403
                flash("No tienes permiso para acceder a esta función", "error")
                return redirect(url_for("main.dashboard"))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@scoring_bp.route("/scoring")
@login_required
@requiere_permiso("sco_ejecutar")
def scoring_page():
    """Página de evaluación de scoring"""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers import cargar_configuracion, cargar_scoring
    
    config = cargar_configuracion()
    scoring = cargar_scoring()
    
    lineas_credito = config.get("LINEAS_CREDITO", {})
    criterios = scoring.get("criterios", {})
    secciones = scoring.get("secciones", [])
    niveles_riesgo = scoring.get("niveles_riesgo", [])
    factores_rechazo = scoring.get("factores_rechazo_automatico", [])
    
    # Preparar criterios agrupados por sección para el template
    scoring_criterios_agrupados = []
    criterios_por_seccion = {}
    
    # Agrupar criterios por sección
    for criterio_id, criterio_data in criterios.items():
        seccion_id = criterio_data.get("seccion", "otros")
        if seccion_id not in criterios_por_seccion:
            criterios_por_seccion[seccion_id] = []
        criterios_por_seccion[seccion_id].append({
            "id": criterio_id,
            **criterio_data
        })
    
    # Construir estructura agrupada
    for seccion in secciones:
        seccion_id = seccion.get("id", "")
        criterios_seccion = criterios_por_seccion.get(seccion_id, [])
        if criterios_seccion:
            scoring_criterios_agrupados.append({
                "seccion": seccion,
                "criterios": criterios_seccion
            })
    
    # Agregar criterios sin sección asignada
    criterios_sin_seccion = criterios_por_seccion.get("otros", [])
    if criterios_sin_seccion:
        scoring_criterios_agrupados.append({
            "seccion": {"id": "otros", "nombre": "Otros Criterios", "icono": "bi-gear"},
            "criterios": criterios_sin_seccion
        })
    
    return render_template(
        "scoring.html",
        lineas_credito=lineas_credito,
        criterios=criterios,
        scoring_criterios=criterios,
        scoring_criterios_agrupados=scoring_criterios_agrupados,
        secciones=secciones,
        scoring_secciones=secciones,
        niveles_riesgo=niveles_riesgo,
        factores_rechazo=factores_rechazo,
        config_json=json.dumps({
            "lineas_credito": lineas_credito,
            "criterios": criterios,
            "niveles_riesgo": niveles_riesgo
        })
    )


@scoring_bp.route("/scoring", methods=["POST"])
@login_required
@requiere_permiso("sco_ejecutar")
def calcular_scoring():
    """
    Procesar evaluación de scoring usando ScoringService.
    REFACTORIZADO: 2026-01-26 - Ahora usa ScoringService para lógica consistente.
    """
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    
    from db_helpers import cargar_scoring, guardar_evaluacion, cargar_configuracion
    from db_helpers_scoring_linea import cargar_scoring_por_linea
    from ..services.scoring_service import ScoringService
    from ..utils.timezone import obtener_hora_colombia
    from ..utils.formatting import parse_currency_value
    
    try:
        # Obtener datos del formulario
        form_data = request.form.to_dict()
        
        nombre_cliente = form_data.get("nombre_cliente", "").strip()
        cedula = form_data.get("cedula", "").strip()
        linea_credito = form_data.get("linea_credito", "")
        monto_solicitado = parse_currency_value(form_data.get("monto_solicitado", 0))
        
        if not nombre_cliente or not cedula:
            flash("Nombre y cédula son requeridos", "error")
            return redirect(url_for("scoring.scoring_page"))
        
        # =====================================================================
        # USAR SCORING SERVICE PARA CÁLCULO Y RECHAZO AUTOMÁTICO
        # =====================================================================
        
        # Cargar configuración específica de la línea de crédito (si existe)
        scoring_config_linea = None
        if linea_credito:
            scoring_config_linea = cargar_scoring_por_linea(linea_credito)
        
        # Si no hay config específica de línea, usar config global
        if not scoring_config_linea:
            scoring_config_linea = cargar_scoring()
        
        # Instanciar el servicio con la configuración
        scoring_service = ScoringService(scoring_config_linea)
        
        # Preparar valores para el servicio (limpiar datos del formulario)
        valores_criterios = {}
        for key, value in form_data.items():
            # Excluir campos que no son criterios
            if key not in ["nombre_cliente", "cedula", "linea_credito", "monto_solicitado", "csrf_token"]:
                # Intentar convertir valores numéricos
                try:
                    clean_val = str(value).replace('$', '').replace('.', '').replace(',', '').replace('%', '').strip()
                    if clean_val and (clean_val.isdigit() or clean_val.replace('.', '', 1).isdigit()):
                        valores_criterios[key] = float(clean_val)
                    else:
                        valores_criterios[key] = value
                except:
                    valores_criterios[key] = value
        
        # 1. VERIFICAR RECHAZO AUTOMÁTICO PRIMERO (usando el servicio)
        rechazo_info = scoring_service.verificar_rechazo_automatico(valores_criterios)
        
        rechazo_automatico = rechazo_info.get("rechazo", False)
        razon_rechazo = rechazo_info.get("razon")
        factor_rechazo = rechazo_info.get("factor")
        
        # 2. CALCULAR SCORING COMPLETO (usando el servicio)
        resultado_scoring = scoring_service.calcular_scoring(valores_criterios, linea_credito)
        
        # Extraer valores del resultado del servicio
        score_total = resultado_scoring.get("score", 0)
        score_normalizado = resultado_scoring.get("score_normalizado", 0)
        nivel_riesgo = resultado_scoring.get("nivel", "Sin clasificar")
        nivel_detalle = resultado_scoring.get("nivel_detalle", {})
        criterios_evaluados = resultado_scoring.get("criterios_evaluados", [])
        aprobado = resultado_scoring.get("aprobado", False)
        puntaje_minimo = resultado_scoring.get("puntaje_minimo", 17)
        
        # Sobrescribir aprobado si hubo rechazo automático
        if rechazo_automatico:
            aprobado = False
        
        # Crear evaluación con datos del servicio
        evaluacion = {
            "timestamp": obtener_hora_colombia().isoformat(),
            "asesor": session.get("username"),
            "nombre_cliente": nombre_cliente,
            "cedula": cedula,
            "linea_credito": linea_credito,
            "monto_solicitado": monto_solicitado,
            "resultado": {
                "score": score_total,
                "score_normalizado": score_normalizado,
                "nivel": nivel_riesgo,
                "aprobado": aprobado,
                "rechazo_automatico": rechazo_automatico,
                "razon_rechazo": razon_rechazo,
                "factor_rechazo": factor_rechazo,
                "puntaje_minimo": puntaje_minimo
            },
            "criterios_evaluados": criterios_evaluados,
            "nivel_riesgo": nivel_riesgo,
            "nivel_detalle": nivel_detalle,
            "estado_comite": None,
            "origen": "Manual"
        }
        
        # Guardar evaluación
        guardar_evaluacion(evaluacion)
        
        # =====================================================================
        # RE-RENDERIZAR FORMULARIO CON RESULTADOS
        # =====================================================================
        
        # Cargar configuración para el template
        config = cargar_configuracion()
        lineas_credito = config.get("LINEAS_CREDITO", {})
        
        # Usar la misma config que el servicio
        criterios = scoring_config_linea.get("criterios", {})
        secciones = scoring_config_linea.get("secciones", [])
        niveles_riesgo = scoring_config_linea.get("niveles_riesgo", [])
        factores_rechazo = scoring_config_linea.get("factores_rechazo_automatico", [])
        
        # Agrupar criterios por sección
        from db_helpers_scoring_linea import obtener_secciones_criterios
        criterios_por_seccion = obtener_secciones_criterios(linea_credito)
        
        scoring_criterios_agrupados = []
        for seccion in secciones:
            seccion_id = seccion.get("id", "")
            seccion_criterios = criterios_por_seccion.get(seccion_id, [])
            if seccion_criterios:
                scoring_criterios_agrupados.append({
                    "seccion": seccion,
                    "criterios": seccion_criterios
                })
        
        criterios_sin_seccion = criterios_por_seccion.get("otros", [])
        if criterios_sin_seccion:
            scoring_criterios_agrupados.append({
                "seccion": {"id": "otros", "nombre": "Otros Criterios", "icono": "bi-gear"},
                "criterios": criterios_sin_seccion
            })
        
        # Renderizar scoring.html con los resultados Y el formulario
        return render_template(
            "scoring.html",
            lineas_credito=lineas_credito,
            criterios=criterios,
            scoring_criterios=criterios,
            scoring_criterios_agrupados=scoring_criterios_agrupados,
            secciones=secciones,
            scoring_secciones=secciones,
            niveles_riesgo=niveles_riesgo,
            factores_rechazo=factores_rechazo,
            config_json=json.dumps({
                "lineas_credito": lineas_credito,
                "criterios": criterios,
                "niveles_riesgo": niveles_riesgo
            }),
            # Agregar datos de resultado
            evaluacion=evaluacion,
            scoring_result=evaluacion["resultado"],
            form_values=form_data  # Para mantener valores del formulario
        )
        
    except Exception as e:
        traceback.print_exc()
        flash(f"Error procesando evaluación: {str(e)}", "error")
        return redirect(url_for("scoring.scoring_page"))


@scoring_bp.route("/api/scoring/invalidar-cache", methods=["POST"])
@login_required
@requiere_permiso("cfg_sco_editar")
def api_scoring_invalidar_cache():
    """Invalida el cache de scoring."""
    import sys
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent.parent.resolve()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
        
    from db_helpers_scoring_linea import invalidar_cache_scoring_linea
    import logging
    logger = logging.getLogger(__name__)

    try:
        linea_id = request.get_json().get("linea_id") if request.is_json else None

        invalidar_cache_scoring_linea(linea_id)

        return jsonify({"success": True, "message": "Cache de scoring invalidado"})
    except Exception as e:
        logger.error(f"Error invalidando cache: {e}")
        return jsonify({"success": False, "error": str(e)}), 500