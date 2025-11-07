"""
Quick reference commands for managing your GCP Mental Health Chatbot deployment.
Copy and paste these into your terminal as needed.
"""

# ============================================================================
# LOCAL MACHINE COMMANDS (Windows)
# ============================================================================

# 1. Zip your model folder
"""
cd "c:\\Users\\raghav khandelwal\\Desktop\\mistral7b"
python zip_merged_model.py
"""

# 2. Upload to GCP Cloud Storage (using gsutil - install Google Cloud SDK first)
"""
gsutil cp merged_mental_health_model.zip gs://mental-health-model-storage/
gsutil cp fastapi_server.py gs://mental-health-model-storage/
gsutil cp requirements.txt gs://mental-health-model-storage/
gsutil cp gcp_vm_setup.sh gs://mental-health-model-storage/
"""

# ============================================================================
# GCP VM COMMANDS (via SSH terminal)
# ============================================================================

# 1. One-command setup (after first SSH connection)
"""
curl -O https://storage.googleapis.com/mental-health-model-storage/gcp_vm_setup.sh
bash gcp_vm_setup.sh
"""

# OR download setup script from Cloud Storage
"""
gsutil cp gs://mental-health-model-storage/gcp_vm_setup.sh .
bash gcp_vm_setup.sh
"""

# 2. Start the server
"""
cd ~/mental-health-chatbot
./start_server.sh
"""

# 3. Check server status
"""
./check_status.sh
"""

# 4. View server logs (live)
"""
tail -f ~/mental-health-chatbot/server.log
"""

# 5. Stop the server
"""
./stop_server.sh
"""

# 6. Check GPU status
"""
nvidia-smi
"""

# 7. Get your external IP
"""
curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"
"""

# 8. Test API from VM
"""
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help with anxiety"}'
"""

# 9. Check if server is running
"""
ps aux | grep fastapi
"""

# 10. Restart server
"""
./stop_server.sh
./start_server.sh
"""

# ============================================================================
# GCLOUD CLI COMMANDS (from local machine, if you install Google Cloud SDK)
# ============================================================================

# Install Google Cloud SDK:
# https://cloud.google.com/sdk/docs/install

# 1. SSH into your VM
"""
gcloud compute ssh mental-health-chatbot-vm --zone=us-central1-a
"""

# 2. Copy files to VM
"""
gcloud compute scp fastapi_server.py mental-health-chatbot-vm:~/mental-health-chatbot/ --zone=us-central1-a
"""

# 3. Start VM (if stopped)
"""
gcloud compute instances start mental-health-chatbot-vm --zone=us-central1-a
"""

# 4. Stop VM (to save credits)
"""
gcloud compute instances stop mental-health-chatbot-vm --zone=us-central1-a
"""

# 5. Get VM external IP
"""
gcloud compute instances describe mental-health-chatbot-vm --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
"""

# 6. View VM info
"""
gcloud compute instances describe mental-health-chatbot-vm --zone=us-central1-a
"""

# ============================================================================
# COST MONITORING
# ============================================================================

# Check current billing (via gcloud)
"""
gcloud billing accounts list
gcloud billing projects describe YOUR_PROJECT_ID
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

# If model loading fails (out of memory), check available memory:
"""
free -h
nvidia-smi
"""

# If port 8000 is already in use:
"""
lsof -i :8000
kill -9 PID_NUMBER
"""

# View all Python processes:
"""
ps aux | grep python
"""

# Check disk space:
"""
df -h
"""

# Check if firewall is blocking:
"""
sudo iptables -L -n
"""

# ============================================================================
# USEFUL GCP CONSOLE LINKS
# ============================================================================

"""
Compute Engine VM Instances:
https://console.cloud.google.com/compute/instances

Cloud Storage Buckets:
https://console.cloud.google.com/storage/browser

VPC Firewall Rules:
https://console.cloud.google.com/networking/firewalls/list

Billing & Cost Management:
https://console.cloud.google.com/billing

Quotas (for GPU access):
https://console.cloud.google.com/iam-admin/quotas

Monitoring & Logging:
https://console.cloud.google.com/logs/query
"""

print("📋 Quick Reference Commands loaded!")
print("Copy and paste commands from this file as needed.")
