// Global state
let currentSection = 'home';
let searchSource = 'subtitlecat'; // Always search from Subtitle Cat website

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    showHome();
});

// Setup event listeners
function setupEventListeners() {
    // Search input enter key
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }

    // File upload change
    const fileInput = document.getElementById('upload-file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = document.getElementById('file-name');
            if (e.target.files.length > 0) {
                fileName.textContent = e.target.files[0].name;
            } else {
                fileName.textContent = '';
            }
        });
    }

    // Upload form submit
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUpload);
    }

    // Video to SRT form submit
    const videoToSrtForm = document.getElementById('video-to-srt-form');
    if (videoToSrtForm) {
        videoToSrtForm.addEventListener('submit', handleVideoToSrt);
    }

    // Video file change
    const videoInput = document.getElementById('video-upload');
    if (videoInput) {
        videoInput.addEventListener('change', function(e) {
            const fileName = document.getElementById('video-file-name');
            if (e.target.files.length > 0) {
                fileName.textContent = e.target.files[0].name;
                fileName.style.display = 'block';
            } else {
                fileName.textContent = '';
                fileName.style.display = 'none';
            }
        });
    }
}

// Navigation functions
function showHome() {
    currentSection = 'home';
    hideAllSections();
    const homeSection = document.getElementById('home-section');
    const whySection = document.getElementById('why-section');
    if (homeSection) homeSection.style.display = 'block';
    if (whySection) whySection.style.display = 'block';
    updateNav('Home');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showEnterprise() {
    currentSection = 'enterprise';
    hideAllSections();
    const enterpriseSection = document.getElementById('enterprise-section');
    if (enterpriseSection) enterpriseSection.style.display = 'block';
    updateNav('Enterprise');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showVideoToSRT() {
    currentSection = 'video-srt';
    hideAllSections();
    const videoSection = document.getElementById('video-srt-section');
    if (videoSection) videoSection.style.display = 'block';
    updateNav('Video to SRT');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showUpload() {
    currentSection = 'upload';
    hideAllSections();
    const uploadSection = document.getElementById('upload-section');
    if (uploadSection) uploadSection.style.display = 'block';
    updateNav('Upload');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showAbout() {
    currentSection = 'about';
    hideAllSections();
    const aboutSection = document.getElementById('about-section');
    if (aboutSection) aboutSection.style.display = 'block';
    updateNav('About');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showRegister() {
    currentSection = 'register';
    hideAllSections();
    const registerSection = document.getElementById('register-section');
    if (registerSection) registerSection.style.display = 'block';
    updateNav('Register');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showSignIn() {
    currentSection = 'signin';
    hideAllSections();
    const signinSection = document.getElementById('signin-section');
    if (signinSection) signinSection.style.display = 'block';
    updateNav('Sign In');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function hideAllSections() {
    // Hide all main sections
    const sections = [
        'home-section',
        'why-section',
        'enterprise-section',
        'video-srt-section',
        'upload-section',
        'about-section',
        'register-section',
        'signin-section'
    ];
    
    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        if (section) {
            section.style.display = 'none';
        }
    });
}

function updateNav(activeLink) {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.textContent.trim() === activeLink) {
            link.classList.add('active');
        }
    });
}

// Perform search
async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    const language = document.getElementById('language-filter').value;
    const resultsContainer = document.getElementById('results-container');

    if (!query) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle"></i>
                <p>Please enter a search term</p>
            </div>
        `;
        return;
    }

    // Show loading
    resultsContainer.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner"></i>
            <p>Searching SubtitleFox...</p>
        </div>
    `;

    try {
        let url = `/api/search?q=${encodeURIComponent(query)}&source=${searchSource}`;
        if (language) {
            url += `&lang=${encodeURIComponent(language)}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.error) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>${data.error}</p>
                </div>
            `;
            return;
        }

        displayResults(data.results || [], data.source || 'local');

    } catch (error) {
        console.error('Search error:', error);
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-circle"></i>
                <p>Error searching subtitles. Please try again.</p>
            </div>
        `;
    }
}

// Display search results
function displayResults(results, source = 'local') {
    const resultsContainer = document.getElementById('results-container');

    if (results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <p>No subtitles found. Try a different search term.</p>
            </div>
        `;
        return;
    }

    let html = '';
    if (source === 'subtitlecat') {
        html += `<div class="source-badge"><i class="fas fa-globe"></i> Results from Subtitle Cat website</div>`;
    }

    results.forEach(subtitle => {
        const meta = [];
        if (subtitle.language) meta.push(`<span><i class="fas fa-language"></i> ${subtitle.language}</span>`);
        if (subtitle.year) meta.push(`<span><i class="fas fa-calendar"></i> ${subtitle.year}</span>`);
        if (subtitle.season && subtitle.episode) {
            meta.push(`<span><i class="fas fa-tv"></i> S${subtitle.season.toString().padStart(2, '0')}E${subtitle.episode.toString().padStart(2, '0')}</span>`);
        }
        if (subtitle.downloads !== undefined) {
            meta.push(`<span><i class="fas fa-download"></i> ${subtitle.downloads} downloads</span>`);
        }
        if (subtitle.upload_date) {
            meta.push(`<span><i class="fas fa-clock"></i> ${formatDate(subtitle.upload_date)}</span>`);
        }
        if (subtitle.external) {
            meta.push(`<span><i class="fas fa-external-link-alt"></i> External</span>`);
        }

        const downloadButton = subtitle.external 
            ? `<button class="btn-download" onclick="downloadExternalSubtitle('${subtitle.download_url}', '${escapeHtml(subtitle.filename)}')">
                <i class="fas fa-download"></i> Download
               </button>
               <button class="btn-import" onclick="importSubtitle('${subtitle.external_url}', '${escapeHtml(subtitle.title)}', '${subtitle.language || 'English'}', ${subtitle.year || 'null'})">
                <i class="fas fa-save"></i> Import
               </button>`
            : `<button class="btn-download" onclick="downloadSubtitle(${subtitle.id})">
                <i class="fas fa-download"></i> Download
               </button>`;

        html += `
            <div class="subtitle-card ${subtitle.external ? 'external-subtitle' : ''}">
                <div class="subtitle-header">
                    <div>
                        <div class="subtitle-title">${escapeHtml(subtitle.title)}</div>
                        <div class="subtitle-meta">
                            ${meta.join('')}
                        </div>
                    </div>
                    <div class="subtitle-actions">
                        ${downloadButton}
                    </div>
                </div>
            </div>
        `;
    });

    resultsContainer.innerHTML = html;
}

// Download subtitle
async function downloadSubtitle(id) {
    try {
        const response = await fetch(`/api/download/${id}`);
        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'subtitle.srt';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        performSearch();

    } catch (error) {
        console.error('Download error:', error);
        alert('Error downloading subtitle. Please try again.');
    }
}

// Download external subtitle
async function downloadExternalSubtitle(downloadUrl, filename) {
    try {
        const response = await fetch('/api/download-external', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                download_url: downloadUrl,
                filename: filename
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error('Download error:', error);
        alert('Error downloading subtitle: ' + error.message);
    }
}

// Import subtitle from external source
async function importSubtitle(url, title, language, year) {
    if (!confirm(`Import "${title}" to your local database?`)) {
        return;
    }

    try {
        const response = await fetch('/api/import-from-subtitlecat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                title: title,
                language: language,
                year: year
            })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Subtitle imported successfully!');
            performSearch();
        } else {
            throw new Error(data.error || 'Import failed');
        }

    } catch (error) {
        console.error('Import error:', error);
        alert('Error importing subtitle: ' + error.message);
    }
}

