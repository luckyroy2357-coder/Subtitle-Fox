import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, quote
import time
import os

class SubtitleCatScraper:
    BASE_URL = "https://www.subtitlecat.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search(self, query, language=None):
        """Search for subtitles on Subtitle Cat"""
        try:
            # Search URL - Subtitle Cat uses this format
            search_url = f"{self.BASE_URL}/index.php?search={quote(query)}"
            if language:
                search_url += f"&lang={quote(language)}"
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Try multiple selector patterns for Subtitle Cat
            # Pattern 1: Table rows (common in subtitle sites)
            subtitle_rows = soup.find_all('tr')
            
            # Pattern 2: Divs with subtitle classes
            if not subtitle_rows:
                subtitle_rows = soup.find_all('div', class_=re.compile(r'subtitle|result|item|row', re.I))
            
            # Pattern 3: List items
            if not subtitle_rows:
                subtitle_rows = soup.find_all('li', class_=re.compile(r'subtitle|result|item', re.I))
            
            for row in subtitle_rows[:30]:  # Limit to 30 results
                try:
                    # Find title link - multiple patterns
                    title_link = None
                    
                    # Try finding link with subtitle pattern
                    title_link = row.find('a', href=re.compile(r'subtitle|index\.php|download', re.I))
                    
                    # If not found, try any link
                    if not title_link:
                        title_link = row.find('a', href=True)
                    
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    if not title or len(title) < 3:
                        continue
                    
                    subtitle_url = urljoin(self.BASE_URL, title_link.get('href', ''))
                    
                    # Extract language from row text or title
                    row_text = row.get_text()
                    language_name = 'English'  # Default
                    lang_patterns = [
                        r'\b(English|Spanish|French|German|Italian|Portuguese|Russian|Chinese|Japanese|Korean|Arabic|Hindi|Turkish|Polish|Dutch|Swedish|Norwegian|Danish|Finnish|Greek|Hebrew|Thai|Vietnamese|Indonesian|Malay)\b',
                        re.I
                    ]
                    lang_match = re.search(lang_patterns[0], row_text, lang_patterns[1])
                    if lang_match:
                        language_name = lang_match.group(1)
                    
                    # Extract year
                    year_match = re.search(r'\b(19|20)\d{2}\b', title + ' ' + row_text)
                    year = int(year_match.group()) if year_match else None
                    
                    # Find download link
                    download_link = row.find('a', href=re.compile(r'download|\.srt|\.vtt|\.zip|\.rar', re.I))
                    if not download_link:
                        download_link = title_link
                    
                    download_url = urljoin(self.BASE_URL, download_link.get('href', '')) if download_link else subtitle_url
                    
                    # Avoid duplicates
                    if any(r['url'] == subtitle_url for r in results):
                        continue
                    
                    results.append({
                        'title': title,
                        'language': language_name,
                        'year': year,
                        'url': subtitle_url,
                        'download_url': download_url,
                        'source': 'subtitlecat.com'
                    })
                except Exception as e:
                    continue
            
            # Fallback: Find all subtitle-related links
            if not results:
                all_links = soup.find_all('a', href=re.compile(r'subtitle|download|\.srt|index\.php.*search', re.I))
                seen_urls = set()
                
                for link in all_links[:30]:
                    try:
                        title = link.get_text(strip=True)
                        href = link.get('href', '')
                        
                        if not title or len(title) < 3 or href in seen_urls:
                            continue
                        
                        subtitle_url = urljoin(self.BASE_URL, href)
                        seen_urls.add(subtitle_url)
                        
                        # Extract year
                        year_match = re.search(r'\b(19|20)\d{2}\b', title)
                        year = int(year_match.group()) if year_match else None
                        
                        results.append({
                            'title': title,
                            'language': 'English',
                            'year': year,
                            'url': subtitle_url,
                            'download_url': subtitle_url,
                            'source': 'subtitlecat.com'
                        })
                    except:
                        continue
            
            return results[:20]  # Return max 20 results
            
        except requests.RequestException as e:
            print(f"Error searching Subtitle Cat: {e}")
            return []
        except Exception as e:
            print(f"Error parsing results: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def download_subtitle(self, subtitle_url, save_path):
        """Download a subtitle file from Subtitle Cat"""
        try:
            # If URL already points to a file, download directly
            if re.search(r'\.(srt|vtt|ass|ssa|sub|zip|rar)$', subtitle_url, re.I):
                file_response = self.session.get(subtitle_url, timeout=30, stream=True)
                file_response.raise_for_status()
                
                with open(save_path, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                return os.path.getsize(save_path) > 100
            
            # Otherwise, get the subtitle page first
            response = self.session.get(subtitle_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple methods to find download link
            download_url = None
            
            # Method 1: Direct download link
            download_link = soup.find('a', href=re.compile(r'\.srt|\.vtt|\.ass|\.ssa|\.sub|download', re.I))
            if download_link:
                download_url = urljoin(self.BASE_URL, download_link.get('href', ''))
            
            # Method 2: Iframe source
            if not download_url:
                iframe = soup.find('iframe', src=re.compile(r'subtitle|download|\.srt', re.I))
                if iframe:
                    download_url = urljoin(self.BASE_URL, iframe.get('src', ''))
            
            # Method 3: Form action
            if not download_url:
                form = soup.find('form', action=re.compile(r'download|\.srt', re.I))
                if form:
                    download_url = urljoin(self.BASE_URL, form.get('action', ''))
            
            # Method 4: Use the page URL itself (might be direct)
            if not download_url:
                download_url = subtitle_url
            
            # Download the file
            file_response = self.session.get(download_url, timeout=30, stream=True, allow_redirects=True)
            file_response.raise_for_status()
            
            # Save the file
            with open(save_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file size
            if os.path.getsize(save_path) < 50:
                os.remove(save_path)
                return False
            
            # Try to verify it's a subtitle file (optional check)
            try:
                with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)
                    # Check for common subtitle patterns
                    if re.search(r'\d{2}:\d{2}:\d{2}|\d+\s*\n\d{2}:\d{2}|WEBVTT|Dialogue:', content, re.I):
                        return True
                    # If no pattern found but file exists and has content, assume it's valid
                    if len(content.strip()) > 50:
                        return True
            except:
                # If can't read as text, might be zip/rar
                if save_path.endswith(('.zip', '.rar')):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error downloading subtitle: {e}")
            import traceback
            traceback.print_exc()
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except:
                    pass
            return False

