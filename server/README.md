# AI Review Backend

This server proxies requests to Volcengine ARK, so API keys stay server-side.

## Run

```bash
export ARK_API_KEY='your_key_here'
export ARK_MODEL='doubao-seed-2-0-mini-260215'
python3 server/app.py
```

Server listens on `http://localhost:8787` by default.

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

Response includes `reply` and `saved_file`.

Saved files are written to `server/data/<script_id>/<timestamp>-reply.md`.
