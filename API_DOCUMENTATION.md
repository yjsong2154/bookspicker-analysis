# Bookspicker Analysis Service API Documentation

## Base URL

Assuming local development: `http://localhost:8001`

---

## 📚 Books

### 1. Upload Book (EPUB)

Uploads an EPUB file, analyzes it, and saves the book metadata and vector/tags.

- **URL**: `/books/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: (File, required) The .epub file.
  - `isbn`: (String, required)
  - `title`: (String, required)
  - `author`: (String, optional)

### 2. Manual Book Registration

Manually register a book with pre-analyzed data (vectors, tags).

- **URL**: `/books/`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Body**:

```json
{
  "isbn": "string",
  "title": "string",
  "author": "string",
  "description": "string",
  "published_year": 0,
  "tags": { "tag_name": 10 },
  "embedding": [0.0, 0.1, ...]
}
```

### 3. Get Book List

- **URL**: `/books/`
- **Method**: `GET`
- **Query Parameters**:
  - `skip`: (int, default 0)
  - `limit`: (int, default 20)
  - `q`: (string, optional) Search query for title/author.

### 4. Get Book Detail

- **URL**: `/books/{book_id}`
- **Method**: `GET`

---

## 👤 Users

### 1. Create User

- **URL**: `/users/`
- **Method**: `POST`
- **Body**:

```json
{
  "name": "string",
  "email": "string",
  "id_backend": 0
}
```

### 2. Record Read History (Internal IDs)

- **URL**: `/users/{user_id}/books/{book_id}`
- **Method**: `POST`

### 3. Record Read History (External IDs)

Record a read book using the backend's User ID and Book ISBN.

- **URL**: `/users/record-read`
- **Method**: `POST`
- **Body**:

```json
{
  "id_backend": 123,
  "isbn": "978-..."
}
```

### 4. Get User Read History

- **URL**: `/users/{user_id}/books`
- **Method**: `GET`

---

## 🔍 Analysis

### 1. Analyze EPUB File

Analyzes an uploaded EPUB and returns tags and vectors without saving to DB.

- **URL**: `/analysis/analyze`
- **Method**: `POST`
- **Body**: `file` (multipart)

---

## 💡 Recommendations

### 1. Advanced Recommendations

Recalculates user preferences based on history and returns categorized recommendations.

- **URL**: `/users/{id_backend}/advanced-recommendations`
- **Method**: `GET`
- **Response**:

```json
{
  "sections": [
    {
      "title": "ai가 가장 추천",
      "books": [ { "isbn": "...", "title": "...", ... } ]
    },
    {
      "title": "ai가 추천하는 책",
      "books": [ ... ]
    },
    {
      "title": "{tagName}",
      "books": [ ... ]
    }
  ]
}
```

### 2. Simple Recommendations (Internal ID)

- **URL**: `/users/{user_id}/recommendations`
- **Method**: `GET`
