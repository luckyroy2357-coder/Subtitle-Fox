@echo off
echo ========================================
echo SubtitleFox - GitHub Setup Script
echo ========================================
echo.

echo Step 1: Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo Error: Git is not installed. Please install Git first.
    pause
    exit /b 1
)

echo.
echo Step 2: Adding all files to Git...
git add .

echo.
echo Step 3: Creating initial commit...
git commit -m "Initial commit: SubtitleFox application"

echo.
echo ========================================
echo Git repository initialized successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Go to https://github.com and create a new repository
echo 2. Copy the repository URL
echo 3. Run: git remote add origin YOUR_REPO_URL
echo 4. Run: git branch -M main
echo 5. Run: git push -u origin main
echo.
echo Then deploy to Vercel:
echo 1. Go to https://vercel.com
echo 2. Import your GitHub repository
echo 3. Follow the deployment guide in VERCEL_DEPLOYMENT.md
echo.
pause

