# Casino Banner Management System

A web application for managing casino banners with an admin panel. Features a responsive carousel display and easy-to-use admin interface.

## Features

- Dynamic banner carousel with 3 slots
- Admin panel for managing banners
- Image upload functionality
- Responsive design
- Secure authentication

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access the application:
- Main website: http://localhost:5000
- Admin panel: http://localhost:5000/admin

## Admin Login Credentials
- Username: admin
- Password: 123

## Usage

### Admin Panel
1. Access the admin panel at http://localhost:5000/admin
2. Log in using the credentials above
3. Add/Edit/Delete banners:
   - Upload casino logos
   - Set header text and subtext
   - Choose display order
   - Set which banner displays first

### Banner Management
- Maximum 3 banners allowed
- One banner can be set to "Display First"
- Supported image formats: PNG, JPG, JPEG, GIF
- Maximum file size: 16MB

## Project Structure
```
ys95website/
├── static-demo/          # Static files (CSS, images)
│   ├── pictures/         # Uploaded banner images
│   ├── index.html       # Main website
│   └── style.css        # Styles
├── templates/           # Admin panel templates
│   ├── admin_login.html
│   └── admin_panel.html
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Notes
- The `casino.db` file will be created automatically on first run
- Uploaded images are stored in `static-demo/pictures/`
- Make sure to keep the admin credentials secure in production
