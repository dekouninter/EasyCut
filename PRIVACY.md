# Privacy Policy for EasyCut

**Last Updated:** February 15, 2026

## Overview

EasyCut is a desktop application for downloading YouTube videos and recording live streams. This privacy policy explains how we handle your data.

## Information We Collect

### YouTube Authentication (OAuth 2.0)

When you click "Sync with YouTube":
- We request access to your YouTube account via Google OAuth 2.0
- Scope requested: `youtube.readonly` (read-only access to your YouTube data)
- We receive an access token from Google that allows the app to download videos on your behalf

### Data Storage

**Locally Stored Data:**
- OAuth access tokens (stored in `config/youtube_token.pickle`)
- YouTube cookies (stored in `config/yt_cookies.txt`)
- Download history (stored in `config/history_downloads.json`)
- Application settings (stored in `config/config.json`)
- Application logs (stored in `config/app.log`)

**All data is stored locally on your computer. Nothing is sent to external servers.**

## Data Usage

EasyCut uses your YouTube authentication to:
- Download videos you request
- Record live streams you specify
- Access video metadata (title, duration, quality options)

## Data Sharing

**We do NOT:**
- Send your data to any external servers
- Share your information with third parties
- Collect analytics or telemetry
- Track your usage
- Store your data in the cloud

**Your data stays on your computer.**

## Google OAuth Permissions

EasyCut requests the following scope:
- **`https://www.googleapis.com/auth/youtube.readonly`**: Read-only access to YouTube

This allows the app to:
- Download videos from YouTube on your behalf
- Access video information (title, quality, etc.)
- Maintain authenticated sessions for downloads

We **cannot** and **do not**:
- Upload videos to your account
- Modify your playlists or subscriptions
- Post comments
- Change account settings
- Access your personal information beyond what's necessary for authentication

## Data Retention

- OAuth tokens are stored until you click "Logout"
- OAuth cookies file is stored until you click "Logout"
- Download history is kept until you clear it manually
- Application logs are stored locally (no automatic rotation in current code)
- You can delete all data by removing the `config/` folder

## Data Security

- OAuth tokens are stored locally using Python's pickle format
- No passwords are stored (authentication is handled by Google)
- All communication with YouTube uses HTTPS
- Your credentials never pass through our servers (because we don't have servers)

## Your Rights

You have the right to:
- Revoke EasyCut's access to your YouTube account at any time via [Google Account Settings](https://myaccount.google.com/permissions)
- Delete all locally stored data
- Stop using the application at any time
- Request clarification about our data practices

## Third-Party Services

EasyCut uses:
- **Google OAuth 2.0**: For YouTube authentication (see [Google's Privacy Policy](https://policies.google.com/privacy))
- **yt-dlp**: Open-source tool for video downloads (no data collection)
- **FFmpeg**: Optional media processing tool (not invoked by current code)

## Open Source

EasyCut is open-source software. You can review the entire source code at:
https://github.com/dekouninter/EasyCut

## Children's Privacy

EasyCut does not knowingly collect data from children under 13. The app is intended for general audiences.

## Changes to This Policy

We may update this privacy policy. Changes will be posted with a new "Last Updated" date.

## Contact

For questions about this privacy policy or data practices:
- **GitHub**: https://github.com/dekouninter/EasyCut/issues
- **Developer**: Deko Costa
- **Email**: easycutdark@gmail.com

## Legal Compliance & User Responsibility

**Personal Use Only:**

EasyCut is designed for personal, non-commercial use. When using this application:

1. **You are responsible** for complying with:
   - YouTube's Terms of Service
   - Copyright laws in your jurisdiction
   - Content creators' rights

2. **Acceptable downloads:**
   - Your own content uploaded to YouTube
   - Content with explicit permission from the creator
   - Content permitted under fair use (where applicable)

3. **The developers are NOT responsible for:**
   - Copyright violations by users
   - Misuse of the software
   - Legal consequences from unauthorized downloads

**By using EasyCut, you accept full responsibility for your actions.**

## Consent

By using EasyCut and clicking "Sync with YouTube", you:
- Consent to this privacy policy
- Acknowledge the legal disclaimer
- Accept responsibility for your downloads
- Agree to use the software for personal, legal purposes only

---

**Summary:**
- All data stays on your computer
- We don't send anything to external servers
- OAuth tokens are stored securely locally
- You can revoke access anytime
- Open-source and transparent
- **FOR PERSONAL USE ONLY - You are responsible for legal compliance**
