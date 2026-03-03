# GreenFleet Commander

**AI-powered fleet sustainability intelligence for MyGeotab**

GreenFleet Commander transforms raw fleet data into actionable sustainability insights. It scores every vehicle's EV readiness, tracks carbon emissions, simulates electrification scenarios with real financial projections, and uses AI to answer natural language fleet questions — all from within MyGeotab.

## Features

- **Fleet Sustainability Dashboard** — Real-time carbon emissions tracking with trend analysis
- **EV Readiness Scoring** — Per-vehicle score (0-100) analyzing distance, idle time, trip patterns, and charging opportunity
- **Electrification Simulator** — Interactive "what-if" tool: slide to electrify vehicles and see projected CO2 reduction, fuel savings, and 5-year TCO
- **AI Assistant** — Ask Geotab Ace sustainability questions in natural language
- **Eco-Driving Leaderboard** — Gamified driver rankings with badges for sustainable driving behavior
- **Fleet Map** — Color-coded vehicle positions by EV readiness score
- **Sustainability Reports** — One-click PDF export of comprehensive fleet sustainability analysis
- **Automated Monitoring** — n8n workflows for speed alerts, idle monitoring, and weekly sustainability digests

## Quick Start

### 1. Create a Geotab Demo Account
Visit [my.geotab.com/registration.html](https://my.geotab.com/registration.html) and select **"Create a Demo Database"**. Verify your email.

### 2. Install the Add-In
1. Log into MyGeotab
2. Go to **Administration > System Settings > Add-Ins**
3. Paste the contents of `addin/config.json`
4. Click **Save**, then refresh the page
5. Find **"GreenFleet Commander"** in the left sidebar

### 3. Backend Setup (Optional — for AI reports)
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

## Architecture

```
MyGeotab Add-In (Browser)         Python Backend (Vercel)       n8n (Self-hosted)
   |                                   |                            |
   |-- Geotab API                      |-- Claude API               |-- Geotab API polling
   |-- Geotab Ace AI                   |-- Report generation        |-- Slack/Discord alerts
   |-- Chart.js + Leaflet + jsPDF      |                            |-- Weekly digests
```

## Technology Stack

- **Frontend**: MyGeotab Add-In (HTML/CSS/JavaScript)
- **APIs**: Geotab API (Device, Trip, StatusData, LogRecord, ExceptionEvent), Geotab Ace AI
- **Visualization**: Chart.js, Leaflet + OpenStreetMap
- **Export**: jsPDF
- **Backend**: Python FastAPI + Claude API
- **Automation**: n8n (Docker)
- **Hosting**: GitHub Pages (Add-In), Vercel (Backend)

## Demo Video

[Coming soon]

## Screenshots

[Coming soon]

## AI Development

This project was built using AI-assisted "vibe coding" with Claude Code (Opus 4.6). See [PROMPTS.md](PROMPTS.md) for all prompts used during development.

## License

MIT
