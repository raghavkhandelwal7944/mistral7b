# GCP Deployment - Quick Start Summary

## What You've Got

I've created a complete deployment package for hosting your Mental Health Chatbot on Google Cloud Platform. Here's what's included:

### 📁 Files Created

1. **GCP_DEPLOYMENT_GUIDE.md** - Complete step-by-step deployment guide
2. **gcp_vm_setup.sh** - Automated setup script for your VM
3. **test_gcp_chatbot.py** - Python client to test your deployed model
4. **chat_web_interface.html** - Beautiful web chat interface
5. **gcp_quick_reference.py** - Quick command reference
6. **zip_merged_model.py** - Script to zip your model

### 🎯 Why GCP?

- ✅ You have $300 free credit
- ✅ Fast GPU inference (T4)
- ✅ No local memory usage
- ✅ Accessible from anywhere
- ✅ Professional deployment

### 💰 Cost Breakdown

**With T4 GPU:**
- ~$0.35/hour (~$250/month if running 24/7)
- Your $300 credit = ~1 month of 24/7 OR 3+ months part-time

**How to save credits:**
- Stop VM when not using (only pay ~$2/month for storage)
- Use only when needed, start/stop as required

---

## 🚀 Quick Start (30-60 minutes total)

### Step 1: Prepare Your Model (5 min)
```cmd
cd "c:\Users\raghav khandelwal\Desktop\mistral7b"
python zip_merged_model.py
```

### Step 2: GCP Setup (10 min)
1. Go to https://console.cloud.google.com/
2. Create project: `mental-health-chatbot`
3. Enable APIs: Compute Engine + Cloud Storage
4. Create bucket: `mental-health-model-storage`

### Step 3: Upload Model (15-30 min)
1. In Cloud Storage bucket, click "UPLOAD FILES"
2. Upload: `merged_mental_health_model.zip`
3. Upload: `fastapi_server.py`, `requirements.txt`, `gcp_vm_setup.sh`

### Step 4: Request GPU Access (5 min + wait time)
1. Go to **IAM & Admin** → **Quotas**
2. Request: 1x NVIDIA T4 GPU in `us-central1`
3. Wait for approval email (5-60 min usually)

### Step 5: Create VM (5 min)
1. **Compute Engine** → **VM instances** → **CREATE**
2. Name: `mental-health-chatbot-vm`
3. Region: `us-central1-a`
4. Machine: `n1-standard-4`
5. GPU: `1x NVIDIA T4`
6. Boot disk: `Deep Learning VM with CUDA 11.8`, 100GB
7. Firewall: Allow HTTP/HTTPS
8. Click **CREATE**

### Step 6: Configure Firewall (3 min)
1. **VPC Network** → **Firewall** → **CREATE RULE**
2. Name: `allow-fastapi-8000`
3. Source: `0.0.0.0/0`
4. TCP port: `8000`
5. Click **CREATE**

### Step 7: Deploy Model (10 min)
SSH into VM and run:
```bash
# Download and run setup script
gsutil cp gs://mental-health-model-storage/gcp_vm_setup.sh .
bash gcp_vm_setup.sh

# Start server
./start_server.sh

# Get your API URL
./check_status.sh
```

### Step 8: Test It! (2 min)
**From browser:**
- Go to: `http://YOUR_VM_IP:8000/docs`
- Try the `/chat` endpoint

**From Python:**
```python
import requests
API_URL = "http://YOUR_VM_IP:8000/chat"
response = requests.post(API_URL, json={"message": "I'm feeling anxious"})
print(response.json()["response"])
```

**Using web interface:**
1. Open `chat_web_interface.html`
2. Update `API_URL` with your VM IP
3. Open in browser
4. Start chatting!

---

## 📊 Cost Management

### Daily Usage Patterns

**Pattern 1: Development (8 hours/day)**
- Cost: ~$2.80/day = ~$84/month
- Your $300 lasts: ~3.5 months

**Pattern 2: Part-time (4 hours/day)**
- Cost: ~$1.40/day = ~$42/month
- Your $300 lasts: ~7 months

