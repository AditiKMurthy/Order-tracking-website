// Listens to Kafka.
package com.omnistream;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;

import java.util.Collections;
import java.util.Properties;

public class Consumer {
    public static KafkaConsumer<String, String> createConsumer() {
        // Get Kafka configuration from environment variables
        String bootstrapServers = System.getenv("KAFKA_BOOTSTRAP_SERVERS");
        if (bootstrapServers == null || bootstrapServers.isEmpty()) {
            bootstrapServers = "localhost:9092"; // Fallback for development
        }
        
        String consumerGroup = System.getenv("KAFKA_CONSUMER_GROUP");
        if (consumerGroup == null || consumerGroup.isEmpty()) {
            consumerGroup = "java-processor-group"; // Fallback for development
        }
        
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, consumerGroup);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        // Optional SASL configurations for Cloud Kafka
        String saslMechanism = System.getenv("KAFKA_SASL_MECHANISM");
        String securityProtocol = System.getenv("KAFKA_SECURITY_PROTOCOL");
        String saslJaasConfig = System.getenv("KAFKA_SASL_JAAS_CONFIG");
        
        if (saslMechanism != null && !saslMechanism.isEmpty()) {
            props.put("security.protocol", securityProtocol != null ? securityProtocol : "SASL_SSL");
            props.put("sasl.mechanism", saslMechanism);
            props.put("sasl.jaas.config", saslJaasConfig);
        }

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Collections.singletonList("order-events"));
        return consumer;
    }
}