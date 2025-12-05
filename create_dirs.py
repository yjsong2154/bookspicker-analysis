import os
try:
    os.makedirs("storage/epubs", exist_ok=True)
    os.makedirs("storage/temp", exist_ok=True)
    print("Directories created")
except Exception as e:
    print(f"Error: {e}")
