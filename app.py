from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import logging
import sys
from datetime import datetime

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

app = Flask(__name__, static_folder='static-demo', static_url_path='/static-demo')
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Use absolute path for database on PythonAnywhere
if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    db_path = os.path.join(os.path.expanduser('~'), 'casino-banner-system', 'casino.db')
else:
    db_path = 'casino.db'  # Local development

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static-demo', 'pictures')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

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
    background_color = db.Column(db.String(500), nullable=False, default='#1a1a1a')  # Increased max length to 500
    redirect_url = db.Column(db.String(500), nullable=False, default='#')

class TopRatedCasino(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    casino_name = db.Column(db.String(100), nullable=False)
    logo_path = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # Changed to Float for decimal ratings
    deposit_bonus = db.Column(db.String(100), nullable=False)
    free_spins = db.Column(db.String(100))  # Made nullable
    features = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    redirect_url = db.Column(db.String(500), nullable=False)
    is_exclusive = db.Column(db.Boolean, default=False)

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

@login_manager.user_loader
def load_user(user_id):
    logging.info(f"Loading user with ID: {user_id}")
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('static-demo', 'index.html')

@app.route('/giveaway')
def giveaway():
    logging.info("Serving giveaway.html from static-demo")
    return send_from_directory('static-demo', 'giveaway.html')

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
        
        # Write debug info to a file
        with open('debug_log.txt', 'a') as f:
            f.write(f"\nLogin attempt at {datetime.now()}\n")
            f.write(f"Username: {username}\n")
            f.write(f"Password: {password}\n")
        
        user = User.query.filter_by(username=username).first()
        
        if user:
            with open('debug_log.txt', 'a') as f:
                f.write(f"User found in database\n")
                f.write(f"Stored hash: {user.password_hash}\n")
            
            is_valid = user.check_password(password)
            
            with open('debug_log.txt', 'a') as f:
                f.write(f"Password check result: {is_valid}\n")
            
            if is_valid:
                login_user(user)
                with open('debug_log.txt', 'a') as f:
                    f.write("Login successful!\n")
                return redirect(url_for('admin_panel'))
        else:
            with open('debug_log.txt', 'a') as f:
                f.write("User not found in database\n")
        
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
        'order': b.order,
        'background_color': b.background_color,
        'redirect_url': b.redirect_url
    } for b in banners])

