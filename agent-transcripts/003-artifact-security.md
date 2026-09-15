# Agent Transcript 003 — Artifact Security

## Problem
Generated HTML must be treated as untrusted.

## Correction
Use an allowlist sanitizer and do not permit JavaScript, iframe, embed, object, or event-handler attributes.

## Trade-off
This limits highly interactive artifacts but provides a safer MVP viewer.
