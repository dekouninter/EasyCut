# OAuth Authentication Setup for EasyCut
## 🎯 Who Needs This?

**👤 End Users (downloading releases):**  
✅ **You DON'T need this!** OAuth credentials are already embedded in `EasyCut.exe`.  
Just download, run, and click "Sync with YouTube".

**👨‍💻 Developers (running from source code):**  
✅ **You NEED this!** Follow the steps below to create your own OAuth credentials.

---
## 🔐 Secure YouTube Authentication

EasyCut now uses Google OAuth 2.0 for secure authentication with YouTube. This allows you to download videos while keeping your browser fully available for browsing.

### OAuth Scope Used

- **Scope**: `https://www.googleapis.com/auth/youtube.readonly`
- **Purpose**: Read-only access to YouTube metadata and authenticated downloads

### Verification (Remove Google Warning)

If you are seeing the Google OAuth warning screen, follow these steps in your own Google Cloud project:

1. Open **Google Cloud Console** and select your project.
2. Go to **APIs & Services** → **OAuth consent screen**.
3. Fill app name, support email, and developer contact email.
4. Add **Test Users** while your app is in Testing mode.
5. Ensure the scope is limited to `https://www.googleapis.com/auth/youtube.readonly`.
6. Publish the app when you are ready to remove the warning.

### Files Created by EasyCut

- `config/credentials.json` — Your OAuth client credentials (developer setup)
- `config/youtube_token.pickle` — OAuth token cache (created after login)
- `config/yt_cookies.txt` — Cookies exported for yt-dlp (created after login)

## ✅ Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Create a new project:
   - Click on the project dropdown
   - Click "NEW PROJECT"
   - Enter a name: `EasyCut` or whatever you prefer
   - Click "CREATE"

### Step 2: Enable YouTube Data API

1. Search for "YouTube Data API v3" in the search bar
2. Click on it
3. Click "ENABLE"
4. Wait a few seconds for it to enable

### Step 3: Create OAuth Credentials

1. Go to "Credentials" in the left menu
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - User type: "External"
   - Click "CREATE"
   - Fill in the required fields (app name, user support email, etc.)
   - Click "SAVE & CONTINUE" through all steps
4. Back to OAuth client ID creation:
   - Application type: **"Desktop application"**
   - Name: `EasyCut` (doesn't matter)
   - Click "CREATE"

**Note:** EasyCut uses a local redirect URI (`http://localhost`) during OAuth flow.

### Step 4: Download Credentials

1. A popup will appear - click **"DOWNLOAD JSON"**
2. This downloads `credentials.json`

### Step 5: Place Credentials File

1. Copy the downloaded `credentials.json` to the `config` folder of EasyCut:
   ```
   EasyCut/
   ├── config/
   │   └── credentials.json    ← Place here
   ├── main.py
   ├── requirements.txt
   └── ...
   ```

### Step 6: Authenticate in EasyCut

1. Open EasyCut
2. You should see a **"YouTube Authentication"** banner at the top
3. Click **"Sync with YouTube"**
4. Your browser will open automatically
5. Sign in with your Google account
6. Click **"Allow"** when asked for permissions
7. Done! ✅ You're authenticated!

**Behind the scenes**: EasyCut creates `config/youtube_token.pickle` and `config/yt_cookies.txt`, which are used for authenticated downloads.

## 🔄 What Happens

- **First time**: Browser opens, you login once
- **Next times**: Just click "Download" - no login needed!
- **Tokens are saved locally**: In `config/youtube_token.pickle`
- **Your browser stays free**: Downloads happen separately from your browser cookies

## 🚀 Now You Can

✅ Download videos while browsing YouTube  
✅ Download live streams  
✅ Monitor and download multiple videos at once  
✅ No DPAPI errors  
✅ No browser interference  

## ❌ Troubleshooting

#### "credentials.json not found"
- Make sure you downloaded it from Google Cloud
- Place it in `config/` folder
- Restart EasyCut

#### "Authentication failed"
- Check internet connection
- Make sure YouTube Data API is enabled
- Try logging out and re-authenticating

#### "OAuth Error 403: Access Denied"
- Your OAuth app is still in Testing mode
- Add your Google account as a **Test User** in the Google Cloud Console
- Or publish the OAuth consent screen

**Note:** Some error messages may reference `OAUTH_SETUP.md`. Use the steps in this document.

#### "Failed to get cookies"
- Try clicking "Sync with YouTube" again
- Make sure you granted permissions when browser asked

## 🔒 Security Notes

- ✅ Your password never goes through EasyCut
- ✅ Authentication is handled by Google
- ✅ Tokens are stored securely locally
- ✅ You can revoke access anytime from Google account

## 📚 More Information

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2/)
- [YouTube Data API Guide](https://developers.google.com/youtube/v3/getting-started)
- [BUILD.md](BUILD.md) — Building with embedded OAuth credentials
- [README.md](README.md) — Main documentation
