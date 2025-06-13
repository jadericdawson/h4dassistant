````markdown
# 🧠 Modern Gmail-Aware Chatbot

A full-stack example that combines:

| Layer | Tech | Purpose |
|-------|------|---------|
| **Data / SQL** | **MindsDB** running as an **MCP** server in Docker | Turns Gmail into a SQL-queriable table (`gmail_receipts.emails`) |
| **Memory** | **ChromaDB** (embedded) | Vector store for long-term conversation context |
| **AI** | **OpenAI GPT-4.1 Remote-MCP** | Generates SQL, interprets results, and answers open questions |
| **Backend** | Python + Flask + SSE | Streams “thinking” steps and final replies |
| **Frontend** | React (Vite/CRA) | Sleek dark-mode chat UI with live progress bubbles |
| **Tunnelling** | LocalXpose | Secure public URL for the MCP port so OpenAI can reach MindsDB |

---

## 1  Quick-start (60-second version)

```bash
# 1. pull repo & cd in
git clone https://github.com/yourname/mindsdb-chatbot.git
cd mindsdb-chatbot

# 2. copy & edit environment file
cp .env.example .env          # add your OpenAI key here
# → ensure MINDSDB_MCP_ACCESS_TOKEN=mcp-token

# 3. launch MindsDB (HTTP + MCP) in Docker
docker run --name mindsdb \
  -p 47334:47334 \
  -p 47337:47337 \
  -e MINDSDB_APIS=http,mcp \
  -e MINDSDB_MCP_ACCESS_TOKEN=mcp-token \
  -d mindsdb/mindsdb

# 4. verify MCP locally
curl -s -H "Authorization: Bearer mcp-token" \
     -H "Accept: text/event-stream" \
     http://127.0.0.1:47337/sse | head

# 5. expose port 47337 with LocalXpose  ➜ copy the https URL
loclx tunnel http --to 127.0.0.1:47337 --region us &
#   MINDSDB_MCP_URL="https://xxx.loclx.io/sse"  ← paste into .env

# 6. backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py   # runs on http://localhost:5000

# 7. frontend
cd modern-chatbot
npm install
npm start       # opens http://localhost:3000
```

Open the browser, say “my name is Jaderic Dawson” then “what is my name?” – the bot should remember.

## 2 Directory layout

```
├─ app.py                ← Flask + streaming SSE
├─ requirements.txt
├─ chroma_db/            ← persisted vector store
├─ .env.example
├─ docker/               ← optional compose files
└─ modern-chatbot/       ← React UI
   ├─ src/
   └─ package.json
```

## 3 Environment variables (.env)

| Key | Example | Description |
|-----|---------|-------------|
| OPENAI_API_KEY | sk-... | Remote-MCP & GPT-4.1 access |
| MINDSDB_MCP_ACCESS_TOKEN | mcp-token | Same token passed to Docker & HTTP header |
| MINDSDB_MCP_URL | https://xyz.loclx.io/sse | Public /sse endpoint (port 47337) |

## 4 MindsDB container recipes

### 4.1 Run once, keep forever

```bash
docker run --name mindsdb \
  -p 47334:47334 -p 47337:47337 \
  -e MINDSDB_APIS=http,mcp \
  -e MINDSDB_MCP_ACCESS_TOKEN=mcp-token \
  -v mindsdb_data:/root/mdb_storage \
  -d mindsdb/mindsdb
```

Restart later: `docker start mindsdb`  
Logs: `docker logs -f mindsdb`  
Remove: `docker rm mindsdb` (data stays in the volume)

### 4.2 Health checks

```bash
# Studio GUI (should be HTML)
curl -I http://127.0.0.1:47334

# MCP (must print 'event: endpoint')
curl -s -H "Authorization: Bearer mcp-token" -H "Accept: text/event-stream" \
     http://127.0.0.1:47337/sse | head
```

## 5 Backend endpoints

| Route | Method | Purpose |
|-------|--------|---------|
| /api/chat | POST JSON {message:"..."} | Streams thinking + final reply |
| /api/history | GET | Returns full stored conversation from Chroma |
| / | static | React build (production) |

## 6 Conversation memory

In-RAM window – last 6 messages kept in conversation_context.

Long-term – every turn persists to ChromaDB (`./chroma_db`).

Retrieval – top 3 semantic matches are prepended to the prompt each round.

To reset memory:

```bash
rm -rf chroma_db/*   # cold start
```

## 7 SQL generator prompt (Gmail)

See `app.py` – generates operator-rich Gmail search and wraps it in:

```sql
SELECT * FROM gmail_receipts.emails
WHERE query = '...'
ORDER BY date DESC LIMIT 1;
```

## 8 LocalXpose tips

One tunnel per port – expose 47337 for MCP, optionally 47334 for Studio.

Auto-restart tunnel in crontab:

```bash
@reboot /usr/bin/loclx tunnel http --to 127.0.0.1:47337 --region us &
```

If tunnel URL changes, update `.env` and restart `app.py`.

## 9 Troubleshooting

| Symptom | Fix |
|---------|-----|
| 424 Failed Dependency | MCP URL wrong or token missing. Curl `/sse` locally; retunnel to 47337. |
| Front-end shows thinking forever | Check Flask logs; usually router produced empty intent or OpenAI key invalid. |
| “container name already in use” | `docker start mindsdb` (don’t run again). |
| Can’t remember name | Ensure ChromaDB not deleted; verify retrieval code in `app.py`. |

## 10 License & credits

MIT. Built with ♥ by Jaderic Dawson and ChatGPT-o3.

Copy that into **`README.md`** at your repo root and push—new contributors can now set up the entire stack in minutes.
````
# H4D_Assistant
# H4D_Assistant
