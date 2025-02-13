from app import app, db, Banner, User
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(username='admin', password_hash=generate_password_hash('123'))
        db.session.add(admin)
        
        # Create sample banners
        banners = [
            Banner(
                casino_name='Joker',
                logo_path='/static-demo/pictures/Jokeri-logo.png',
                bonus_amount='300% up to €1500',
                bonus_extra='150 Free Spins',
                is_focused=True,
                order=1,
                background_color='#1a1a1a'
            ),
            Banner(
                casino_name='NuBet',
                logo_path='/static-demo/pictures/Nubet-logo-1-1.png',
                bonus_amount='200% up to €1000',
                bonus_extra='100 Free Spins',
                is_focused=False,
                order=2,
                background_color='#FFD700'
            ),
            Banner(
                casino_name='LuckySpin',
                logo_path='/static-demo/pictures/Luckycircus.png',
                bonus_amount='400% up to €2000',
                bonus_extra='200 Free Spins',
                is_focused=False,
                order=3,
                background_color='#C0C0C0'
            )
        ]
        
        for banner in banners:
            db.session.add(banner)
        
        # Commit changes
        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
