#!/bin/bash
set -e

echo "🚀 AI Platform Deploy Script"
echo "====================================="
echo "📌 Mode: Deterministic (Temp=0, Seed=40)"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
fi

# Install Ollama if not present
if ! command -v ollama &> /dev/null; then
    echo "📦 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✅ Ollama installed"
fi

# Pull model
echo "🤖 Pulling Llama 3.2 7B model..."
ollama pull llama3.2:7b
echo "✅ Model ready"

# Clone or update repo
if [ ! -d "/opt/ai-platform" ]; then
    echo "📂 Cloning repository..."
    sudo mkdir -p /opt/ai-platform
    sudo chown -R $USER:$USER /opt/ai-platform
    git clone https://github.com/yourusername/ai-platform.git /opt/ai-platform
else
    echo "📂 Updating repository..."
    cd /opt/ai-platform
    git pull
fi

# Create .env file
cd /opt/ai-platform
cat > .env << 'EOF'
MODEL_NAME=llama3.2:7b
MODEL_TEMPERATURE=0.0
MODEL_SEED=40
MODEL_TOP_P=0.95
MODEL_MAX_TOKENS=4096
CACHE_ENABLED=true
ENABLE_ACCURACY_SCORING=true
LOG_LEVEL=INFO
EOF

# Start services
echo "🚀 Starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services..."
sleep 15

# Health check
echo "🔍 Health check..."
curl -f http://localhost:8000/health || echo "⚠️ Health check failed"

echo ""
echo "✅ Deployment complete!"
echo "====================================="
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔍 Health: http://localhost:8000/health"
echo ""
echo "📌 Mode: Deterministic (Temp=0, Seed=40)"
echo "====================================="
