import requests

# Test the homepage
print("Testing GET / ...")
try:
    r = requests.get("http://127.0.0.1:5000/")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("✅ Homepage loaded successfully")
    if 'SecretHunter' in r.text or 'upload' in r.text.lower():
        print("✅ Homepage contains expected content")
except Exception as e:
    print(f"❌ Error: {e}")
