# Stage 1: Build the Java App using a Maven container
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package

# Stage 2: Run the built JAR using the stable Eclipse Temurin Java 17 container
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/backend-processor-1.0-SNAPSHOT-jar-with-dependencies.jar app.jar

# Explicitly tell the container to wait for Kafka & Postgres to be up
CMD ["java", "-jar", "app.jar"]