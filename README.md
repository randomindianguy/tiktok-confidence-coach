# 🎤 Confidence Coach — TikTok OA Demo (Deploy-Ready)

**AI-powered coaching for first-time TikTok creators who freeze mid-recording.**

This folder contains the complete, integrated website ready for deployment to Railway + Vercel.

---

## 📁 What's Inside

```
confidence-coach-deploy/
├── index.html          # Integrated marketing site + recording demo
├── app.js              # Recording logic + API integration
├── style.css           # Complete styles (marketing + demo)
├── app.py              # Backend (Local Whisper + Claude API)
├── requirements.txt    # Python dependencies
├── .env                # Your API key (DO NOT commit to public repo)
├── .env.example        # Template for others
├── .gitignore          # Protects your API key
├── nixpacks.toml       # Railway deployment config
└── README.md           # This file
```

---

## 🚀 Quick Start (Local Testing)

### Step 1: Install Dependencies

```bash
# Install ffmpeg (required for Whisper)
brew install ffmpeg

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Start Backend

```bash
python app.py
```

You should see:
```
Loading Whisper model (this may take a minute first time)...
Whisper model loaded!

🎤 Confidence Coach API
========================================
Target: First-time creators (0-1K followers)
Problem: Freezing mid-recording
Solution: Context-aware continuation prompts
Stack: Local Whisper + Claude API
========================================

Starting server on http://localhost:5001
```

### Step 3: Open Frontend

**Option A: Just open the file**
```bash
open index.html
```

**Option B: Use a local server** (better for testing)
```bash
# Python server
python -m http.server 3000

# OR Node.js
npx serve -p 3000
```

Then open: `http://localhost:3000`

### Step 4: Test It!

1. Allow camera/microphone access
2. Click "Start Recording"
3. Talk for 30-60 seconds, deliberately pause for 4+ seconds
4. Click "Stop" then "Analyze with AI"
5. See your transcript + AI coaching prompts!

---

## 🌐 Deploy to Production

### Part 1: Deploy Backend to Railway

#### Option A: Using GitHub (Recommended)

1. **Create GitHub repo**
   ```bash
   cd confidence-coach-deploy
   git init
   git add .
   git commit -m "Initial commit: Confidence Coach for TikTok OA"
   git branch -M main

   # Create repo on github.com, then:
   git remote add origin https://github.com/YOUR_USERNAME/confidence-coach.git
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `confidence-coach` repo
   - Railway auto-detects Python (thanks to `nixpacks.toml`)

3. **Add Environment Variable**
   - In Railway dashboard, click "Variables" tab
   - Add: `ANTHROPIC_API_KEY` = `sk-ant-api03-XJbZ068Yy...` (your key from .env)

4. **Get URL**
   - Click "Settings" → "Generate Domain"
   - Copy URL (e.g., `https://confidence-coach-production.up.railway.app`)
   - **IMPORTANT:** Save this URL for next step!

#### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up

# Add environment variable
railway variables set ANTHROPIC_API_KEY=sk-ant-api03-XJbZ068Yy...

# Get URL
railway domain
```

---

### Part 2: Deploy Frontend to Vercel

#### Step 1: Update API URL

In `app.js` line 6, change:
```javascript
const API_URL = 'http://localhost:5001';
```

To:
```javascript
const API_URL = 'https://YOUR-RAILWAY-URL.up.railway.app';
```

Example:
```javascript
const API_URL = 'https://confidence-coach-production.up.railway.app';
```

#### Step 2: Commit and Push

```bash
git add app.js
git commit -m "Update API URL for production"
git push
```

#### Step 3: Deploy on Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "Add New" → "Project"
4. Import your `confidence-coach` repo
5. **Configure:**
   - Framework Preset: **Other** (or leave as is)
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
6. Click "Deploy"
7. Wait 30 seconds
8. **Copy your URL!** (e.g., `https://confidence-coach.vercel.app`)

