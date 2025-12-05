from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)

def test_workflow():
    # 1. Upload Book
    epub_path = r"c:\dev_folder\ssafy\bookspicker-analysis\auto_analysis\input\인간 실격 - 민음사 세계문학전집 103 -- 다자이 오사무 -- ( WeLib.org ).epub"
    if not os.path.exists(epub_path):
        print(f"Sample EPUB not found at {epub_path}")
        return

    print("Testing Upload...")
    with open(epub_path, "rb") as f:
        response = client.post(
            "/books/upload",
            data={"title": "No Longer Human", "author": "Osamu Dazai"},
            files={"file": ("sample.epub", f, "application/epub+zip")}
        )
    
    if response.status_code != 200:
        print(f"Upload failed: {response.status_code} {response.text}")
        # Continue testing other parts if possible, but upload is critical
        # return
    else:
        book_data = response.json()
        book_id = book_data["id"]
        print(f"Book uploaded: {book_data['title']} (ID: {book_id})")
        print(f"Tags: {book_data.get('tags')}")

    # 2. Create User
    print("\nTesting User Creation...")
    response = client.post(
        "/users/",
        json={"name": "Test User", "email": "test@example.com"}
    )
    if response.status_code == 400: # Already exists
        print("User might already exist.")
        # Assuming user 1 exists if we ran this before
        user_id = 1 
        # Or fetch user 1
        response = client.get("/users/1")
        if response.status_code == 200:
            user_id = response.json()["id"]
        else:
            print("Could not find user 1")
            return
    elif response.status_code == 200:
        user_data = response.json()
        user_id = user_data["id"]
        print(f"User created: {user_data['name']} (ID: {user_id})")
    else:
        print(f"User creation failed: {response.status_code} {response.text}")
        return

    # 3. Record Reading
    # We need a book_id. If upload failed, we can't do this properly unless we have existing books.
    # Let's assume upload succeeded or we try with ID 1.
    target_book_id = 1
    if 'book_id' in locals():
        target_book_id = book_id

    print(f"\nTesting Record Reading for User {user_id}, Book {target_book_id}...")
    response = client.post(
        f"/users/{user_id}/books/{target_book_id}",
        json={"status": "finished", "rating": 5, "progress": 1.0}
    )
    if response.status_code == 200:
        print(f"Reading recorded: {response.json()}")
    else:
        print(f"Record reading failed: {response.status_code} {response.text}")

    # 4. Get Recommendations
    print(f"\nTesting Recommendations for User {user_id}...")
    response = client.get(f"/users/{user_id}/recommendations")
    if response.status_code == 200:
        print(f"Recommendations: {response.json()}")
    else:
        print(f"Recommendations failed: {response.status_code} {response.text}")

if __name__ == "__main__":
    test_workflow()
