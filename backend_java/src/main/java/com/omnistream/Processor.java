// Calculates the delivery date.
package com.omnistream;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.json.JSONObject;
import redis.clients.jedis.Jedis;

import java.time.Duration;
import java.time.LocalDate;

public class Processor {
    public static void main(String[] args) {
        KafkaConsumer<String, String> consumer = Consumer.createConsumer();
        Repository repository = new Repository();
        
        // Get Redis configuration from environment variables
        String redisHost = System.getenv("REDIS_HOST");
        if (redisHost == null || redisHost.isEmpty()) {
            redisHost = "localhost"; // Fallback for development
        }
        
        String redisPortStr = System.getenv("REDIS_PORT");
        int redisPort = 6379; // Default port
        if (redisPortStr != null && !redisPortStr.isEmpty()) {
            try {
                redisPort = Integer.parseInt(redisPortStr);
            } catch (NumberFormatException e) {
                System.err.println("Invalid REDIS_PORT value: " + redisPortStr);
            }
        }
        
        // Connect to Redis Speed Layer
        try (Jedis jedis = new Jedis(redisHost, redisPort)) {
            System.out.println("Java Background Engine is running and monitoring 'order-events' conveyor belt...");

            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                for (ConsumerRecord<String, String> record : records) {
                    try {
                        JSONObject orderEvent = new JSONObject(record.value());
                        int orderId = orderEvent.getInt("order_id");
                        
                        // Fake delivery calculation engine logic
                        String syntheticDeliveryDate = LocalDate.now().plusDays(3).toString();
                        String processStatus = "PROCESSED";

                        // 1. Persist Update inside main operational database
                        repository.updateOrder(orderId, syntheticDeliveryDate, processStatus);

                        // 2. Synchronize Speed Layer (Cache write-through)
                        jedis.set("order:status:" + orderId, processStatus);
                        jedis.set("order:delivery:" + orderId, syntheticDeliveryDate);
                        System.out.println("[Redis] Hydrated Speed Layer cache for Order ID " + orderId);

                    } catch (Exception e) {
                        System.err.println("Failed processing event index entry: " + e.getMessage());
                    }
                }
            }
        }
    }
}