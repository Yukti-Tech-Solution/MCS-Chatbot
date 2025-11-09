# MCS Act Chatbot

Complete RAG-based chatbot application for Maharashtra Cooperative Societies Act queries. This application helps society members understand legal procedures through an intelligent question-answering system.

## Features

- **ChatGPT-like Interface**: Modern, dark-themed UI with smooth interactions
- **Context-Aware Responses**: Answers based on actual MCS Act documents with citations
- **Fast Response Times**: Powered by Groq API (primary) and Google Gemini (fallback)
- **Vector Search**: Efficient semantic search using Supabase with pgvector extension
- **PDF Processing**: Automatic text extraction and chunking from PDF documents
- **Source Citations**: Responses include references to source documents

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed ([Download](https://www.python.org/downloads/))
- **Node.js 18+** installed ([Download](https://nodejs.org/))
- **Groq API Key** ([Get from Groq Console](https://console.groq.com))
- **Google Gemini API Key** ([Get from Google AI Studio](https://aistudio.google.com/app/apikey))
- **Supabase Account** ([Sign up for free](https://supabase.com))

## Project Structure

```
mcs-act-chatbot/
├── backend/
│   ├── main.py              # FastAPI application with RAG logic
│   ├── pdf_processor.py     # PDF extraction and Supabase upload
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variables template
│   ├── .env                 # Your actual API keys (create this)
│   ├── README.md            # Backend setup instructions
│   └── pdfs/                # Place your PDF files here
│
├── frontend/
│   ├── public/              # Static assets
│   ├── src/
│   │   ├── App.jsx          # Main React app component
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx  # Chat UI component
│   │   │   ├── Message.jsx        # Message display component
│   │   │   └── InputBox.jsx       # Input component
│   │   ├── main.jsx         # React entry point
│   │   ├── index.css        # Global styles
│   │   └── api.js           # API helper functions
│   ├── index.html           # HTML template
│   ├── package.json         # Node.js dependencies
│   ├── vite.config.js       # Vite configuration
│   └── .env.example         # Frontend environment template
│
└── README.md                # This file
```

## Quick Start Guide

### Step 1: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   
   Create a `.env` file in the `backend` directory:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
   SUPABASE_URL=YOUR_SUPABASE_URL_HERE
   SUPABASE_KEY=YOUR_SUPABASE_KEY_HERE
   ```

4. **Set up Supabase Database:**
   
   Open your Supabase project dashboard and run this SQL in the SQL Editor:
   
   ```sql
   -- Enable pgvector extension
   CREATE EXTENSION IF NOT EXISTS vector;

   -- Create the documents table
   CREATE TABLE mcs_documents (
       id BIGSERIAL PRIMARY KEY,
       content TEXT NOT NULL,
       metadata JSONB,
       embedding vector(384),
       created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Create index for vector similarity search
   CREATE INDEX ON mcs_documents USING ivfflat (embedding vector_cosine_ops);

   -- Create RPC function for similarity search
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

5. **Prepare PDF files:**
   
   Create a `pdfs` folder in the backend directory and add your MCS Act PDF files:
   ```bash
   mkdir pdfs
   # Copy your PDF files to the pdfs folder
   ```

6. **Process PDFs (one-time setup):**
   ```bash
   python pdf_processor.py
   ```
   
   This will extract text, create chunks, generate embeddings, and upload to Supabase.

7. **Start the backend server:**
   ```bash
   uvicorn main:app --reload
   ```
   
   The server will run at **http://localhost:8000**
   
   API documentation available at **http://localhost:8000/docs**

### Step 2: Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables (optional):**
   
   If your backend runs on a different URL, create `.env.local`:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   The app will run at **http://localhost:5173**

### Step 3: Access the Application

1. Open your browser and navigate to **http://localhost:5173**
2. Start asking questions about the MCS Act!

## API Keys Setup

### Groq API Key

1. Go to [Groq Console](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

### Supabase Setup

1. Go to [Supabase](https://supabase.com) and sign up
2. Create a new project
3. Go to Settings → API
4. Copy your:
   - **Project URL** → `SUPABASE_URL`
   - **Service Role Key** → `SUPABASE_KEY` (⚠️ Keep this secret!)
5. Run the SQL script provided in Step 1.4 to set up the database

## Usage Examples

### Example Questions

- "What are the requirements for forming a cooperative society?"
- "What is the procedure for registering a cooperative society?"
- "What are the rights and duties of members?"
- "How is the management committee elected?"
- "What are the audit requirements?"

### API Usage

You can also use the API directly:

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the requirements for forming a cooperative society?"}'
```

## Troubleshooting

### Backend Issues

**Problem:** "Missing required environment variables"
- **Solution:** Ensure `.env` file exists in the `backend` directory with all required keys

**Problem:** "Failed to search documents"
- **Solution:** 
  - Verify Supabase table `mcs_documents` exists
  - Check that you've run `pdf_processor.py` to upload documents
  - Verify Supabase credentials in `.env`

**Problem:** "Both LLM APIs failed"
- **Solution:**
  - Check your API keys are valid
  - Verify internet connection
  - Check API quota/limits

### Frontend Issues

**Problem:** "Failed to get response from server"
- **Solution:**
  - Ensure backend server is running on port 8000
  - Check CORS settings if running on different ports
  - Verify `.env.local` has correct `VITE_API_URL`

**Problem:** Build errors
- **Solution:**
  - Delete `node_modules` and `package-lock.json`
  - Run `npm install` again
  - Check Node.js version (should be 18+)

## Deployment

### Backend Deployment

For production deployment:

1. **Update CORS settings** in `main.py`:
   ```python
   allow_origins=["https://your-frontend-domain.com"]
   ```

2. **Use environment variables** in your hosting platform
3. **Set up a production WSGI server** (e.g., Gunicorn with Uvicorn workers)

### Frontend Deployment

1. **Build the production bundle:**
   ```bash
   npm run build
   ```

2. **Deploy the `dist` folder** to your hosting service (Vercel, Netlify, etc.)

3. **Set environment variables** in your hosting platform:
   - `VITE_API_URL`: Your backend API URL

## Technology Stack

- **Backend:**
  - FastAPI - Modern Python web framework
  - Sentence Transformers - Embedding generation
  - Supabase - Vector database with pgvector
  - Groq API - Fast LLM inference
  - Google Gemini - Fallback LLM
  - PyPDF2 - PDF text extraction

- **Frontend:**
  - React 18 - UI framework
  - Vite - Build tool and dev server
  - Axios - HTTP client

## License

This project is for educational and internal use purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review backend and frontend README files
3. Check API documentation at `/docs` endpoint

---

**Happy Chatting! 🚀**

