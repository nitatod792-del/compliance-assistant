# AI Review Backend

This server proxies requests to Volcengine ARK, so API keys stay server-side.

## Run

```bash
export ARK_API_KEY='your_key_here'
export ARK_MODEL='doubao-seed-2-0-mini-260215'
# Optional: enable token protection for APIs
# export SCRIPT_CLUSTER_TOKEN='replace_with_random_token'
python3 server/app.py
```

Server listens on `http://localhost:8787` by default.

If your NAT mapping points to this server, you can open the script page directly from the mapped URL (for example `https://<your-domain>/script-cluster.html`) and it will call same-origin APIs.

## API

### 1) Compliance review

`POST /api/ai-review`

Body:

```json
{ "text": "待审核文案" }
```

### 2) Script chat and file persistence

`POST /api/script-chat`

Body:

```json
{
  "title": "雨夜追凶",
  "script_id": "rain-night-case",
  "system_prompt": "你是专业编剧助手...",
  "instruction": "输出分镜提纲",
  "script_text": "剧本文本..."
}
```

When `SCRIPT_CLUSTER_TOKEN` is set, clients must send header `X-API-Token`.

Response includes `reply` and `saved_file`.

Saved files are written to `server/data/<script_id>/<timestamp>-reply.md`.

### 3) Script groups (for management UI)

`GET /api/script-groups`

### 4) Script replies list (for management UI)

`GET /api/script-replies?script_id=<id>&limit=50`

Index data is tracked in `server/data/replies-index.jsonl`.
