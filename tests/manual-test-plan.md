# Manual Test Plan

1. Start with `docker compose up --build -d`.
2. Pull the local models.
3. Run ingestion.
4. Open the frontend.
5. Create two sessions.
6. Verify messages remain isolated.
7. Ask a product question and verify sources.
8. Ask a follow-up and verify context.
9. Ask for a Ship 30 for 30 essay.
10. Ask for a Markdown/HTML artifact.
11. Verify artifact viewer.
12. Test Ollama restart/failure.
13. Restart the stack and verify persistence.
