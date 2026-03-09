# AI Review Backend

This server proxies AI review requests to Volcengine ARK, so API keys stay server-side.

## Run

```bash
export ARK_API_KEY='your_key_here'
export ARK_MODEL='doubao-seed-1-6-flash-250715'
python3 server/app.py
```

Server listens on `http://localhost:8787` by default.

## API

`POST /api/ai-review`

Body:

```json
{ "text": "待审核文案" }
```
