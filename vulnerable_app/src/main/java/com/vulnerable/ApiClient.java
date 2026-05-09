package com.vulnerable;

public class ApiClient {

    // Clé API Google Maps - HARDCODÉE !
    private static final String GOOGLE_MAPS_KEY = "AIzaSyDx-wNqRsPc7VwhQZqFeXzM0xVfYnWmWNY";
    
    // Token Stripe hardcodé
    private static final String STRIPE_KEY = "sk_live_YOUR_FAKE_STRIPE_KEY_HERE_12345FAKE";
    
    // Token Firebase
    private static final String FIREBASE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE2ZTkxNGU0NTc0ZTc1ODQzOTYyZWM2OTUzYTdmOWU5YzU5ODBjZWEifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhdWQiOiJodHRwczovL2lkZW50aXR5dG9vbGtpdC5nb29nbGVhcGlzLmNvbS9nb29nbGUuaWRlbnRpdHkuaWRlbnRpdHl0b29sa2l0LnYxLklkZW50aXR5VG9vbGtpdCIsInN1YiI6IjExMzE5NzA2NTA4NTk4MTUwNzE2IiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiItSmoxR0IyREE3TlZSdzNIdHdFUUx3In0.signature";
    
    // URL API privée
    private static final String API_BASE_URL = "https://api.internal-server.com/v2/secure";
    
    // Clé secrète pour signature
    private static final String SECRET_KEY = "MyVerySecureSecret123!@#$%^&*()_+-=[]{}|;:,.<>?";
    
    // Mot de passe administrateur
    private static final String ADMIN_PASSWORD = "Admin@2025!SecurePass";
    
    // Connection OAuth Token
    private static final String OAUTH_TOKEN = "ya29.a0AfH6SMBx8P8Z9L5M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z";
    
    public void initializeApi() {
        // Utilisation des différentes clés
        String url = API_BASE_URL + "?key=" + GOOGLE_MAPS_KEY;
        String auth = "Bearer " + STRIPE_KEY;
        
        // Appel API avec le secret
        callSecureEndpoint(url, auth, SECRET_KEY);
    }
    
    private void callSecureEndpoint(String url, String auth, String secret) {
        // Implémentation
    }
}
