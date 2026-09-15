# Agent Transcript — Ingestion Bug Recovery

## Problem
Transcript ingestion initially failed because PostgreSQL JSONB metadata was being passed incorrectly. The ingestion process also selected unrelated Markdown files.

## Investigation
The ingestion query was narrowed to transcript.md files under episode directories, and metadata serialization was corrected before insertion.

## Resolution
The ingestion pipeline was updated to:
- select only episode transcript files
- serialize metadata as JSON
- insert valid JSONB data
- generate embeddings using Ollama

## Result
10 podcast transcripts were ingested successfully, producing 562 searchable chunks.
