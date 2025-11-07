#!/bin/bash
# GCP VM Setup Script - Run this on your GCP VM after first SSH connection
# This automates the setup process from the deployment guide

set -e  # Exit on error

echo "🚀 Starting GCP Mental Health Chatbot Setup..."
echo "================================================"

# Install required packages
echo "📦 Installing Python packages..."
pip install -q transformers torch accelerate fastapi uvicorn python-multipart huggingface_hub

# Create working directory
echo "📁 Creating working directory..."
mkdir -p ~/mental-health-chatbot
cd ~/mental-health-chatbot

# Download model from Cloud Storage
echo "⬇️  Downloading model from Google Cloud Storage..."
echo "   (This may take 10-15 minutes depending on file size)"
gsutil cp gs://mental-health-model-storage/merged_mental_health_model.zip .

# Unzip model
echo "📂 Extracting model files..."
unzip -q merged_mental_health_model.zip

# Verify files
echo "✅ Verifying model files..."
if [ -d "merged_mental_health_model" ]; then
    echo "   Model directory found:"
    ls -lh merged_mental_health_model/ | head -5
else
    echo "❌ Error: Model directory not found!"
    exit 1
fi

# Download server code
echo "⬇️  Downloading server code..."
gsutil cp gs://mental-health-model-storage/fastapi_server.py .
gsutil cp gs://mental-health-model-storage/requirements.txt .

# Install additional dependencies from requirements
echo "📦 Installing additional dependencies..."
pip install -q -r requirements.txt

# Create startup script
echo "📝 Creating startup script..."
cat > start_server.sh << 'EOF'
#!/bin/bash
cd ~/mental-health-chatbot
export MODEL_PATH=./merged_mental_health_model
nohup python fastapi_server.py > server.log 2>&1 &
echo "✅ Server started in background!"
echo "📋 Check logs with: tail -f ~/mental-health-chatbot/server.log"
sleep 2
EXTERNAL_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
echo "🌐 Access your API at: http://${EXTERNAL_IP}:8000"
echo "📖 API docs at: http://${EXTERNAL_IP}:8000/docs"
EOF

chmod +x start_server.sh

# Create stop script
echo "📝 Creating stop script..."
cat > stop_server.sh << 'EOF'
#!/bin/bash
pkill -f "python fastapi_server.py"
echo "🛑 Server stopped."
EOF

chmod +x stop_server.sh

# Create status check script
echo "📝 Creating status check script..."
cat > check_status.sh << 'EOF'
#!/bin/bash
if pgrep -f "python fastapi_server.py" > /dev/null; then
    echo "✅ Server is running"
    EXTERNAL_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
    echo "🌐 API URL: http://${EXTERNAL_IP}:8000"
    echo "📖 Docs URL: http://${EXTERNAL_IP}:8000/docs"
    echo ""
    echo "Recent logs:"
    tail -20 ~/mental-health-chatbot/server.log
else
    echo "❌ Server is not running"
    echo "Start with: ./start_server.sh"
fi
EOF

chmod +x check_status.sh

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Start the server:    ./start_server.sh"
echo "2. Check status:        ./check_status.sh"
echo "3. View logs:           tail -f server.log"
echo "4. Stop server:         ./stop_server.sh"
echo ""
echo "Wait 2-3 minutes after starting for model to load into GPU memory."
echo "================================================"
