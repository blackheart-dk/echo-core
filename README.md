# 🌐 Personal Persona Sync (MCP)

A secure, private, local-first Model Context Protocol (MCP) server that grants LLMs (like Claude and Cursor) a continuous, self-updating digital identity memory engine—backed up entirely by your own private GitHub repository.

Unlike native AI memory features that store your personal life updates, health metrics, and habits on corporate servers, **Personal Persona Sync** ensures your data remains 100% decentralized, private, and under your absolute control.

---

## ✨ Features

- 🧠 **Autonomous Context Grounding:** Automatically reads your persona matrix at the start of a session to adapt the AI's tone, knowledge level, and behavioral guardrails.
- ✍️ **Passive Memory Stitching:** The AI listens to your chat conversation, extracts relevant updates (e.g., injuries, location changes, new skills), and pushes structured logs to GitHub completely in the background.
- 🔒 **Zero-Knowledge Privacy:** Your personal life data scales exclusively between your local AI client app and your private GitHub repo. No mid-tier databases, no third-party telemetry.
- ⚡ **Token-Efficient Schema:** Uses an opinionated, highly compressed JSON architecture designed to maximize LLM context window efficiency.

---

## 🛠️ Architecture Overview

```text
[ Local AI Client ] (Claude Desktop / Cursor)
         │
         ▼ (Standard Input/Output via JSON-RPC)
[ Local MCP Server ] (Python FastMCP Process)
         │
         ▼ (Encrypted HTTPS Payload via Personal Access Token)
[ Your GitHub Repository ] ──► `persona_profile.json`
```

---

## Quick start

### MacOS / Linux

curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

### Windows

powershell -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
