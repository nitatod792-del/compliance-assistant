#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import request

ARK_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL = os.getenv("ARK_MODEL", "doubao-seed-1-6-flash-250715")
API_KEY = os.getenv("ARK_API_KEY", "").strip()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_POST(self):
        if self.path != "/api/ai-review":
            self._send(404, {"error": "not_found"})
            return
        if not API_KEY:
            self._send(500, {"error": "missing_ark_api_key_env", "hint": "set ARK_API_KEY in server env"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw or "{}")
            text = str(payload.get("text", "")).strip()
            if not text:
                self._send(400, {"error": "missing_text"})
                return

            system_prompt = (
                "你是内容审核助手。仅输出JSON，不要解释。"
                "格式: {risk_level, decision, hit_points, reason, suggestion}。"
                "risk_level: P0/P1/P2/P3; decision: reject/restrict/revise/downgrade/pass"
            )
            user_prompt = "请审核以下文案并给出结构化结论:\n" + text

            ark_payload = {
                "model": MODEL,
                "temperature": 0.1,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            }
            req = request.Request(
                ARK_URL,
                data=json.dumps(ark_payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}",
                },
                method="POST",
            )
            with request.urlopen(req, timeout=120) as resp:
                ark_raw = resp.read().decode("utf-8")
            ark_data = json.loads(ark_raw)
            content = (((ark_data.get("choices") or [{}])[0]).get("message") or {}).get("content", "{}")
            try:
                ai = json.loads(content)
            except json.JSONDecodeError:
                ai = {"raw": content}
            self._send(200, {"ok": True, "ai": ai})
        except Exception as e:
            self._send(500, {"error": "ai_review_failed", "detail": str(e)})


def main():
    port = int(os.getenv("PORT", "8787"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[ok] compliance ai-review server on :{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
