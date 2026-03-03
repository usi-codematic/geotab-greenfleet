# 🌿 GreenFleet Commander

**AI-powered fleet sustainability intelligence for MyGeotab**

GreenFleet Commander transforms raw fleet telematics into actionable sustainability insights. It scores every vehicle's EV readiness, tracks carbon emissions, simulates electrification scenarios with real financial projections, and answers natural language fleet questions — all from within MyGeotab.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Sustainability Dashboard** | Real-time CO2 emissions tracking with 30-day trend charts and fleet-wide KPIs |
| **EV Readiness Scoring** | Per-vehicle score (0–100) analyzing daily distance, idle time, trip patterns, predictability, and charging opportunity |
| **Electrification Simulator** | Interactive what-if tool: slide to electrify top-scored vehicles and see projected CO2 savings, fuel cost reduction, carbon credits, and 5-year TCO |
| **AI Assistant** | Natural language fleet queries — ask about fuel consumption, EV recommendations, safety incidents, or efficiency trends |
| **Eco-Driving Leaderboard** | Gamified driver rankings with badges (Eco Champion, Star Driver) based on exception events |
| **Fleet Map** | Live vehicle positions color-coded by EV readiness (Leaflet + OpenStreetMap) |
| **PDF Reports** | One-click sustainability report export with executive summary, rankings, and recommendations |
| **Automated Monitoring** | n8n workflows for speed alerts, idle monitoring, and weekly sustainability digests via Slack |

## 🚀 Quick Start

### 1. Create a Geotab Demo Account
Visit [my.geotab.com/registration.html](https://my.geotab.com/registration.html) and select **"Create a Demo Database"**. Verify your email.

### 2. Install the Add-In
1. Log into MyGeotab
2. Go to **Administration → System Settings → Add-Ins**
3. Paste the contents of [`addin/config.json`](addin/config.json)
4. Click **Save**, then refresh the page
5. Find **"GreenFleet Commander"** in the left sidebar under Add-Ins

### 3. Backend Setup (Optional — for AI-powered reports)
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env  # Fill in your credentials
python main.py
```

### 4. n8n Automation (Optional — for fleet monitoring)
```bash
cd n8n
docker compose up -d
```

## 🏗️ Architecture

```
MyGeotab Add-In (Browser)         Python Backend (Vercel)       n8n (Self-hosted)
   │                                   │                            │
   ├── Geotab API                      ├── Claude API               ├── Geotab API polling
   │   (Device, Trip, StatusData,      │   (narrative reports,      │   (every 15 min)
   │    LogRecord, ExceptionEvent)     │    EV recommendations)     │
   │                                   │                            ├── Slack/Discord alerts
   ├── AI Assistant                    └── Report generation        │
   │   (Ace API or local fallback)                                  └── Weekly sustainability
   │                                                                    digest
   ├── Chart.js (emissions, fuel)
   ├── Leaflet (fleet map)
   └── jsPDF (PDF export)
```

**Three deliverables:**
1. **MyGeotab Add-In** (primary) — Single HTML file hosted on GitHub Pages
2. **Python Backend** (AI layer) — FastAPI on Vercel for Claude-powered insights
3. **n8n Automation** (monitoring) — Self-hosted workflows for fleet alerts

## 🔧 Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | MyGeotab Add-In (single HTML file, vanilla JS/CSS) |
| **APIs** | Geotab API, Geotab Ace AI (with local fallback) |
| **Visualization** | Chart.js, Leaflet + OpenStreetMap, MarkerCluster |
| **Export** | jsPDF, DOMPurify |
| **Backend** | Python FastAPI, Claude API, Day.js |
| **Automation** | n8n (Docker Compose) |
| **Hosting** | GitHub Pages (Add-In), Vercel (Backend) |

## 🧠 EV Readiness Scoring Algorithm

Each vehicle receives a score from 0–100 based on five weighted factors:

| Factor | Weight | What It Measures |
|--------|--------|-----------------|
| Daily Distance | 30 pts | Avg daily km vs EV range (≤100km = full score) |
| Predictability | 20 pts | Low coefficient of variation in daily distances |
| Idle Time | 20 pts | Higher idle % = more EV benefit (no fuel wasted idling) |
| Charging Opportunity | 20 pts | Return-to-base ratio for overnight charging |
| Trip Compatibility | 10 pts | % of trips under 100km (within single-charge range) |

## 🔒 Technical Notes

- **CSS Isolation**: All styles use `#gfc-app` ID selectors with `!important` to prevent MyGeotab parent styles from overriding the Add-In layout. Styles are placed inside `<body>` because MyGeotab strips `<head>` content during DOM injection.
- **Security**: All dynamic DOM construction uses `createElement()`/`textContent` — no `innerHTML`. DOMPurify is included as an additional safety layer.
- **Geotab Compatibility**: File and namespace follow Geotab's Add-In requirements (no dashes in URLs, non-hyphenated namespace `geotab.addin.greenfleetcommander`).
- **Graceful Degradation**: When Geotab Ace AI is unavailable (e.g., demo databases), the AI Assistant generates local analytics from loaded fleet data.

## 🤖 AI Development

This project was built using AI-assisted "vibe coding" with Claude Code (Opus 4.6). See [PROMPTS.md](PROMPTS.md) for all prompts and the full development journey — from initial architecture through iterative debugging of MyGeotab CSS injection issues.

## 📄 License

MIT
