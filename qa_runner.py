
import requests
import re
# from bs4 import BeautifulSoup # Assuming available? No.
# We will use regex as before.

BASE_URL = "http://127.0.0.1:5000"
USERNAME = "hpsupersu"
PASSWORD = "loanaP25@"

s = requests.Session()

def login():
    try:
        r = s.get(f"{BASE_URL}/login")
        csrf_match = re.search(r'name="csrf_token" value="(.*?)"', r.text)
        if not csrf_match:
            print("❌ No CSRF token")
            return False
        token = csrf_match.group(1)
        r = s.post(f"{BASE_URL}/login", data={
            "csrf_token": token,
            "username": USERNAME,
            "password": PASSWORD
        }, allow_redirects=False)
        return r.status_code in [200, 302]
    except Exception as e:
        print(f"Login error: {e}")
        return False

def get_field_map():
    r = s.get(f"{BASE_URL}/scoring")
    mapping = {}
    html = r.text
    label_indices = [m.start() for m in re.finditer(r'<label', html)]
    for i, idx in enumerate(label_indices):
        next_idx = label_indices[i+1] if i+1 < len(label_indices) else len(html)
        snippet = html[idx:next_idx]
        label_match = re.search(r'<label[^>]*>(.*?)</label>', snippet, re.DOTALL)
        if label_match:
            label_text = re.sub(r'<[^>]+>', '', label_match.group(1)).strip()
            
            # Check for select
            select_match = re.search(r'<select[^>]*name="([^"]*)"[^>]*>(.*?)</select>', snippet, re.DOTALL)
            if select_match:
                name = select_match.group(1)
                options_html = select_match.group(2)
                options = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', options_html, re.DOTALL)
                # options is list of (value, text)
                mapping[label_text] = {"name": name, "type": "select", "options": options}
            else:
                input_match = re.search(r'name="([^"]*)"', snippet)
                if input_match:
                    name = input_match.group(1)
                    mapping[label_text] = {"name": name, "type": "input"}
    return mapping

def run_case(case_name, data, field_map):
    print(f"\nRunning {case_name}...")
    payload = {}
    
    # Static fields
    payload["nombre_cliente"] = "QA Test User"
    payload["cedula"] = "12345"
    payload["nombre_cliente_nombre"] = "QA Test User"
    payload["nombre_cliente_cedula"] = "12345"

    def find_field_info(partial):
        for k, v in field_map.items():
            if partial.lower() in k.lower():
                return v
        return None

    for label_kw, value in data.items():
        info = find_field_info(label_kw)
        if info:
            key = info["name"]
            val_to_send = value
            
            if info["type"] == "select":
                # Find best matching option
                best_match = None
                # Check exact value match 
                for opt_val, opt_text in info["options"]:
                    if value.lower() == opt_val.lower():
                        best_match = opt_val
                        break
                # Check exact text match
                if not best_match:
                    for opt_val, opt_text in info["options"]:
                        if value.lower() in opt_text.lower():
                            best_match = opt_val
                            break
                
                if best_match:
                    val_to_send = best_match
                    print(f"  Matched '{value}' to option '{best_match}' for code '{key}'")
                else:
                    print(f"Warning: No option match for '{value}' in {key}. Options: {[o[1] for o in info['options'][:5]]}...")
            
            payload[key] = val_to_send
        else:
            print(f"⚠️ Could not map '{label_kw}'")

    # Special handling
    # Linea de credito might need specific handling if the select has IDs
    # But usually <option value="Name">Name</option>
    
    # Handle 'linea_credito' vs 'tipo_credito' ambiguity
    if "tipo_credito" in payload:
        payload["linea_credito"] = payload["tipo_credito"]
    
    # Send request
    # Need CSRF?
    # Usually getting the form first gives us a token?
    # We are using session, but HTMX or Flask-WTF might need it.
    # The /scoring page likely has a csrf_token hidden input.
    # We'll re-fetch scoring to get fresh token if needed, or just hope session cookie is enough (it's not for POST).
    
    # Fetch scoring again to get CSRF
    r_form = s.get(f"{BASE_URL}/scoring")
    csrf_match = re.search(r'name="csrf_token" value="(.*?)"', r_form.text)
    if csrf_match:
        payload["csrf_token"] = csrf_match.group(1)
    
    # POST
    r = s.post(f"{BASE_URL}/scoring", data=payload)
    
    # Analyze result
    if "Resultado de Scoring" in r.text or "Aprobado" in r.text or "Rechazado" in r.text:
        print("Response received")
        
        # Extract Score, Risk, Decision
        score_match = re.search(r'Score:.*?(\d+)', r.text) # Regex might need tuning
        # In the HTML, score is usually in a div with class "score-value" or similar
        # <div class="score-display">867</div>
        score_val = re.search(r'class="score-display[^"]*">\s*(\d+)', r.text)
        
        risk_val = re.search(r'class="badge risk-badge[^"]*">\s*(.*?)\s*</span>', r.text, re.DOTALL)
        
        decision = "Rechazado"
        if "APROBADO" in r.text.upper():
            decision = "Aprobado"
        elif "COMITÉ" in r.text.upper() or "COMITE" in r.text.upper():
            decision = "Comité"
            
        print(f"  Score: {score_val.group(1) if score_val else 'Unknown'}")
        print(f"  Risk: {risk_val.group(1).encode('ascii','replace').decode() if risk_val else 'Unknown'}")
        print(f"  Decision: {decision}")
        # print snippet of risk
        # We'll dump the text around "Nivel de Riesgo"
        
    else:
        print(f"Failed? status: {r.status_code}")
        if r.status_code == 500:
            print("Server Error")
        else:
             print("  Could not find recognizable result indicators.")
             # Check for validation errors
             if "alert" in r.text:
                 err = re.search(r'alert-[a-z]+[^>]*>(.*?)</div>', r.text, re.DOTALL)
                 msg = re.sub(r'<[^>]+>', '', err.group(1)).strip() if err else 'Unknown'
                 print(f"  Alert Found: {msg.encode('ascii','replace').decode()}")
             else:
                 title_match = re.search(r'<title>(.*?)</title>', r.text)
                 title = title_match.group(1) if title_match else "No Title"
                 print("  Page Title:", title.encode('ascii','replace').decode())
                 # Dump clean text
                 print("--- BODY START ---")
                 clean_text = re.sub(r'<[^>]+>', ' ', r.text)
                 print(clean_text[:2000].encode('ascii', 'replace').decode())
                 print("--- BODY END ---")

