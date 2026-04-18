# OAuth2 Setup Guide

## Overview
This guide explains how to set up OAuth2 credentials for Google, GitHub, and Microsoft authentication in the AI Legal Assistant application.

## Prerequisites
- Google Cloud Platform account
- GitHub account
- Microsoft Azure account
- Domain name (for production deployment)

## 1. Google OAuth2 Setup

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "Google+ API" and "People API" in APIs & Services

### Step 2: Create OAuth2 Credentials
1. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
2. Select "Web application"
3. Fill in the form:
   - **Name**: AI Legal Assistant
   - **Authorized JavaScript origins**: `http://localhost:8501`
   - **Authorized redirect URIs**: `http://localhost:8501/oauth2/callback`
4. Save and copy the **Client ID** and **Client Secret**

### Step 3: Update Configuration
Replace the placeholder values in `app.py`:
```python
GOOGLE_CLIENT_ID = "your_actual_google_client_id"
GOOGLE_CLIENT_SECRET = "your_actual_google_client_secret"
```

## 2. GitHub OAuth2 Setup

### Step 1: Create GitHub OAuth App
1. Go to [GitHub Settings](https://github.com/settings/developers)
2. Click "OAuth Apps" → "New OAuth App"
3. Fill in the form:
   - **Application name**: AI Legal Assistant
   - **Homepage URL**: `http://localhost:8501`
   - **Authorization callback URL**: `http://localhost:8501/oauth2/callback`
   - **Enable Device Flow**: Unchecked

### Step 2: Update Configuration
Replace the placeholder values in `app.py`:
```python
GITHUB_CLIENT_ID = "your_actual_github_client_id"
GITHUB_CLIENT_SECRET = "your_actual_github_client_secret"
```

## 3. Microsoft OAuth2 Setup

### Step 1: Create Azure AD Application
1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Fill in the form:
   - **Name**: AI Legal Assistant
   - **Supported account types**: "Accounts in any organizational directory"
   - **Redirect URI**: `http://localhost:8501/oauth2/callback`
   - **Allow public client flows**: Yes

### Step 2: Configure API Permissions
1. Go to "API permissions" → "Add a permission"
2. Add these permissions:
   - **User.Read**: Read user profile
   - **email**: Read user email
   - **openid**: Sign in with OpenID Connect

### Step 3: Update Configuration
Replace the placeholder values in `app.py`:
```python
MICROSOFT_CLIENT_ID = "your_actual_microsoft_client_id"
MICROSOFT_CLIENT_SECRET = "your_actual_microsoft_client_secret"
```

## 4. Production Deployment

### Domain Configuration
For production deployment, replace `localhost:8501` with your actual domain:
```python
# Update redirect URIs in OAuth2Provider.get_config()
"redirect_uri": "https://yourdomain.com/oauth2/callback"
```

### Environment Variables (Recommended)
For better security, use environment variables instead of hardcoding:
```python
import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your_google_client_secret")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "your_github_client_id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "your_github_client_secret")
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "your_microsoft_client_id")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "your_microsoft_client_secret")
```

## 5. Testing

### Local Testing
1. Update the configuration with your actual credentials
2. Run the application: `streamlit run app.py`
3. Visit `http://localhost:8501`
4. Click the OAuth2 login buttons to test authentication

### Troubleshooting

### Common Issues
- **invalid_client**: Check client ID and secret are correct
- **redirect_uri_mismatch**: Ensure redirect URI matches exactly
- **access_denied**: User denied authorization or missing permissions

### Security Notes
- Never commit client secrets to version control
- Use HTTPS in production
- Implement proper state validation for CSRF protection
- Regularly rotate client secrets

## 6. Configuration File

You can also create a `.env` file for local development:
```bash
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
```

Then load it in your app:
```python
from dotenv import load_dotenv
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# ... other variables
```
