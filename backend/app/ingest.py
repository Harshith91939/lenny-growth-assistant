import argparse
import asyncio
import json
import re
import uuid
from pathlib import Path

import httpx
from sqlalchemy import text

from .db import SessionLocal
from .llm import embed


REPO_TREE = (
    "https://api.github.com/repos/"
    "ChatPRD/lennys-podcast-transcripts/git/trees/main?recursive=1"
)

RAW_BASE = (
    "https://raw.githubusercontent.com/"
    "ChatPRD/lennys-podcast-transcripts/main/"
)


def parse_md(raw: str):
    metadata = {}
    body = raw

    if raw.startswith("---"):
        parts = raw.split("---", 2)

        if len(parts) == 3:
            header, body = parts[1], parts[2]

            for line in header.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip().strip('"')

    return metadata, body.strip()


def chunks(text_value: str, size=1800, overlap=250):
    text_value = re.sub(r"\n{3,}", "\n\n", text_value)

    output = []
    start = 0

    while start < len(text_value):
        end = min(len(text_value), start + size)
        piece = text_value[start:end]

        if len(piece.strip()) > 100:
            output.append(piece.strip())

        if end == len(text_value):
            break

        start = end - overlap

    return output


async def main(limit=None):
    async with httpx.AsyncClient(timeout=60) as client:

        response = await client.get(REPO_TREE)
        response.raise_for_status()

        tree = response.json()["tree"]

        # IMPORTANT:
        # Only ingest actual podcast transcript files.
        paths = [
            item["path"]
            for item in tree
            if item["path"].startswith("episodes/")
            and item["path"].endswith("/transcript.md")
        ]

        if limit:
            paths = paths[:limit]

        print(f"Found {len(paths)} transcript files.")

        async with SessionLocal() as db:

            for index, path in enumerate(paths, 1):

                print(f"[{index}/{len(paths)}] Downloading {path}")

                raw_response = await client.get(RAW_BASE + path)
                raw_response.raise_for_status()

                raw = raw_response.text

                metadata, body = parse_md(raw)

                title = metadata.get("title") or Path(path).parent.name
                guest = metadata.get("guest")
                source_url = (
                    metadata.get("youtube_url")
                    or metadata.get("url")
                )

                document_id = uuid.uuid4()

                # JSONB values passed through raw SQL must be JSON strings.
                metadata_json = json.dumps(metadata)

                await db.execute(
                    text(
                        """
                        INSERT INTO documents(
                            id,
                            title,
                            guest,
                            source_url,
                            content,
                            metadata
                        )
                        VALUES(
                            :id,
                            :title,
                            :guest,
                            :source_url,
                            :content,
                            CAST(:metadata AS jsonb)
                        )
                        """
                    ),
                    {
                        "id": document_id,
                        "title": title,
                        "guest": guest,
                        "source_url": source_url,
                        "content": body,
                        "metadata": metadata_json,
                    },
                )

                transcript_chunks = chunks(body)

                print(
                    f"    {len(transcript_chunks)} chunks; "
                    f"creating embeddings..."
                )

                for chunk_index, chunk in enumerate(transcript_chunks):

                    embedding = await embed(chunk)

                    vector = "[" + ",".join(
                        str(value) for value in embedding
                    ) + "]"

                    await db.execute(
                        text(
                            """
                            INSERT INTO chunks(
                                id,
                                document_id,
                                chunk_index,
                                content,
                                embedding,
                                metadata
                            )
                            VALUES(
                                :id,
                                :document_id,
                                :chunk_index,
                                :content,
                                CAST(:embedding AS vector),
                                CAST(:metadata AS jsonb)
                            )
                            """
                        ),
                        {
                            "id": uuid.uuid4(),
                            "document_id": document_id,
                            "chunk_index": chunk_index,
                            "content": chunk,
                            "embedding": vector,
                            "metadata": metadata_json,
                        },
                    )

                await db.commit()

                print(f"    ✓ Ingested: {title}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )

    args = parser.parse_args()

    asyncio.run(main(args.limit))