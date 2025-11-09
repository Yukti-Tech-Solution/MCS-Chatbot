"""
MCS Act Chatbot API - Main FastAPI Application
Handles RAG-based question answering using Groq/Gemini and Supabase vector search
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from supabase import create_client, Client
from groq import Groq
import google.generativeai as genai
import os
import json
import re
from io import BytesIO
from dotenv import load_dotenv
from pathlib import Path
from resources import get_relevant_links

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

# Initialize Gemini for embeddings and LLM
print("Initializing Gemini client...")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(GEMINI_MODEL)
print("Gemini client initialized!")

# Initialize Supabase client
print("Initializing Supabase client...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase client initialized!")

# Initialize Groq client
print("Initializing Groq client...")
groq_client = Groq(api_key=GROQ_API_KEY)
print("Groq client initialized!")


# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str
    sources: list
    related_links: list = []  # Government resources and official links


def search_similar_documents(query: str, top_k: int = 3) -> list:
    """
    Search for similar documents in Supabase using vector similarity
    
    Uses Gemini text-embedding-004 model for generating query embeddings.
    
    Args:
        query: User's question string
        top_k: Number of top similar documents to retrieve (default: 3)
    
    Returns:
        List of document dictionaries with content and metadata
    
    Raises:
        Exception: If embedding generation or database query fails
    """
    try:
        # Generate embedding for the query using Gemini
        print(f"Generating embedding for query: {query[:50]}...")
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="RETRIEVAL_QUERY"
        )
        query_embedding = result['embedding']
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
                    'query_embedding': query_embedding,
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


def simplify_legal_terms(text: str) -> str:
    """
    Replace common legal jargon with simple explanations in brackets
    
    This function helps non-technical users understand legal terms by
    adding simple explanations right after complex terms.
    
    Args:
        text: Response text with potential legal terms
    
    Returns:
        Text with simplified legal terms (explanations added in brackets)
    """
    # Dictionary of legal terms and their simple explanations
    legal_terms = {
        "mutatis mutandis": "with necessary changes",
        "prima facie": "at first glance / on the surface",
        "ipso facto": "by that very fact / automatically",
        "bona fide": "genuine / in good faith",
        "caveat": "warning / condition",
        "suo moto": "on its own / without being asked",
        "ad hoc": "temporary / for this specific purpose",
        "quorum": "minimum number of members needed",
        "resolution": "official decision",
        "bylaws": "society rules",
        "AGM": "Annual General Meeting (yearly meeting of all members)",
        "nominee": "person appointed to represent",
        "proxy": "someone authorized to vote on your behalf",
        "arrears": "unpaid dues / pending payments",
        "audit": "official checking of accounts"
    }
    
    result_text = text
    for term, explanation in legal_terms.items():
        # Case-insensitive replacement with explanation in brackets
        # Only replace if not already explained (avoid duplicates)
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        # Check if term is already followed by an explanation in brackets
        if not re.search(re.escape(term) + r'\s*\([^)]*\)', result_text, re.IGNORECASE):
            result_text = pattern.sub(f"{term} ({explanation})", result_text)
    
    return result_text


def generate_response(question: str, context: str) -> str:
    """
    Generate response using LLM (Groq first, Gemini as fallback)
    
    Uses a detailed system prompt to ensure responses are in simple language
    suitable for non-technical society members.
    
    Args:
        question: User's question
        context: Retrieved context from documents
    
    Returns:
        Generated answer string with simplified legal terms
    
    Raises:
        Exception: If both LLM APIs fail
    """
    # Create detailed system prompt for legal assistant
    # This prompt ensures responses are user-friendly and practical
    system_prompt = """You are a helpful legal assistant for Maharashtra Cooperative Societies Act, speaking to regular society members (not lawyers).

IMPORTANT INSTRUCTIONS:

1. Use SIMPLE, everyday language - avoid legal jargon

2. If you must use legal terms, explain them in brackets like: "mutation (transfer of property rights)"

3. Give practical examples from daily society life

4. Break complex answers into numbered steps

5. Always cite the specific Act section number

6. If information is not in context, say "I don't have this specific information in the MCS Act documents I have access to."

7. Be empathetic and helpful - remember users may be stressed about society issues

RESPONSE FORMAT:

- Start with a brief, clear answer (2-3 sentences)

- Then provide detailed explanation

- End with "Relevant Act: Section X of MCS Act"

- Add "💡 Tip:" for practical advice when relevant"""

    # Create user prompt with context and question
    user_prompt = f"""Context from MCS Act:

{context}

Question: {question}

