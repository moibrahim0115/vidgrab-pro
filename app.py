from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
from urllib.parse import urlparse
import tempfile

app = Flask(__name__)

# مجلد مؤقت للتحميلات
DOWNLOAD_FOLDER = tempfile.gettempdir()

# منصات مدعومة
SUPPORTED_PLATFORMS = {
    'youtube': ['youtube.com', 'youtu.be'],
    'facebook': ['facebook.com', 'fb.watch'],
    'twitter': ['twitter.com', 'x.com'],
    'instagram': ['instagram.com'],
    'tiktok': ['tiktok.com', 'vm.tiktok.com']
}

def get_platform(url):
    """التعرف على المنصة من الرابط"""
    domain = urlparse(url).netloc.lower()
    for platform, domains in SUPPORTED_PLATFORMS.items():
        for d in domains:
            if d in domain:
                return platform
    return 'unknown'

def format_duration(seconds):
    """تنسيق المدة"""
    if not seconds:
        return "00:00"
    
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_views(views):
    """تنسيق عدد المشاهدات"""
    if not views:
        return "0"
    
    if views >= 1000000:
        return f"{views/1000000:.1f}M"
    elif views >= 1000:
        return f"{views/1000:.1f}K"
    else:
        return str(views)

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_video_info():
    """الحصول على معلومات الفيديو"""
    data = request.json
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'success': False, 'error': 'Please enter a video URL'})
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            response_data = {
                'success': True,
                'info': {
                    'title': info.get('title', 'Unknown Video'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': format_duration(info.get('duration', 0)),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': format_views(info.get('view_count', 0)),
                    'platform': get_platform(url)
                }
            }
            
            return jsonify(response_data)
    
    except Exception as e:
        error_msg = str(e)
        if "Private video" in error_msg:
            return jsonify({'success': False, 'error': 'This video is private and cannot be downloaded'})
        elif "Video unavailable" in error_msg:
            return jsonify({'success': False, 'error': 'Video is unavailable or has been removed'})
        else:
            return jsonify({'success': False, 'error': f'Unable to process this video URL: {error_msg}'})

@app.route('/api/download', methods=['POST'])
def download_video():
    """معالجة طلب التحميل"""
    data = request.json
    url = data.get('url', '').strip()
    format_type = data.get('format', 'video')
    
    if not url:
        return jsonify({'success': False, 'error': 'Please enter a video URL'})
    
    try:
        # في PythonAnywhere، يمكننا استخدام خدمة تحميل خارجية
        # أو إعادة توجيه المستخدم لخدمة تحميل
        
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'success': True,
                'message': 'Video is ready for download',
                'filename': f"{info['title']}.{'mp3' if format_type == 'audio' else 'mp4'}",
                'title': info.get('title', 'video'),
                'direct_url': f"https://example.com/download?url={url}&format={format_type}"
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
