# Local Testing Guide

Complete guide for testing the authentication system locally before deploying to production.

## Prerequisites

- Python 3.13 installed
- Node.js and npm installed
- SendGrid account (for email verification)
- Twitter API key (for monitoring features)
- Gemini API key (for AI summaries)

## Step 1: Backend Setup

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install the new authentication packages:
- `passlib[bcrypt]` - Password hashing
- `python-jose[cryptography]` - JWT tokens

### Configure Environment Variables

Create or update `backend/.env`:

```bash
# Database (SQLite for local development)
# DATABASE_URL is optional - will use SQLite if not set

# Twitter API
TWITTER_API_KEY=your_twitter_api_key

# Gemini API
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# SendGrid Email
SENDGRID_API_KEY=your_sendgrid_api_key
FROM_EMAIL=kai@ai-productivity.tools

# Authentication (NEW - REQUIRED)
SESSION_SECRET=dev-secret-key-change-in-production
```

**Generate a proper SESSION_SECRET for development:**
```bash
openssl rand -hex 32
```

Example output: `7c9e6679f3a8f9e4c8d6a5b4e3f2g1h0i9j8k7l6m5n4o3p2q1r0`

### Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
[STARTUP] Creating database tables...
[STARTUP] ✅ Database tables created
[STARTUP] Starting job scheduler...
[STARTUP] ✅ Application started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify backend is running:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

## Step 2: Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Configure Environment Variables

The frontend uses the default `http://localhost:8000/api` for local development, so no changes needed.

If you want to explicitly set it, create `frontend/.env.local`:

```bash
VITE_API_URL=http://localhost:8000/api
```

### Start Frontend Server

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

**Open in browser:** http://localhost:5173/

## Step 3: Test Authentication Flow

### Test 1: Registration

1. **Open** http://localhost:5173/
2. **You should see the login page** (not the main app)
3. Click **"立即注册" (Register)**
4. Enter:
   - Email: `test@example.com` (use a real email you can access)
   - Password: `Test123!@#` (meets strong password requirements)
   - Confirm password: `Test123!@#`
5. Click **"注册" (Register)**

**Expected Result:**
- You should see "注册成功！请查收邮件并输入验证码"
- Check your email for a 6-digit verification code
- Backend logs should show:
  ```
  INFO: POST /api/auth/register
  [EMAIL SERVICE] ✅ Email sent successfully
  ```

**If email not received:**
- Check spam/junk folder
- Verify `SENDGRID_API_KEY` is correct
- Verify `FROM_EMAIL` is verified in SendGrid
- Check backend terminal for errors

### Test 2: Email Verification

1. **Check your email** for verification code
2. **Enter the 6-digit code** in the verification page
3. Click **"验证并登录" (Verify and Login)**

**Expected Result:**
- Account is activated
- You're automatically logged in
- You see the main app with navbar showing your email
- Backend logs:
  ```
  INFO: POST /api/auth/verify-email
  ```

### Test 3: Check Database

```bash
cd backend
sqlite3 xtrack.db  # or your database name
```

```sql
-- Check your user
SELECT id, email, name, status, created_at FROM users;

-- Should show:
-- id | email | name | status | created_at
-- 1  | test@example.com | NULL | active | 2025-12-29 ...

-- Check verification codes
SELECT email, code, code_type, used, expires_at FROM verification_codes;

-- Should show the code you just used (with used=1)
```

Exit SQLite: `.exit`

### Test 4: Create a Job (Test User Isolation)

1. **Click "Add Job"**
2. Enter:
   - Username: `elonmusk`
   - Frequency: `daily`
   - Topics: `AI, Tesla`
   - Email: Should be pre-filled with your email
3. **Click "Create Job"**

**Expected Result:**
- Job created successfully
- You can see the job in the list
- Backend logs:
  ```
  INFO: POST /api/jobs/
  ```

**Check database:**
```sql
SELECT j.id, j.x_username, j.user_id, u.email 
FROM jobs j 
JOIN users u ON j.user_id = u.id;

-- Should show:
-- id | x_username | user_id | email
-- 1  | elonmusk   | 1       | test@example.com
```

### Test 5: User Isolation

