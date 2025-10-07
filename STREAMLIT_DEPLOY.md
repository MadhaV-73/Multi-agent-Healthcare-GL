# 🚀 Streamlit Cloud Deployment Guide

## Deploying Your Multi-Agent Healthcare UI to Streamlit Cloud

Follow these steps to deploy your Streamlit application to the cloud for free!

---

## 📋 Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository (✅ Already done!)
   - Repository: `https://github.com/MadhaV-73/Multi-agent-Healthcare-GL`

2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
   - Use your GitHub account to sign in

3. **Files Required** (✅ All included):
   - `app_integrated.py` - Main Streamlit app
   - `requirements.txt` - Python dependencies
   - `.streamlit/config.toml` - Streamlit configuration
   - `data/` folder - Required data files

---

## 🎯 Step-by-Step Deployment

### Step 1: Sign Up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign up"** or **"Continue with GitHub"**
3. Authorize Streamlit to access your GitHub account
4. Complete the registration process

### Step 2: Deploy Your App

1. **From Streamlit Cloud Dashboard:**
   - Click **"New app"** button
   
2. **Configure Your App:**
   ```
   Repository: MadhaV-73/Multi-agent-Healthcare-GL
   Branch: main
   Main file path: app_integrated.py
   ```

3. **Advanced Settings (Optional):**
   - Click "Advanced settings"
   - Set Python version: `3.9` or `3.10` or `3.11`
   - Keep other defaults

4. **Deploy:**
   - Click **"Deploy!"**
   - Wait 2-5 minutes for initial deployment

### Step 3: Monitor Deployment

- Watch the deployment logs in real-time
- First deployment takes longer (installing dependencies)
- Look for: `You can now view your Streamlit app in your browser.`

---

## ⚙️ Configuration Notes

### ✅ Backend API Configuration (Already Set Up!)

**Good News!** Your backend is deployed and the app is configured to use it automatically!

**Backend URL:** `https://multi-agent-healthcare-gl-1.onrender.com`

The app is configured with this priority order:
1. **Streamlit Secrets** (for Streamlit Cloud deployment)
2. **Environment Variable** (`API_BASE_URL`)
3. **Default Production URL** (your deployed backend)

### For Streamlit Cloud Deployment

When deploying to Streamlit Cloud, add this to your app's secrets:

1. Go to your app settings in Streamlit Cloud
2. Click **"Secrets"** in the left sidebar
3. Add the following:

```toml
[api]
base_url = "https://multi-agent-healthcare-gl-1.onrender.com"
```

4. Click **"Save"**

### For Local Development

You can use either:

**Option 1:** Create `.streamlit/secrets.toml` (gitignored):
```toml
[api]
base_url = "https://multi-agent-healthcare-gl-1.onrender.com"
```

**Option 2:** Set environment variable:
```powershell
$env:API_BASE_URL="https://multi-agent-healthcare-gl-1.onrender.com"
streamlit run app_integrated.py
```

**Option 3:** Do nothing! The app will use the production URL by default.

---

## 🔧 Managing Your Deployed App

### Update Your App
Any push to your GitHub repository's main branch will automatically redeploy the app!

```powershell
git add .
git commit -m "Update app"
git push origin main
```

### View Logs
- Click on your app in Streamlit Cloud dashboard
- Click "Manage app" → "Logs"
- View real-time application logs

### Reboot App
- Go to app settings
- Click "Reboot"
- Useful if app is stuck or needs fresh start

### Delete App
- Click "Delete app" in settings
- Confirm deletion

---

## 📊 App Settings in Streamlit Cloud

### Environment Variables / Secrets

1. Go to your app settings
2. Click "Secrets"
3. Add your secrets in TOML format:

```toml
# API Configuration
[api]
base_url = "https://your-api-endpoint.com"
api_key = "your-secret-key"

# Other settings
[database]
connection_string = "your-db-connection"
```

Access in code:
```python
import streamlit as st
api_url = st.secrets["api"]["base_url"]
```

---

## 🐛 Common Issues & Solutions

### ❌ "ModuleNotFoundError"
**Solution**: Ensure all dependencies are in `requirements.txt`
```powershell
pip freeze > requirements.txt
```

### ❌ "File not found" Error
**Solution**: Check that data files are committed to git
```powershell
git add data/
git commit -m "Add data files"
git push
```

### ❌ App Exceeds Resource Limits
**Solution**: 
- Free tier has resource limits
- Optimize data loading with `@st.cache_data`
- Consider upgrading to paid plan

### ❌ Backend API Not Accessible
**Solution**: 
- Deploy backend separately (Railway, Render, etc.)
- Update `API_BASE_URL` to deployed backend URL
- Or implement standalone mode

---

## 🌟 Best Practices

### 1. Use Caching
```python
@st.cache_data
def load_data():
    return pd.read_csv("data/file.csv")
```

### 2. Optimize File Sizes
- Keep data files under 100MB for free tier
- Compress images
- Use efficient data formats (parquet vs CSV)

### 3. Handle Errors Gracefully
```python
try:
    response = requests.get(API_URL)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    st.error(f"Connection error: {e}")
```

### 4. Add Health Checks
```python
def check_api_status():
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        return response.status_code == 200
    except:
        return False

if not check_api_status():
    st.warning("⚠️ Backend API is not accessible")
```

---

## 📈 Resource Limits (Free Tier)

| Resource | Limit |
|----------|-------|
| **Apps** | 1 public app |
| **CPU** | 1 CPU core |
| **Memory** | 1 GB RAM |
| **Storage** | Limited |
| **Uptime** | May sleep after inactivity |

**Paid Plans** available for:
- Multiple apps
- More resources
- Private apps
- Custom domains
- Priority support

---

## 🎬 Quick Deployment Checklist

- [ ] GitHub repository is public
- [ ] All code pushed to `main` branch
- [ ] `requirements.txt` is up to date
- [ ] `.streamlit/config.toml` is configured
- [ ] Data files are committed
- [ ] Streamlit Cloud account created
- [ ] App deployed through Streamlit Cloud UI
- [ ] Backend API considerations addressed

---

## 🔗 Useful Links

- **Streamlit Cloud**: https://share.streamlit.io
- **Documentation**: https://docs.streamlit.io/streamlit-community-cloud
- **Community Forum**: https://discuss.streamlit.io
- **Your Repository**: https://github.com/MadhaV-73/Multi-agent-Healthcare-GL

---

## 📧 Need Help?

- Check Streamlit Community Forum: https://discuss.streamlit.io
- Review app logs in Streamlit Cloud dashboard
- Check GitHub repository for issues

---

**Happy Deploying! 🚀**
