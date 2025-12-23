from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from subtitle_scraper import SubtitleCatScraper
from video_to_srt import video_to_srt

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # python-dotenv not installed, use defaults

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///subtitles.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['VIDEO_UPLOAD_FOLDER'] = os.getenv('VIDEO_UPLOAD_FOLDER', 'video_uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 500 * 1024 * 1024))  # 500MB default

# Ensure upload folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['VIDEO_UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# Database Models
class Subtitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    season = db.Column(db.Integer, nullable=True)
    episode = db.Column(db.Integer, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    filename = db.Column(db.String(200), nullable=False)
    filepath = db.Column(db.String(300), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    downloads = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'language': self.language,
            'season': self.season,
            'episode': self.episode,
            'year': self.year,
            'filename': self.filename,
            'upload_date': self.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
            'downloads': self.downloads,
            'file_size': self.file_size
        }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['GET'])
def search_subtitles():
    query = request.args.get('q', '').strip()
    language = request.args.get('lang', '').strip()
    source = request.args.get('source', 'local')  # 'local' or 'subtitlecat'
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Search from Subtitle Cat website (external source)
    if source == 'subtitlecat':
        scraper = SubtitleCatScraper()
        external_results = scraper.search(query, language)
        
        # Convert to our format
        formatted_results = []
        for result in external_results:
            formatted_results.append({
                'id': None,  # External results don't have IDs
                'title': result['title'],
                'language': result['language'],
                'season': None,
                'episode': None,
                'year': result['year'],
                'filename': f"{result['title']}.srt",
                'upload_date': None,
                'downloads': 0,
                'file_size': 0,
                'external': True,
                'external_url': result['url'],
                'download_url': result['download_url'],
                'source': 'subtitlecat.com'
            })
        
        return jsonify({
            'results': formatted_results,
            'count': len(formatted_results),
            'source': 'subtitlecat'
        })
    
    # Search local database
    search_query = Subtitle.query.filter(
        Subtitle.title.ilike(f'%{query}%')
    )
    
    if language:
        search_query = search_query.filter(Subtitle.language.ilike(f'%{language}%'))
    
    results = search_query.order_by(Subtitle.downloads.desc()).limit(50).all()
    
    return jsonify({
        'results': [subtitle.to_dict() for subtitle in results],
        'count': len(results),
        'source': 'local'
    })

@app.route('/api/subtitles', methods=['GET'])
def get_all_subtitles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Subtitle.query.order_by(Subtitle.upload_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'subtitles': [subtitle.to_dict() for subtitle in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@app.route('/api/upload', methods=['POST'])
def upload_subtitle():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    title = request.form.get('title', '').strip()
    language = request.form.get('language', 'English').strip()
    season = request.form.get('season', type=int) or None
    episode = request.form.get('episode', type=int) or None
    year = request.form.get('year', type=int) or None
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    # Validate file extension
    allowed_extensions = {'.srt', '.vtt', '.ass', '.ssa', '.sub'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Only .srt, .vtt, .ass, .ssa, .sub files are allowed'}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    file_size = os.path.getsize(filepath)
    
    # Create database entry
    subtitle = Subtitle(
        title=title,
        language=language,
        season=season,
        episode=episode,
        year=year,
        filename=filename,
        filepath=filepath,
        file_size=file_size
    )
    
    db.session.add(subtitle)
    db.session.commit()
    
    return jsonify({
        'message': 'Subtitle uploaded successfully',
        'subtitle': subtitle.to_dict()
    }), 201

@app.route('/api/download/<int:subtitle_id>', methods=['GET'])
def download_subtitle(subtitle_id):
    subtitle = Subtitle.query.get_or_404(subtitle_id)
    
    # Update download count
    subtitle.downloads += 1
    db.session.commit()
    
    return send_file(
        subtitle.filepath,
        as_attachment=True,
        download_name=subtitle.filename
    )

@app.route('/api/languages', methods=['GET'])
def get_languages():
    languages = db.session.query(Subtitle.language).distinct().all()
    return jsonify({
        'languages': [lang[0] for lang in languages]
    })

@app.route('/api/import-from-subtitlecat', methods=['POST'])
def import_from_subtitlecat():
    """Import a subtitle from Subtitle Cat website and save it locally"""
    data = request.get_json()
    subtitle_url = data.get('url', '').strip()
    title = data.get('title', '').strip()
    language = data.get('language', 'English').strip()
    year = data.get('year')
    
    if not subtitle_url:
        return jsonify({'error': 'Subtitle URL is required'}), 400
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        scraper = SubtitleCatScraper()
        
        # Generate filename
        safe_title = secure_filename(title)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_title}.srt"
        unique_filename = f"{timestamp}_{safe_title}.srt"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Download the subtitle
        success = scraper.download_subtitle(subtitle_url, filepath)
        
        if not success or not os.path.exists(filepath):
            return jsonify({'error': 'Failed to download subtitle file'}), 400
        
        file_size = os.path.getsize(filepath)
        
        # Create database entry
        subtitle = Subtitle(
            title=title,
            language=language,
            year=year,
            filename=filename,
            filepath=filepath,
            file_size=file_size
        )
        
        db.session.add(subtitle)
        db.session.commit()
        
        return jsonify({
            'message': 'Subtitle imported successfully',
            'subtitle': subtitle.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error importing subtitle: {str(e)}'}), 500

@app.route('/api/download-external', methods=['POST'])
def download_external_subtitle():
    """Download a subtitle directly from external source"""
    data = request.get_json()
    download_url = data.get('download_url', '').strip()
    filename = data.get('filename', 'subtitle.srt').strip()
    
    if not download_url:
        return jsonify({'error': 'Download URL is required'}), 400
    
    try:
        scraper = SubtitleCatScraper()
        
        # Create temp file path
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"{timestamp}_{secure_filename(filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
        # Download the subtitle
        success = scraper.download_subtitle(download_url, filepath)
        
        if not success or not os.path.exists(filepath):
            return jsonify({'error': 'Failed to download subtitle file'}), 400
        
        # Send file to user
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Error downloading subtitle: {str(e)}'}), 500

@app.route('/api/video-to-srt', methods=['POST'])
def convert_video_to_srt():
    """Convert uploaded video file to SRT subtitle file"""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    language = request.form.get('language', 'en-US').strip()
    
    if video_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file extension
    allowed_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
    file_ext = os.path.splitext(video_file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'error': 'Invalid video file type. Supported: .mp4, .avi, .mov, .mkv, .wmv, .flv, .webm, .m4v'}), 400
    
    try:
        # Save video file
        filename = secure_filename(video_file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"{timestamp}_{filename}"
        video_path = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], video_filename)
        video_file.save(video_path)
        
        # Generate SRT filename
        srt_filename = os.path.splitext(video_filename)[0] + '.srt'
        srt_path = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], srt_filename)
        
        # Convert video to SRT
        success, message = video_to_srt(video_path, srt_path, language)
        
        if not success:
            # Clean up video file on error
            if os.path.exists(video_path):
                os.remove(video_path)
            return jsonify({'error': message}), 500
        
        # Return SRT file for download
        return send_file(
            srt_path,
            as_attachment=True,
            download_name=srt_filename
        )
        
    except Exception as e:
        return jsonify({'error': f'Error processing video: {str(e)}'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

