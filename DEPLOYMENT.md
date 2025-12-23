# SubtitleFox Deployment Guide

This guide covers deploying SubtitleFox to production environments.

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- FFmpeg (for Video to SRT feature)
- PostgreSQL or MySQL (recommended for production, SQLite works for small deployments)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**
- Download from https://www.gyan.dev/ffmpeg/builds/
- Extract and add to PATH

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY` - Generate a strong random key
- `DATABASE_URL` - Your database connection string
- Other configuration as needed

### 4. Initialize Database

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

## Deployment Options

### Option 1: Gunicorn (Recommended for Linux/macOS)

1. **Install Gunicorn:**
```bash
pip install gunicorn
```

2. **Run with Gunicorn:**
```bash
gunicorn -c gunicorn_config.py wsgi:app
```

Or use the config file:
```bash
gunicorn wsgi:app
```

3. **Run as a service (systemd):**

Create `/etc/systemd/system/subtitlefox.service`:

```ini
[Unit]
Description=SubtitleFox Gunicorn Application Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/subtitlefox
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable subtitlefox
sudo systemctl start subtitlefox
```

### Option 2: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create upload directories
RUN mkdir -p uploads video_uploads

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "wsgi:app"]
```

Build and run:
```bash
docker build -t subtitlefox .
docker run -d -p 5000:5000 --name subtitlefox subtitlefox
```

### Option 3: Heroku Deployment

1. **Create `Procfile`:**
```
web: gunicorn wsgi:app
```

2. **Create `runtime.txt`:**
```
python-3.11.0
```

3. **Deploy:**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

### Option 4: PythonAnywhere

1. Upload files via Files tab
2. Open Bash console
3. Install dependencies:
```bash
pip3.10 install --user -r requirements.txt
```
4. Configure web app:
   - Source code: `/home/yourusername/subtitlefox`
   - WSGI file: `/home/yourusername/subtitlefox/wsgi.py`
5. Reload web app

### Option 5: AWS EC2 / DigitalOcean / Linode

1. **SSH into server**
2. **Install dependencies:**
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv nginx ffmpeg
```

3. **Clone and setup:**
```bash
git clone <your-repo> subtitlefox
cd subtitlefox
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configure Nginx:**

Create `/etc/nginx/sites-available/subtitlefox`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 500M;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/subtitlefox /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Run with Gunicorn:**
```bash
gunicorn -c gunicorn_config.py wsgi:app
```

## Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Set up HTTPS/SSL certificate (Let's Encrypt)
- [ ] Configure proper file storage (AWS S3, etc.)
- [ ] Set up regular database backups
- [ ] Configure logging and monitoring
- [ ] Set up firewall rules
- [ ] Configure CORS if needed
- [ ] Set up rate limiting
- [ ] Test all features thoroughly

## Environment-Specific Settings

### Development
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Production
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
gunicorn -c gunicorn_config.py wsgi:app
```

## Database Migration (if using PostgreSQL/MySQL)

If switching from SQLite to PostgreSQL/MySQL:

1. Export data from SQLite:
```bash
python -c "from app import app, db, Subtitle; import json; app.app_context().push(); print(json.dumps([s.to_dict() for s in Subtitle.query.all()]))" > backup.json
```

2. Update `DATABASE_URL` in `.env`

3. Initialize new database:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

4. Import data (if needed)

## Troubleshooting

### FFmpeg not found
- Ensure FFmpeg is installed and in PATH
- Check with: `ffmpeg -version`

### Database errors
- Check database connection string
- Ensure database exists and user has permissions
- Check database logs

### File upload issues
- Check `MAX_CONTENT_LENGTH` setting
- Ensure upload directories exist and are writable
- Check disk space

### Port already in use
- Change port in `gunicorn_config.py` or `.env`
- Or stop the process using the port

## Security Notes

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use strong SECRET_KEY** - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
3. **Enable HTTPS** - Use Let's Encrypt or similar
4. **Restrict file uploads** - Validate file types and sizes
5. **Use environment variables** - Never hardcode secrets
6. **Regular updates** - Keep dependencies updated
7. **Backup database** - Set up automated backups

## Support

For issues or questions, check the README.md or open an issue on GitHub.

