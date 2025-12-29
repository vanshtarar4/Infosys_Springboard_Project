# Frontend Configuration Guide

## Environment Variables

The frontend uses environment variables to configure the API endpoint.

### Setup Instructions

Create a `.env.local` file in the `frontend/` directory with the following content:

```bash
# API Base URL
# Development
NEXT_PUBLIC_API_URL=http://localhost:8001

# Production (example)
# NEXT_PUBLIC_API_URL=https://api.yourproduction.com
```

### Available Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8001` |

### Usage

The application will automatically use the configured API URL for all backend requests. If not set, it defaults to `http://localhost:8001`.

### Production Deployment

For production deployment, set the environment variable in your hosting platform:
- **Vercel**: Add to Environment Variables in project settings
- **Netlify**: Add to Site settings > Environment variables
- **Docker**: Pass via `-e` flag or docker-compose.yml

Example:
```bash
NEXT_PUBLIC_API_URL=https://api.yourproduction.com
```
