"""
MCS Act Chatbot API - Main FastAPI Application
Handles RAG-based question answering using Groq/Gemini and Supabase vector search
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from supabase import create_client, Client
from groq import Groq
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file (robust lookup)
# 1) Load from current working directory if available
load_dotenv()
# 2) Explicitly load .env placed next to this file to avoid cwd/reloader issues
_env_path = Path(__file__).resolve().parent / '.env'
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path, override=True)

# Initialize FastAPI application
app = FastAPI(
    title="MCS Act Chatbot API",
    description="RAG-based chatbot for Maharashtra Cooperative Societies Act queries",
    version="1.0.0"
)

# Configure CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-8b")

# Fallback: try to load from project-level API_keys.txt if any are missing
if not all([GROQ_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    try:
        project_root = Path(__file__).resolve().parent.parent
        api_keys_path = project_root / 'API_keys.txt'
        if api_keys_path.exists():
            with open(api_keys_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    key, val = [part.strip() for part in line.split(':', 1)]
                    if key.lower().startswith('groq') and not os.getenv('GROQ_API_KEY'):
                        os.environ['GROQ_API_KEY'] = val
                    elif key.lower().startswith('gemini') and not os.getenv('GEMINI_API_KEY'):
                        os.environ['GEMINI_API_KEY'] = val
                    elif key.lower().startswith('supabase') and 'http' in val and not os.getenv('SUPABASE_URL'):
                        os.environ['SUPABASE_URL'] = val
                    elif 'service_role' in key.lower() and not os.getenv('SUPABASE_KEY'):
                        os.environ['SUPABASE_KEY'] = val
            # Re-read
            GROQ_API_KEY = os.getenv("GROQ_API_KEY")
            GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
            SUPABASE_URL = os.getenv("SUPABASE_URL")
            SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    except Exception:
        pass

# Validate required environment variables
if not all([GROQ_API_KEY, GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Initialize SentenceTransformer model for embeddings
# Using all-MiniLM-L6-v2: lightweight, fast, good quality
print("Loading embedding model...")
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("Embedding model loaded successfully!")

# Initialize Supabase client
print("Initializing Supabase client...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase client initialized!")

# Initialize Groq client
print("Initializing Groq client...")
groq_client = Groq(api_key=GROQ_API_KEY)
print("Groq client initialized!")

# Initialize Gemini client
print("Initializing Gemini client...")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(GEMINI_MODEL)
print("Gemini client initialized!")


# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str
    sources: list


def search_similar_documents(query: str, top_k: int = 3) -> list:
    """
    Search for similar documents in Supabase using vector similarity
    
    Args:
        query: User's question string
        top_k: Number of top similar documents to retrieve (default: 3)
    
    Returns:
        List of document dictionaries with content and metadata
    
    Raises:
        Exception: If embedding generation or database query fails
    """
    try:
        # Generate embedding for the query
        print(f"Generating embedding for query: {query[:50]}...")
        query_embedding = embedding_model.encode(query, convert_to_numpy=True)
        query_embedding_list = query_embedding.tolist()
        print("Embedding generated successfully!")
        
        # Query Supabase using RPC function for vector similarity search
        # This assumes you have a match_documents function in Supabase
        # If not, you can use direct table query with pgvector
        print("Searching Supabase for similar documents...")
        
        # Method 1: Using RPC function (if you have match_documents function)
        try:
            response = supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding_list,
                    'match_threshold': 0.5,
                    'match_count': top_k
                }
            ).execute()
            
            documents = response.data if response.data else []
            
        except Exception as rpc_error:
            # Method 2: Direct table query using pgvector (fallback)
            print(f"RPC function not available, using direct query: {str(rpc_error)}")
            
            # Query the mcs_documents table directly
            # Note: This requires proper pgvector setup in Supabase
            response = supabase.table('mcs_documents').select('*').execute()
            
            # Calculate similarity manually (simplified approach)
            # In production, use Supabase's vector similarity functions
            if response.data:
                # For now, return all documents (you should implement proper vector search)
                # This is a fallback - proper implementation requires pgvector functions
                documents = response.data[:top_k] if len(response.data) > top_k else response.data
            else:
                documents = []
        
        print(f"Found {len(documents)} similar documents")
        return documents
        
    except Exception as e:
        print(f"Error in search_similar_documents: {str(e)}")
        raise Exception(f"Failed to search documents: {str(e)}")


def generate_response(question: str, context: str) -> str:
    """
    Generate response using LLM (Groq first, Gemini as fallback)
    
    Args:
        question: User's question
        context: Retrieved context from documents
    
    Returns:
        Generated answer string
    
    Raises:
        Exception: If both LLM APIs fail
    """
    # Create system prompt for legal assistant
    system_prompt = """You are a legal assistant specialized in Maharashtra Cooperative Societies Act.
