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
        // Get database configuration from environment variables
        this.dbUrl = getEnv("DATABASE_URL", "jdbc:postgresql://localhost:5432/order_db");
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