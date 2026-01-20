#!/usr/bin/env python3
"""
Test script para verificar integración en producción con autenticación.
Usa credenciales de hpsupersu para probar acceso a rutas protegidas.
"""

import requests
import sys

BASE_URL = "https://loansi.pythonanywhere.com"
LOGIN_URL = f"{BASE_URL}/login"
DASHBOARD_URL = f"{BASE_URL}/dashboard"
ADMIN_URL = f"{BASE_URL}/admin"
SCORING_URL = f"{BASE_URL}/scoring"

# Credenciales (Solicitadas por el usuario)
USERNAME = "hpsupersu"
PASSWORD = "loanaP25@"

def run_integration_tests():
    print("=" * 60)
    print(f"TEST INTEGRACIÓN: {BASE_URL}")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. LOGIN
    print("\n1. Intentando Login con hpsupersu...")
    try:
        # Obtener página de login para extraer CSRF token
        print("   ⏳ Obteniendo página de login para CSRF token...")
        login_page_response = session.get(LOGIN_URL)
        
        csrf_token = None
        # Intento robusto de extracción de CSRF con regex
        import re
        # Buscar input con name="csrf_token"
        token_match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]*)"', login_page_response.text)
        if not token_match:
             # Intentar orden inverso de atributos
             token_match = re.search(r'<input[^>]*value="([^"]*)"[^>]*name="csrf_token"', login_page_response.text)
             
        if token_match:
            csrf_token = token_match.group(1)
            print(f"   ✅ CSRF Token encontrado: {csrf_token[:10]}...")
        else:
            print("   ⚠️ No se encontró CSRF token. Imprimiendo parte del HTML para depurar:")
            print(login_page_response.text[:1000]) # Imprimir primeros 1000 chars
        
        payload = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        if csrf_token:
            payload["csrf_token"] = csrf_token
        
        headers = {
            "Referer": LOGIN_URL,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = session.post(LOGIN_URL, data=payload, headers=headers)
        
        if response.status_code == 200:
            # En login exitoso, Flask puede redirigir. Requests sigue redirecciones por defecto.
            # Verificamos si llegamos al dashboard o admin.
            if "dashboard" in response.url or "admin" in response.url or "Bienvenido" in response.text or "Panel" in response.text:
                 print("   ✅ Login EXITOSO.")
            else:
                 # A veces el login falla y devuelve la misma página de login con error
                 if "Credenciales incorrectas" in response.text:
                     print("   ❌ Login FALLÓ: Credenciales incorrectas.")
                     return False
                 elif "Bloqueada" in response.text:
                     print("   ❌ Login FALLÓ: Cuenta bloqueada.")
                     return False
                 else:
                     print(f"   ⚠️ Login completado pero respuesta ambigua. URL actual: {response.url}")
        else:
            print(f"   ❌ Error en petición Login: {response.status_code}")
            print(f"   📄 Contenido respuesta error: {response.text[:500]}") # Ver qué dice Flask
            return False
            
    except Exception as e:
        print(f"   ❌ Excepción durante Login: {e}")
        return False

    # 2. VERIFICAR SESIÓN (DASHBOARD)
    print("\n2. Verificando acceso a Dashboard Protegido...")
    try:
        response = session.get(DASHBOARD_URL)
        if response.status_code == 200 and "login" not in response.url:
            print("   ✅ Acceso a Dashboard autorizado.")
        else:
            print(f"   ❌ Fallo acceso a Dashboard. URL: {response.url}, Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # 3. VERIFICAR ADMIN
    print("\n3. Verificando acceso a Panel de Administración...")
    try:
        response = session.get(ADMIN_URL)
        if response.status_code == 200:
            if "Admin" in response.text or "Usuarios" in response.text:
                print("   ✅ Acceso Admin verificado.")
            else:
                print("   ⚠️ Acceso Admin posible pero contenido no reconocido.")
        elif response.status_code == 403:
            print("   ❌ Acceso Denegado (403) - Rol insuficiente?")
            return False
        else:
            print(f"   ❌ Error acceso Admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    # 4. VERIFICAR SCORING
    print("\n4. Verificando acceso a Módulo Scoring...")
    try:
        response = session.get(SCORING_URL)
        if response.status_code == 200:
             print("   ✅ Acceso Scoring verificado.")
        else:
             print(f"   ❌ Error acceso Scoring: {response.status_code}")
             return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    print("\n" + "=" * 60)
    print("VEREDICTO FINAL: INTEGRACIÓN EXITOSA")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
