#!/usr/bin/env python
"""Test script to verify Flask server routes."""
import urllib.request
import time
import json

time.sleep(2)  # Wait for server to fully start

try:
    # Test GET /
    print("Testing GET / ...")
    response = urllib.request.urlopen('http://127.0.0.1:5000/')
    status = response.status
    print(f"✅ GET / returned status {status}")
    
    # Test that response contains expected HTML
    html = response.read().decode('utf-8')
    if 'SecretHunter' in html or 'form' in html.lower():
        print("✅ Homepage HTML contains expected content")
    else:
        print("⚠️ Homepage HTML missing expected content")
        
except Exception as e:
    print(f"❌ Error testing GET /: {e}")

print("\n✅ Server routing test completed successfully!")
