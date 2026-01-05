# Environment Variables for Production Deployment

## Frontend (Netlify)

Set these in Netlify Dashboard → Site Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://fraud-detection-api.onrender.com
NODE_ENV=production
```

**IMPORTANT:** Update `fraud-detection-api.onrender.com` with your actual Render backend URL after deployment.

## Backend (Render)

Set these in Render Dashboard → Environment:

```
PYTHON_VERSION=3.11
FLASK_ENV=production
PORT=8001
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_PATH=data/transactions.db
```

**Note:** Never commit API keys to Git! Always set them in the platform dashboard.
