from flask import Flask, request, send_file, render_template, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'uploads'
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'video')
WATERMARK_FOLDER = os.path.join(UPLOAD_FOLDER, 'watermark')
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(WATERMARK_FOLDER, exist_ok=True)

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files or 'watermark' not in request.files:
        return jsonify({'error': 'No video or watermark file uploaded'}), 400
    
    video = request.files['video']
    watermark = request.files['watermark']

    if video.filename == '' or watermark.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(video.filename, ALLOWED_VIDEO_EXTENSIONS):
        return jsonify({'error': 'Invalid video file type'}), 400

    if not allowed_file(watermark.filename, ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'error': 'Invalid watermark file type'}), 400

    video_filename = secure_filename(video.filename)
    watermark_filename = secure_filename(watermark.filename)

    video_path = os.path.join(VIDEO_FOLDER, video_filename)
    watermark_path = os.path.join(WATERMARK_FOLDER, watermark_filename)

    video.save(video_path)
    watermark.save(watermark_path)

    output_file = os.path.join(UPLOAD_FOLDER, 'output.mp4')

    # Run FFmpeg command to overlay watermark
    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-i', watermark_path,
        '-filter_complex', 'overlay=10:10',  # Adjust position as needed
        output_file
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Error processing video: ' + str(e)}), 500

    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
