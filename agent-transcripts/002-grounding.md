# Agent Transcript 002 — Grounding

## Problem
A generic LLM answer would not satisfy the requirement for transcript-grounded responses.

## Correction
Added an ingestion pipeline, embeddings, pgvector retrieval, source metadata, and an explicit insufficient-evidence policy.

## Verification
The API response returns source metadata with each grounded answer.
