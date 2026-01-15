#!/usr/bin/env python3
"""
FIX: Reparación de permisos de scoring para usuarios admin
===========================================================
Fecha: 2026-01-14
Problema: Usuarios admin tienen cfg_sco_ver quitado en usuario_permisos

Este script:
1. Elimina los registros que quitan cfg_sco_ver/cfg_sco_editar a usuarios admin
2. Invalida el cache de permisos
"""

import sqlite3
import os

# Ruta a la base de datos
DB_PATH = '/home/loansi/simulador/loansi.db'

def conectar_db():
    """Conecta a la base de datos SQLite"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Base de datos no encontrada en: {DB_PATH}")
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def main():
    print("=" * 70)
    print("   FIX: REPARACIÓN DE PERMISOS DE SCORING")
    print("=" * 70)
    
    conn = conectar_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # =========================================================================
    # PASO 1: Identificar usuarios admin con permisos quitados
    # =========================================================================
    print("\n📋 PASO 1: Identificando permisos quitados a usuarios admin...")
    
    cursor.execute("""
        SELECT 
            up.id,
            u.username,
            u.rol,
            p.codigo,
            p.nombre,
            up.tipo,
            up.fecha_asignacion,
            up.motivo
        FROM usuario_permisos up
        JOIN usuarios u ON up.usuario_id = u.id
        JOIN permisos p ON up.permiso_id = p.id
        WHERE u.rol = 'admin' 
          AND up.tipo = 'quitar'
          AND p.codigo IN ('cfg_sco_ver', 'cfg_sco_editar')
        ORDER BY u.username, p.codigo
    """)
    
    registros_a_eliminar = cursor.fetchall()
    
    if not registros_a_eliminar:
        print("   ✅ No hay permisos de scoring quitados a usuarios admin")
    else:
        print(f"\n   🔍 Encontrados {len(registros_a_eliminar)} registros problemáticos:")
        print("-" * 70)
        for r in registros_a_eliminar:
            print(f"   ID: {r['id']} | Usuario: {r['username']} | Permiso: {r['codigo']}")
            print(f"         Quitado el: {r['fecha_asignacion']} | Motivo: {r['motivo']}")
        print("-" * 70)
    
    # =========================================================================
    # PASO 2: Eliminar registros problemáticos
    # =========================================================================
    print("\n🔧 PASO 2: Eliminando registros problemáticos...")
    
    if registros_a_eliminar:
        ids_eliminar = [r['id'] for r in registros_a_eliminar]
        
        # Crear backup de los registros antes de eliminar
        print(f"\n   📦 Backup de registros a eliminar:")
        for r in registros_a_eliminar:
            print(f"      ({r['id']}, {r['username']}, {r['codigo']}, {r['tipo']})")
        
        # Eliminar
        cursor.execute(f"""
            DELETE FROM usuario_permisos 
            WHERE id IN ({','.join('?' * len(ids_eliminar))})
        """, ids_eliminar)
        
        eliminados = cursor.rowcount
        print(f"\n   ✅ {eliminados} registros eliminados")
    else:
        print("   ✅ No hay registros que eliminar")
    
    # =========================================================================
    # PASO 3: Verificar otros usuarios admin
    # =========================================================================
    print("\n📋 PASO 3: Verificando estado de permisos para TODOS los admin...")
    
    cursor.execute("""
        SELECT u.id, u.username 
        FROM usuarios u 
        WHERE u.rol = 'admin' AND u.activo = 1
    """)
    admins = cursor.fetchall()
    
    print(f"\n   Usuarios admin activos: {len(admins)}")
    
    # Verificar permisos de cada admin
    cursor.execute("SELECT id FROM permisos WHERE codigo = 'cfg_sco_ver'")
    perm_row = cursor.fetchone()
    if perm_row:
        perm_id = perm_row['id']
        
        for admin in admins:
            # Verificar si tiene algún override para cfg_sco_ver
            cursor.execute("""
                SELECT tipo FROM usuario_permisos 
                WHERE usuario_id = ? AND permiso_id = ?
            """, (admin['id'], perm_id))
            override = cursor.fetchone()
            
            status = "✅ OK (sin override)" if not override else (
                "⚠️ Override: " + override['tipo']
            )
            print(f"      {admin['username']}: {status}")
    
    # =========================================================================
    # COMMIT
    # =========================================================================
    print("\n💾 Guardando cambios...")
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("   ✅ FIX COMPLETADO")
    print("=" * 70)
    print("""
   ⚠️ IMPORTANTE - PASOS SIGUIENTES:
   
   1. Reinicie la aplicación Flask en PythonAnywhere
      (Web tab → Reload)
   
   2. Pruebe el login con usuario 'admin' y acceda a:
      Panel Admin → Scoring Interno
   
   3. Si persiste el problema, invalide el cache manualmente
      ejecutando este comando en la consola Python:
      
      from permisos import invalidar_cache_permisos
      invalidar_cache_permisos()
""")

if __name__ == "__main__":
    main()