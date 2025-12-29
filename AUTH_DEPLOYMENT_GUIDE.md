# Authentication System Deployment Guide

Complete guide for deploying the XTrack authentication system to Railway (backend) and Vercel (frontend).

## Prerequisites

- Railway account with PostgreSQL database
- Vercel account
- SendGrid account with API key configured
- GitHub repository with the latest code

## Step 1: Update Environment Variables

### Railway Backend

Add these NEW environment variables in Railway dashboard:

```bash
# Authentication (NEW - Required)
SESSION_SECRET=<generate with: openssl rand -hex 32>

# Existing variables (keep these)
DATABASE_URL=<automatically set by Railway PostgreSQL>
TWITTER_API_KEY=<your twitter api key>
GEMINI_API_KEY=<your gemini api key>
GEMINI_MODEL=gemini-2.0-flash-exp
SENDGRID_API_KEY=<your sendgrid api key>
FROM_EMAIL=kai@ai-productivity.tools
```

To generate SESSION_SECRET:
```bash
openssl rand -hex 32
```

Example output: `7c9e6679f3a8f9e4c8d6a5b4e3f2g1h0i9j8k7l6m5n4o3p2q1r0`

## Step 2: Database Migration

The database will automatically migrate when you deploy. The following will be created:

### New Columns in `users` table:
- `password_hash` - Encrypted user passwords
- `name` - Optional display name
- `status` - Account status (unverified/active/suspended)
- `last_login_at` - Last login timestamp

### New Table: `verification_codes`
- Stores email verification codes
- Stores password reset codes
- Auto-expires after 5-10 minutes

### Migration is Automatic

When you push to GitHub and Railway redeploys:
```python
# This runs automatically in main.py
Base.metadata.create_all(bind=engine)
```

If you need manual migration, see [`DATABASE_MIGRATION.md`](DATABASE_MIGRATION.md).

## Step 3: Deploy Backend to Railway

### Push Code to GitHub

```bash
cd /path/to/xtrack
git add .
git commit -m "Add authentication system with email verification"
git push origin main
```

### Railway will automatically:
1. Detect the changes
2. Install new dependencies (`passlib`, `python-jose`)
3. Run database migrations
4. Redeploy the backend

### Verify Deployment

1. Check Railway logs:
   ```
   [STARTUP] Creating database tables...
   [STARTUP] ✅ Database tables created
   [STARTUP] ✅ Application started successfully
   ```

2. Test the API:
   ```bash
   curl https://your-app.up.railway.app/api/auth/me
   # Should return 401 Unauthorized (expected - not logged in)
   ```

## Step 4: Deploy Frontend to Vercel

### Update Frontend Environment Variable

In Vercel dashboard:

```bash
VITE_API_URL=https://your-railway-backend.up.railway.app/api
```

### Push and Deploy

Vercel will automatically redeploy when you push to GitHub.

### Verify Frontend

Visit your Vercel URL: `https://your-app.vercel.app`

You should see the login page instead of the main app.

## Step 5: Testing the Complete Flow

### Test 1: User Registration

1. Click "立即注册" (Register)
2. Enter email and strong password
3. Click "注册" (Register)
4. You should receive an email with a 6-digit code
5. Enter the verification code
6. You should be logged in automatically

**If email not received**:
- Check SendGrid dashboard for delivery status
- Check spam/junk folder
- Verify `FROM_EMAIL` is verified in SendGrid
- Check Railway logs for email errors

### Test 2: Login

1. Logout
2. Enter your email and password
3. Check "记住我" (Remember me) if desired
4. Click "登录" (Login)
5. You should be logged in

### Test 3: Create a Monitoring Job

1. After login, click "Add Job"
2. Enter an X username (e.g., "elonmusk")
3. Set frequency and topics
4. Your email should be pre-filled
5. Create the job
6. **Verify**: The job should be associated with your user account
7. Logout and login with a different account - you should NOT see the first user's jobs

### Test 4: Forgot Password

1. Logout
2. Click "忘记密码？" (Forgot Password)
3. Enter your email
4. Receive verification code via email
5. Enter code and new password
6. You should be logged in with new password

### Test 5: Profile Management

