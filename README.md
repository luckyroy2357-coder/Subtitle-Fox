# SubtitleFox - Subtitle Search & Download Website

A full-featured subtitle search and download website that fetches subtitles from Subtitle Cat, built with Flask and modern web technologies.

## Features

- 🔍 **Search Subtitles**: Search for subtitles by movie/TV show title
- 🌍 **Multi-language Support**: Filter subtitles by language
- 📥 **Download Subtitles**: Download subtitle files (.srt, .vtt, .ass, .ssa, .sub)
- 📤 **Upload Subtitles**: Upload and share subtitles with the community
- 📊 **Download Statistics**: Track download counts for each subtitle
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices
- 🎨 **Modern UI**: Beautiful, user-friendly interface

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## Usage

### Searching for Subtitles

1. Enter a movie or TV show name in the search box
2. Optionally select a language filter
3. Click "Search" or press Enter
4. Browse the results and click "Download" to get the subtitle file

### Uploading Subtitles

1. Click "Upload" in the navigation menu
2. Fill in the subtitle information:
   - Title (required)
   - Language (required, defaults to English)
   - Year (optional)
   - Season & Episode (optional, for TV shows)
3. Select a subtitle file (.srt, .vtt, .ass, .ssa, or .sub)
4. Click "Upload Subtitle"

## Project Structure

```
subtitle-cat/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── style.css         # Stylesheet
│   └── script.js         # Frontend JavaScript
├── uploads/              # Uploaded subtitle files (created automatically)
└── subtitles.db          # SQLite database (created automatically)
```

## API Endpoints

- `GET /` - Main page
- `GET /api/search?q=<query>&lang=<language>` - Search subtitles
- `GET /api/subtitles` - Get all subtitles (paginated)
- `POST /api/upload` - Upload a new subtitle
- `GET /api/download/<id>` - Download a subtitle file
- `GET /api/languages` - Get list of available languages

## Database Schema

The application uses SQLite with the following schema:

- **Subtitle** table:
  - id (Primary Key)
  - title (Movie/TV show name)
  - language
  - season (optional)
  - episode (optional)
  - year (optional)
  - filename
  - filepath
  - upload_date
  - downloads (counter)
  - file_size

## Configuration

You can modify the following settings in `app.py`:

- `UPLOAD_FOLDER`: Directory for storing uploaded files
- `MAX_CONTENT_LENGTH`: Maximum file size (default: 16MB)
- `SECRET_KEY`: Flask secret key (change in production)
- Database URI: Currently using SQLite, can be changed to PostgreSQL/MySQL

## Production Deployment

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

Quick deployment steps:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Deploy with Gunicorn:**
   ```bash
   gunicorn -c gunicorn_config.py wsgi:app
   ```

4. **Or use Docker:**
   ```bash
   docker build -t subtitlefox .
   docker run -d -p 5000:5000 subtitlefox
   ```

For more deployment options (Heroku, AWS, DigitalOcean, etc.), see [DEPLOYMENT.md](DEPLOYMENT.md)

## License

This project is open source and available for educational purposes.

## Contributing

Feel free to submit issues and enhancement requests!

