from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    # LLM provider: ollama or anthropic
    llm_provider: str = "ollama"

    # Local Ollama
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3.2:3b"

    # Embeddings
    embedding_model: str = "nomic-embed-text"

    # Anthropic / Claude Agent SDK
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # Frontend
    cors_origins: str = "http://localhost:3000"

    # Logging
    log_level: str = "INFO"


settings = Settings()