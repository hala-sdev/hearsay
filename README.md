# Hearsay

Hearsay is a fact-checking engine. You paste a paragraph, it extracts the individual claims, and verifies each one against Wikipedia. Each claim is labeled Supported, Contradicted, or Not enough evidence, and every verdict cites the exact Wikipedia passage it is based on.

**[Live demo](https://hearsay-production.up.railway.app)** · [How it works](#how-it-works) · [Evaluation](#evaluation)

<p align="center">
  <img src="docs/screenshot.png" alt="Hearsay checking a paragraph" width="600">
</p>

## Motivation

LLMs can hallucinate, stating false information with full confidence. I wanted a system that grounds every verdict in a real source and abstains when the evidence isn't there, instead of guessing.

Hearsay can be used directly, or as a verification layer on top of another AI system. It includes an MCP server, so AI assistants like Claude can call it as a tool.

## How it works

1. **Claim extraction.** An LLM (gpt-oss-120b on Groq) splits the input text into single, checkable claims.
2. **Retrieval.** Each claim is searched in a Wikipedia index in Qdrant using hybrid search (dense embeddings for meaning, BM25 for keywords).
3. **Verification.** A judge LLM (Gemini) labels the claim based on the retrieved passages, and must quote the sentences it relied on.
4. **Live search fallback.** If the judge returns Not enough evidence, Hearsay searches live Wikipedia and runs the judge again. The index keeps most checks fast and cheap, and the live search covers what the index is missing.
5. **Quote verification.** Before results are shown, every quote is checked in code against the source passage. The LLM does not decide this. If none of the quotes can be verified, the verdict is downgraded to Not enough evidence.

In evaluation, 98.6% of the quotes returned by the judge were found in the source text.

## Using the demo

- The demo allows 5 checks per hour. A single check can include a full paragraph with several claims.
- It runs on free-tier hosting, so the first request after a period of inactivity can take a few seconds.
- Try a claim you've always believed but never verified. Mine was that goldfish have a three-second memory. They don't.

## Evaluation

I tested Hearsay on the [FEVER](https://fever.ai/dataset/fever.html) dataset, which uses the same three labels.

| What | Result |
|---|---|
| Retrieval: correct Wikipedia page in the top 5 (1,624 claims) | 97% |
| Verdict accuracy against FEVER's labels (122 claims) | 65.6% |
| Verdict accuracy after reviewing every mistake by hand | 85.2% |
| Quotes found in the source text | 98.6% |

I went through all 42 mistakes by hand. 24 of them were FEVER labels that were wrong or out of date (for example, claims about people who have since changed roles), 11 were real Hearsay errors, and 7 were the judge reading more into the evidence than it says. The full analysis is in [`eval/analysis.ipynb`](eval/analysis.ipynb). 

## Engineering notes

- **Out of memory.** In a local test with the free tier's 512 MB limit, the container was killed during live search. Embedding 40 passages in one batch added about 110 MB. Batches of 2 brought that down to about 20 MB.
- **Cold start.** After sleeping, the server took 34 seconds to start, because it loaded everything, including the models, before it could accept requests. Loading the models in the background after startup brought it down to about 3 seconds.
- **Tracing.** Langfuse traces showed that the judge model takes about 84% of each check (26 of 31 seconds), while search and claim extraction take under a second each. Since a check takes around 30 seconds, the API returns a check ID straight away and the page shows each claim's result as it's ready.

## Limitations and next steps

- **Wikipedia only, in English.** The same pipeline could check against other trusted sources.
- **Retrieval can miss the right article**, so some claims come back Not enough evidence even when Wikipedia covers them. Next step: better live-search queries and fetching more than two pages.
- **Verdicts can vary between runs.** In a second evaluation run, 11 of 122 labels changed. Next step: run the judge more than once and take the majority verdict.

## Running it locally

<details>
<summary>Setup</summary>

Requires Python 3.11, a Postgres database, a Qdrant Cloud cluster, and free API keys for Groq and Gemini.

```bash
git clone https://github.com/hala-sdev/hearsay.git
cd hearsay
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m nltk.downloader punkt_tab
cp .env.example .env        # fill in your keys
alembic upgrade head
python scripts/setup_checkpoints.py
```

Set `LANGFUSE_TRACING_ENABLED=false` in `.env` if you don't use Langfuse.

Build the Wikipedia index. This embeds the 10,031 articles listed in `data/titles.json` into Qdrant. It takes a while, and if it stops, it picks up where it left off:

```bash
python -m scripts.build_index
```

Then start the server and open http://localhost:8000:

```bash
uvicorn hearsay.api.main:app --reload
```

</details>

<details>
<summary>Running the tests</summary>

The tests use their own Postgres database on port 5433:

```bash
docker run -d -p 5433:5432 -e POSTGRES_PASSWORD=test -e POSTGRES_DB=hearsay_test postgres:17
pip install -r requirements-dev.txt
DATABASE_URL="postgresql://postgres:test@localhost:5433/hearsay_test?sslmode=disable" alembic upgrade head
pytest
```

Any placeholder values work for the API keys in `.env`. The tests don't call the real APIs. GitHub Actions runs the same tests on every push.

</details>

<details>
<summary>Using Hearsay from Claude (MCP)</summary>

The MCP server in `mcp_server/` exposes one tool, `check_claims`, which calls the live API. It has its own small environment:

```bash
cd mcp_server
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Add this to your Claude Desktop config, then restart Claude Desktop:

```json
{
  "mcpServers": {
    "hearsay": {
      "command": "/path/to/hearsay/mcp_server/.venv/bin/python",
      "args": ["/path/to/hearsay/mcp_server/server.py"]
    }
  }
}
```

On Windows, the command path is `C:\\path\\to\\hearsay\\mcp_server\\.venv\\Scripts\\python.exe`.

</details>

## License

MIT
