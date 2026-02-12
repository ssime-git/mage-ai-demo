FROM mageai/mageai:0.9.79

# Install jq and other useful tools
USER root
RUN apt-get update && apt-get install -y \
    jq \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /home/src
