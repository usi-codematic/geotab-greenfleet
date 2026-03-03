# AI Prompts Used in GreenFleet Commander Development

This document records all AI prompts and interactions used during the vibe coding development of GreenFleet Commander, as required by the Geotab Vibe Coding Competition.

## Tools Used
- **Claude Code (Claude Opus 4.6)** — Primary development assistant for architecture, code generation, debugging, and iteration
- **Geotab Ace** — In-app AI for natural language fleet queries (integrated into the Add-In)

---

## Phase 1: Research & Architecture

### Prompt 1: Project Vision — Sustainability Focus
> "I want to build something around fleet sustainability for this competition. There's a real gap in fleet management — companies have all this telematics data but no easy way to understand their environmental impact or plan an EV transition. Build a solution that helps fleet managers measure their carbon footprint, identify which vehicles are best suited for electrification, and track eco-driving behavior. Use the Geotab API docs and competition resources as reference. Use git for version control. Let me know when you need things from me (like geotab environment login credentials). Test everything."

**Result**: Claude researched all competition resources — the vibe guide, Add-In documentation, Ace AI guide, Data Connector guide, Zenith design system, and hackathon idea suggestions. Proposed the GreenFleet Commander concept aligning the sustainability focus with the competition's prize categories.

### Prompt 2: Architecture Decision
> "Go with full stack with n8n automation if it'd be free. Otherwise go with client side + python backend."

**Result**: Designed the full architecture — MyGeotab Add-In (single HTML file) + Python FastAPI backend on Vercel + n8n Docker automation workflows. Created a 14-step implementation plan.

### Prompt 3: Plan Approval
> "Save the plan to this folder then proceed and bypass permissions."

**Result**: Plan saved to PLAN.md. Full project scaffolded with directory structure, config files, .gitignore, LICENSE, and initial README.

---

## Phase 2: Implementation

### Prompt 4: Project Setup & Git Init
> (Continued from Prompt 3 — automatic execution)

**Result**: Initialized git repository, created complete directory structure (addin/, backend/, n8n/, demo/), all config files (.env.example, .gitignore, LICENSE, addin/config.json), Add-In SVG icon, and initial commit.

### Prompt 5: Geotab API Client
> (Automatic — part of implementation flow)

**Result**: Built `backend/services/geotab_client.py` with full API wrapper: authenticate, api_call, api_multicall, fetch_devices, fetch_trips, fetch_status_data, fetch_log_records, fetch_exception_events, test_ace_query. Includes runnable test suite.

### Prompt 6: Complete Add-In Implementation
> (Automatic — the entire greenfleet-commander.html was generated in one pass)

**Result**: Created ~1000-line single-file MyGeotab Add-In with:
- Zenith-styled CSS with `.gfc-` namespace prefix
- 6 tabs: Dashboard, Simulator, Leaderboard, AI Assistant, Map, Reports
- EV readiness scoring algorithm (5-factor, 0-100 scale)
- Chart.js emissions trend and fuel consumption charts
- Interactive electrification simulator with sliders and financial projections
- Geotab Ace AI integration (3-step: create-chat → send-prompt → poll results)
- Leaflet map with color-coded markers and clustering
- Eco-driving leaderboard with gamification badges
- jsPDF report generator with branded output
- All DOM construction uses safe methods (createElement/textContent) — no innerHTML

### Prompt 7: Security Fix
> (Triggered by pre-commit hook detecting innerHTML usage)

**Result**: Rewrote all dynamic DOM construction to use document.createElement() and textContent instead of innerHTML. Added DOMPurify CDN as additional safety layer for any HTML that must be rendered (Ace AI responses).

### Prompt 8: Python Backend
> (Automatic — continued implementation)

**Result**: Created FastAPI backend with:
- `POST /api/sustainability-report` — Claude-generated narrative report
- `POST /api/ev-recommendation` — AI-powered EV transition analysis
- `GET /api/health` — Health check
- Carbon calculation service with unit tests (7/7 passing)
- Vercel deployment configuration

### Prompt 9: n8n Workflows
> (Automatic — continued implementation)

**Result**: Created 3 n8n automation workflows:
- **Speed Alerts** — Every 15 min, detect excessive speeding, Slack notification
- **Idle Monitor** — Every hour, flag vehicles idle >30 min, Slack alert
- **Weekly Digest** — Monday 9 AM, aggregate week's emissions/distance/idle stats, Slack block kit message
- Docker Compose setup for self-hosted n8n

---

## Phase 3: Testing & Debugging

### Prompt 10: API Credential Testing
> "I have my credentials ready. Database name: 'vibe_database' but try 'demo_vibe_database' if that fails because that's showing in the page url."

**Result**: Authenticated successfully with `demo_vibe_database`. Full API test suite passed 7/7:
- 50 devices in fleet
- 3,620 trips (30 days)
- 1,280 exception events (7 days)
- Fuel diagnostic data available
- GPS log records available

### Prompt 11: Data Format Bug Discovery & Fix
> (Automatic — discovered during API data analysis)

**Result**: Found two critical bugs from analyzing real API responses:
1. **Distance already in km** — Add-In was dividing by 1000 unnecessarily (API returns km, not meters)
2. **Duration format is HH:MM:SS** — parseDuration() only handled ISO 8601 PT format, but Geotab returns "01:27:41" style

