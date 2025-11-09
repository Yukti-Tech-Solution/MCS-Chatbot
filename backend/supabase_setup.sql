-- ============================================
-- MCS Act Chatbot - Supabase Database Setup
-- ============================================
-- Run this script in your Supabase SQL Editor
-- (Dashboard → SQL Editor → New Query)

-- Step 1: Enable pgvector extension (required for vector similarity search)
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Create the documents table
CREATE TABLE IF NOT EXISTS mcs_documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(384),  -- 384 is the dimension for all-MiniLM-L6-v2 model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create index for vector similarity search (improves query performance)
CREATE INDEX IF NOT EXISTS mcs_documents_embedding_idx 
ON mcs_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Step 4: Create RPC function for similarity search
-- This function allows efficient vector similarity queries
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 3
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

-- Step 5: Set up Row Level Security (RLS) - Optional but recommended for production
-- Enable RLS on the table
ALTER TABLE mcs_documents ENABLE ROW LEVEL SECURITY;

-- Create policy to allow service role to access all documents
-- (This is already allowed by default, but explicit is better)
CREATE POLICY "Service role can access all documents"
ON mcs_documents
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);

-- ============================================
-- Verification Queries (run these to verify setup)
-- ============================================

-- Check if table exists
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'mcs_documents';

-- Check if function exists
SELECT routine_name, routine_type 
FROM information_schema.routines 
WHERE routine_name = 'match_documents';

-- Check if extension is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- ============================================
-- Cleanup (if you need to start over)
-- ============================================
-- DROP FUNCTION IF EXISTS match_documents;
-- DROP TABLE IF EXISTS mcs_documents;
-- DROP EXTENSION IF EXISTS vector;

