# Gmail API Setup Guide

This guide explains how to set up Gmail API with OAuth 2.0 for sending emails from XTrack.

## Why Gmail API instead of SMTP?

- ✅ **More Secure**: Uses OAuth 2.0 instead of passwords
- ✅ **No App Passwords**: Don't need to generate or manage app passwords
- ✅ **Better Control**: Can revoke access anytime from Google Account settings
- ✅ **Official Method**: Uses Google's official API

## Setup Steps

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project name (e.g., "XTrack")
5. Click "Create"

### Step 2: Enable Gmail API

1. In the Google Cloud Console, go to **"APIs & Services"** > **"Library"**
2. Search for **"Gmail API"**
3. Click on "Gmail API"
4. Click **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** > **"OAuth consent screen"**
2. Select **"External"** user type
3. Click **"Create"**
4. Fill in the required fields:
   - **App name**: XTrack (or your preferred name)
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click **"Save and Continue"**
6. On the "Scopes" page, click **"Add or Remove Scopes"**
7. Search for and add: `https://www.googleapis.com/auth/gmail.send`
8. Click **"Update"** then **"Save and Continue"**
9. On "Test users" page, click **"Add Users"**
10. Add your Gmail address (the one you'll use to send emails)
11. Click **"Save and Continue"**

### Step 4: Create OAuth Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"Create Credentials"** > **"OAuth client ID"**
3. Select **"Desktop app"** as the application type
4. Enter a name (e.g., "XTrack Email Client")
5. Click **"Create"**
6. Click **"OK"** on the success dialog

### Redirect URIs (Desktop App)
For a desktop OAuth client, add these redirect URIs:
```
http://localhost
http://localhost:8080/
http://localhost:8090/
```

### Step 5: Download Credentials

1. In the "OAuth 2.0 Client IDs" section, find your newly created client
2. Click the **download icon** (⬇️) on the right
3. Save the file as **`credentials.json`**
4. Move it to your **`backend`** directory:
   ```bash
   mv ~/Downloads/client_secret_*.json /path/to/xtrack/backend/credentials.json
   ```

### Step 6: Configure Environment Variables

1. Open `backend/.env` (or create from `.env.example`)
2. Add or update:
   ```env
   FROM_EMAIL=your_email@gmail.com
   GMAIL_CREDENTIALS_FILE=credentials.json
   GMAIL_TOKEN_FILE=token.pickle
   ```

### Step 7: First Run - OAuth Authorization

1. Start your backend server:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. The first time the email service tries to send an email, it will:
   - Open a browser window automatically
   - Ask you to sign in to your Google Account
   - Show the OAuth consent screen
   - Ask you to grant permissions

3. **Click "Allow"** to grant permissions

4. The browser will show "The authentication flow has completed"

5. A `token.pickle` file will be created automatically in the `backend` directory

6. **You're done!** The token will be reused for future requests

## File Structure

After setup, your backend directory should have:
```
backend/
├── credentials.json    # OAuth client credentials (keep secret!)
├── token.pickle        # Access token (auto-generated, keep secret!)
├── .env               # Your configuration
├── app/
└── ...
```

⚠️ **Security Note**: Never commit `credentials.json` or `token.pickle` to git! They're in `.gitignore` by default.

## Testing Email

### Option 1: Use the Frontend Test Function

1. Go to http://localhost:5173
2. Click "Quick Test"
3. Enter a username and email address
4. Click "Run Test"
5. Check the email inbox

### Option 2: Use the API Directly

```bash
curl -X POST "http://localhost:8000/api/monitoring/test" \
  -H "Content-Type: application/json" \
  -d '{
    "x_username": "elonmusk",
    "hours_back": 24,
    "topics": ["AI"],
    "email": "your_email@gmail.com"
  }'
```

## Troubleshooting

### "credentials.json not found"

- Make sure you've downloaded the OAuth credentials from Google Cloud Console
- Place the file in the `backend` directory
- Rename it to `credentials.json` (not `client_secret_*.json`)

### "OAuth flow failed"

- Make sure you've enabled Gmail API in Google Cloud Console
- Check that your email is added as a test user in OAuth consent screen
- Try deleting `token.pickle` and re-authorizing

### "Insufficient permissions"

- Make sure you added the `gmail.send` scope in OAuth consent screen
- Delete `token.pickle` and re-authorize to get new permissions

### Browser doesn't open during OAuth

- Check your firewall settings
- The app tries to open `http://localhost:[random-port]`
- You can manually copy the URL from the terminal and paste in browser

### "Access blocked: This app's request is invalid"

- Make sure your app is in "Testing" mode (not "Published") in OAuth consent screen
- Add your email to the test users list
- Wait a few minutes for Google to propagate the changes

### Token expired

- The token automatically refreshes
- If refresh fails, delete `token.pickle` and re-authorize

## Revoking Access

To revoke XTrack's access to your Gmail:

1. Go to [Google Account - Apps with access](https://myaccount.google.com/permissions)
2. Find "XTrack" (or whatever you named it)
3. Click "Remove Access"
4. Delete `token.pickle` from the backend directory

## Re-authorizing

If you need to re-authorize (e.g., changed Gmail account):

1. Delete `token.pickle`:
   ```bash
   cd backend
   rm token.pickle
   ```
2. Restart the server
3. The OAuth flow will start again automatically

## Production Deployment

For production:

1. **Keep credentials secure**: Store `credentials.json` securely (e.g., AWS Secrets Manager)
2. **Use environment variables**: 
   ```env
   GMAIL_CREDENTIALS_FILE=/secure/path/to/credentials.json
   GMAIL_TOKEN_FILE=/secure/path/to/token.pickle
   ```
3. **Consider service accounts**: For server-to-server, use service accounts instead
4. **Move to "Published" mode**: If you want any Gmail user to use it (requires verification)

## Differences from SMTP

| Feature | Gmail API (OAuth) | SMTP |
|---------|------------------|------|
| Security | OAuth 2.0 tokens | Username + Password/App Password |
| Setup | Google Cloud Console | Just credentials |
| Access Control | Can revoke from Google Account | Need to change password |
| Rate Limits | Higher (up to 1 billion/day) | Lower |
| Official Support | Yes | Yes, but older method |
| 2FA Required | No | Yes (for App Password) |

## Additional Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
