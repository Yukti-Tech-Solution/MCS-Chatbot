# MCS Act Chatbot - Backend

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

1. Copy `.env.example` to `.env`

2. Fill in your API keys:

   - **GROQ_API_KEY**: Get from https://console.groq.com
   - **GEMINI_API_KEY**: Get from https://aistudio.google.com/app/apikey
   - **SUPABASE_URL**: From Supabase project settings (Dashboard → Settings → API)
   - **SUPABASE_KEY**: Service role key from Supabase (Dashboard → Settings → API → service_role key)

### 3. Set Up Supabase Database

1. Create a new table `mcs_documents` in your Supabase project:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the documents table
CREATE TABLE mcs_documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(384),  -- 384 is the dimension for all-MiniLM-L6-v2
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for vector similarity search
CREATE INDEX ON mcs_documents USING ivfflat (embedding vector_cosine_ops);

-- Create RPC function for similarity search (optional but recommended)
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(384),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        mcs_documents.id,
        mcs_documents.content,
        mcs_documents.metadata,
        1 - (mcs_documents.embedding <=> query_embedding) as similarity
    FROM mcs_documents
    WHERE 1 - (mcs_documents.embedding <=> query_embedding) > match_threshold
    ORDER BY mcs_documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

### 4. Prepare PDF Files

1. Create `pdfs` folder in backend directory (if it doesn't exist)

2. Place your MCS Act PDF files inside the `pdfs` folder

3. Supported format: PDF only

### 5. Process PDFs (One-time)

```bash
python pdf_processor.py
```

This will:
- Extract text from all PDFs in the `pdfs` folder
- Chunk into manageable pieces (500 words per chunk with 50 word overlap)
- Generate embeddings using sentence-transformers
- Upload to Supabase database

**Note**: The first run will download the embedding model (~80MB), which may take a few minutes.

### 6. Start Server

```bash
uvicorn main:app --reload
```

Or using Python directly:

```bash
python main.py
```

Server runs at: **http://localhost:8000**

API docs at: **http://localhost:8000/docs**

## API Endpoints

### POST /api/chat

Send a question to the chatbot.

**Request:**
```json
{
    "question": "What are the requirements for forming a cooperative society?"
}
```

**Response:**
```json
{
    "answer": "According to the MCS Act...",
    "sources": [
        {
            "filename": "mcs_act.pdf",
            "chunk_id": 1,
            "total_chunks": 50
        }
    ]
}
```

### GET /api/health

Check if server is running and models are loaded.

**Response:**
```json
{
    "status": "healthy",
    "model": "loaded",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
}
```

### GET /

Get API information.

**Response:**
```json
{
    "message": "MCS Act Chatbot API",
    "docs": "/docs",
    "version": "1.0.0"
}
```

## Troubleshooting

### Error: "Missing required environment variables"
- Make sure you've created a `.env` file with all required keys

### Error: "Failed to search documents"
- Check that Supabase table `mcs_documents` exists
- Verify that you've uploaded PDFs using `pdf_processor.py`
- Check Supabase connection credentials

### Error: "Both LLM APIs failed"
- Verify your Groq and Gemini API keys are valid
- Check your internet connection
- Ensure API keys have sufficient quota

### Embedding model download slow
- First-time download is normal (~80MB)
- Ensure stable internet connection
- Model will be cached for future use

