from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for
import os
import uuid
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>澳电博士照片征集</title>
    <style>
        body {
            font-family: "微软雅黑", Arial, sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            position: relative;
        }
        .bg-blur {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            background: url('/must.jpg') no-repeat center center;
            background-size: cover;
            filter: blur(10px) brightness(0.85);
        }
        .container {
            max-width: 500px;
            margin: 48px auto;
            background: rgba(255,255,255,0.93);
            border-radius: 14px;
            box-shadow: 0 4px 24px rgba(30, 136, 229, 0.13);
            padding: 38px 32px 28px 32px;
            position: relative;
            z-index: 1;
        }
        h2 {
            text-align: center;
            color: #1976d2;
            margin-bottom: 16px;
            letter-spacing: 2px;
        }
        .desc {
            color: #444;
            font-size: 17px;
            margin-bottom: 32px;
            text-align: center;
            line-height: 1.8;
            background: #e3f2fd;
            border-radius: 8px;
            padding: 14px 10px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #1976d2;
            font-weight: bold;
            font-size: 15px;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 22px;
            border: 1px solid #90caf9;
            border-radius: 5px;
            box-sizing: border-box;
            font-size: 15px;
            background: #f7fbff;
        }
        input[type="file"] {
            padding: 6px;
        }
        input[type="submit"] {
            width: 100%;
            background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
            color: #fff;
            border: none;
            padding: 14px;
            border-radius: 5px;
            font-size: 17px;
            cursor: pointer;
            font-weight: bold;
            letter-spacing: 1px;
            transition: background 0.2s, box-shadow 0.2s;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
        }
        input[type="submit"]:hover {
            background: linear-gradient(90deg, #1565c0 0%, #1976d2 100%);
        }
        .footer {
            text-align: center;
            color: #90caf9;
            font-size: 13px;
            margin-top: 18px;
        }
        .success-message {
            background: #e8f5e9;
            color: #388e3c;
            border: 1px solid #c8e6c9;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 18px;
            text-align: center;
            font-size: 15px;
        }
        .show-link {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 28px 0 0 0;
        }
        .show-link a {
            display: inline-block;
            background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
            color: #fff;
            font-weight: bold;
            text-decoration: none;
            font-size: 18px;
            padding: 14px 36px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.13);
            transition: background 0.2s, box-shadow 0.2s, transform 0.1s;
            letter-spacing: 2px;
        }
        .show-link a:hover {
            background: linear-gradient(90deg, #1565c0 0%, #1976d2 100%);
            transform: scale(1.04);
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="bg-blur"></div>
    <div class="container">
        {% if success %}
        <div class="success-message">
            上传成功！感谢您的参与！
        </div>
        <div class="show-link">
            <a href="{{ url_for('show') }}">🎉 点击这里查看所有已上传照片</a>
        </div>
        {% endif %}
        <h2>澳电博士照片征集</h2>
        <div class="desc">
            征集过往照片，记录博士生活的点点滴滴。<br>
            欢迎上传你在澳电博士期间的精彩瞬间，让我们一起珍藏这段美好回忆！
        </div>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label for="description">照片描述</label>
            <input type="text" name="description" id="description" placeholder="请输入照片描述" required>
            <label for="images">选择照片（可多选）</label>
            <input type="file" name="images" id="images" multiple accept="image/*" required>
            <input type="submit" value="上传">
        </form>
        <div class="show-link" style="margin-top:18px;">
            <a href="{{ url_for('show') }}">👀 查看所有已上传照片</a>
        </div>
        <div class="footer">
            澳电博士 · 照片征集平台
        </div>
    </div>
</body>
</html>
'''

SHOW_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>照片展示 - 澳电博士照片征集</title>
    <style>
        body {
            font-family: "微软雅黑", Arial, sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            background: #f4f8fb;
        }
        .container {
            max-width: 900px;
            margin: 40px auto;
            background: #fff;
            border-radius: 14px;
            box-shadow: 0 4px 24px rgba(30, 136, 229, 0.13);
            padding: 32px 28px 24px 28px;
        }
        h2 {
            text-align: center;
            color: #1976d2;
            margin-bottom: 24px;
            letter-spacing: 2px;
        }
        .gallery {
            display: flex;
            flex-wrap: wrap;
            gap: 24px;
            justify-content: center;
        }
        .photo-card {
            background: #e3f2fd;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
            padding: 14px 14px 10px 14px;
            width: 240px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .photo-card img {
            max-width: 210px;
            max-height: 180px;
            border-radius: 7px;
            margin-bottom: 10px;
            box-shadow: 0 1px 6px rgba(25, 118, 210, 0.10);
        }
        .desc {
            color: #333;
            font-size: 15px;
            text-align: center;
            margin-bottom: 4px;
            min-height: 32px;
            font-weight: bold;
        }
        .time {
            color: #90caf9;
            font-size: 12px;
            text-align: center;
        }
        .back-link {
            display: block;
            text-align: center;
            margin: 18px 0 0 0;
        }
        .back-link a {
            color: #1976d2;
            font-weight: bold;
            text-decoration: none;
            font-size: 16px;
        }
        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>照片展示</h2>
        <div class="gallery">
            {% for item in photos %}
            <div class="photo-card">
                <img src="{{ url_for('uploaded_file', folder=item['folder'], filename=item['filename']) }}" alt="photo">
                <div class="desc">{{ item['desc'] }}</div>
                <div class="time">{{ item['time'] }}</div>
            </div>
            {% endfor %}
        </div>
        <div class="back-link">
            <a href="{{ url_for('index') }}">返回上传页面</a>
        </div>
    </div>
</body>
</html>
'''

def create_upload_dir():
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    dir_name = f"{now}_{unique_id}"
    path = os.path.join(UPLOAD_FOLDER, dir_name)
    os.makedirs(path, exist_ok=True)
    return path, dir_name, now

@app.route('/must.jpg')
def must_img():
    return send_from_directory('.', 'must.jpg')

@app.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder), filename)

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE, success=False)

@app.route('/upload', methods=['POST'])
def upload_files():
    description = request.form.get('description', '').strip()
    files = request.files.getlist('images')
    if not description or not files or all(f.filename == '' for f in files):
        return render_template_string(HTML_PAGE, success=False)

    upload_dir, dir_name, now = create_upload_dir()
    saved_files = []

    for file in files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_dir, filename)
            try:
                file.save(filepath)
                saved_files.append(filename)
            except Exception:
                continue

    desc_path = os.path.join(upload_dir, 'description.txt')
    try:
        with open(desc_path, 'w', encoding='utf-8') as f:
            f.write(description)
    except Exception:
        pass

    return render_template_string(HTML_PAGE, success=True)

@app.route('/show')
def show():
    photos = []
    if not os.path.exists(UPLOAD_FOLDER):
        return render_template_string(SHOW_PAGE, photos=photos)
    for folder in sorted(os.listdir(UPLOAD_FOLDER), reverse=True):
        folder_path = os.path.join(UPLOAD_FOLDER, folder)
        if not os.path.isdir(folder_path):
            continue
        desc = ""
        desc_path = os.path.join(folder_path, 'description.txt')
        if os.path.exists(desc_path):
            with open(desc_path, 'r', encoding='utf-8') as f:
                desc = f.read()
        # 取所有图片文件
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
                photos.append({
                    'folder': folder,
                    'filename': filename,
                    'desc': desc,
                    'time': folder.split('_')[0] + " " + folder.split('_')[1] if '_' in folder else folder
                })
    return render_template_string(SHOW_PAGE, photos=photos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)