1. Login
2. Click your email in top-right corner
3. Click "个人资料" (Profile)
4. Update your name
5. Change password
6. Logout to verify changes

## Step 6: Monitor and Debug

### Check Railway Logs

```bash
railway logs
```

Look for:
- `[STARTUP] ✅ Application started successfully`
- `[INFO] POST /api/auth/register`
- `[INFO] POST /api/auth/login`
- `[EMAIL SERVICE] ✅ Email sent successfully`

### Check Database

In Railway PostgreSQL:

```sql
-- Check users
SELECT id, email, name, status, created_at FROM users;

-- Check verification codes (recent)
SELECT email, code_type, used, expires_at 
FROM verification_codes 
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;

-- Check jobs with user associations
SELECT j.id, j.x_username, u.email as owner_email, j.is_active
FROM jobs j
JOIN users u ON j.user_id = u.id;
```

## Troubleshooting

### Issue: "Invalid authentication token"

**Cause**: Frontend and backend URL mismatch, or token expired.

**Solution**:
1. Verify `VITE_API_URL` in Vercel matches Railway URL
2. Clear browser localStorage and try again
3. Check CORS settings in `backend/app/main.py`

### Issue: "No verification email received"

**Cause**: SendGrid not configured or domain not verified.

**Solution**:
1. Check SendGrid dashboard for activity
2. Verify `FROM_EMAIL` matches verified sender in SendGrid
3. Check SendGrid API key is correct in Railway
4. Look for errors in Railway logs

### Issue: "Database column does not exist"

**Cause**: Database migration didn't run.

**Solution**:
1. Check Railway logs for migration errors
2. Manually run migration SQL (see DATABASE_MIGRATION.md)
3. Or recreate PostgreSQL service for fresh start

### Issue: "User can see other users' jobs"

**Cause**: Jobs router not properly filtering by user.

**Solution**:
1. Verify you're using the updated `jobs.py` router
2. Check that authentication is required for all job endpoints
3. Redeploy backend

### Issue: CORS Error in Browser Console

**Cause**: Frontend URL not in CORS allowed origins.

**Solution**:
Update `backend/app/main.py`:
```python
allow_origins=[
    "http://localhost:5173",
    "https://your-vercel-app.vercel.app",  # Add your actual URL
    "https://*.vercel.app"
],
```

## Security Checklist

- [ ] `SESSION_SECRET` is a strong random 32+ character string
- [ ] `SESSION_SECRET` is different in production vs development
- [ ] SendGrid API key is kept secret (not in code)
- [ ] HTTPS is enabled (automatic on Railway/Vercel)
- [ ] CORS is configured to only allow your frontend domain
- [ ] Password requirements are enforced (8+ chars, mixed case, numbers, special chars)
- [ ] Email verification is required before account activation
- [ ] Verification codes expire after 5-10 minutes
- [ ] Users can only access their own jobs and summaries

## Performance Considerations

### Database Indexes

The migration creates indexes on:
- `users.email` - for fast login lookups
- `verification_codes.email` - for code lookups
- `verification_codes.expires_at` - for cleanup queries

### Cleanup Old Verification Codes

Consider adding a periodic cleanup job:

```python
# Optional: Add to scheduler.py
def cleanup_expired_codes():
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=7)
        db.query(VerificationCode).filter(
            VerificationCode.created_at < cutoff
        ).delete()
        db.commit()
    finally:
        db.close()

# Run daily
scheduler.add_job(cleanup_expired_codes, 'cron', hour=3)
```

## Next Steps

1. ✅ Test all authentication flows thoroughly
2. ✅ Monitor Railway logs for first few days
3. ✅ Set up error monitoring (optional: Sentry)
4. ✅ Create user documentation
5. ✅ Consider adding:
   - Two-factor authentication (2FA)
   - OAuth login (Google, GitHub)
   - Account deletion
   - Email change with verification
   - Login history/activity log

## Support

For issues:
1. Check Railway logs: `railway logs`
2. Check Vercel function logs
3. Check browser console for frontend errors
4. Review this guide's troubleshooting section
5. Check DATABASE_MIGRATION.md for database issues

---

**Congratulations!** Your authentication system is now deployed and ready to use. 🎉

