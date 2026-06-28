// Saves to Postgres.
package com.omnistream;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;

public class Repository {
    private final String dbUrl;
    private final String user;
    private final String password;
    
    public Repository() {
        // Check for DATABASE_URL first, fallback to POSTGRES_URL if set by compose
        String rawDbUrl = System.getenv("DATABASE_URL");
        if (rawDbUrl == null || rawDbUrl.isEmpty()) {
            rawDbUrl = System.getenv("POSTGRES_URL");
        }
        if (rawDbUrl == null || rawDbUrl.isEmpty()) {
            rawDbUrl = "jdbc:postgresql://localhost:5432/order_db";
        }
        
        // Handle postgresql:// vs jdbc:postgresql:// format for JDBC
        if (rawDbUrl.startsWith("postgresql://")) {
            rawDbUrl = "jdbc:" + rawDbUrl;
        }
        this.dbUrl = rawDbUrl;
        
        this.user = getEnv("POSTGRES_USER", "postgres");
        this.password = getEnv("POSTGRES_PASSWORD", "password");
    }
    
    /**
     * Helper method to get environment variable with fallback
     */
    private String getEnv(String key, String defaultValue) {
        String value = System.getenv(key);
        if (value == null || value.isEmpty()) {
            System.out.println("[Config] Using default for " + key);
            return defaultValue;
        }
        return value;
    }

    public void updateOrder(int orderId, String deliveryDate, String status) {
        String query = "UPDATE orders SET status = ?, delivery_date = ? WHERE id = ?";
        try (Connection conn = DriverManager.getConnection(dbUrl, user, password);
             PreparedStatement pstmt = conn.prepareStatement(query)) {
            
            pstmt.setString(1, status);
            pstmt.setString(2, deliveryDate);
            pstmt.setInt(3, orderId);
            pstmt.executeUpdate();
            System.out.println("[Postgres] Updated Order ID " + orderId + " to status " + status);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}