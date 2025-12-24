import os
import sys
from sqlalchemy import text

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app.database import SessionLocal, engine
from app import models

def reset_users():
    print("🗑️  Cleaning 'user_books' and 'users' tables in Analysis Server...")
    
    # Create a new session
    db = SessionLocal()
    try:
        # Check if tables exist
        # Using execute with text for raw SQL is often simpler for bulk delete if we don't care about object lifecycle events (which we usually don't for reset)
        # But let's use standard sqlalchemy delete or truncate
        
        # SQLite doesn't support TRUNCATE, so we use DELETE
        # Order matters due to foreign keys: user_books -> users
        
        db.execute(text("DELETE FROM user_books"))
        db.execute(text("DELETE FROM users"))
        db.commit()
        
        print("✅  Successfully cleared user data.")
    except Exception as e:
        print(f"❌  Failed to user data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if "-y" in sys.argv:
        confirm = 'y'
    else:
        confirm = input("⚠️  Are you sure you want to clear ALL USER DATA (Analysis Server)? (y/n): ")
    
    if confirm.lower() == 'y':
        reset_users()
    else:
        print("❌  Cancelled.")
