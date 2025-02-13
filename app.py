from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import logging
import sys

# Ensure log directory exists
log_dir = os.path.join(os.path.expanduser('~'), 'casino-banner-system', 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'app.log')

# Set up logging
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Also print to console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

logging.info("Application starting...")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///casino.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static-demo', 'pictures')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Create database tables
with app.app_context():
    db.create_all()
    # Create admin user if it doesn't exist
    User.query.delete()  # Clear existing users
    db.session.commit()
    
    # Create new admin user
    admin = User(username='admin')
    admin.password_hash = generate_password_hash('123', method='sha256')
    db.session.add(admin)
    db.session.commit()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    casino_name = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(200), nullable=False)
    bonus_amount = db.Column(db.String(100), nullable=False)
    bonus_extra = db.Column(db.String(100), nullable=False)
    is_focused = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    logging.info(f"Loading user with ID: {user_id}")
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('static-demo', 'index.html')

@app.route('/pictures/<path:filename>')
def serve_pictures(filename):
    return send_from_directory('static-demo/pictures', filename)

@app.route('/style.css')
def serve_css():
    return send_from_directory('static-demo', 'style.css')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logging.info(f"Login attempt - Username: {username}, Password: {password}")
        
        user = User.query.filter_by(username=username).first()
        logging.info(f"User found: {user is not None}")
        
        if user:
            logging.info(f"Stored password hash: {user.password_hash}")
            result = user.check_password(password)
            logging.info(f"Password check result: {result}")
            
            if result:
                login_user(user)
                logging.info("User logged in successfully!")
                return redirect(url_for('admin_panel'))
            else:
                logging.info("Password check failed")
        else:
            logging.info("User not found")
        
        flash('Invalid username or password')
    return render_template('admin_login.html')

@app.route('/admin')
@login_required
def admin_panel():
    banners = Banner.query.order_by(Banner.order).all()
    return render_template('admin_panel.html', banners=banners)

@app.route('/api/banners', methods=['GET'])
def get_banners():
    banners = Banner.query.order_by(Banner.order).all()
    return jsonify([{
        'id': b.id,
        'casino_name': b.casino_name,
        'logo_path': b.logo_path,
        'bonus_amount': b.bonus_amount,
        'bonus_extra': b.bonus_extra,
        'is_focused': b.is_focused,
        'order': b.order
    } for b in banners])

@app.route('/api/banners', methods=['POST'])
@login_required
def add_banner():
    if Banner.query.count() >= 3:
        return jsonify({'error': 'Maximum 3 banners allowed'}), 400
    
    data = request.json
    banner = Banner(
        casino_name=data['casino_name'],
        logo_path=data['logo_path'],
        bonus_amount=data['bonus_amount'],
        bonus_extra=data['bonus_extra'],
        is_focused=data['is_focused'] == 'true',
        order=data['order']
    )
    
    if banner.is_focused:
        # Set all other banners to not focused
        Banner.query.update({Banner.is_focused: False})
    
    db.session.add(banner)
    db.session.commit()
    logging.info('Banner added successfully')
    return jsonify({'message': 'Banner added successfully'})

@app.route('/api/banners/<int:id>', methods=['PUT'])
@login_required
def update_banner(id):
    banner = Banner.query.get_or_404(id)
    data = request.json
    
    # If this banner will be focused, unfocus all others first
    if data['is_focused'] == 'true' and not banner.is_focused:
        Banner.query.update({Banner.is_focused: False})
    
    banner.casino_name = data['casino_name']
    banner.logo_path = data['logo_path']
    banner.bonus_amount = data['bonus_amount']
    banner.bonus_extra = data['bonus_extra']
    banner.is_focused = data['is_focused'] == 'true'
    banner.order = data['order']
    
    db.session.commit()
    logging.info('Banner updated successfully')
    return jsonify({'message': 'Banner updated successfully'})

@app.route('/api/banners/<int:id>', methods=['DELETE'])
@login_required
def delete_banner(id):
    banner = Banner.query.get_or_404(id)
    db.session.delete(banner)
    db.session.commit()
    logging.info('Banner deleted successfully')
    return jsonify({'message': 'Banner deleted successfully'})

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logging.info('File uploaded successfully')
        return jsonify({
            'message': 'File uploaded successfully',
            'path': f'pictures/{filename}'
        })
    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
