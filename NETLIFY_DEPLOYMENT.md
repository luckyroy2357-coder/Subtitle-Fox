# Deploying SubtitleFox to Netlify

Netlify is a great alternative to Vercel for Flask applications. This guide will help you deploy SubtitleFox to Netlify.

## Prerequisites

- GitHub account (your code is already on GitHub)
- Netlify account (sign up at https://netlify.com - free tier available)

## Step 1: Deploy to Netlify

### Option A: Via Netlify Dashboard (Recommended)

1. **Go to Netlify**: https://app.netlify.com
2. **Sign in** with your GitHub account
3. **Click "Add new site" → "Import an existing project"**
4. **Choose GitHub** and authorize Netlify
5. **Select your repository**: `luckyroy2357-coder/Subtitle-Fox`
6. **Configure build settings**:
   - **Build command**: `pip install -r requirements.txt`
   - **Publish directory**: `.` (leave empty or use `.`)
   - **Functions directory**: `netlify/functions`
7. **Environment variables** (Click "Show advanced"):
   - `SECRET_KEY` = (generate: `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `FLASK_ENV` = `production`
   - `DATABASE_URL` = `sqlite:///subtitles.db` (or your database URL)
   - `NETLIFY` = `true`
8. **Click "Deploy site"**

### Option B: Via Netlify CLI

1. **Install Netlify CLI**:
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify**:
   ```bash
   netlify login
   ```

3. **Initialize and deploy**:
   ```bash
   netlify init
   netlify deploy --prod
   ```

## Step 2: Configure Netlify Settings

### Build Settings

1. Go to **Site settings** → **Build & deploy**
2. **Build command**: `pip install -r requirements.txt`
3. **Publish directory**: `.` (or leave empty)
4. **Functions directory**: `netlify/functions`

### Environment Variables

Go to **Site settings** → **Environment variables** and add:

```
SECRET_KEY = (your generated secret key)
FLASK_ENV = production
DATABASE_URL = sqlite:///subtitles.db
NETLIFY = true
```

### Function Settings

1. Go to **Site settings** → **Functions**
2. Set **Function timeout** to 26 seconds (max for free tier) or upgrade for longer
3. For video processing, you may need Pro plan (60s timeout)

## Step 3: Set Up Database (Important!)

### Option 1: Netlify Functions + External Database (Recommended)

Since Netlify is serverless, SQLite won't work. Use:

- **Supabase** (Free PostgreSQL): https://supabase.com
- **Neon** (Free PostgreSQL): https://neon.tech
- **PlanetScale** (Free MySQL): https://planetscale.com
- **MongoDB Atlas** (Free MongoDB): https://www.mongodb.com/cloud/atlas

### Option 2: Netlify Postgres (Beta)

If available in your region:
1. Go to **Site settings** → **Functions** → **Postgres**
2. Create a new database
3. Copy connection string
4. Add as `DATABASE_URL` environment variable

## Step 4: File Storage

For file uploads, use external storage:

- **Netlify Large Media** (if available)
- **AWS S3** (recommended)
- **Cloudinary** (free tier available)
- **Supabase Storage** (if using Supabase)

## Advantages of Netlify

✅ Better Python/Flask support  
✅ More flexible serverless functions  
✅ Built-in form handling  
✅ Better file upload support  
✅ Free tier with good limits  
✅ Easy GitHub integration  
✅ Automatic HTTPS  
✅ Custom domains  

## Limitations

⚠️ **Function Timeout**: 10s (Hobby), 26s (Pro), 60s (Business)  
⚠️ **File System**: Read-only (use external storage)  
⚠️ **Database**: SQLite won't work (use external database)  
⚠️ **FFmpeg**: Not available (video processing needs external service)  

## Troubleshooting

### Build Fails
- Check build logs in Netlify dashboard
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility

### Function Timeout
- Optimize your code
- Use background functions for long tasks
- Upgrade to Pro plan for longer timeouts

### Database Errors
- Ensure `DATABASE_URL` is set correctly
- Use PostgreSQL/MySQL instead of SQLite
- Check connection string format

### Import Errors
- Ensure `serverless-wsgi` is in requirements.txt
- Check that all imports are available
- Verify Python version

## Continuous Deployment

Once connected:
- Every push to `main` branch auto-deploys
- Preview deployments for pull requests
- Deploy logs available in dashboard

## Custom Domain

1. Go to **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Follow DNS configuration instructions
4. Netlify provides free SSL certificate

## Next Steps

1. ✅ Deploy to Netlify
2. ⬜ Set up external database (PostgreSQL recommended)
3. ⬜ Configure file storage (AWS S3 or similar)
4. ⬜ Set up custom domain (optional)
5. ⬜ Configure monitoring and logging

## Support

- Netlify Docs: https://docs.netlify.com
- Netlify Functions: https://docs.netlify.com/functions/overview/
- Netlify Python: https://docs.netlify.com/functions/languages/python/

## Your Repository

GitHub: https://github.com/luckyroy2357-coder/Subtitle-Fox