**Pattern 3: On-demand (1 hour sessions)**
- Cost: ~$0.35/session
- Your $300 lasts: ~850 sessions

### How to Stop VM (IMPORTANT!)
```bash
# From GCP Console
Compute Engine → VM instances → Select VM → STOP

# From gcloud CLI
gcloud compute instances stop mental-health-chatbot-vm --zone=us-central1-a
```

**When stopped:** Only pay ~$2/month for disk storage

### Set Budget Alerts
1. **Billing** → **Budgets & alerts**
2. Create alerts at: $50, $100, $200, $250

---

## 🔧 Management Commands

### Start/Stop Server
```bash
# On the VM
./start_server.sh    # Start server
./stop_server.sh     # Stop server
./check_status.sh    # Check if running
```

### View Logs
```bash
tail -f ~/mental-health-chatbot/server.log
```

### Restart Server
```bash
./stop_server.sh && ./start_server.sh
```

### Check GPU
```bash
nvidia-smi
```

---

## 🌐 Access Methods

### 1. Python Client
```python
# Update API_URL in test_gcp_chatbot.py
python test_gcp_chatbot.py
```

### 2. Web Interface
- Open `chat_web_interface.html`
- Update `API_URL`
- Open in browser

### 3. Direct API
```python
import requests
requests.post("http://YOUR_IP:8000/chat", 
              json={"message": "Hello"})
```

### 4. curl
```bash
curl -X POST "http://YOUR_IP:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need help"}'
```

---

## ❓ Troubleshooting

### Server won't start
```bash
# Check logs
tail -50 ~/mental-health-chatbot/server.log

# Check GPU
nvidia-smi

# Restart
./stop_server.sh
./start_server.sh
```

### Can't connect from browser
1. Check VM external IP hasn't changed
2. Verify firewall rule exists (port 8000)
3. Check server is running: `./check_status.sh`

### Out of memory
- Upgrade to `n1-standard-8` (30GB RAM)
- Or use quantization (I can help)

### GPU quota denied
- Wait for approval (can take up to 48 hours)
- Or use CPU-only VM (much slower)

---

## 📚 Next Steps

### Once Deployed:
1. ✅ Test thoroughly with various queries
2. ✅ Set up budget alerts
3. ✅ Bookmark your API URL
4. ✅ Share web interface with others

### Optional Enhancements:
- **Add authentication** (I can create this)
- **Auto-scaling** (Cloud Run deployment)
- **Monitoring dashboard** (Stackdriver)
- **Custom domain** (yourbot.com)
- **Rate limiting** (prevent abuse)

---

## 🆘 Need Help?

If you get stuck:
1. Check `GCP_DEPLOYMENT_GUIDE.md` for detailed steps
2. Review `gcp_quick_reference.py` for commands
3. Check server logs: `tail -f server.log`
4. Let me know the specific error!

---

## 📝 Important Notes

1. **Always stop VM** when not using to save credits
2. **Monitor billing** regularly in GCP Console
3. **GPU approval** can take 5-60 minutes (usually quick)
4. **First model load** takes 2-3 minutes after starting server
5. **External IP** may change if you stop/start VM (use static IP if needed)

---

## ✅ Success Checklist

- [ ] Model zipped and uploaded to Cloud Storage
- [ ] VM created with T4 GPU
- [ ] Firewall rule created for port 8000
- [ ] Setup script run successfully
- [ ] Server started and running
- [ ] Can access API at `http://YOUR_IP:8000/docs`
- [ ] Tested chat endpoint successfully
- [ ] Budget alerts configured
- [ ] Know how to stop/start VM

---

## 🎉 You're All Set!

Once deployed, your chatbot will be:
- ✅ Running on professional GPU hardware
- ✅ Accessible from anywhere in the world
- ✅ Fast and responsive
- ✅ Not using your local resources
- ✅ Costing only when running

**Start with the Quick Start above and refer to GCP_DEPLOYMENT_GUIDE.md for detailed instructions!**