// Handle upload
async function handleUpload(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData();
    const fileInput = document.getElementById('upload-file');
    const title = document.getElementById('upload-title').value.trim();
    const language = document.getElementById('upload-language').value.trim();
    const year = document.getElementById('upload-year').value;
    const season = document.getElementById('upload-season').value;
    const episode = document.getElementById('upload-episode').value;

    if (!fileInput.files[0]) {
        showMessage('Please select a file', 'error');
        return;
    }

    if (!title) {
        showMessage('Please enter a title', 'error');
        return;
    }

    formData.append('file', fileInput.files[0]);
    formData.append('title', title);
    formData.append('language', language || 'English');
    if (year) formData.append('year', year);
    if (season) formData.append('season', season);
    if (episode) formData.append('episode', episode);

    const messageDiv = document.getElementById('upload-message');
    messageDiv.className = 'message';
    messageDiv.textContent = 'Uploading...';
    messageDiv.style.display = 'block';

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Subtitle uploaded successfully!', 'success');
            form.reset();
            document.getElementById('file-name').textContent = '';
        } else {
            showMessage(data.error || 'Upload failed', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showMessage('Error uploading subtitle. Please try again.', 'error');
    }
}

// Show message
function showMessage(message, type) {
    const messageDiv = document.getElementById('upload-message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    if (days < 365) return `${Math.floor(days / 30)} months ago`;
    return `${Math.floor(days / 365)} years ago`;
}

// Handle Video to SRT conversion
async function handleVideoToSrt(e) {
    e.preventDefault();

    const videoInput = document.getElementById('video-upload');
    const language = document.getElementById('video-language').value;
    const statusDiv = document.getElementById('video-processing-status');
    const processBtn = document.getElementById('process-video-btn');

    if (!videoInput.files[0]) {
        showVideoStatus('Please select a video file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('video', videoInput.files[0]);
    formData.append('language', language);

    // Show processing status
    processBtn.disabled = true;
    processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    statusDiv.innerHTML = `
        <div class="processing-message">
            <i class="fas fa-cog fa-spin"></i>
            <p>Processing video... This may take a few minutes depending on video length.</p>
            <p class="processing-steps">Extracting audio → Converting to text → Generating SRT file</p>
        </div>
    `;
    statusDiv.style.display = 'block';

    try {
        const response = await fetch('/api/video-to-srt', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            // Download the SRT file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Get filename from Content-Disposition header
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'subtitle.srt';
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            showVideoStatus('SRT file generated and downloaded successfully!', 'success');
            document.getElementById('video-to-srt-form').reset();
            document.getElementById('video-file-name').textContent = '';
            document.getElementById('video-file-name').style.display = 'none';
        } else {
            const error = await response.json();
            showVideoStatus(error.error || 'Error processing video', 'error');
        }
    } catch (error) {
        console.error('Video processing error:', error);
        showVideoStatus('Error processing video. Please try again.', 'error');
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = '<i class="fas fa-magic"></i> Convert Video to SRT';
    }
}

// Show video processing status
function showVideoStatus(message, type) {
    const statusDiv = document.getElementById('video-processing-status');
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    const className = type === 'success' ? 'success' : 'error';
    
    statusDiv.innerHTML = `
        <div class="processing-message ${className}">
            <i class="fas ${icon}"></i>
            <p>${message}</p>
        </div>
    `;
    statusDiv.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
