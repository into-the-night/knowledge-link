# KnowledgeLink

A full-stack web application that allows users to save web links, which are automatically processed to generate summaries and vector embeddings. Users can search through their saved links using natural language queries.

## Features

- **Save Links**: Store web links with automatic metadata extraction
- **Auto-fetch Metadata**: Automatically fetches title and description from web pages
- **Tagging System**: Organize links with custom tags
- **MongoDB Storage**: Uses async MongoDB (motor) for efficient data storage
- **Modern UI**: Clean, responsive interface built with React

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Motor**: Async MongoDB driver for Python
- **Pydantic**: Data validation using Python type annotations
- **BeautifulSoup4**: Web scraping for metadata extraction
- **HTTPX**: Async HTTP client

### Frontend
- **React**: JavaScript library for building user interfaces
- **Vite**: Fast build tool and development server
- **Axios**: HTTP client for API requests

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (running locally or remote instance)
- uv (Python package manager) - optional but recommended

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies using uv (recommended):
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

Or using pip:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the backend directory:
```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=knowledge_link
COLLECTION_NAME=links
```

4. Start MongoDB if running locally:
```bash
# On Ubuntu/Debian
sudo systemctl start mongodb

# Using Docker
docker run -d -p 27017:27017 mongo
```

5. Run the backend server:
```bash
python run.py
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

- `GET /` - API information
- `POST /api/links` - Create a new link
- `GET /api/links` - Get all links (with pagination)
- `GET /api/links/{link_id}` - Get a specific link
- `DELETE /api/links/{link_id}` - Delete a link
- `GET /health` - Health check endpoint

## Usage

1. Open the frontend in your browser (`http://localhost:5173`)
2. Enter a URL in the form
3. Optionally add title, description, and tags
4. Click "Save Link" to store the link
5. View all saved links below the form
6. Click the × button to delete a link

## Project Structure

```
knowledge-link/
├── backend/
│   ├── config.py          # Configuration settings
│   ├── database.py        # MongoDB connection
│   ├── main.py           # FastAPI application
│   ├── models.py         # Pydantic models
│   ├── requirements.txt  # Python dependencies
│   └── run.py           # Server runner
├── frontend/
│   ├── src/
│   │   ├── api/         # API client
│   │   ├── components/  # React components
│   │   ├── App.jsx      # Main app component
│   │   └── main.jsx     # Entry point
│   └── package.json     # Node dependencies
└── README.md
```

## Future Enhancements

- Vector embeddings generation for semantic search
- Natural language search functionality
- User authentication and authorization
- Link categorization and folders
- Bulk import/export functionality
- Browser extension for quick link saving
- Link preview cards
- Full-text search with Elasticsearch

## License

MIT
