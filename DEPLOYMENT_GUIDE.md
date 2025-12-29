# XTrack Deployment Guide

Complete step-by-step guide to deploy XTrack to Railway (Backend + Database) and Vercel (Frontend).

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
3. **GitHub Account**: Required for both Railway and Vercel
4. **API Keys**:
   - Twitter API key from [twitterapi.io](https://twitterapi.io)
   - Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🚂 Part 1: Deploy Backend to Railway

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

This will open your browser to authenticate with GitHub.

### Step 3: Push Code to GitHub (if not already)

```bash
cd /Users/wenkai/ai-project/xtrack
git init
git add .
git commit -m "Initial commit with database support"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 4: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `xtrack` repository
5. Railway will detect it's a Python project

### Step 5: Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically create the database and set `DATABASE_URL` environment variable

### Step 6: Configure Environment Variables

In Railway dashboard, go to your backend service → **"Variables"** tab:

```bash
TWITTER_API_KEY=your_twitter_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
FROM_EMAIL=your_email@gmail.com
```

**Note**: The `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

### Step 7: Configure Build Settings

Railway should auto-detect the Python project, but verify:

1. Go to **"Settings"** tab
2. Verify **"Root Directory"** is set to `backend/`
3. Build command should be: `pip install -r requirements.txt`
4. Start command should be: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 8: Deploy

Railway will automatically deploy. Monitor the deployment logs:

1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Watch the logs for any errors

You should see:
```
[STARTUP] Creating database tables...
[STARTUP] ✅ Database tables created
[STARTUP] Starting job scheduler...
[SCHEDULER] ✅ Scheduler started
```

### Step 9: Get Your Backend URL

1. Go to **"Settings"** tab
2. Under **"Domains"**, click **"Generate Domain"**
3. Copy your domain (e.g., `https://xtrack-backend.up.railway.app`)

**Save this URL - you'll need it for the frontend!**

### Step 10: Test Backend

```bash
# Test health endpoint
curl https://your-backend-url.up.railway.app/health

# Should return: {"status":"healthy"}
```

---

## 🎨 Part 2: Update Frontend Configuration

### Step 1: Update Frontend API URL

Edit `frontend/src/App.jsx`:

```javascript
// Change:
const API_BASE = 'http://localhost:8000/api'

// To:
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
```

### Step 2: Create Production Environment File

Create `frontend/.env.production`:

```bash
VITE_API_URL=https://your-railway-backend-url.up.railway.app/api
```

Replace with your actual Railway URL from Part 1, Step 9.

---

## ▲ Part 3: Deploy Frontend to Vercel

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy Frontend

```bash
cd frontend
vercel
```

Follow the prompts:
- **Set up and deploy?** → Yes
- **Which scope?** → Your account
- **Link to existing project?** → No
- **Project name** → `xtrack`
- **Directory** → `.` (current directory)
- **Override settings?** → Yes
  - **Build Command**: `npm run build`
  - **Output Directory**: `dist`
  - **Install Command**: `npm install`

### Step 4: Add Environment Variable

```bash
vercel env add VITE_API_URL production
```

When prompted, enter:
```
https://your-railway-backend-url.up.railway.app/api
```

### Step 5: Deploy to Production

```bash
vercel --prod
```

You'll get a URL like: `https://xtrack.vercel.app`

---

## ✅ Part 4: Verification

### Test Backend

```bash
# Health check
curl https://your-backend-url.up.railway.app/health

# Get jobs (should return empty array initially)
curl https://your-backend-url.up.railway.app/api/jobs/
```

### Test Database Connection

In Railway dashboard:
1. Go to PostgreSQL database
2. Click **"Connect"** tab
3. Click **"psql"** to open database console
4. Run:
```sql
\dt  -- List tables (should show users, jobs, summaries)
SELECT * FROM jobs;  -- Should be empty initially
```

### Test Frontend

1. Open `https://xtrack.vercel.app` in browser
2. Try creating a job
3. Check if it appears in the list
4. Try running the test function

---

## 🔄 Future Updates

### Update Backend

```bash
# Commit your changes
git add .
git commit -m "Update backend"
git push

# Railway will auto-deploy
```

Or manually:
```bash
cd backend
railway up
```

### Update Frontend

```bash
cd frontend
vercel --prod
```

---

## 💰 Cost Estimate

### Railway
- **Starter Plan**: $5/month
  - 500 hours of compute time
  - Includes PostgreSQL database
  - No credit card required for trial

### Vercel
- **Hobby Plan**: Free
  - Perfect for personal projects
  - Unlimited deployments
  - 100 GB bandwidth/month
- **Pro Plan**: $20/month (for commercial use)

**Total: $5-25/month**

---

## 🐛 Troubleshooting

### Backend Issues

**Database connection failed:**
```bash
# Check if DATABASE_URL is set in Railway
railway variables

# Should show DATABASE_URL=postgresql://...
```

**Job scheduler not running:**
- Check Railway logs for APScheduler errors
- Verify environment variables are set correctly

**Gmail OAuth not working:**
- Upload `credentials.json` to Railway using Railway CLI:
  ```bash
  railway run --service backend bash
  # Then manually upload credentials.json
  ```
- Note: Gmail OAuth requires manual setup for production

### Frontend Issues

**API calls failing (CORS errors):**
- Verify `VITE_API_URL` environment variable in Vercel
- Check Railway backend logs for CORS configuration

**Environment variables not working:**
- Redeploy after adding environment variables:
  ```bash
  vercel --prod
  ```

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [React Environment Variables](https://vitejs.dev/guide/env-and-mode.html)

---

## 🎉 Success Checklist

- [ ] Backend deployed to Railway
- [ ] PostgreSQL database connected
- [ ] Environment variables configured
- [ ] Backend health check passes
- [ ] Frontend deployed to Vercel
- [ ] Frontend can communicate with backend
- [ ] Can create and view jobs
- [ ] Test function works
- [ ] Scheduled jobs are running (check Railway logs after 1 hour)

---

## 🔐 Security Notes

1. **Never commit sensitive files**:
   - `.env` files (use `.env.example` instead)
   - `credentials.json` (Gmail OAuth)
   - `token.pickle` (Gmail OAuth)
   - API keys

2. **Use environment variables** for all secrets in Railway and Vercel

3. **Enable HTTPS** (automatic on Railway and Vercel)

4. **Set up proper CORS** (already configured in backend)

---

## 💡 Next Steps After Deployment

1. **Set up custom domain** (optional):
   - Railway: Settings → Domains → Add custom domain
   - Vercel: Settings → Domains → Add custom domain

2. **Enable monitoring**:
   - Railway has built-in metrics
   - Add error tracking (e.g., Sentry)

3. **Set up email notifications**:
   - Complete Gmail OAuth setup in production
   - Or use a service like SendGrid for production emails

4. **Database backups**:
   - Railway Pro includes automatic backups
   - Or set up manual backups with pg_dump

5. **Scale as needed**:
   - Railway: Upgrade plan for more resources
   - Vercel: Automatically scales

---

Need help? Check the troubleshooting section or open an issue on GitHub!