1. **Logout** (click email in top-right → Profile → "登出账号")
2. **Register a second user** with different email (e.g., `test2@example.com`)
3. **Verify the second user's email**
4. **After login, check jobs list**

**Expected Result:**
- The second user sees NO jobs (empty state)
- The first user's job is NOT visible
- Backend logs show different `user_id` for the new user

**Verify in database:**
```sql
-- User 1's jobs
SELECT id, x_username FROM jobs WHERE user_id = 1;

-- User 2's jobs  
SELECT id, x_username FROM jobs WHERE user_id = 2;

-- Should be separate
```

### Test 6: Login

1. **Logout**
2. **Click "立即登录" (Login)**
3. Enter:
   - Email: `test@example.com`
   - Password: `Test123!@#`
   - Check "记住我" (Remember me)
4. **Click "登录" (Login)**

**Expected Result:**
- Logged in successfully
- You see your jobs again
- Token stored in localStorage (check DevTools → Application → Local Storage)

### Test 7: Forgot Password

1. **Logout**
2. **Click "忘记密码？" (Forgot Password)**
3. **Enter your email:** `test@example.com`
4. **Click "发送验证码" (Send Code)**
5. **Check email** for reset code
6. **Enter code and new password:** `NewPass123!@#`
7. **Click "重置密码并登录" (Reset and Login)**

**Expected Result:**
- Password reset successfully
- Auto-logged in
- Old password no longer works

**Test old password doesn't work:**
1. Logout
2. Try to login with old password: `Test123!@#` - should fail
3. Login with new password: `NewPass123!@#` - should work

### Test 8: Profile Management

1. **Login**
2. **Click your email in top-right**
3. **Click "个人资料" (Profile)**
4. **Update name:** Enter "Test User"
5. **Click "保存修改" (Save)**

**Expected Result:**
- Name updated
- Success message shown

**Test password change:**
1. **Switch to "修改密码" tab**
2. Enter:
   - Old password: `NewPass123!@#`
   - New password: `FinalPass123!@#`
   - Confirm: `FinalPass123!@#`
3. **Click "修改密码" (Change Password)**

**Expected Result:**
- Password changed
- Success message shown

**Verify:**
1. Logout
2. Login with new password: `FinalPass123!@#`

### Test 9: Run a Monitoring Job

