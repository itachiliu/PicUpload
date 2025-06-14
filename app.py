from flask import Flask, request, jsonify, render_template_string, send_from_directory
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
    </style>
</head>
<body>
    <div class="bg-blur"></div>
    <div class="container">
        {% if success %}
        <div class="success-message">
            上传成功！感谢您的参与！
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
        <div class="footer">
            澳电博士 · 照片征集平台
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
    return path

@app.route('/must.jpg')
def must_img():
    # 允许直接访问 must.jpg
    return send_from_directory('.', 'must.jpg')

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE, success=False)

@app.route('/upload', methods=['POST'])
def upload_files():
    description = request.form.get('description', '').strip()
    files = request.files.getlist('images')
    if not description or not files or all(f.filename == '' for f in files):
        return render_template_string(HTML_PAGE, success=False)

    upload_dir = create_upload_dir()
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

if __name__ == '__main__':
    app.run(debug=True)