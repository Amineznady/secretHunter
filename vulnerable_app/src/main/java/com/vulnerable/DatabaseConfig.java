package com.vulnerable;

public class DatabaseConfig {

    // Connexion MySQL avec mot de passe
    private static final String DB_URL = "jdbc:mysql://db.company.com:3306/production_db";
    private static final String DB_USER = "admin_user";
    private static final String DB_PASSWORD = "P@ssw0rd123!Hardcoded";
    
    // MongoDB
    private static final String MONGODB_URI = "mongodb+srv://admin:MyMongoPass2025@cluster0.mongodb.net/mydb";
    
    // PostgreSQL
    private static final String POSTGRES_CONNECTION = "postgresql://postgres:SecurePostgres2025!@db-server.internal:5432/secure_db";
    
    // Redis
    private static final String REDIS_URL = "redis://redis-admin:RedisPass123@cache.example.com:6379";
    
    // Informations sensibles
    public static final String COMPANY_EMAIL = "admin@confidential-company.com";
    public static final String SUPPORT_EMAIL = "support@confidential-company.com";
    public static final String DBA_EMAIL = "dba-team@confidential-company.com";
    
    // Clé API AWS
    private static final String AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE";
    private static final String AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";
    
    // Endpoint privé
    private static final String AWS_S3_BUCKET = "s3://secure-bucket-prod-2025/confidential/";
    
    public String getConnectionString() {
        return DB_URL + "?user=" + DB_USER + "&password=" + DB_PASSWORD;
    }
}
