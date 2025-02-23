import sqlite3
import os

def migrate():
    try:
        # Get the database path
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'casino.db')
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('PRAGMA foreign_keys=off')
        cursor.execute('BEGIN TRANSACTION')
        
        try:
            # Create table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS top_rated_casino (
                    id INTEGER PRIMARY KEY,
                    casino_name TEXT NOT NULL,
                    logo_path TEXT NOT NULL,
                    rating FLOAT NOT NULL,
                    deposit_bonus TEXT NOT NULL,
                    free_spins TEXT,
                    features TEXT NOT NULL,
                    redirect_url TEXT NOT NULL,
                    is_exclusive BOOLEAN DEFAULT 0,
                    order_front INTEGER DEFAULT 0,
                    order_all INTEGER DEFAULT 0,
                    order_new INTEGER DEFAULT 0,
                    order_pp INTEGER DEFAULT 0
                )
            ''')
            
            # Commit transaction
            conn.commit()
            print("Migration completed successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"Error during migration: {str(e)}")
            raise
        
        finally:
            cursor.execute('PRAGMA foreign_keys=on')
            conn.close()
            
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")

if __name__ == '__main__':
    migrate()
