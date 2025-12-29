# Quick Deployment Guide

## 🚀 Deploy in 15 Minutes

### Prerequisites
- GitHub account
- Railway account (free tier)
- Vercel account (free tier)
- Twitter API key from [twitterapi.io](https://twitterapi.io)
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## Step 1: Push to GitHub (2 min)

```bash
cd /Users/wenkai/ai-project/xtrack
git init
git add .
git commit -m "Initial commit with database"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

---

## Step 2: Deploy Backend to Railway (5 min)

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `xtrack` repository
4. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
5. Go to backend service → **"Variables"** tab, add:
   ```
   TWITTER_API_KEY=your_twitter_api_key
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-2.5-flash
   FROM_EMAIL=your_email@gmail.com
   ```
6. Go to **"Settings"** → **"Domains"** → **"Generate Domain"**
7. **Copy your backend URL** (e.g., `https://xtrack-backend.up.railway.app`)

---

## Step 3: Deploy Frontend to Vercel (5 min)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel
```

Follow prompts:
- Project name: `xtrack`
- Build Command: `npm run build`
- Output Directory: `dist`

Add environment variable:
```bash
vercel env add VITE_API_URL production
# Enter: https://your-railway-backend-url.up.railway.app/api

vercel --prod
```

---

## Step 4: Test (3 min)

### Test Backend:
```bash
curl https://your-backend-url.up.railway.app/health
```

### Test Frontend:
Open `https://xtrack.vercel.app` and try:
1. Create a job
2. Run test function

---

## 🎉 Done!

Your app is now live at:
- **Frontend**: `https://xtrack.vercel.app`
- **Backend**: `https://your-app.up.railway.app`
- **Database**: PostgreSQL on Railway (managed automatically)

---

## 📝 Important Notes

1. **Database migrations**: Railway automatically creates tables on first startup
2. **Job scheduling**: Jobs run 24/7 on Railway (no laptop needed!)
3. **Costs**: $5/month Railway + Free Vercel = $5/month total
4. **Scaling**: Both platforms auto-scale as needed

---

## 🔄 Future Updates

**Backend:**
```bash
git add .
git commit -m "Update"
git push
# Railway auto-deploys
```

**Frontend:**
```bash
cd frontend
vercel --prod
```

---

## 🐛 Quick Troubleshooting

**CORS errors**: Add your Vercel URL to backend CORS settings in `app/main.py`

**API not responding**: Check Railway logs in dashboard → Deployments

**Database errors**: Verify `DATABASE_URL` is set in Railway variables

For detailed troubleshooting, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📱 What's Running?

- ✅ FastAPI backend on Railway
- ✅ PostgreSQL database on Railway
- ✅ APScheduler running jobs 24/7
- ✅ React frontend on Vercel
- ✅ Automatic HTTPS on both platforms

---

**Need help?** Check the full [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

