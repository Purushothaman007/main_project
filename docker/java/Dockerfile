FROM eclipse-temurin:17-jdk-alpine

# Create non-root sandbox user
RUN addgroup -S sandbox && adduser -S sandbox -G sandbox -u 1000

WORKDIR /app

RUN chown -R sandbox:sandbox /app

USER sandbox

CMD ["java"]
