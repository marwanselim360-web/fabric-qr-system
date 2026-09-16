import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import qrcode

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# قاعدة بيانات مؤقتة لتخزين الأقمشة
fabrics_db = []

@app.route('/')
def index():
    return render_template('index.html', fabrics=fabrics_db)

@app.route('/add', methods=['POST'])
def add_fabric():
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    files = request.files.getlist('images')
    image_filenames = []
    
    for file in files:
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_filenames.append(filename)
    
    if not image_filenames:
        image_filenames.append('default.png')
        
    fabric_id = len(fabrics_db) + 1
    
    view_url = request.host_url + f'fabric/{fabric_id}'
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(view_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_filename = f'qr_{fabric_id}.png'
    qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_filename)
    img.save(qr_path)
    
    fabric_data = {
        'id': fabric_id,
        'name': name,
        'price': price,
        'description': description,
        'images': image_filenames,
        'qr_code': qr_filename,
        'url': view_url
    }
    fabrics_db.append(fabric_data)
    
    return redirect(url_for('index'))

@app.route('/fabric/')
def view_fabric(fabric_id):
    fabric = next((f for f in fabrics_db if f['id'] == fabric_id), None)
    if not fabric:
        return "القماش غير موجود", 404
    return render_template('view.html', fabric=fabric)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)