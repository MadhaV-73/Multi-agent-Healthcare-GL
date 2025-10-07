# 🚀 Render Deployment Guide - FastAPI Backend

## Deploying Your FastAPI Backend to Render

This guide will help you deploy your Multi-Agent Healthcare FastAPI backend to Render.

---

## 📋 Prerequisites

1. **GitHub Repository** (✅ Done!)
   - Repository: `https://github.com/MadhaV-73/Multi-agent-Healthcare-GL`

2. **Render Account**
   - Sign up at [render.com](https://render.com)
   - Free tier available!

3. **Required Files** (✅ All included):
   - `api/main.py` - FastAPI application
   - `requirements.txt` - Dependencies
   - `Procfile` - Start command for Render
   - `render.yaml` - Render configuration

---

## 🎯 Quick Deployment Steps

### Step 1: Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"**
4. Authorize Render to access your repositories

### Step 2: Create a New Web Service

1. From your Render Dashboard, click **"New +"**
2. Select **"Web Service"**
3. Connect your GitHub repository:
   - Click **"Connect account"** if not connected
   - Find and select: `MadhaV-73/Multi-agent-Healthcare-GL`

### Step 3: Configure the Service

Fill in the following settings:

```
Name: multi-agent-healthcare-api
Region: Oregon (US West) or closest to you
Branch: main
Root Directory: (leave blank)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Step 4: Select Plan

- Choose **"Free"** plan (suitable for testing and demos)
- Free tier includes:
  - 750 hours/month
  - Automatic HTTPS
  - Sleeps after inactivity
  - Wakes on request

### Step 5: Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for initial deployment
3. Watch the build logs in real-time

---

## ✅ Verify Deployment

Once deployed, you'll get a URL like:
```
https://multi-agent-healthcare-api.onrender.com
```

### Test Your API:

1. **Root Endpoint:**
   ```
   https://your-app-name.onrender.com/
   ```

2. **Health Check:**
   ```
   https://your-app-name.onrender.com/api/v1/health
   ```

3. **API Documentation:**
   ```
   https://your-app-name.onrender.com/docs
   ```

---

## 🔧 Configuration Files Explained

### `Procfile`
```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```
- Tells Render how to start your FastAPI application
- `api.main:app` points to the `app` object in `api/main.py`
- `$PORT` is automatically set by Render

### `render.yaml`
```yaml
services:
  - type: web
    name: multi-agent-healthcare-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```
- Infrastructure as Code configuration
- Allows automatic deployment from GitHub

---

## 🔄 Update Your Streamlit App

After deploying the backend, update your Streamlit app to use the new API URL:

### Option 1: Update `app_integrated.py` directly
```python
# Change this line:
API_BASE_URL = "http://localhost:8000"

# To this (replace with your actual Render URL):
API_BASE_URL = "https://your-app-name.onrender.com"
```

### Option 2: Use Streamlit Secrets (Recommended)
In Streamlit Cloud, add to secrets:
```toml
[api]
base_url = "https://your-app-name.onrender.com"
```

Then in your code:
```python
import streamlit as st
API_BASE_URL = st.secrets.get("api", {}).get("base_url", "http://localhost:8000")
```

---

## 🐛 Troubleshooting

### ❌ Error: "ModuleNotFoundError: No module named 'app'"

**Problem:** Render is looking for `app.py` but your app is in `api/main.py`

**Solution:** ✅ Fixed! Use the correct start command:
```
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### ❌ Build Failed

**Check:**
1. All dependencies are in `requirements.txt`
2. Python version compatibility (3.11 recommended)
3. Build logs for specific error messages

### ❌ Service Starts But Crashes

**Check:**
1. Environment variables are set correctly
2. All required data files are in the repository
3. Database connections (if any) are configured
4. Check runtime logs in Render dashboard

### ❌ 503 Service Unavailable

**Possible Causes:**
- Free tier app is sleeping (first request takes 30-60 seconds to wake)
- Application crashed during startup
- Check logs in Render dashboard

### ❌ CORS Issues

Your API already has CORS configured in `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

If you have issues, you can restrict origins:
```python
allow_origins=[
    "https://your-streamlit-app.streamlit.app",
    "http://localhost:8501"
]
```

---

## 📊 Monitoring Your App

### View Logs
1. Go to your service in Render dashboard
2. Click **"Logs"** tab
3. View real-time application logs

### Check Metrics
1. Click **"Metrics"** tab
2. View CPU, Memory, and Request metrics

### Manual Deploy
1. Go to **"Manual Deploy"** section
2. Click **"Deploy latest commit"**
3. Or set up auto-deploy on push

---

## 🔐 Environment Variables

Add environment variables in Render dashboard:

1. Go to your service
2. Click **"Environment"** tab
3. Add key-value pairs:

```
DEBUG_MODE=False
LOG_LEVEL=INFO
```

Access in your code:
```python
import os
debug_mode = os.getenv("DEBUG_MODE", "False") == "True"
```

---

## 💰 Free Tier Limitations

| Feature | Free Tier |
|---------|-----------|
| **Apps** | Multiple web services |
| **RAM** | 512 MB |
| **CPU** | Shared |
| **Bandwidth** | 100 GB/month |
| **Sleep** | After 15 min inactivity |
| **Build Time** | 10 minutes max |
| **Uptime** | 750 hours/month |

**Note:** Free apps spin down after inactivity and wake on the first request (30-60 seconds delay).

---

## 🚀 Upgrade Options

Paid plans start at $7/month and include:
- ✅ Always-on (no sleeping)
- ✅ More RAM and CPU
- ✅ Custom domains
- ✅ Priority support
- ✅ Better performance

---

## 📝 Deployment Checklist

- [ ] GitHub repository is up to date
- [ ] `Procfile` created with correct start command
- [ ] `render.yaml` created (optional but recommended)
- [ ] `requirements.txt` includes all dependencies
- [ ] Render account created and GitHub connected
- [ ] Web service created in Render
- [ ] Deployment successful
- [ ] API endpoints tested
- [ ] Streamlit app updated with new API URL
- [ ] End-to-end testing completed

---

## 🔗 Useful Resources

- **Render Documentation**: https://render.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Your Render Dashboard**: https://dashboard.render.com
- **Your GitHub Repo**: https://github.com/MadhaV-73/Multi-agent-Healthcare-GL

---

## 🆘 Need Help?

- **Render Support**: https://render.com/docs/support
- **Render Community**: https://community.render.com
- **Check Logs**: Always check application logs first
- **GitHub Issues**: Create an issue in your repository

---

## 🎬 Next Steps After Deployment

1. **Test all API endpoints** using the `/docs` page
2. **Update Streamlit app** with the new backend URL
3. **Deploy Streamlit app** to Streamlit Cloud
4. **End-to-end testing** of the complete system
5. **Monitor performance** and logs

---

**Your API will be live at:** `https://your-app-name.onrender.com` 🎉

**Happy Deploying! 🚀**