1. **Create a job** (if you don't have one)
2. **Click the Play button** (▶) next to the job
3. **Wait for completion** (may take 10-30 seconds due to Twitter API rate limiting)

**Expected Result:**
- Summary generated
- Can view summaries
- Summary is associated with your user

**If you get rate limit errors:**
- This is expected with free Twitter API
- Wait 5 seconds between requests
- Check backend logs for Twitter API calls

### Test 10: Email Notifications

1. **With a job that has summaries**
2. **Click the email icon** (📧) next to a summary
3. **Confirm or enter email**

**Expected Result:**
- Email sent with summary
- Check your inbox for the summary email

## Step 4: Check Logs

### Backend Logs (in terminal where you ran `uvicorn`)

Look for:
```
✅ Successful operations
INFO: POST /api/auth/register - successful registrations
INFO: POST /api/auth/login - successful logins
[EMAIL SERVICE] ✅ Email sent successfully - verification emails sent

❌ Errors to watch for
ERROR: ... - any error messages
[EMAIL SERVICE] ❌ Failed to send email - email failures
Rate limit exceeded - Twitter API limits
```

### Frontend Logs (Browser DevTools → Console)

Look for:
```
✅ No errors in console
❌ Watch for:
- CORS errors (should not happen locally)
- 401 Unauthorized (means auth not working)
- Network errors
```

## Step 5: Database Inspection

### Check All Tables

```bash
cd backend
sqlite3 xtrack.db
```

```sql
-- List all tables
.tables
-- Should show: jobs  summaries  users  verification_codes

-- Check users
SELECT id, email, name, status, created_at, last_login_at FROM users;

-- Check jobs with owners
SELECT j.id, j.x_username, j.frequency, j.is_active, u.email as owner
FROM jobs j
LEFT JOIN users u ON j.user_id = u.id;

-- Check summaries
SELECT id, job_id, tweets_count, created_at FROM summaries
ORDER BY created_at DESC
LIMIT 5;

-- Check recent verification codes
SELECT email, code, code_type, used, 
       datetime(expires_at, 'localtime') as expires_at_local
FROM verification_codes
WHERE created_at > datetime('now', '-1 hour')
ORDER BY created_at DESC;
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'passlib'"

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "SESSION_SECRET not found"

**Solution:** Add to `backend/.env`:
```bash
SESSION_SECRET=dev-secret-key-for-testing
```

### Issue: "No verification email received"

**Solutions:**
1. Check spam folder
2. Verify SendGrid API key: `echo $SENDGRID_API_KEY` (or check .env)
3. Check backend logs for email errors
4. Test SendGrid API key:
   ```bash
   curl -X POST https://api.sendgrid.com/v3/mail/send \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{...}'
   ```

### Issue: "CORS error in browser"

**This shouldn't happen locally**, but if it does:
1. Verify backend is running on `http://localhost:8000`
2. Verify frontend is running on `http://localhost:5173`
3. Check `backend/app/main.py` has `http://localhost:5173` in CORS origins

### Issue: "Cannot create job - 401 Unauthorized"

**Solution:**
1. Make sure you're logged in
2. Check if token exists: DevTools → Application → Local Storage
3. Try logout and login again

### Issue: "Can see other users' jobs"

**This is a bug** - verify:
1. `backend/app/routers/jobs.py` requires authentication
2. Jobs are filtered by `current_user.id`
3. Restart backend server

## Step 6: Pre-Deployment Checklist

Before deploying to Railway/Vercel, verify:

### Backend
- [ ] All tests pass locally
- [ ] No errors in backend logs
- [ ] Email verification works
- [ ] User isolation works (multiple users can't see each other's jobs)
- [ ] Password reset works
- [ ] Strong passwords are enforced
- [ ] `.env` file is NOT committed to git

### Frontend
- [ ] Login page shows on first visit
- [ ] Registration flow works
- [ ] Main app shows after login
- [ ] Navbar shows user email
- [ ] Profile modal works
- [ ] Logout works
- [ ] No errors in browser console

### Database
- [ ] Users table has new columns (password_hash, name, status, last_login_at)
- [ ] Verification_codes table exists
- [ ] Jobs are associated with user_id
- [ ] User isolation works

### Security
- [ ] Passwords are hashed (check database - should see bcrypt hash)
- [ ] SESSION_SECRET is set (not the default)
- [ ] Verification codes expire
- [ ] Tokens expire after configured time

## Step 7: Clean Up Before Deploy

### Reset Database for Fresh Start (Optional)

If you want a clean database for production:

```bash
cd backend
rm xtrack.db  # Delete local SQLite database
# Tables will be recreated on next server start
```

### Generate Production SESSION_SECRET

```bash
openssl rand -hex 32
```

**Save this for Railway environment variables!**

### Update .gitignore

Verify these are ignored:
```
backend/.env
backend/xtrack.db
backend/*.db
frontend/.env.local
node_modules/
__pycache__/
```

## Ready to Deploy?

Once all local tests pass:

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add authentication system"
   ```

2. **Push to GitHub:**
   ```bash
   git push origin main
   ```

3. **Follow deployment guide:**
   - See `AUTH_DEPLOYMENT_GUIDE.md` for Railway/Vercel deployment

---

## Quick Test Script

Save time with this quick test script:

```bash
#!/bin/bash
# test-auth.sh

echo "🧪 Testing Authentication System..."

# Test 1: Health check
echo "1. Testing backend health..."
curl -s http://localhost:8000/health | grep "healthy" && echo "✅ Backend healthy" || echo "❌ Backend not responding"

# Test 2: Registration (replace with your email)
echo "2. Testing registration..."
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!@#"}' | grep "message" && echo "✅ Registration works" || echo "❌ Registration failed"

# Test 3: Check database
echo "3. Checking database..."
sqlite3 backend/xtrack.db "SELECT COUNT(*) FROM users" && echo "✅ Database accessible" || echo "❌ Database error"

echo "Done! Check logs for details."
```

Make executable: `chmod +x test-auth.sh`

Run: `./test-auth.sh`

---

Happy testing! 🚀

