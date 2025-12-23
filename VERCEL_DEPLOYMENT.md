# Deploying SubtitleFox to Vercel

This guide will help you deploy SubtitleFox to Vercel via GitHub.

## Prerequisites

- GitHub account
- Vercel account (sign up at https://vercel.com)
- Git installed on your computer

## Step 1: Initialize Git Repository

1. **Open terminal in your project directory**

2. **Initialize Git repository:**
   ```bash
   git init
   ```

3. **Add all files:**
   ```bash
   git add .
   ```

4. **Create initial commit:**
   ```bash
   git commit -m "Initial commit: SubtitleFox application"
   ```

## Step 2: Create GitHub Repository

1. **Go to GitHub** (https://github.com)
2. **Click "New repository"**
3. **Repository name:** `subtitlefox` (or your preferred name)
4. **Description:** "Subtitle search and translation platform"
5. **Choose Public or Private**
6. **DO NOT initialize with README** (we already have files)
7. **Click "Create repository"**

## Step 3: Connect Local Repository to GitHub

1. **Copy the repository URL** from GitHub (e.g., `https://github.com/yourusername/subtitlefox.git`)

2. **Add remote origin:**
   ```bash
   git remote add origin https://github.com/yourusername/subtitlefox.git
   ```

3. **Push to GitHub:**
   ```bash
   git branch -M main
   git push -u origin main
   ```

## Step 4: Deploy to Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. **Go to Vercel** (https://vercel.com)
2. **Sign in** with GitHub
3. **Click "Add New Project"**
4. **Import your GitHub repository:**
   - Select `subtitlefox` repository
   - Click "Import"
5. **Configure Project:**
   - **Framework Preset:** Other
   - **Root Directory:** `./`
   - **Build Command:** Leave empty (Vercel will auto-detect)
   - **Output Directory:** Leave empty
   - **Install Command:** `pip install -r requirements.txt`
6. **Environment Variables:**
   - Click "Environment Variables"
   - Add the following:
     - `SECRET_KEY` = (generate a random key)
     - `FLASK_ENV` = `production`
     - `DATABASE_URL` = `sqlite:///subtitles.db` (or your database URL)
7. **Click "Deploy"**

### Option B: Via Vercel CLI

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Follow the prompts:**
   - Link to existing project? No
   - Project name: subtitlefox
   - Directory: ./
   - Override settings? No

5. **Set environment variables:**
   ```bash
   vercel env add SECRET_KEY
   vercel env add FLASK_ENV production
   ```

## Step 5: Configure Vercel Settings

### Important Settings:

1. **Function Timeout:**
   - Go to Project Settings → Functions
   - Set Max Duration to 300 seconds (for video processing)

2. **Environment Variables:**
   - Go to Project Settings → Environment Variables
   - Add all required variables from `.env.example`

3. **Build Settings:**
   - Framework: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

## Step 6: Update Vercel Configuration (if needed)

If you encounter issues, you may need to update `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

## Important Notes for Vercel

### Limitations:

1. **File Storage:**
   - Vercel is serverless, so local file storage is ephemeral
   - Consider using:
     - AWS S3 for file storage
     - Vercel Blob Storage (if available)
     - External storage service

2. **Database:**
   - SQLite won't persist on Vercel
   - Use external database:
     - PostgreSQL (Vercel Postgres, Supabase, Neon)
     - MySQL (PlanetScale, Railway)
     - MongoDB Atlas

3. **FFmpeg:**
   - FFmpeg may not be available in Vercel's serverless environment
   - Video to SRT feature may need alternative implementation
   - Consider using external API services for video processing

### Recommended Setup:

1. **Use Vercel Postgres:**
   ```bash
   vercel postgres create
   ```

2. **Update DATABASE_URL:**
   - Get connection string from Vercel dashboard
   - Add to environment variables

3. **Use External Storage:**
   - Set up AWS S3 or similar
   - Update upload handlers to use external storage

## Troubleshooting

### Build Fails:
- Check `requirements.txt` for compatibility
- Ensure all dependencies are listed
- Check Vercel build logs

### Function Timeout:
- Increase timeout in Vercel settings
- Optimize video processing (use external service)

### Database Errors:
- Ensure DATABASE_URL is set correctly
- Check database connection from Vercel functions
- Use connection pooling for PostgreSQL

### File Upload Issues:
- Implement external storage (S3, etc.)
- Check file size limits
- Verify CORS settings

## Continuous Deployment

Once connected:
- Every push to `main` branch auto-deploys
- Preview deployments for pull requests
- Check deployment status in Vercel dashboard

## Next Steps

1. Set up external database (PostgreSQL recommended)
2. Configure file storage (AWS S3 or similar)
3. Set up custom domain (optional)
4. Configure monitoring and logging
5. Set up backups

## Support

- Vercel Docs: https://vercel.com/docs
- Vercel Python: https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python
- GitHub Integration: https://vercel.com/docs/concepts/git

