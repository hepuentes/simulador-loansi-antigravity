
import requests
import re
import time

BASE_URL = "http://127.0.0.1:5000"

try:
    s = requests.Session()
    print("Getting /login...")
    r = s.get(f"{BASE_URL}/login")
    print(f"Status: {r.status_code}")
    if r.status_code != 200:
        print(r.text)
        exit()
    
    csrf_match = re.search(r'name="csrf_token" value="(.*?)"', r.text)
    if not csrf_match:
        print("No CSRF token found")
        exit()
    token = csrf_match.group(1)
    print(f"Token: {token}")

    print("Posting to /login...")
    r = s.post(f"{BASE_URL}/login", data={
        "csrf_token": token,
        "username": "hpsupersu",
        "password": "loanaP25@"
    })
    print(f"Login Status: {r.status_code}")
    print(f"Login URL: {r.url}")
    
    if r.status_code == 500:
        print("Server Error Content:")
        print(r.text)

except Exception as e:
    print(f"Exception: {e}")
