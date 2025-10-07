# 🚀 Deployment Instructions - Streamlit Community Cloud

This guide walks you through deploying the Multi-Agent Healthcare Assistant to Streamlit Community Cloud for a public, shareable URL.

---

## 📋 Prerequisites

1. **GitHub Account** - Your code must be in a GitHub repository
2. **Streamlit Cloud Account** - Free tier available at [share.streamlit.io](https://share.streamlit.io)
3. **Project Files** - Ensure all files are committed to your repo

---

## ⚙️ Pre-Deployment Checklist

### 1. Verify Requirements.txt

Your `requirements.txt` should include all dependencies:

```txt
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
pillow>=10.0.0
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.0
python-multipart>=0.0.6
pytesseract>=0.3.10
pdfplumber>=0.10.0
requests>=2.31.0
pytest>=8.0.0
```

**Action:** Run this to verify all imports work:
```powershell
pip install -r requirements.txt
python -c "import streamlit, pandas, numpy, PIL, fastapi"
```

### 2. Check File Structure

Ensure your repo has:
```
├── app_integrated.py          # Main Streamlit app
├── requirements.txt           # Dependencies
├── config.py                  # Configuration
├── agents/                    # All agent modules
├── api/                       # FastAPI backend
├── data/                      # Sample CSVs/JSONs
├── utils/                     # Utilities
└── README.md                  # Documentation
```

### 3. Test Locally

**IMPORTANT:** Test the app locally before deploying:
```powershell
streamlit run app_integrated.py
```

Visit http://localhost:8501 and verify:
- ✅ Homepage loads
- ✅ X-Ray upload works
- ✅ Analysis completes successfully
- ✅ No import errors
- ✅ Sample data loads correctly

---

## 🌐 Step-by-Step Deployment to Streamlit Cloud

### Step 1: Push Code to GitHub

```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Streamlit Cloud deployment"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/multi-agent-healthcare.git

# Push to GitHub
git push -u origin main
```

### Step 2: Sign Up for Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign up with GitHub"**
3. Authorize Streamlit to access your GitHub repositories
4. Complete account setup

### Step 3: Deploy Your App

1. **Click "New app"** in Streamlit Cloud dashboard

2. **Fill in deployment settings:**
   - **Repository:** `YOUR_USERNAME/multi-agent-healthcare`
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `app_integrated.py`

3. **Advanced settings (click "Advanced settings"):**
   - **Python version:** 3.11 (recommended)
   - **Secrets:** (None needed for this app)

4. **Click "Deploy!"**

### Step 4: Wait for Deployment

Streamlit Cloud will:
- ✅ Clone your repository
- ✅ Install dependencies from `requirements.txt`
- ✅ Build the app
- ✅ Start the Streamlit server

**Typical deployment time:** 2-5 minutes

### Step 5: Get Your Public URL

Once deployed, you'll get a public URL like:
```
https://YOUR_USERNAME-multi-agent-healthcare-app-integrated-HASH.streamlit.app
```

**Save this URL** - you'll need it for your assignment submission!

---

## 🔧 Configuration for Deployment

### Backend API Note

**IMPORTANT:** The Streamlit app includes a local FastAPI backend (`api/main.py`), but **Streamlit Cloud only runs the Streamlit app**.

**Two deployment options:**

#### Option 1: Streamlit-Only (Recommended for Assignment)

The current `app_integrated.py` has **built-in Coordinator integration** that works without the FastAPI backend:

```python
# In app_integrated.py, X-ray analysis directly calls:
from agents.coordinator import Coordinator
coordinator = Coordinator(data_dir="./data", upload_dir="./uploads")
result = coordinator.execute_pipeline(upload_data)
```

**✅ This works on Streamlit Cloud out-of-the-box!**

#### Option 2: Full Backend Deployment (Advanced)

If you want the FastAPI backend, deploy separately on Render.com:

1. Create `Procfile` in repo root:
   ```
   web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```

2. Deploy to [Render.com](https://render.com):
   - Create new Web Service
   - Connect GitHub repo
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

3. Update `API_BASE_URL` in `app_integrated.py`:
   ```python
   API_BASE_URL = "https://your-backend.onrender.com"
   ```

**For this assignment, Option 1 (Streamlit-only) is sufficient.**

---

## 🐛 Troubleshooting Common Issues

### Issue 1: Import Errors

**Symptom:** `ModuleNotFoundError: No module named 'xyz'`

**Solution:** Add missing module to `requirements.txt` and redeploy

### Issue 2: File Not Found Errors

**Symptom:** `FileNotFoundError: data/pharmacies.json`

**Solution:** Ensure all data files are committed to GitHub:
```powershell
git add data/
git commit -m "Add data files"
git push
```

Then click "Reboot" in Streamlit Cloud dashboard.

### Issue 3: Memory Errors

**Symptom:** App crashes with "Out of memory"

**Solution:** Optimize data loading - use `@st.cache_data`:
```python
@st.cache_data
def load_pharmacies():
    return pd.read_json("data/pharmacies.json")
```

### Issue 4: Slow Loading

**Symptom:** App takes 20+ seconds to load

**Solution:** 
- Cache expensive operations
- Reduce data file sizes if too large
- Use `st.spinner()` for user feedback

### Issue 5: App Crashed

**Symptom:** "This app has encountered an error"

**Solution:**
1. Check Streamlit Cloud logs (click "Manage app" → "Logs")
2. Fix errors locally first
3. Push fixes and reboot app

---

## 📊 Post-Deployment Testing

Once deployed, test these critical paths:

### Test 1: Homepage
- [ ] Visit your public URL
- [ ] Verify homepage loads with system stats
- [ ] Check API status indicator

### Test 2: X-Ray Upload
- [ ] Go to X-Ray Analysis page
- [ ] Upload a sample X-ray (use `uploads/test_xray.png`)
- [ ] Fill patient form (age 42, gender F, city Mumbai, pincode 400001)
- [ ] Click "Run complete agent pipeline"

### Test 3: Analysis Results
- [ ] Verify condition probabilities display
- [ ] Check OTC medicine recommendations shown
- [ ] Confirm pharmacy matching works
- [ ] Validate event log visible

### Test 4: Safety Features
- [ ] Test with low SpO2 (85%) - should show red flags
- [ ] Test with emergency symptoms - should escalate to doctor
- [ ] Verify disclaimers visible throughout

### Test 5: Edge Cases
- [ ] Upload invalid file - should show error gracefully
- [ ] Leave required fields empty - should validate
- [ ] Test with different cities - should match pharmacies

---

## 📝 Update README with Public URL

Once deployed, update your `README.md`:

```markdown
## 🌐 Live Demo

**Public URL:** https://YOUR_USERNAME-multi-agent-healthcare-app-integrated-HASH.streamlit.app

Try it now! Upload a chest X-ray and see the multi-agent system in action.
```

---

## 📦 Submission Checklist

Before submitting, ensure:

- [x] App deployed successfully to Streamlit Cloud
- [x] Public URL accessible (test in incognito browser)
- [x] README.md updated with public URL
- [x] Sample screenshots captured (see `sample_outputs/screenshots/`)
- [x] Sample order JSON present (`sample_outputs/sample_order.json`)
- [x] All tests passing (`pytest -q`)
- [x] Presentation slides ready (`docs/presentation.pptx`)

---

## 🔗 Useful Links

- **Streamlit Cloud Docs:** https://docs.streamlit.io/streamlit-community-cloud
- **Streamlit Deployment Guide:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **Streamlit Forum:** https://discuss.streamlit.io (for help)
- **Troubleshooting:** https://docs.streamlit.io/knowledge-base/deploy/deployment-issues

---

## 🎯 Expected Deployment Result

After successful deployment, your panel presentation can showcase:

1. **Live Demo:** Share your public Streamlit URL
2. **No Local Setup:** Reviewers can try it instantly
3. **Professional Presentation:** Cloud deployment shows production readiness
4. **Backup Plan:** If live demo fails, have screenshots ready

---

## ⚡ Quick Deploy Commands Summary

```powershell
# 1. Verify requirements
pip install -r requirements.txt

# 2. Test locally
streamlit run app_integrated.py

# 3. Commit and push
git add .
git commit -m "Ready for deployment"
git push origin main

# 4. Deploy on Streamlit Cloud
# Visit https://share.streamlit.io
# Click "New app" → Select repo → Deploy

# 5. Get public URL and update README
# Copy URL from Streamlit Cloud dashboard
```

---

## 💡 Pro Tips

1. **Deploy Early:** Don't wait until last minute - deployment can reveal issues
2. **Test Incognito:** Verify public URL works in incognito/private browsing
3. **Monitor Logs:** Streamlit Cloud provides real-time logs for debugging
4. **Share Widely:** Once deployed, URL works for anyone (no login needed)
5. **Reboot Anytime:** If issues occur, click "Reboot app" in Streamlit dashboard

---

## 📞 Need Help?

If you encounter deployment issues:

1. Check Streamlit Cloud logs first
2. Search [Streamlit Forum](https://discuss.streamlit.io)
3. Review [deployment troubleshooting guide](https://docs.streamlit.io/knowledge-base/deploy)

---

**Ready to deploy? Follow the steps above and your Multi-Agent Healthcare Assistant will be live in minutes!** 🚀

