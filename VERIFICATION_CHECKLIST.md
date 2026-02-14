# Google OAuth Verification Checklist

## 📋 Pre-Submission Checklist

Before submitting your app for Google OAuth verification, ensure you have completed all items below.

---

## ✅ Step 1: Prepare Documentation

- [x] **Privacy Policy** created → [PRIVACY.md](PRIVACY.md)
- [x] **Terms of Service** created → [TERMS.md](TERMS.md)
- [ ] **Privacy Policy URL** accessible online
  - [ ] Upload PRIVACY.md to GitHub repository
  - [ ] Get raw GitHub URL: `https://raw.githubusercontent.com/dekouninter/EasyCut/main/PRIVACY.md`
  - [ ] Verify URL is publicly accessible (open in browser)

- [ ] **Terms of Service URL** accessible online
  - [ ] Upload TERMS.md to GitHub repository
  - [ ] Get raw GitHub URL: `https://raw.githubusercontent.com/dekouninter/EasyCut/main/TERMS.md`
  - [ ] Verify URL is publicly accessible

- [ ] **Homepage URL** accessible
  - Use: `https://github.com/dekouninter/EasyCut`
  - [ ] Verify README.md is complete and professional

---

## ✅ Step 2: Create Demonstration Video

Google requires a video showing your app in action.

**Requirements:**
- Length: 1-3 minutes
- Shows complete OAuth flow
- Demonstrates why you need the requested scope (`youtube.readonly`)
- Shows the app's functionality

**What to Show:**
1. App opening
2. Clicking "Sync with YouTube"
3. Browser opening with Google login
4. Granting permissions
5. Successful authentication
6. Using the app to download a video
7. (Optional) Logout process

**Hosting Options:**
- YouTube (unlisted): https://www.youtube.com/upload
- Google Drive (public link): https://drive.google.com/
- Loom: https://www.loom.com/

- [ ] Video recorded
- [ ] Video uploaded
- [ ] Video URL obtained
- [ ] Video is publicly accessible (test in incognito mode)

---

## ✅ Step 3: Prepare OAuth Consent Screen

Go to: https://console.cloud.google.com/ → Your Project → OAuth consent screen

### App Information:

- [ ] **App name**: EasyCut
- [ ] **User support email**: easycutdark@gmail.com (or your email)
- [ ] **App logo** (optional but recommended):
  - Size: 120x120 pixels minimum
  - Format: PNG or JPEG
  - Use app icon from `assets/` folder

### App Domain:

- [ ] **Application home page**: https://github.com/dekouninter/EasyCut
- [ ] **Privacy policy link**: https://raw.githubusercontent.com/dekouninter/EasyCut/main/PRIVACY.md
- [ ] **Terms of service link**: https://raw.githubusercontent.com/dekouninter/EasyCut/main/TERMS.md

### Authorized Domains:

- [ ] Add: `github.com` (if using GitHub for hosting)

### Developer Contact Information:

- [ ] **Email**: easycutdark@gmail.com

---

## ✅ Step 4: Verify Scopes

In OAuth consent screen → Scopes:

- [ ] **Scope added**: `https://www.googleapis.com/auth/youtube.readonly`
- [ ] **Justification prepared** (why you need this scope):

```
EasyCut requires read-only access to YouTube to:
1. Download videos that users request
2. Access video metadata (title, quality, duration)
3. Record live streams on user's behalf
4. Maintain authenticated sessions for downloads

The app does NOT modify any user data, post content, or change account settings.
All functionality is read-only and user-initiated.
```

---

## ✅ Step 5: Complete Verification Form

### Brand Information:

**App Name:**
```
EasyCut
```

**App Description (max 120 characters):**
```
Professional YouTube video downloader and audio converter with OAuth 2.0 authentication
```

