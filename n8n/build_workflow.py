"""Ghép mã trong src/ thành file workflow n8n để nhập (import).

Chạy lại sau khi sửa src/*.js:  python n8n/build_workflow.py
"""

import json
from pathlib import Path

HERE = Path(__file__).parent
read = lambda name: (HERE / "src" / name).read_text(encoding="utf-8")

nodes = [
    {
        "id": "a1f0c6c2-0001-4a5e-9d10-000000000001",
        "name": "Chạy thử bằng tay",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [0, 0],
        "parameters": {},
    },
    {
        "id": "a1f0c6c2-0002-4a5e-9d10-000000000002",
        "name": "Webhook nhận sản phẩm",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [0, 200],
        "webhookId": "5d1f3a52-7c4b-4c1e-9a7e-6b2f0e3c9a11",
        "parameters": {
            "httpMethod": "POST",
            "path": "marketing-content",
            "responseMode": "lastNode",
            "options": {},
        },
    },
    {
        "id": "a1f0c6c2-0003-4a5e-9d10-000000000003",
        "name": "Chuẩn bị yêu cầu Claude",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [260, 100],
        "parameters": {"jsCode": read("build_request.js")},
    },
    {
        "id": "a1f0c6c2-0004-4a5e-9d10-000000000004",
        "name": "Gọi Claude API",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [520, 100],
        "parameters": {
            "method": "POST",
            "url": "https://api.anthropic.com/v1/messages",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpHeaderAuth",
            "sendHeaders": True,
            "headerParameters": {
                "parameters": [
                    {"name": "anthropic-version", "value": "2026-10-21"},
                    {"name": "anthropic-beta", "value": "server-side-fallback-2026-07-01"},
                ]
            },
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.request) }}",
            "options": {"timeout": 300000},
        },
    },
    {
        "id": "a1f0c6c2-0005-4a5e-9d10-000000000005",
        "name": "Đọc kết quả",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [780, 100],
        "parameters": {"jsCode": read("parse_response.js")},
    },
]

connections = {
    "Chạy thử bằng tay": {"main": [[{"node": "Chuẩn bị yêu cầu Claude", "type": "main", "index": 0}]]},
    "Webhook nhận sản phẩm": {"main": [[{"node": "Chuẩn bị yêu cầu Claude", "type": "main", "index": 0}]]},
    "Chuẩn bị yêu cầu Claude": {"main": [[{"node": "Gọi Claude API", "type": "main", "index": 0}]]},
    "Gọi Claude API": {"main": [[{"node": "Đọc kết quả", "type": "main", "index": 0}]]},
}

workflow = {
    "name": "Marketing: tạo nội dung Facebook, YouTube, Zalo bằng Claude",
    "nodes": nodes,
    "connections": connections,
    "settings": {"executionOrder": "v1"},
    "pinData": {},
}

out = HERE / "marketing-content.json"
out.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Đã ghi {out}")
