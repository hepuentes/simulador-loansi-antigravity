
import requests
import re

BASE_URL = "http://127.0.0.1:5000"
USERNAME = "hpsupersu"
PASSWORD = "loanaP25@"

s = requests.Session()

def login():
    # Get login page to get CSRF token
    r = s.get(f"{BASE_URL}/login")
    csrf_match = re.search(r'name="csrf_token" value="(.*?)"', r.text)
    if not csrf_match:
        print("❌ Could not find CSRF token on login page")
        return False
    csrf_token = csrf_match.group(1)

    # Login
    login_data = {
        "csrf_token": csrf_token,
        "username": USERNAME,
        "password": PASSWORD
    }
    r = s.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
    if "dashboard" in r.url or "Redirecting" in r.text or r.status_code == 302 or r.status_code == 200:
        # Check if we are really logged in by hitting a protected route
        check = s.get(f"{BASE_URL}/scoring")
        if check.status_code == 200 and "login" not in check.url:
            print("✅ Logged in successfully")
            return True
        else:
            print(f"❌ Login verify failed. URL: {check.url}")
            print("Trying to proceed anyway...")
            return True
    else:
        print(f"❌ Login failed. Status: {r.status_code}, URL: {r.url}")
        # print(r.text[:500])
        return False

def discover_scoring_fields():
    r = s.get(f"{BASE_URL}/scoring")
    if r.status_code != 200:
        print(f"❌ Failed to get scoring page: {r.status_code}")
        return

    print("\n--- Field Mapping ---")
    # Clean HTML a bit
    html = r.text.replace('\n', ' ')
    
    # Regex to find label and then the next input/select
    # Pattern: <label ...>TEXT</label> ... <(input|select) ... name="NAME"
    
    print("\n--- Field Mapping (Robust) ---")
    html = r.text
    # Find all labels
    label_indices = [m.start() for m in re.finditer(r'<label', html)]
    
    for i, idx in enumerate(label_indices):
        # Snippet from this label to the next label (or end)
        next_idx = label_indices[i+1] if i+1 < len(label_indices) else len(html)
        snippet = html[idx:next_idx]
        
        # Get label text
        label_match = re.search(r'<label[^>]*>(.*?)</label>', snippet, re.DOTALL)
        if label_match:
            label_text = re.sub(r'<[^>]+>', '', label_match.group(1)).strip()
            
            # Get input name
            input_match = re.search(r'name="([^"]*)"', snippet)
            if input_match:
                name = input_match.group(1)
                print(f"'{label_text}' -> '{name}'")

if __name__ == "__main__":
    if login():
        discover_scoring_fields()