# Define Cases
case_a = {
    "Linea de Crédito": "LoansiFlex",
    "Edad": "51",
    "Puntaje DataCrédito": "867",
    "Ingreso Estimado": "1286000",
    "Cuota Mensual": "46",
    "Manejo TDC": "81-100%",
    "Comportamiento": "12",
    "Mora Reciente": "0",
    "Créditos Cerrados": "8",
    "Créditos Vigentes": "4",
    "Cupo Inicial": "24000000",
    "Saldo Actual": "20273000",
    "Saldo Actual vs Cupo": "84",
    "Tipo de Empleo": "Empleado indefinido",
    "Sector Económico": "Comercio",
    "Antigüedad Laboral": "36",
    "Coherencia Ingreso": "1423500",
    "Tipo de Vivienda": "Propia con hipoteca",
    "Destino del Crédito": "Libre inversión",
    "Verificación Documental": "Completa y formal",
    "Consultas Últimos": "1",
    "Monto Solicitado": "4000000"
}

case_b = {
    "Linea de Crédito": "LoansiMoto",
    "Edad": "23",
    "Puntaje DataCrédito": "450",
    "Ingreso Estimado": "2100000",
    "Cuota Mensual": "18",
    "Manejo TDC": "0-20%", # approximate for 'No tiene'
    "Comportamiento": "8",
    "Mora Reciente": "1",
    "Créditos Cerrados": "0",
    "Créditos Vigentes": "1",
    "Cupo Inicial": "0",
    "Saldo Actual": "500000",
    "Saldo Actual vs Cupo": "0",
    "Tipo de Empleo": "Independiente",
    "Sector Económico": "Transporte",
    "Antigüedad Laboral": "8",
    "Coherencia Ingreso": "1800000",
    "Tipo de Vivienda": "Familiar",
    "Destino del Crédito": "Vehículo", # 'Compra de Moto' -> Vehículo
    "Verificación Documental": "básica", # 'Parcial' -> Documentación básica...
    "Consultas Últimos": "5",
    "Monto Solicitado": "2000000"
}

case_c = {
    "Linea de Crédito": "LoansiFlex",
    "Edad": "62",
    "Puntaje DataCrédito": "920",
    "Ingreso Estimado": "8500000",
    "Cuota Mensual": "12",
    "Manejo TDC": "0-20%",
    "Comportamiento": "12",
    "Mora Reciente": "0",
    "Créditos Cerrados": "15",
    "Créditos Vigentes": "2",
    "Cupo Inicial": "50000000",
    "Saldo Actual": "2000000",
    "Saldo Actual vs Cupo": "4",
    "Tipo de Empleo": "Independiente", # 'Pensionado' not in options, using Independiente
    "Sector Económico": "Financiero", # Or Pensionado if available as sector
    "Antigüedad Laboral": "120",
    "Coherencia Ingreso": "8500000",
    "Tipo de Vivienda": "Propia sin deuda",
    "Destino del Crédito": "Libre inversión", # 'Otros' -> Libre inversión
    "Verificación Documental": "Completa",
    "Consultas Últimos": "0",
    "Monto Solicitado": "10000000"
}

if __name__ == "__main__":
    if login():
        fmap = get_field_map()
        run_case("Case A", case_a, fmap)
        run_case("Case B", case_b, fmap)
        run_case("Case C", case_c, fmap)
    else:
        print("Login failed")