Provide a detailed answer with act section references if applicable. Use simple language and explain any legal terms."""

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
        
        # Simplify legal terms before returning
        response_text = simplify_legal_terms(response_text)
        
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
            
            # Simplify legal terms before returning
            response_text = simplify_legal_terms(response_text)
            
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
            # Still get general links even if no documents found
            related_links = get_relevant_links(question, "")
            return ChatResponse(
                answer="I couldn't find any relevant information in the MCS Act documents. Please try rephrasing your question or ensure that PDFs have been processed and uploaded to the database.",
                sources=[],
                related_links=related_links
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
        
        # Step 5: Get relevant government links based on question and context
        related_links = get_relevant_links(question, context)
        
        # Step 6: Return response with sources and related links
        return ChatResponse(
            answer=answer,
            sources=sources,
            related_links=related_links
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


def escape_html_for_pdf(text: str) -> str:
    """
    Escape HTML special characters for ReportLab Paragraph
    
    Args:
        text: Text to escape
    
    Returns:
        Escaped text safe for ReportLab Paragraph
    """
    if not text:
        return ""
    # Escape ampersand first to avoid double-escaping
    text = str(text).replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text


@app.post("/api/download-pdf")
async def download_act_pdf(request: ChatRequest):
    """
    Generate and download a PDF with relevant act sections
    
    This endpoint creates a PDF document containing the relevant MCS Act
    sections based on the user's question. The PDF includes:
    - User's question
    - Relevant document sections
    - Source information
    - Footer disclaimer
    
    Args:
        request: ChatRequest with question field
    
    Returns:
        PDF file as downloadable stream
    
    Raises:
        HTTPException: If question is empty, no documents found, or PDF generation fails
    """
    try:
        # Try importing reportlab - if it fails, provide clear error
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
        except ImportError as import_err:
            error_msg = f"ReportLab library not installed: {str(import_err)}. Please install it using: pip install reportlab==4.0.7"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Validate question is not empty
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        print(f"PDF Download requested for question: {question[:50]}...")
        
        # Search for relevant documents (get more for PDF - 5 instead of 3)
        try:
            documents = search_similar_documents(question, top_k=5)
        except Exception as search_err:
            error_msg = f"Failed to search documents: {str(search_err)}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Check if documents were found
        if not documents or len(documents) == 0:
            raise HTTPException(
                status_code=404,
                detail="No relevant information found for this query"
            )
        
        print(f"Found {len(documents)} documents for PDF generation")
        
        # Create PDF in memory buffer
        buffer = BytesIO()
        try:
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch
            )
        except Exception as doc_err:
            error_msg = f"Failed to create PDF document: {str(doc_err)}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Define styles for PDF
        styles = getSampleStyleSheet()
        
        # Custom title style - centered, dark blue, larger font
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor='darkblue',
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Custom heading style - dark green, medium font
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='darkgreen',
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Custom body style - justified text, readable font size
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=14
        )
        
        # Custom source style - italic, smaller font
        source_style = ParagraphStyle(
            'CustomSource',
            parent=styles['BodyText'],
            fontSize=10,
            textColor='gray',
            fontName='Helvetica-Oblique',
            spaceAfter=6
        )
        
        # Build PDF content
        story = []
        
        try:
            # Title
            story.append(Paragraph("Maharashtra Cooperative Societies Act", title_style))
            story.append(Spacer(1, 0.1*inch))
            
            # User's question - escape HTML characters
            escaped_question = escape_html_for_pdf(question)
            story.append(Paragraph(f"<b>Query:</b> {escaped_question}", heading_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Add each relevant section
            for i, doc_data in enumerate(documents, 1):
                try:
                    # Extract content and metadata
                    content = doc_data.get('content', '')
                    metadata = doc_data.get('metadata', {})
                    filename = metadata.get('filename', 'Unknown Document')
                    
                    # Skip if content is empty
                    if not content or not content.strip():
                        print(f"Warning: Document {i} has empty content, skipping...")
                        continue
                    
                    # Section header
                    story.append(Paragraph(f"<b>Section {i}</b>", heading_style))
                    
                    # Source information - escape filename
                    escaped_filename = escape_html_for_pdf(filename)
                    story.append(Paragraph(f"<i>Source: {escaped_filename}</i>", source_style))
                    story.append(Spacer(1, 0.1*inch))
                    
                    # Content formatting for PDF
                    # Split by newlines, escape each line, then join with <br/>
                    lines = content.split('\n')
                    escaped_lines = []
                    for line in lines:
                        # Skip empty lines or add them as breaks
                        if not line.strip():
                            escaped_lines.append("")
                        else:
                            # Escape HTML special characters
                            escaped_line = escape_html_for_pdf(line)
                            escaped_lines.append(escaped_line)
                    
                    # Join lines with <br/> tags for paragraph breaks
                    formatted_content = '<br/>'.join(escaped_lines)
                    
                    # Limit content length to avoid PDF generation issues
                    if len(formatted_content) > 50000:  # Limit to ~50KB of text per section
                        formatted_content = formatted_content[:50000] + "<br/><br/><i>[Content truncated for PDF generation]</i>"
                    
                    story.append(Paragraph(formatted_content, body_style))
                    story.append(Spacer(1, 0.2*inch))
                    
                    # Page break after each section except last
                    if i < len(documents):
                        story.append(PageBreak())
                        
                except Exception as section_err:
                    print(f"Error processing document {i}: {str(section_err)}")
                    # Continue with next document instead of failing completely
                    continue
            
            # Footer with disclaimer
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(
                "<i>This document is generated from the MCS Act Legal Assistant. "
                "Please verify with official sources for legal proceedings.</i>",
                source_style
            ))
            
        except Exception as content_err:
            error_msg = f"Failed to build PDF content: {str(content_err)}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Build PDF document
        try:
            doc.build(story)
            buffer.seek(0)
        except Exception as build_err:
            error_msg = f"Failed to build PDF: {str(build_err)}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        if not pdf_bytes or len(pdf_bytes) == 0:
            raise HTTPException(status_code=500, detail="Generated PDF is empty")
        
        print(f"PDF generated successfully, size: {len(pdf_bytes)} bytes")
        
        # Return as downloadable file
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=MCS_Act_Info.pdf",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error generating PDF: {str(e)}"
        print(error_msg)
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
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
        "embedding_model": "gemini-text-embedding-004"
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

