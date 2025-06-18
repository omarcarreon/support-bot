# Railway Deployment Guide

## Prerequisites
1. Railway account (https://railway.app)
2. GitHub repository with your code
3. Environment variables ready

## Deployment Steps

### 1. Connect to Railway
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 2. Add PostgreSQL Database
1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will create a PostgreSQL database
4. Copy the `DATABASE_URL` from the database service

### 3. Configure Environment Variables
In your Railway project settings, add these environment variables:

```
# Database
DATABASE_URL=your_railway_postgresql_url

# Security
SECRET_KEY=your-secret-key-here

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# WhatsApp Cloud API
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_VERIFY_TOKEN=your_verify_token
WHATSAPP_APP_SECRET=your_app_secret

# Redis (optional - can use Railway Redis or external)
REDIS_URL=your_redis_url

# Optional - Twilio (if using voice calls)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

### 4. Deploy
1. Railway will automatically detect your FastAPI app
2. It will use the `Procfile` or `railway.toml` for configuration
3. The app will be deployed to `https://your-app-name.railway.app`

### 5. Update WhatsApp Webhook
1. Go to your Meta Developer Dashboard
2. Update the webhook URL to: `https://your-app-name.railway.app/api/v1/whatsapp/webhook`
3. Verify the webhook

## Troubleshooting

### Common Issues:
1. **Environment Variables**: Make sure all required variables are set
2. **Database Connection**: Check that `DATABASE_URL` is correct
3. **Port Configuration**: Railway uses `$PORT` environment variable
4. **Dependencies**: All required packages are in `requirements.txt`

### Logs:
- Check Railway logs in the dashboard
- Use `railway logs` if using Railway CLI

## Cost
- **Railway PostgreSQL**: $5/month for 1GB
- **Railway App**: Free tier available, then pay per usage
- **Total**: ~$5-10/month for small usage 