@app.route('/api/banners', methods=['POST'])
@login_required
def add_banner():
    try:
        if Banner.query.count() >= 3:
            return jsonify({'error': 'Maximum 3 banners allowed'}), 400

        data = request.json
        logging.info(f"Received banner data: {data}")

        # Validate required fields
        required_fields = ['casino_name', 'logo_path', 'bonus_amount', 'bonus_extra', 'redirect_url', 'background_color']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Determine order based on color
        color = data['background_color']
        if '#C0C0C0' in color:  # Silver
            order = 1
        elif '#FFD700' in color:  # Gold
            order = 2
        else:  # Bronze
            order = 3

        # Create new banner
        banner = Banner(
            casino_name=data['casino_name'],
            logo_path=data['logo_path'],
            bonus_amount=data['bonus_amount'],
            bonus_extra=data['bonus_extra'],
            redirect_url=data['redirect_url'],
            background_color=data['background_color'],
            order=order  # Set order based on color
        )

        db.session.add(banner)
        db.session.commit()
        logging.info(f"Banner added successfully: {banner.casino_name}")
        return jsonify({'message': 'Banner added successfully'})

    except Exception as e:
        logging.error(f"Error adding banner: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/banners/<int:id>', methods=['PUT'])
@login_required
def update_banner(id):
    banner = Banner.query.get_or_404(id)
    data = request.json
    
    if data['is_focused'] == 'true' and not banner.is_focused:
        Banner.query.update({Banner.is_focused: False})
    
    banner.casino_name = data['casino_name']
    banner.logo_path = data['logo_path']
    banner.bonus_amount = data['bonus_amount']
    banner.bonus_extra = data['bonus_extra']
    banner.is_focused = data['is_focused'] == 'true'
    banner.order = data['order']
    banner.background_color = data.get('background_color', '#1a1a1a')
    banner.redirect_url = data.get('redirect_url', '#')
    
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

@app.route('/api/top-rated-casinos', methods=['GET'])
def get_top_rated_casinos():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
        
    try:
        casinos = TopRatedCasino.query.order_by(TopRatedCasino.order).all()
        return jsonify([{
            'id': c.id,
            'casino_name': c.casino_name,
            'logo_path': c.logo_path,
            'deposit_bonus': c.deposit_bonus,
            'free_spins': c.free_spins,
            'redirect_url': c.redirect_url,
            'rating': c.rating,
            'features': c.features,
            'is_exclusive': c.is_exclusive,
            'order': c.order
        } for c in casinos])
    except Exception as e:
        logging.error(f"Error getting casinos: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/top-rated-casinos', methods=['POST'])
@login_required
def add_top_rated_casino():
    try:
        # Check if file was uploaded
        if 'logo' not in request.files:
            return jsonify({'error': 'No logo file provided'}), 400
            
        logo = request.files['logo']
        if not logo.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        # Validate file type
        if not allowed_file(logo.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        # Save the logo file
        filename = secure_filename(logo.filename)
        logo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Get form data with defaults
        casino_name = request.form.get('casino_name')
        deposit_bonus = request.form.get('deposit_bonus')
        free_spins = request.form.get('free_spins')
        redirect_url = request.form.get('redirect_url')
        rating = request.form.get('rating')
        features = request.form.get('features', '')
        is_exclusive = request.form.get('is_exclusive') == 'true'

        # Validate required fields
        if not all([casino_name, deposit_bonus, free_spins, redirect_url, rating]):
            return jsonify({'error': 'All fields are required'}), 400

        try:
            rating = float(rating)
            if not (0.5 <= rating <= 5.0):
                return jsonify({'error': 'Rating must be between 0.5 and 5.0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid rating value'}), 400

        # Get highest order
        highest_order = db.session.query(db.func.max(TopRatedCasino.order)).scalar() or 0

        # Create new casino
        casino = TopRatedCasino(
            casino_name=casino_name,
            logo_path=filename,  # Store just the filename
            deposit_bonus=deposit_bonus,
            free_spins=free_spins,
            redirect_url=redirect_url,
            rating=rating,
            features=features,
            is_exclusive=is_exclusive,
            order=highest_order + 1
        )

        db.session.add(casino)
        db.session.commit()

        return jsonify({
            'message': 'Casino added successfully',
            'casino': {
                'id': casino.id,
                'casino_name': casino.casino_name,
                'logo_path': casino.logo_path,
                'deposit_bonus': casino.deposit_bonus,
                'free_spins': casino.free_spins,
                'redirect_url': casino.redirect_url,
                'rating': casino.rating,
                'features': casino.features,
                'is_exclusive': casino.is_exclusive,
                'order': casino.order
            }
        })

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding casino: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/top-rated-casinos/<int:id>', methods=['PUT'])
@login_required
def update_top_rated_casino(id):
    try:
        casino = TopRatedCasino.query.get_or_404(id)
        data = request.json
        casino.casino_name = data['casino_name']
        casino.logo_path = data['logo_path']
        try:
            rating = float(data['rating'])
            # Validate rating range
            if not (0.5 <= rating <= 5.0):
                return jsonify({'error': 'Rating must be between 0.5 and 5.0'}), 400
            # Round to nearest 0.5
            rating = round(rating * 2) / 2
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid rating value'}), 400
        casino.rating = rating
        casino.deposit_bonus = data['deposit_bonus']
        casino.free_spins = data.get('free_spins', '')
        casino.features = ','.join(data['features'])
        casino.is_exclusive = data.get('is_exclusive', False)
        casino.redirect_url = data.get('redirect_url', '#')
        db.session.commit()
        return jsonify({'message': 'Casino updated successfully'})
    except Exception as e:
        logging.error(f"Error updating top rated casino: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/top-rated-casinos/<int:id>', methods=['DELETE'])
@login_required
def delete_top_rated_casino(id):
    try:
        casino = TopRatedCasino.query.get_or_404(id)
        db.session.delete(casino)
        db.session.commit()
        return jsonify({'message': 'Casino deleted successfully'})
    except Exception as e:
        logging.error(f"Error deleting top rated casino: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/top-rated-casinos/reorder', methods=['POST'])
@login_required
def reorder_casinos():
    try:
        data = request.json
        logging.info(f"Reordering casinos with data: {data}")
        
        dragged_id = data['draggedId']
        drop_id = data['dropId']
        dragged_order = data['draggedOrder']
        drop_order = data['dropOrder']
        
        # Get all casinos
        casinos = TopRatedCasino.query.all()
        
        # Update orders
        if dragged_order < drop_order:
            # Moving down - update orders between dragged and drop positions
            for casino in casinos:
                if casino.id == dragged_id:
                    casino.order = drop_order
                elif dragged_order < casino.order <= drop_order:
                    casino.order -= 1
        else:
            # Moving up - update orders between drop and dragged positions
            for casino in casinos:
                if casino.id == dragged_id:
                    casino.order = drop_order
                elif drop_order <= casino.order < dragged_order:
                    casino.order += 1
        
        db.session.commit()
        logging.info("Casino order updated successfully")
        return jsonify({'message': 'Order updated successfully'})
        
    except Exception as e:
        logging.error(f"Error reordering casinos: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

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
        logging.info(f'File uploaded successfully to {file_path}')
        return jsonify({
            'message': 'File uploaded successfully',
            'path': f'pictures/{filename}'  # This path is relative to static-demo
        })
    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
