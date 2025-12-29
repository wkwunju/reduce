# Database Migration Guide

This guide explains how to migrate your XTrack database to support the new authentication system.

## Changes Overview

The authentication system adds:
- New fields to the `users` table: `password_hash`, `name`, `status`, `last_login_at`
- New `verification_codes` table for email verification and password reset

## Migration Options

### Option 1: Automatic Migration (Railway with PostgreSQL)

If you're using Railway with PostgreSQL, the database tables will be automatically created/updated when you deploy the updated code.

1. **Deploy backend to Railway** (it will automatically run migrations)
2. **Verify in Railway Dashboard**:
   - Go to your PostgreSQL service
   - Check that the tables have the new columns

### Option 2: Manual Migration (Local or Railway PostgreSQL)

If you need to manually run the migration:

#### For PostgreSQL:

```sql
-- Connect to your database first
-- psql -U postgres -d xtrack  (local)
-- or use Railway's PostgreSQL connection string

-- Add new columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'unverified';
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP;

-- Create verification_codes table
CREATE TABLE IF NOT EXISTS verification_codes (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    code_type VARCHAR(30) NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_verification_codes_email ON verification_codes(email);
CREATE INDEX IF NOT EXISTS idx_verification_codes_code ON verification_codes(code);
CREATE INDEX IF NOT EXISTS idx_verification_codes_expires ON verification_codes(expires_at);
```

#### For SQLite (Local Development):

```sql
-- Connect to your database
-- sqlite3 xtrack.db

-- Add new columns to users table
ALTER TABLE users ADD COLUMN password_hash TEXT;
ALTER TABLE users ADD COLUMN name TEXT;
ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'unverified';
ALTER TABLE users ADD COLUMN last_login_at DATETIME;

-- Create verification_codes table
CREATE TABLE IF NOT EXISTS verification_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    code_type TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_verification_codes_email ON verification_codes(email);
CREATE INDEX IF NOT EXISTS idx_verification_codes_code ON verification_codes(code);
CREATE INDEX IF NOT EXISTS idx_verification_codes_expires ON verification_codes(expires_at);
```

### Option 3: Fresh Start (Recommended for Development)

If you're in development and don't have important data:

1. **Backup any important data** (if needed)

2. **Drop and recreate tables**:
   - For Railway: Delete the PostgreSQL service and create a new one
   - For local: Delete your database file and let the app recreate it

3. **Restart your application** - it will create all tables with the new schema

## Environment Variables

Don't forget to add the new required environment variable:

### Railway (Production)

In your Railway dashboard, add:

```bash
SESSION_SECRET=your-random-32-character-string
```

Generate a secure random string:
```bash
openssl rand -hex 32
```

### Local Development

Update your `backend/.env` file:

```bash
SESSION_SECRET=your-random-32-character-string-for-dev
```

## Verification

After migration, verify the changes:

### Check Users Table

```sql
-- PostgreSQL
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users';

-- SQLite
PRAGMA table_info(users);
```

You should see:
- `password_hash` column
- `name` column
- `status` column
- `last_login_at` column

### Check Verification Codes Table

```sql
-- PostgreSQL
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'verification_codes';

-- SQLite
PRAGMA table_info(verification_codes);
```

## Migrating Existing Users

If you have existing users in your database, they won't have passwords yet. You have two options:

### Option A: Reset All Users (Simple)

1. Clear the users table:
```sql
DELETE FROM users;
```

2. Ask all users to register again with the new system

### Option B: Keep Existing Users (Complex)

1. Set all existing users to a temporary password:
```sql
-- This is a hashed version of "ChangeMe123!"
UPDATE users 
SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7evQlkNcqy',
    status = 'active'
WHERE password_hash IS NULL;
```

2. Notify users to:
   - Use "ChangeMe123!" as their initial password
   - Change their password immediately after first login

## Troubleshooting

### Error: column "password_hash" does not exist

**Solution**: Run the migration SQL commands above.

### Error: table "verification_codes" does not exist

**Solution**: Run the CREATE TABLE command for verification_codes.

### Error: TWITTER_API_KEY not found

This is unrelated to the migration. Make sure your environment variables are set correctly.

### Users can't login after migration

If you used Option B above, make sure users know their temporary password is "ChangeMe123!".

## Next Steps

1. ✅ Run the database migration
2. ✅ Add SESSION_SECRET environment variable
3. ✅ Deploy the updated code
4. ✅ Test the registration flow
5. ✅ Test the login flow
6. ✅ Test email verification

## Support

If you encounter issues:

1. Check Railway logs: `railway logs`
2. Check the database connection in Railway dashboard
3. Verify all environment variables are set correctly
4. Make sure SendGrid is configured for email verification

---

**Important**: Always backup your database before running migrations in production!