**Long Description:**
```
EasyCut is a free, open-source desktop application that allows users to download YouTube videos, record live streams, and convert media to audio formats. The app uses Google OAuth 2.0 for secure authentication, requesting only read-only access to YouTube. All processing happens locally on the user's device, with no data sent to external servers.

Key Features:
- Download YouTube videos in multiple quality options
- Record live streams with monitoring
- Convert videos to MP3, WAV, M4A, OPUS
- Batch download support
- Extract specific time ranges
- Dark/Light theme
- Multi-language (English, Portuguese)

Why OAuth is needed:
EasyCut uses the youtube.readonly scope to download videos on behalf of the authenticated user. This ensures proper attribution and allows downloading of content that requires authentication. The app cannot and does not modify any user data.

Technical Details:
- Built with Python and Tkinter
- Uses yt-dlp for video processing
- Fully open-source (GPL-3.0)
- No telemetry or data collection
- All data stored locally
```

### Scope Justification:

**For `youtube.readonly`:**
```
SCOPE: https://www.googleapis.com/auth/youtube.readonly

JUSTIFICATION:
EasyCut requires read-only YouTube access to download videos at the user's explicit request. The scope is used to:

1. Authenticate with YouTube to download videos
2. Access video metadata (title, quality options, duration)
3. Download videos that require authentication
4. Record live streams on the user's behalf

The app NEVER:
- Modifies user data
- Uploads content
- Posts comments
- Changes playlists or subscriptions
- Accesses data without explicit user action

All downloads are user-initiated by pasting a URL and clicking "Download". The app is transparent, open-source, and privacy-focused, storing all data locally without external servers.

Video demonstration shows the complete flow from authentication to video download.
```

---

## ✅ Step 6: Supporting Materials

- [ ] **Video demonstration URL**: _____________________
- [ ] **Privacy Policy URL**: https://raw.githubusercontent.com/dekouninter/EasyCut/main/PRIVACY.md
- [ ] **Terms of Service URL**: https://raw.githubusercontent.com/dekouninter/EasyCut/main/TERMS.md
- [ ] **Homepage URL**: https://github.com/dekouninter/EasyCut

### Screenshots (if requested):

Take screenshots showing:
1. Main application window
2. OAuth consent screen
3. Successful authentication
4. Video download in progress

---

## ✅ Step 7: Submit for Verification

1. Go to: https://console.cloud.google.com/
2. Select project: EasyCut (sunny-caldron-487419-e4)
3. Navigate to: OAuth consent screen
4. Click: **"PREPARE FOR VERIFICATION"** or **"SUBMIT FOR VERIFICATION"**
5. Fill out the verification questionnaire
6. Upload all prepared materials
7. Submit

---

## ⏱️ Timeline

- **Submission**: ~30 minutes
- **Google Review**: 4-6 weeks typically
- **Possible Responses**:
  - ✅ Approved → You're live!
  - ⚠️ More info needed → Respond quickly to Google's questions
  - ❌ Rejected → Review feedback and resubmit with changes

---

## 📌 Important Notes

### During Review:

- Check email regularly (including spam folder)
- Respond to Google inquiries within 7 days
- Keep app functionality stable
- Don't change OAuth scopes during review

### If Approved:

- ✅ "Unverified app" warning disappears
- ✅ Users can authenticate without "unsafe" screen
- ✅ No daily user limits
- ✅ Professional public launch ready

### If Rejected:

- Review Google's feedback carefully
- Make requested changes
- Resubmit with improvements
- Common issues:
  - Unclear scope justification
  - Missing/inadequate documentation
  - Video doesn't show complete flow

---

## 🎯 Quick Start

1. Push PRIVACY.md and TERMS.md to GitHub: `git push`
2. Get raw GitHub URLs for both
3. Record demonstration video
4. Fill out OAuth consent screen in Google Cloud Console
5. Click "Submit for Verification"
6. Wait 4-6 weeks
7. Launch! 🚀

---

**Good luck with your submission!**

For questions or issues:
- Google OAuth Help: https://support.google.com/cloud/answer/9110914
- Verification Requirements: https://support.google.com/cloud/answer/13463073
