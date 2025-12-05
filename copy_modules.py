import shutil
import os

src = "auto_analysis/modules"
dst = "app/services/modules"

try:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print("Modules copied successfully")
except Exception as e:
    print(f"Error copying modules: {e}")