Answer questions based ONLY on the provided context.
Cite specific act sections when applicable.
If information is not in context, say 'I don't have information about this in the MCS Act documents.'
Be clear, concise, and helpful."""

    # Create user prompt with context and question
    user_prompt = f"""Context from MCS Act:

{context}

Question: {question}

Provide a detailed answer with act section references if applicable."""

    # Try Groq API first
    try:
        print("Attempting to generate response with Groq...")
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            model=GROQ_MODEL,
            temperature=0.3,
            max_tokens=1024
        )
        
        response_text = chat_completion.choices[0].message.content
        print("Response generated successfully with Groq!")
        return response_text
        
    except Exception as groq_error:
        print(f"Groq API failed: {str(groq_error)}")
        print("Falling back to Gemini API...")
        
        # Fallback to Gemini API
        try:
            # Combine system and user prompts for Gemini
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response = gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024
                )
            )
            
            response_text = response.text
            print("Response generated successfully with Gemini!")
            return response_text
            
        except Exception as gemini_error:
            error_msg = f"Both LLM APIs failed. Groq error: {str(groq_error)}, Gemini error: {str(gemini_error)}"
            print(error_msg)
            raise Exception(error_msg)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles user questions with RAG
    
    Args:
        request: ChatRequest with question field
    
    Returns:
        ChatResponse with answer and sources
    
    Raises:
        HTTPException: If question is empty or processing fails
    """
    try:
        # Validate question is not empty
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        print(f"\n{'='*60}")
        print(f"Received question: {question}")
        print(f"{'='*60}\n")
        
        # Step 1: Search for similar documents
        documents = search_similar_documents(question, top_k=3)
        
        # Step 2: Check if documents were found
        if not documents or len(documents) == 0:
            return ChatResponse(
                answer="I couldn't find any relevant information in the MCS Act documents. Please try rephrasing your question or ensure that PDFs have been processed and uploaded to the database.",
                sources=[]
            )
        
        # Step 3: Combine document contents into context string
        context_parts = []
        sources = []
        
        for i, doc in enumerate(documents):
            # Extract content and metadata
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            # Add to context
            context_parts.append(f"[Document {i+1}]\n{content}")
            
            # Extract source information
            source_info = {
                'filename': metadata.get('filename', 'Unknown'),
                'chunk_id': metadata.get('chunk_id', i+1),
                'total_chunks': metadata.get('total_chunks', 'Unknown')
            }
            sources.append(source_info)
        
        context = "\n\n".join(context_parts)
        
        # Step 4: Generate response using LLM
        answer = generate_response(question, context)
        
        # Step 5: Return response with sources
        return ChatResponse(
            answer=answer,
            sources=sources
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Status of the API and model
    """
    return {
        "status": "healthy",
        "model": "loaded",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
    }


@app.get("/")
async def root():
    """
    Root endpoint
    
    Returns:
        API information
    """
    return {
        "message": "MCS Act Chatbot API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

