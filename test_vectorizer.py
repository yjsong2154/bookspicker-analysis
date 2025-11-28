import os
import sys
from dotenv import load_dotenv

# Add module path
sys.path.append(os.path.join(os.getcwd(), 'auto_analysis'))

from modules import vectorizer

load_dotenv()
key = os.getenv("GMS_KEY")
print(f"GMS_KEY present: {bool(key)}")
if key:
    print(f"GMS_KEY length: {len(key)}")
    print(f"GMS_KEY start: {key[:5]}...")

print("Testing vectorizer...")
vec = vectorizer.get_embedding("Hello world")
if vec:
    print(f"Vector generated. Length: {len(vec)}")
else:
    print("Vector generation failed.")
