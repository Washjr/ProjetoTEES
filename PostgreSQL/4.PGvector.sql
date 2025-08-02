-- This SQL script is used to set up the PGvector extension in PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the column for storing vector embeddings in the artigo table
-- The vector size is set to 1536, which is common for models like OpenAI's text-embedding-3-small
ALTER TABLE artigo
ADD COLUMN embedding vector(1536);

-- Create a GIN index on the embedding column for efficient similarity search
-- Use this after inserting data into the embedding column
CREATE INDEX ON artigo 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);