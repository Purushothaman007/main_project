FROM alpine:3.19

# Install GCC compiler toolchain and standard C++ libraries
RUN apk add --no-cache g++ musl-dev libstdc++

# Create non-root sandbox user
RUN addgroup -S sandbox && adduser -S sandbox -G sandbox -u 1000

WORKDIR /app

RUN chown -R sandbox:sandbox /app

USER sandbox

CMD ["g++"]