Fixed across the Add-In and all 3 n8n workflows. Added HH:MM:SS.fraction parsing with ISO 8601 fallback.

---

## Phase 4: MyGeotab Integration & Debugging

### Prompt 12: Identifying Tab Navigation Failure
> "The addin page just has all the contents on the same page without all the formatting (in a very basic setup). The tabs don't seem to be links anyway."

**Context**: After installing the Add-In in MyGeotab, I noticed the tabs weren't switching and all content was visible at once — stacked vertically without proper layout. This was the start of a multi-step debugging process to understand how MyGeotab renders Add-In HTML.

**Result**: Claude investigated and found that the Add-In registration name format was wrong (`geotab.addin.greenfleetCommander` should have matched the filename). Switched tab handlers from addEventListener to inline onclick for iframe robustness.

### Prompt 13: Visual Comparison — Standalone vs MyGeotab
> "The links work now but I'm still not satisfied with what I'm seeing. I've attached screenshots of the Geotab Add-In page versus the standalone page. See how different they look. Are they supposed to look that different? The Add-In page looks so much worse. Maps not even displaying and other things."

**Context**: I took side-by-side screenshots of the standalone page (which looked perfect) versus the MyGeotab version (broken layout, no grid, no cards, map missing) and sent them for comparison. This pushed the debugging deeper into CSS specificity issues.

**Result**: Claude discovered in the Geotab docs that Add-In URLs must not contain dashes, leading to a file rename from `greenfleet-commander.html` to `greenfleetcommander.html`. All CSS rules were rewritten with `#gfc-app` ID selectors and `!important` flags for maximum specificity against MyGeotab parent styles.

### Prompt 14: Persistent Styling Issues
> "Did all that. I'm able to view the standalone page now but the Geotab page is still the same."

**Context**: Even after the CSS specificity overhaul, the MyGeotab version was still unstyled. The standalone page looked perfect, so the CSS itself was correct — but something about how MyGeotab loaded it was stripping the styles.

**Result**: Root cause identified — MyGeotab strips `<head>` content when injecting Add-In HTML into the page DOM. The `<style>` tag was being discarded entirely. Fix: moved the entire `<style>` block from `<head>` into `<body>` inside the `#gfc-app` container. This is valid HTML5 and ensures styles survive MyGeotab's content extraction. After this fix, the Add-In rendered identically to standalone.

### Prompt 15: AI Assistant Error
> "When I ask any question to the AI assistant, I get this error: Error: Cannot read properties of undefined (reading 'chat_id')"

**Context**: While testing each tab in MyGeotab, I tried the AI Assistant and got a JavaScript error. The Geotab Ace API wasn't returning the expected response structure on the demo database.

**Result**: Added a smart fallback — when Ace API is unavailable, the AI Assistant generates analytics responses locally using the already-loaded fleet data. Covers EV recommendations, fuel consumption analysis, safety summaries, and efficiency trends, all using real vehicle data from the Geotab API.

---

## Phase 5: Demo & Submission

### Prompt 16: Demo Data Generation
> (Automatic — generated cached sample data for demo reliability)

**Result**: Created `demo/fallback-data/sample-fleet.json` with real API data (10 devices, 200 trips, 100 events) to ensure demo video recording works even if API is slow.

### Prompt 17: Demo Script
> "Help with demo assets"

**Result**: Created 3-minute video script (`demo/demo-script.md`) with:
- 5-act structure matching all major features
- Exact timing and narration text
- Setup checklist for recording
- Key talking points for each feature

---

## Vibe Coding Observations

### What Worked Well
- **Sustainability-first design**: Starting with a clear environmental mission (carbon tracking, EV transition planning) kept the project focused and meaningful
- **Visual debugging**: Comparing screenshots between standalone and MyGeotab versions was crucial for identifying CSS injection issues that wouldn't show up in unit tests
- **Persistent iteration**: The MyGeotab styling bug required 4 rounds of debugging (registration name → CSS specificity → head stripping → body injection) — each round built on insights from the previous attempt
- **API-first testing**: Testing real API responses before finalizing the Add-In caught data format assumptions early
- **Graceful degradation**: When the Ace AI API wasn't available on the demo database, adding a local analytics fallback kept the feature functional

### What I Learned
- MyGeotab injects Add-In HTML directly into the page DOM (not an iframe), so CSS isolation is critical
- Geotab Add-In URLs cannot contain dashes, and the JS namespace must not be hyphenated
- The `<head>` section is stripped during injection — all styles must be in `<body>`
- Demo databases may not support all API features (like Ace AI), so fallbacks are essential
- Side-by-side visual comparison is more effective than console debugging for layout issues

### AI Capabilities Demonstrated
- Architecture design spanning frontend, backend, and automation layers
- Full-stack implementation from a natural language description
- Automatic bug detection through data analysis
- Code generation following specific design system guidelines (Zenith)
- Integration of multiple external services (Geotab API, Ace AI, Chart.js, Leaflet, jsPDF, Claude API, n8n)
- Iterative debugging with root cause analysis across multiple hypothesis-test cycles
