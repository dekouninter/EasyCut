"""
OAuth Authentication Manager for YouTube
Handles Google OAuth 2.0 authentication and token management
"""

import json
import os
from pathlib import Path
from typing import Optional, Tuple
import webbrowser
import http.cookiejar
import io

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests


class OAuthError(Exception):
    """Custom exception for OAuth authentication errors"""
    pass


class OAuthManager:
    """Manages OAuth authentication with Google for YouTube access"""
    
    # Google OAuth scopes - minimal permissions
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
    
    def __init__(self, config_dir: str = "config", credentials_data: Optional[dict] = None):
        """
        Initialize OAuth Manager
        
        Args:
            config_dir: Directory to store token files
            credentials_data: Optional OAuth credentials dict (for packaged releases)
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.token_file = self.config_dir / "youtube_token.json"
        self._legacy_token_file = self.config_dir / "youtube_token.pickle"
        self.cookies_file = self.config_dir / "yt_cookies.txt"
        self.credentials_file = self.config_dir / "credentials.json"
        
        # Store credentials data (either passed in or will load from file)
        self._credentials_data = credentials_data
        
        self.creds: Optional[Credentials] = None
        self._load_token()
    
    def _load_token(self) -> bool:
        """Load saved token from file (JSON format, with legacy pickle migration)"""
        # Try new JSON format first
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    token_data = json.load(f)
                self.creds = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes'),
                )
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self._refresh_token()
                return True
            except Exception as e:
                print(f"Error loading JSON token: {e}")
                return False

        # Migrate legacy pickle token if it exists
        if self._legacy_token_file.exists():
            try:
                import pickle
                with open(self._legacy_token_file, 'rb') as f:
                    self.creds = pickle.load(f)
                # Re-save in JSON format and remove legacy file
                self._save_token()
                self._legacy_token_file.unlink(missing_ok=True)
                print("Migrated token from pickle to JSON format.")
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self._refresh_token()
                return True
            except Exception as e:
                print(f"Error migrating legacy token: {e}")
                self._legacy_token_file.unlink(missing_ok=True)
                return False

        return False
    
    def _load_credentials(self) -> dict:
        """
        Load OAuth credentials from multiple sources in priority order:
        1. Credentials passed to __init__ (for packaged releases)
        2. credentials.json file in config directory
        3. Raise error if none found
        
        Returns:
            dict: OAuth credentials in Google client config format
        
        Raises:
            OAuthError: If no credentials found
        """
        # Priority 1: Use credentials passed to constructor (packaged releases)
        if self._credentials_data:
            return self._credentials_data
        
        # Priority 2: Load from config/credentials.json (development)
        if self.credentials_file.exists():
            try:
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                    
                    # Validate required fields
                    if 'installed' in credentials:
                        required = ['client_id', 'client_secret']
                        if all(k in credentials['installed'] for k in required):
                            return credentials
                    
                    raise OAuthError(
                        "Invalid credentials.json format. Please follow OAUTH_SETUP.md"
                    )
            except json.JSONDecodeError:
                raise OAuthError(
                    "credentials.json is corrupted. Please recreate it following OAUTH_SETUP.md"
                )
        
        # No credentials found
        raise OAuthError(
            f"OAuth credentials not found.\n\n"
            f"For end-users: Download the official release from GitHub.\n"
            f"For developers: Create {self.credentials_file} following OAUTH_SETUP.md"
        )
    
    def _save_token(self) -> bool:
        """Save token to file in JSON format"""
        try:
            token_data = {
                'token': self.creds.token,
                'refresh_token': self.creds.refresh_token,
                'token_uri': self.creds.token_uri,
                'client_id': self.creds.client_id,
                'client_secret': self.creds.client_secret,
                'scopes': list(self.creds.scopes) if self.creds.scopes else None,
            }
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(token_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving token: {e}")
            return False
    
    def _refresh_token(self) -> bool:
        """Refresh expired token"""
        if not self.creds or not self.creds.refresh_token:
            return False
        
        try:
            self.creds.refresh(Request())
            self._save_token()
            return True
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        if not self.creds:
            return False
        
        # Try to refresh if expired
        if self.creds.expired and self.creds.refresh_token:
            self._refresh_token()
        
        return self.creds is not None and self.creds.valid
    
    def authenticate(self, on_browser_open=None) -> bool:
        """
        Perform OAuth authentication flow
        
        Args:
            on_browser_open: Callback function when browser opens
            
        Returns:
            True if authentication successful
        
        Raises:
            OAuthError: With specific error message for common issues
        """
        try:
            # Load OAuth credentials
            credentials_data = self._load_credentials()
            
            # Create flow from credentials
            flow = InstalledAppFlow.from_client_config(
                credentials_data,
                self.SCOPES,
                redirect_uri='http://localhost'
            )
            
            # Callback when browser opens
            if on_browser_open:
                on_browser_open()
            
            # Success page — styled dark page (no Close button: window.close() is
            # blocked by browsers for tabs not opened by JavaScript).
            _success_html = (
                "<html><head>"
                "<style>"
                "body{font-family:system-ui,sans-serif;background:#0d0f16;color:#e2e8f0;"
                "text-align:center;padding:60px 40px;margin:0;}"
                "</style></head><body>"
                "<h2 style='color:#4ade80;font-size:2em;'>&#x2705; Authentication Successful!</h2>"
                "<p style='font-size:1.1em;'>EasyCut is now connected to your YouTube account.</p>"
                "<p style='color:#94a3b8;margin-top:24px;font-size:0.95em;'>"
                "You can close this tab and return to EasyCut.</p>"
                "</body></html>"
            )

            # Patch WSGI app to send text/html instead of text/plain
            from google_auth_oauthlib.flow import _RedirectWSGIApp
            _orig_call = _RedirectWSGIApp.__call__
            def _html_call(self_wsgi, environ, start_response):
                import wsgiref.util
                start_response("200 OK", [("Content-type", "text/html; charset=utf-8")])
                self_wsgi.last_request_uri = wsgiref.util.request_uri(environ)
                return [self_wsgi._success_message.encode("utf-8")]
            _RedirectWSGIApp.__call__ = _html_call

            self.creds = flow.run_local_server(
                port=0, open_browser=True, success_message=_success_html
            )

            # Restore original method
            _RedirectWSGIApp.__call__ = _orig_call
            
            # Save token for future use
            self._save_token()
            
            return True
        
        except OAuthError:
            # Re-raise our custom errors
            raise
        
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for common OAuth errors
            if 'access_denied' in error_msg or '403' in error_msg:
                raise OAuthError(
                    "❌ Google OAuth Error 403: Access Denied\n\n"
                    "The OAuth app is in Testing mode. To fix:\n\n"
                    "1. Go to: https://console.cloud.google.com/\n"
                    "2. Select project: EasyCut\n"
                    "3. OAuth consent screen → Add Test Users\n"
                    "4. Add your Google email\n"
                    "5. OR publish the app\n\n"
                    "📖 See OAUTH_FIX.md for detailed instructions"
                )
            elif 'redirect_uri_mismatch' in error_msg:
                raise OAuthError(
                    "❌ Redirect URI mismatch\n\n"
                    "The OAuth app redirect URI is not configured correctly.\n"
                    "Please contact the developer."
                )
            else:
                raise OAuthError(f"Authentication failed: {e}")
    
    def get_youtube_cookies(self) -> Optional[str]:
        """
        Get YouTube cookies from authenticated session
        Uses OAuth token to authenticate with YouTube and extract cookies
        
        Returns:
            Path to cookies file or None if failed
        """
        if not self.is_authenticated():
            return None
        
        try:
            # Create authenticated session
            session = requests.Session()
            
            # Add authorization header
            session.headers['Authorization'] = f'Bearer {self.creds.token}'
            session.headers['User-Agent'] = (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # Access YouTube to establish session
            response = session.get('https://www.youtube.com', timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to access YouTube: {response.status_code}")
                return None
            
            # Extract and save cookies in Netscape format
            self._save_cookies_netscape(session.cookies, self.cookies_file)
            
            return str(self.cookies_file)
        
        except Exception as e:
            print(f"Error getting YouTube cookies: {e}")
            return None
    
    @staticmethod
    def _save_cookies_netscape(cookies, filepath: Path):
        """
        Save cookies in Netscape HTTP Cookie File format for yt-dlp
        
        Format:
        .youtube.com	TRUE	/	TRUE	1234567890	cookie_name	cookie_value
        """
        try:
            with open(filepath, 'w') as f:
                # Netscape cookie jar header
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# This is part of EasyCut YouTube Authentication\n")
                f.write("# Do not edit manually\n\n")
                
                for cookie in cookies:
                    # Format: domain flag path secure expiration name value
                    domain = cookie.domain or '.youtube.com'
                    flag = 'TRUE'
                    path = '/'
                    secure = 'TRUE' if cookie.secure else 'FALSE'
                    expires = str(cookie.expires) if cookie.expires else '0'
                    name = cookie.name
                    value = cookie.value
                    
                    f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}\n")
        
        except Exception as e:
            print(f"Error saving cookies: {e}")
    
    def logout(self) -> bool:
        """Remove saved token and logout"""
        try:
            if self.token_file.exists():
                self.token_file.unlink()
            if self.cookies_file.exists():
                self.cookies_file.unlink()
            self.creds = None
            return True
        except Exception as e:
            print(f"Error logging out: {e}")
            return False
    
    def get_user_email(self) -> Optional[str]:
        """Get authenticated user's email"""
        if not self.creds:
            return None
        
        try:
            # The token info is stored in the credentials
            # Try to get from stored info
            if hasattr(self.creds, 'id_token') and self.creds.id_token:
                # id_token may be a dict-like object; guard against None
                tok = self.creds.id_token
                if isinstance(tok, dict):
                    return tok.get('email')
            
            # Alternative: use Google's tokeninfo endpoint
            if getattr(self.creds, 'token', None):
                response = requests.get(
                    f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={self.creds.token}'
                )
                if response.status_code == 200:
                    data = response.json() or {}
                    if isinstance(data, dict):
                        return data.get('email')
        
        except Exception as e:
            print(f"Error getting user email: {e}")
        
        return None
    
    def delete_token(self):
        """Delete stored OAuth token"""
        if self.token_file.exists():
            self.token_file.unlink()
        self.creds = None
