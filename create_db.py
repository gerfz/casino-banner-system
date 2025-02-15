from app import app, db, Banner, User, TopRatedCasino
from werkzeug.security import generate_password_hash
import logging

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
                bonus_extra='+150 Free Spins',
                is_focused=False,
                order=1,
                background_color='#1a1a1a'
            ),
            # Add more sample banners as needed
        ]
        
        for banner in banners:
            db.session.add(banner)

        # Add initial casinos if the table is empty
        if not TopRatedCasino.query.first():
            casinos = [
                TopRatedCasino(
                    casino_name='Spinz Casino',
                    logo_path='/static-demo/pictures/Luckycircus.png',
                    rating=5.0,
                    deposit_bonus='200% up to €500',
                    free_spins='+ 100 Free Spins',
                    features='Fast withdrawals (Pay n Play),Big welcome bonuses,User-friendly Game lobby',
                    order=1,
                    redirect_url='https://example.com/spinz',
                    is_exclusive=True
                ),
                TopRatedCasino(
                    casino_name='Vice Casino',
                    logo_path='/static-demo/pictures/Jokeri-logo.png',
                    rating=4,
                    deposit_bonus='100% up to €300',
                    free_spins='+ 150 Free Spins',
                    features='Big welcome bonus,Alot of providers,Fast withdraws',
                    order=2,
                    redirect_url='https://example.com/vice',  # Added redirect URL
                    is_exclusive=False
                )
            ]
            
            for casino in casinos:
                db.session.add(casino)

        try:
            db.session.commit()
            logging.info("Database initialized successfully")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error initializing database: {str(e)}")
            raise

if __name__ == '__main__':
    init_db()
