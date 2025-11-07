# Deploy Mistral-7B Mental Health Model to Google Cloud Platform

## Complete Step-by-Step Guide

This guide will help you deploy your mental health chatbot to Google Cloud Platform (GCP) using your $300 free credit.

---

## Part 1: Initial GCP Setup (5-10 minutes)

### Step 1: Access Google Cloud Console
1. Go to https://console.cloud.google.com/
2. Sign in with your Google account
3. If this is your first time, you'll be prompted to activate the $300 free credit
   - Click "Activate" or "Try for Free"
   - Enter billing information (required but you won't be charged unless you upgrade)

### Step 2: Create a New Project
1. In the top navigation bar, click the project dropdown (next to "Google Cloud")
2. Click "NEW PROJECT"
3. Enter project details:
   - **Project name:** `mental-health-chatbot`
   - **Project ID:** Will auto-generate (note this down)
4. Click "CREATE"
5. Wait for project creation (30 seconds)
6. Select your new project from the project dropdown

### Step 3: Enable Required APIs
1. Go to **Navigation Menu (☰)** → **APIs & Services** → **Library**
2. Search for and enable these APIs (click "ENABLE" for each):
   - **Compute Engine API** (for virtual machines)
   - **Cloud Storage API** (for file storage)
   - Click "Enable" and wait ~30 seconds for each

---

## Part 2: Upload Your Model to Google Cloud Storage (15-30 minutes)

### Step 4: Create Cloud Storage Bucket
1. Go to **Navigation Menu (☰)** → **Cloud Storage** → **Buckets**
2. Click "CREATE BUCKET"
3. Configure bucket:
   - **Name:** `mental-health-model-storage` (must be globally unique)
   - **Location type:** Region
   - **Region:** `us-central1` (cheapest option)
   - **Storage class:** Standard
   - **Access control:** Uniform
4. Click "CREATE"

### Step 5: Upload Your Model Files
1. First, zip your model on your local machine:
   ```cmd
   cd "c:\Users\raghav khandelwal\Desktop\mistral7b"
   python zip_merged_model.py
   ```

2. In GCP Console, open your bucket `mental-health-model-storage`
3. Click "UPLOAD FILES"
4. Select `merged_mental_health_model.zip`
5. Wait for upload to complete (this uses Google's fast upload - much faster than HuggingFace)

---

## Part 3: Create CPU-Only Virtual Machine (10 minutes)

### Step 6: Create CPU-Only VM Instance (No GPU Needed)
You do NOT need to request GPU quota or upgrade your account. CPU VMs work with the free trial.

1. Go to **Navigation Menu (☰)** → **Compute Engine** → **VM instances**
2. Click "CREATE INSTANCE"
3. Configure instance:

   **Basic settings:**
   - **Name:** `instance-20251104-171533`
   - **Region:** `us-central1`
   - **Zone:** `us-central1-a`

   **Machine configuration:**
   - **Series:** N1
   - **Machine type:** `n1-standard-8` (8 vCPUs, 30 GB memory) — recommended for large models. You can use `n1-standard-4` (4 vCPUs, 15 GB memory) for lowest cost, but may hit memory limits.
   
   **DO NOT ADD GPU** - Leave the GPU section empty

   **Boot disk (click "CHANGE"):**
   - **Operating system:** Ubuntu 22.04 LTS
   - **Boot disk type:** Balanced persistent disk
   - **Size:** 100 GB
   - Click "SELECT"

   **Firewall:**
   - ✅ Check "Allow HTTP traffic"
   - ✅ Check "Allow HTTPS traffic"

4. Click "CREATE"
5. Wait 2-3 minutes for VM to start

---

## Part 4: Deploy Your Model (20-30 minutes)

### Step 7: Connect to Your VM
1. In **Compute Engine** → **VM instances**, find your VM
2. Click "SSH" button (opens browser terminal)
3. Wait for connection (~30 seconds)

### Step 8: Download and Setup Model
In the SSH terminal, run these commands one by one:

```bash
# Update system and install required packages
sudo apt update
sudo apt install python3-pip unzip -y
pip3 install transformers torch accelerate fastapi uvicorn python-multipart

# Create working directory
mkdir -p ~/mental-health-chatbot
cd ~/mental-health-chatbot

# Download model from Cloud Storage
gsutil cp gs://mental-health-model-storage/merged_mental_health_model.zip .

# Unzip model
unzip merged_mental_health_model.zip

# Verify files
ls -la merged_mental_health_model/
```

### Step 9: Upload Server Code to VM
On your **local machine**, create the deployment package:

1. Create a new file `gcp_deploy.zip` with these files:
   - `fastapi_server.py` (already exists)
   - `requirements.txt` (already exists)

2. Upload to your bucket:
   - Go to Cloud Storage → your bucket
   - Click "UPLOAD FILES"
   - Select files: `fastapi_server.py` and `requirements.txt`

3. In the VM SSH terminal, download them:
```bash
cd ~/mental-health-chatbot
gsutil cp gs://mental-health-model-storage/fastapi_server.py .
gsutil cp gs://mental-health-model-storage/requirements.txt .

# Install dependencies
pip3 install -r requirements.txt
```

### Step 10: Create Startup Script
In the SSH terminal, create a startup script:

```bash
cat > start_server.sh << 'EOF'
#!/bin/bash
cd ~/mental-health-chatbot
export MODEL_PATH=./merged_mental_health_model
nohup python3 fastapi_server.py > server.log 2>&1 &
echo "Server started! Check logs with: tail -f ~/mental-health-chatbot/server.log"
echo "Access at: http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"):8000"
EOF

chmod +x start_server.sh
```

### Step 11: Configure Firewall for Port 8000
1. In GCP Console, go to **VPC Network** → **Firewall**
2. Click "CREATE FIREWALL RULE"
3. Configure:
   - **Name:** `allow-fastapi-8000`
   - **Direction:** Ingress
   - **Targets:** All instances in the network
   - **Source IP ranges:** `0.0.0.0/0`
   - **Protocols and ports:** 
     - ✅ Specified protocols and ports
     - **TCP:** `8000`
4. Click "CREATE"

### Step 12: Start the Server
In the SSH terminal:

```bash
./start_server.sh
```

Wait ~5-10 minutes for the model to load into CPU memory (much slower than GPU).

Check if it's running:
```bash
tail -f ~/mental-health-chatbot/server.log
```

Look for: `Uvicorn running on http://0.0.0.0:8000`

Press `Ctrl+C` to stop viewing logs.

### Step 13: Get Your Server URL
In the SSH terminal:
```bash
echo "http://$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google"):8000"
```

Copy this URL. This is your chatbot API endpoint!

---

## Part 5: Test Your Deployment (5 minutes)

### Step 14: Test the API

**Option 1: Using browser**
1. Open the URL from Step 14
2. Add `/docs` to the end: `http://YOUR_IP:8000/docs`
3. You'll see the FastAPI interactive documentation
4. Click "Try it out" on the `/chat` endpoint
5. Enter a test message and click "Execute"

**Option 2: Using Python locally**
```python
import requests

API_URL = "http://YOUR_VM_IP:8000/chat"  # Replace with your URL

response = requests.post(
    API_URL,
    json={
        "message": "I'm feeling anxious today",
        "max_length": 256
    }
)

print(response.json()["response"])
```

---

## Part 6: Cost Management & Monitoring

### Expected Costs with CPU-Only VM:
- **VM (n1-standard-8):** ~$0.27/hour (~$200/month if running 24/7)
- **VM (n1-standard-4):** ~$0.13/hour (~$95/month if running 24/7)
- **Storage (100GB):** ~$2/month
- **Network egress:** ~$0.12/GB

**Your $300 credit will last:**
- If running 24/7 on n1-standard-8: ~1.5 months
- If running 24/7 on n1-standard-4: ~3 months
- If running on-demand or stopped when not in use: Much longer

**How to keep it completely free:**
- You do NOT need to upgrade your account or add payment method beyond the initial $300 credit activation
- Your $300 credit covers all CPU VM and storage costs until it runs out
- Stop your VM when not in use to maximize your credit

### How to Stop VM (to save credits):
1. Go to **Compute Engine** → **VM instances**
2. Select your VM
3. Click "STOP" (at top)
4. VM stops, you only pay for storage (~$2/month)

### How to Start VM Again:
1. Go to **Compute Engine** → **VM instances**
2. Select your VM
3. Click "START"
4. Wait ~2 minutes
5. SSH in and run: `./start_server.sh`

### Set Up Budget Alerts:
1. Go to **Billing** → **Budgets & alerts**
2. Click "CREATE BUDGET"
3. Set alert at $50, $100, $200 to monitor spending

---

## Part 7: Access Your Model

### From Python (anywhere in the world):
```python
import requests

API_URL = "http://YOUR_VM_IP:8000/chat"

def chat(message):
    response = requests.post(
        API_URL,
        json={"message": message, "max_length": 512}
    )
    return response.json()["response"]

# Use it
print(chat("I'm feeling stressed about work"))
```

### From curl:
```bash
curl -X POST "http://YOUR_VM_IP:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I need help with anxiety"}'
```

---

## Troubleshooting

### Model loads slowly or fails:
- **CPU-only VMs are much slower than GPU VMs.** Each reply may take 1–5 minutes or more. This is normal for CPU inference with large models.
- For faster responses, use short prompts and set `max_length` to 64–128 in your API calls.
- If you get out-of-memory errors, upgrade to `n1-standard-8` (8 vCPUs, 30GB RAM) or `n1-highmem-8` (8 vCPUs, 52GB RAM).
- Check logs: `tail -f ~/mental-health-chatbot/server.log`
- Verify RAM and disk space: `free -h` and `df -h`

### Can't access the server:
- Check firewall rule is created (Step 11)
- Verify server is running: `ps aux | grep fastapi`
- Check external IP hasn't changed

### Out of memory:
- Upgrade to `n1-standard-8` (8 vCPUs, 30GB RAM)
- Or use model quantization (I can help with this)

### Responses are too slow:
- **Expected behavior for CPU.** Mistral-7B on CPU takes 1–5+ minutes per response.
- To speed up: use shorter `max_length` (e.g., 64–128 tokens), use smaller prompts.
- For fast responses (2-20 seconds), you would need to upgrade your account and use a GPU VM.

---

## Cost-Saving Tips

1. **Stop VM when not using** (most important!)
2. **Use CPU-only VMs** for all development and testing to stay within free credit
3. **Set up auto-shutdown** after 1 hour of inactivity (optional, saves credit)
4. **Monitor billing** in GCP Console (Billing → Overview) to track your $300 free credit usage
5. **Use n1-standard-4** for testing, n1-standard-8 for better performance (if needed)

---

## Next Steps

1. ✅ Complete all steps above
2. Test your chatbot API
3. Want a web interface? I can create a simple HTML chat UI
4. Want to add authentication? I can secure your API
5. Want auto-scaling? I can set up Cloud Run or GKE

Let me know if you get stuck on any step or want me to create additional scripts!
