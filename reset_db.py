import os
import shutil
import sys

# Add the current directory to sys.path to make sure we can import app modules
sys.path.append(os.getcwd())

from app.database import engine, Base
from app import models  # Import models to ensure they are registered with Base

def reset_database():
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅  All tables dropped.")

    print("🛠️  Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅  All tables created.")

def clear_storage():
    storage_dir = "storage"
    if os.path.exists(storage_dir):
        print(f"🧹  Cleaning storage directory: {storage_dir}")
        try:
            shutil.rmtree(storage_dir)
            os.makedirs(storage_dir)
            # Re-create necessary subdirectories
            os.makedirs(os.path.join(storage_dir, "epubs"), exist_ok=True)
            os.makedirs(os.path.join(storage_dir, "temp"), exist_ok=True)
            print("✅  Storage cleared.")
        except Exception as e:
            print(f"❌  Failed to clear storage: {e}")
    else:
        print(f"ℹ️  Storage directory not found, creating: {storage_dir}")
        os.makedirs(storage_dir)
        os.makedirs(os.path.join(storage_dir, "epubs"), exist_ok=True)
        os.makedirs(os.path.join(storage_dir, "temp"), exist_ok=True)

if __name__ == "__main__":
    # Check for -y flag to skip confirmation
    if "-y" in sys.argv:
        confirm = 'y'
    else:
        confirm = input("⚠️  Are you sure you want to reset the database and storage? This cannot be undone. (y/n): ")
    
    if confirm.lower() == 'y':
        reset_database()
        clear_storage()
        print("\n✨  Reset complete. System is ready for fresh testing.")
    else:
        print("❌  Reset cancelled.")