---

## ✅ Final Testing

1. Open your Vercel URL: `https://confidence-coach.vercel.app`
2. Scroll down to "Try It Yourself" section
3. Allow camera/microphone
4. Record → Analyze → See prompts!

If it works: **You're done!** 🎉

---

## 🐛 Troubleshooting

### Backend Issues

**"Module not found: anthropic"**
```bash
pip install -r requirements.txt
```

**"ffmpeg not found"**
```bash
brew install ffmpeg
```

**Railway crashes with memory error**
- Whisper "base" model might be too big for Railway free tier
- Edit `app.py` line 30: Change `whisper.load_model("base")` to `whisper.load_model("tiny")`

**Backend works locally but not on Railway**
- Check Railway logs in dashboard
- Make sure `ANTHROPIC_API_KEY` environment variable is set
- First deploy takes 3-5 min to download Whisper model

### Frontend Issues

**CORS error: "Blocked by CORS policy"**
- Make sure backend `app.py` has `CORS(app)` enabled
- Backend URL must be `https://` not `http://`
- Check that Railway backend is actually running

**"Camera access denied"**
- Browser settings: Allow camera/microphone for your site
- Try different browser (Chrome works best)

**Recording works but analysis fails**
- Check browser console (F12) for error messages
- Verify API_URL in `app.js` matches your Railway URL
- Test backend directly: `curl https://your-railway-url.up.railway.app/health`

---

## 💰 Cost Estimate

### For Demo/OA (1-2 weeks)
- Railway: **$0** (free tier: 500 hours/month, $5 credit)
- Vercel: **$0** (free tier: unlimited static sites)
- Whisper: **$0** (runs locally/on Railway)
- Claude API: **~$0.10** (if you do 10 test recordings)

**Total:** < $1 for your entire OA demo

### If TikTok Wants to Scale It
- Railway Pro: $20/month (for Whisper model hosting)
- Claude API: ~$0.01/analysis → $10 for 1,000 users
- Vercel Pro: $20/month (optional, free tier works fine)

---

## 🎯 Product Thinking for Interview

If TikTok asks follow-up questions, here's your framework:

### Why Practice Mode First?
"Real-time needs WebSocket streaming, sub-second latency, interrupt handling — weeks of engineering. Practice Mode validates the core hypothesis in days: **Do context-aware prompts actually help creators continue?** If they don't act on prompts in Practice Mode, they won't in real-time either."

### How Would You Measure Success?
"Three-tier metrics:
- **FaT** (activation): First prompt acted upon in first session
- **NaT** (habit): 3+ videos completed in first week
- **NSM** (north star): First-time creator posts per week — ties directly to TikTok's mission"

### What's the Biggest Risk?
"Prompt quality. If prompts feel generic ('Tell us more!'), users ignore them. That's why Claude over GPT-4 — better tone, more conversational. And why we send 15 seconds of context, not the full transcript."

### How Does This Tie to TikTok's Strategy?
"TikTok's growth depends on converting the 95% who don't post. This removes the psychological barrier at the exact moment of freeze. Every completed video that would've been deleted = net-new content for the algorithm."

---

## 🔗 Links

- **Railway:** [railway.app](https://railway.app)
- **Vercel:** [vercel.com](https://vercel.com)
- **Claude API:** [console.anthropic.com](https://console.anthropic.com)
- **Whisper Docs:** [github.com/openai/whisper](https://github.com/openai/whisper)

---

**Built for TikTok AI PM Internship OA**
Not affiliated with TikTok Inc. · Powered by Local Whisper + Claude API

---

## 🙋 Questions?

If something breaks:
1. Check Railway logs (in dashboard)
2. Check browser console (F12 → Console tab)
3. Test backend directly: `curl https://your-url.up.railway.app/health`
4. Double-check `API_URL` in `app.js` matches your Railway URL

**You got this! 🚀**
