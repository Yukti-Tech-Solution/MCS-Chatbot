"""
MCS Act PDF Processor
Extracts text from PDF files, chunks them, generates embeddings, and uploads to Supabase
"""

from pypdf import PdfReader
from supabase import create_client, Client
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment variables")

# Initialize Gemini for embeddings
print("Initializing Gemini for embeddings...")
genai.configure(api_key=GEMINI_API_KEY)
print("Gemini embedding model configured successfully!")

# Initialize Supabase client
print("Initializing Supabase client...")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase client initialized!")

# PDF folder path
PDF_FOLDER = Path("pdfs")


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Complete text content from the PDF
    
    Raises:
        Exception: If PDF cannot be read
    """
    try:
        print(f"  Extracting text from PDF: {pdf_path}")
        
        # Open and read PDF
        reader = PdfReader(pdf_path)
        
        # Extract text from all pages
        text_parts = []
        total_pages = len(reader.pages)
        
        for page_num, page in enumerate(reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                print(f"    Processed page {page_num}/{total_pages}", end='\r')
            except Exception as page_error:
                print(f"\n    Warning: Error extracting page {page_num}: {str(page_error)}")
                continue
        
        # Combine all text
        full_text = "\n\n".join(text_parts)
        print(f"\n  Extracted {len(full_text)} characters from {total_pages} pages")
        
        return full_text
        
    except Exception as e:
        print(f"  Error reading PDF {pdf_path}: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Split text into chunks with overlap for better context preservation
    
    Args:
        text: Full text to chunk
        chunk_size: Number of words per chunk (default: 500)
        overlap: Number of words to overlap between chunks (default: 50)
    
    Returns:
        List of text chunks
    """
    # Split text into words
    words = text.split()
    
    if len(words) <= chunk_size:
        # If text is shorter than chunk size, return as single chunk
        return [text]
    
    chunks = []
    start_idx = 0
    
    # Create chunks with overlap
    while start_idx < len(words):
        # Calculate end index for current chunk
        end_idx = start_idx + chunk_size
        
        # Extract chunk
        chunk_words = words[start_idx:end_idx]
        chunk_text = " ".join(chunk_words)
        
        chunks.append(chunk_text)
        
        # Move start index forward with overlap
        start_idx = end_idx - overlap
        
        # Prevent infinite loop
        if start_idx >= len(words):
            break
    
    print(f"  Created {len(chunks)} chunks from text")
    return chunks


def process_pdfs():
    """
    Main function to process all PDFs in the pdfs folder
    Extracts text, chunks it, generates embeddings, and uploads to Supabase
    """
    # Check if pdfs folder exists, create if not
    if not PDF_FOLDER.exists():
        PDF_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"Created '{PDF_FOLDER}' folder. Please add your PDF files here.")
        return
    
    # Get all PDF files from folder
    pdf_files = list(PDF_FOLDER.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{PDF_FOLDER}' folder.")
        print("Please add your MCS Act PDF files to the 'pdfs' folder and try again.")
        return
    
    print(f"\nFound {len(pdf_files)} PDF file(s) to process")
    print("=" * 60)
    
    total_chunks = 0
    processed_files = 0
    
    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            print(f"\nProcessing: {pdf_file.name}")
            print("-" * 60)
            
            # Step 1: Extract text from PDF
            text = extract_text_from_pdf(str(pdf_file))
            
            if not text or len(text.strip()) == 0:
                print(f"  Warning: No text extracted from {pdf_file.name}, skipping...")
                continue
            
            # Step 2: Chunk the text
            chunks = chunk_text(text, chunk_size=500, overlap=50)
            total_chunks_for_file = len(chunks)
            
            print(f"  Processing {total_chunks_for_file} chunks...")
            
            # Step 3: Process each chunk
            uploaded_count = 0
            for chunk_idx, chunk in enumerate(chunks, 1):
                try:
                    # Generate embedding for chunk using Gemini
                    embedding_result = genai.embed_content(
                        model="models/text-embedding-004",
                        content=chunk,
                        task_type="RETRIEVAL_DOCUMENT"
                    )
                    embedding_list = embedding_result['embedding']
                    
                    # Create metadata
                    metadata = {
                        "filename": pdf_file.name,
                        "chunk_id": chunk_idx,
                        "total_chunks": total_chunks_for_file
                    }
                    
                    # Insert into Supabase mcs_documents table
                    # Note: Ensure your Supabase table has these columns:
                    # - content (text)
                    # - metadata (jsonb)
                    # - embedding (vector)
                    insert_result = supabase.table('mcs_documents').insert({
                        'content': chunk,
                        'metadata': metadata,
                        'embedding': embedding_list
                    }).execute()
                    
                    uploaded_count += 1
                    total_chunks += 1
                    
                    print(f"  Uploaded chunk {chunk_idx}/{total_chunks_for_file}", end='\r')
                    
                except Exception as chunk_error:
                    print(f"\n  Error uploading chunk {chunk_idx}: {str(chunk_error)}")
                    continue
            
            print(f"\n  Successfully uploaded {uploaded_count}/{total_chunks_for_file} chunks from {pdf_file.name}")
            processed_files += 1
            
        except Exception as file_error:
            print(f"\n  Error processing {pdf_file.name}: {str(file_error)}")
            print(f"  Continuing with next file...")
            continue
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Processing complete!")
    print(f"  - Successfully processed: {processed_files}/{len(pdf_files)} PDFs")
    print(f"  - Total chunks uploaded: {total_chunks}")
    print("=" * 60)


if __name__ == "__main__":
    print("MCS Act PDF Processor")
    print("=" * 60)
    process_pdfs()

