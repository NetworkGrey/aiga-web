# AIGA Web — Flask Web Server

**AIGA (Artificial Intelligence Gaming Assistant)** is an AI-powered strategic advisor for Age of Empires Mobile, built by Network Grey and powered by Anthropic Claude.

This repository contains the Flask web server that serves the AIGA chat interface and March Analyser tool.

---

## Live URLs

| Endpoint | URL |
|---|---|
| Health check | https://aiga-web-production.up.railway.app/health |
| March Analyser | https://aiga-web-production.up.railway.app/ |
| AIGA Chat | https://aiga-web-production.up.railway.app/aiga |
| WordPress page | https://networkgrey.co.za/aiga-bot |

---

## Repository Structure

```
aiga-web/
├── static/
│   └── aiga_chat.html        # AIGA chat UI — served at /aiga
├── app.py                    # Flask server — all routes and logic
├── AIGA_March_Analyser.html  # March Analyser front end — served at /
├── Procfile                  # Railway config: web: python app.py
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python version: 3.12.8
└── README.md                 # This file
```

---

## Routes

| Route | Method | Description |
|---|---|---|
| `/health` | GET | Health check — returns `{"status": "ok"}` |
| `/` | GET | Serves March Analyser HTML |
| `/aiga` | GET | Serves AIGA chat UI |
| `/analyse` | POST | March Analyser API — accepts march data, returns JSON verdict |
| `/chat` | POST | AIGA chat API — accepts messages and file uploads, returns AI response |

---

## Tech Stack

| Component | Detail |
|---|---|
| Language | Python 3.12.8 |
| Framework | Flask + Flask-CORS |
| AI backend | Anthropic Claude (Haiku for March Analyser, Sonnet for chat) |
| File uploads | JPG, PNG, WEBP, PDF — base64 encoded, 5MB limit |
| Session management | In-memory, 30-minute expiry |
| Hosting | Railway.app (Hobby plan) |
| Deployment | Auto-deploy from `main` branch on push |

---

## API Reference

### POST `/chat`

Accepts a JSON body:

```json
{
  "message": "Your question here",
  "session_id": "optional-existing-session-id",
  "file_data": "base64-encoded-file-optional",
  "file_type": "image/jpeg",
  "file_name": "screenshot.jpg"
}
```

Returns:

```json
{
  "response": "AIGA's reply",
  "session_id": "session-id-to-reuse"
}
```

Supported file types: `image/jpeg`, `image/png`, `image/webp`, `application/pdf`

### POST `/analyse`

Accepts a JSON body:

```json
{
  "message": "March data as structured text"
}
```

Returns:

```json
{
  "result": "{\"marches\": [...], \"priorities\": [...]}"
}
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key — set in Railway environment |
| `PORT` | No | Port to run on (default 8080 — Railway sets this automatically) |

---

## Deployment

This repo deploys automatically to Railway on every push to `main`.

To deploy manually:
1. Push changes to `main` branch on GitHub
2. Railway detects the push and rebuilds automatically
3. Check deployment status at [railway.app](https://railway.app)

---

## Related Repositories

| Repo | Description |
|---|---|
| `NetworkGrey/aiga-bot` | Discord bot — Python/discord.py, Railway worker process |

---

## Roadmap

- [ ] Gmail OAuth login and user registration
- [ ] Free tier question limit (10 questions per day)
- [ ] Airtable conversation logging
- [ ] PayFast Commander tier payment gating
- [ ] reCAPTCHA v3 bot protection
- [ ] Knowledge base injection for web chat
- [ ] War Chest workbook upload (Commander tier)
- [ ] CORS restriction to WordPress domain

---

## Disclaimer

AIGA&#8482; is an independent fan advisory service created by Network Grey (Pty) Ltd. Not affiliated with, endorsed by, or associated with TiMi Studio Group, Level Infinite, Proxima Beta Pte. Limited, Microsoft Corporation, or Xbox Game Studios. Age of Empires and Age of Empires Mobile are trademarks of Microsoft Corporation. All game content and imagery are the intellectual property of their respective owners.

For players aged 18 and over.

---

*Built by Network Grey (Pty) Ltd | Powered by Anthropic Claude | Version 3.0*
