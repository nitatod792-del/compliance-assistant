#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import request
from urllib.parse import parse_qs, urlparse

ARK_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL = os.getenv("ARK_MODEL", "doubao-seed-2-0-mini-260215")
API_KEY = os.getenv("ARK_API_KEY", "").strip()
ACCESS_TOKEN = os.getenv("SCRIPT_CLUSTER_TOKEN", "").strip()
DATA_DIR = Path(os.getenv("SCRIPT_CLUSTER_DATA_DIR", "server/data"))
INDEX_FILE = DATA_DIR / "replies-index.jsonl"
SCRIPT_PAGE = Path("docs/script-cluster.html")


def slugify(value: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fa5_-]+", "-", value.strip())
    safe = re.sub(r"-+", "-", safe).strip("-")
    return safe or "script"


def call_ark(messages: list, temperature: float = 0.2, json_output: bool = False) -> str:
    payload = {
        "model": MODEL,
        "temperature": temperature,
        "messages": messages,
    }
    if json_output:
        payload["response_format"] = {"type": "json_object"}

    req = request.Request(
        ARK_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=120) as resp:
        ark_raw = resp.read().decode("utf-8")
    ark_data = json.loads(ark_raw)
    content = (((ark_data.get("choices") or [{}])[0]).get("message") or {}).get("content", "")
    return content or ""


def save_script_reply(script_id: str, title: str, script_text: str, system_prompt: str, reply: str) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    folder = DATA_DIR / slugify(script_id or title)
    folder.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    ts = now.strftime("%Y%m%d-%H%M%S")
    out_file = folder / f"{ts}-reply.md"
    content = (
        f"# Script Reply\n\n"
        f"- time: {now.isoformat()}\n"
        f"- script_id: {script_id}\n"
        f"- title: {title}\n\n"
        f"## System Prompt\n\n{system_prompt}\n\n"
        f"## Script\n\n{script_text}\n\n"
        f"## Model Reply\n\n{reply}\n"
    )
    out_file.write_text(content, encoding="utf-8")
    row = {
        "time": now.isoformat(),
        "script_id": script_id,
        "title": title,
        "saved_file": str(out_file),
        "reply_preview": reply[:160],
    }
    with INDEX_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def list_groups() -> list:
    if not INDEX_FILE.exists():
        return []
    groups = {}
    for line in INDEX_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        sid = row.get("script_id", "")
        g = groups.get(sid, {"script_id": sid, "title": row.get("title", sid), "count": 0, "last_time": ""})
        g["count"] += 1
        g["last_time"] = max(g.get("last_time", ""), row.get("time", ""))
        groups[sid] = g
    return sorted(groups.values(), key=lambda x: x.get("last_time", ""), reverse=True)


def list_replies(script_id: str = "", limit: int = 100) -> list:
    if not INDEX_FILE.exists():
        return []
    rows = []
    for line in INDEX_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if script_id and row.get("script_id") != script_id:
            continue
        rows.append(row)
    rows.sort(key=lambda x: x.get("time", ""), reverse=True)
    return rows[:limit]


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

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/script-cluster", "/script-cluster.html"):
            if not SCRIPT_PAGE.exists():
                self.send_error(404, "script page not found")
                return
            body = SCRIPT_PAGE.read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/health":
            self._send(200, {"ok": True, "model": MODEL})
            return
        if parsed.path == "/api/script-groups":
            self._send(200, {"ok": True, "groups": list_groups()})
            return
        if parsed.path == "/api/script-replies":
            q = parse_qs(parsed.query or "")
            sid = (q.get("script_id") or [""])[0]
            try:
                limit = int((q.get("limit") or ["100"])[0])
            except ValueError:
                limit = 100
            self._send(200, {"ok": True, "replies": list_replies(script_id=sid, limit=max(1, min(limit, 500)))})
            return
        self.send_error(404, "not found")

    def do_POST(self):
        if not API_KEY:
            self._send(500, {"error": "missing_ark_api_key_env", "hint": "set ARK_API_KEY in server env"})
            return

        if ACCESS_TOKEN:
            req_token = (self.headers.get("X-API-Token") or "").strip()
            if req_token != ACCESS_TOKEN:
                self._send(401, {"error": "unauthorized", "hint": "missing or invalid X-API-Token"})
                return

        if self.path == "/api/ai-review":
            self.handle_ai_review()
            return
        if self.path == "/api/script-chat":
            self.handle_script_chat()
            return
        self._send(404, {"error": "not_found"})

    def _read_payload(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def handle_ai_review(self):
        try:
            payload = self._read_payload()
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
            content = call_ark(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                json_output=True,
            )
            try:
                ai = json.loads(content)
            except json.JSONDecodeError:
                ai = {"raw": content}
            self._send(200, {"ok": True, "ai": ai})
        except Exception as e:
            self._send(500, {"error": "ai_review_failed", "detail": str(e)})

    def handle_script_chat(self):
        try:
            payload = self._read_payload()
            title = str(payload.get("title", "")).strip() or "未命名剧本"
            script_id = str(payload.get("script_id", "")).strip() or slugify(title)
            script_text = str(payload.get("script_text", "")).strip()
            system_prompt = str(payload.get("system_prompt", "")).strip() or "你是专业编剧助手，请输出结构清晰、可执行的文本建议。"
            extra_instruction = str(payload.get("instruction", "")).strip()
            if not script_text:
                self._send(400, {"error": "missing_script_text"})
                return

            user_content = f"剧本标题：{title}\n\n剧本内容：\n{script_text}\n"
            if extra_instruction:
                user_content += f"\n补充要求：{extra_instruction}\n"

            reply = call_ark(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
            )
            row = save_script_reply(script_id, title, script_text, system_prompt, reply)
            self._send(
                200,
                {
                    "ok": True,
                    "script_id": script_id,
                    "title": title,
                    "reply": reply,
                    "saved_file": row.get("saved_file", ""),
                },
            )
        except Exception as e:
            self._send(500, {"error": "script_chat_failed", "detail": str(e)})


def main():
    port = int(os.getenv("PORT", "8787"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[ok] compliance server on :{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
