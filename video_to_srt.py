import os
import subprocess
import tempfile
from datetime import timedelta
import speech_recognition as sr

def extract_audio_from_video(video_path, audio_path):
    """Extract audio from video file"""
    try:
        # Use ffmpeg to extract audio
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # PCM 16-bit
            '-ar', '16000',  # Sample rate 16kHz
            '-ac', '1',  # Mono
            '-y',  # Overwrite output file
            audio_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        return False
    except FileNotFoundError:
        print("FFmpeg not found. Please install FFmpeg.")
        return False

def audio_to_text_simple(audio_path, language='en-US'):
    """Convert audio to text using speech recognition"""
    recognizer = sr.Recognizer()
    
    try:
        # Load audio file
        audio_file = sr.AudioFile(audio_path)
        
        with audio_file as source:
            audio = recognizer.record(source)
        
        # Use Google Speech Recognition
        try:
            text = recognizer.recognize_google(audio, language=language)
            return text, True
        except sr.UnknownValueError:
            return "Could not understand audio", False
        except sr.RequestError as e:
            return f"Error with speech recognition service: {e}", False
            
    except Exception as e:
        return f"Error processing audio: {str(e)}", False

def create_srt_from_text(text, duration_seconds=60):
    """Create a simple SRT file from text"""
    # Split text into sentences
    sentences = text.split('. ')
    
    # Calculate time per sentence
    time_per_sentence = duration_seconds / len(sentences) if sentences else duration_seconds
    
    srt_content = []
    start_time = 0
    
    for i, sentence in enumerate(sentences, 1):
        if not sentence.strip():
            continue
            
        # Add period if missing
        if not sentence.endswith('.'):
            sentence += '.'
        
        end_time = start_time + time_per_sentence
        
        # Format times
        start_str = format_srt_time(start_time)
        end_str = format_srt_time(end_time)
        
        srt_content.append(f"{i}\n{start_str} --> {end_str}\n{sentence}\n\n")
        
        start_time = end_time
    
    return ''.join(srt_content)

def format_srt_time(seconds):
    """Format seconds to SRT time format (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def get_video_duration(video_path):
    """Get video duration in seconds"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 60  # Default 60 seconds

def video_to_srt(video_path, output_srt_path, language='en-US'):
    """
    Convert video file to SRT subtitle file
    Returns: (success: bool, message: str)
    """
    try:
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
        
        try:
            # Extract audio from video
            print("Extracting audio from video...")
            if not extract_audio_from_video(video_path, temp_audio_path):
                return False, "Failed to extract audio from video. Make sure FFmpeg is installed."
            
            # Get video duration
            duration = get_video_duration(video_path)
            print(f"Video duration: {duration} seconds")
            
            # Convert audio to text
            print("Converting audio to text...")
            text, success = audio_to_text_simple(temp_audio_path, language)
            
            if not success:
                return False, text
            
            # Create SRT file
            print("Creating SRT file...")
            srt_content = create_srt_from_text(text, duration)
            
            # Save SRT file
            with open(output_srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            
            return True, "SRT file created successfully"
            
        finally:
            # Clean up temporary audio file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                
    except Exception as e:
        return False, f"Error processing video: {str(e)}"

