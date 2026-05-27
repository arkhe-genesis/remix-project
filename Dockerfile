FROM ubuntu:22.04

# Install necessary build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone llama.cpp repository
WORKDIR /app
RUN git clone https://github.com/ggerganov/llama.cpp.git .

# Build llama-server
RUN make server

# Copy the GGUF model into the container
# This assumes arkhe-os.gguf is available in the build context
COPY arkhe-os.gguf /app/models/arkhe-os.gguf

# Expose port 8080 for the server
EXPOSE 8080

# Run llama-server when the container launches
ENTRYPOINT ["/app/llama-server", "-m", "/app/models/arkhe-os.gguf", "--host", "0.0.0.0", "--port", "8080"]
