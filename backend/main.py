"""
GreenFleet Commander — FastAPI Backend
Provides Claude AI-powered sustainability reports and EV recommendations.
Deploy to Vercel free tier.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="GreenFleet Commander API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.github.io",
        "https://*.geotab.com",
        "http://localhost:*",
        "http://127.0.0.1:*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FleetData(BaseModel):
    total_vehicles: int = 0
    total_co2_tonnes: float = 0
    total_distance_km: float = 0
    avg_ev_score: int = 0
    ev_ready_count: int = 0
    top_vehicles: list = []
    top_fuel_consumers: list = []


class SustainabilityReportRequest(BaseModel):
    fleet_data: FleetData
    geotab_session: dict | None = None


class EVRecommendationRequest(BaseModel):
    fleet_data: FleetData
    budget: float = 500000
    timeline_years: int = 5


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "GreenFleet Commander"}


@app.post("/api/sustainability-report")
async def generate_sustainability_report(req: SustainabilityReportRequest):
    """Generate a Claude-powered narrative sustainability report."""
    try:
        import anthropic
    except ImportError:
        raise HTTPException(500, "Anthropic SDK not installed")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(500, "ANTHROPIC_API_KEY not configured")

    fd = req.fleet_data
    prompt = f"""You are a fleet sustainability analyst. Generate a professional executive
sustainability report based on this fleet data:

Fleet Size: {fd.total_vehicles} vehicles
Total CO2 Emissions (30 days): {fd.total_co2_tonnes:.1f} tonnes
Total Distance: {fd.total_distance_km:,.0f} km
Average EV Readiness Score: {fd.avg_ev_score}/100
Vehicles EV-Ready (Score 75+): {fd.ev_ready_count}

Top EV-Ready Vehicles:
{chr(10).join(f"- {v.get('name','?')}: Score {v.get('score',0)}, Avg {v.get('avgDaily',0):.1f} km/day" for v in fd.top_vehicles[:5])}

Top Fuel Consumers:
{chr(10).join(f"- {v.get('name','?')}: {v.get('fuelL',0):.0f}L estimated" for v in fd.top_fuel_consumers[:5])}

Write a 3-section report:
1. Executive Summary (2-3 paragraphs)
2. Key Findings & Risks
3. Recommended Actions (prioritized list with estimated impact)

Be specific with numbers. Use a professional but accessible tone."""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "report": message.content[0].text,
        "model": "claude-sonnet-4-6",
        "fleet_summary": {
            "vehicles": fd.total_vehicles,
            "co2_tonnes": fd.total_co2_tonnes,
            "ev_ready": fd.ev_ready_count
        }
    }


@app.post("/api/ev-recommendation")
async def generate_ev_recommendation(req: EVRecommendationRequest):
    """Generate AI-powered EV transition recommendations with ROI analysis."""
    try:
        import anthropic
    except ImportError:
        raise HTTPException(500, "Anthropic SDK not installed")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(500, "ANTHROPIC_API_KEY not configured")

    fd = req.fleet_data
    prompt = f"""You are an EV fleet transition consultant. Create a detailed electrification
recommendation based on this fleet data:

Fleet: {fd.total_vehicles} vehicles, {fd.ev_ready_count} are EV-ready (score 75+)
Budget: ${req.budget:,.0f}
Timeline: {req.timeline_years} years
Current CO2: {fd.total_co2_tonnes:.1f} tonnes/month

Top EV Candidates:
{chr(10).join(f"- {v.get('name','?')}: Score {v.get('score',0)}, {v.get('avgDaily',0):.1f} km/day, ~${v.get('annualFuel',0):,.0f}/yr fuel" for v in fd.top_vehicles[:10])}

Provide:
1. Phase 1 (Year 1): Which vehicles to convert first and why
2. Phase 2-3 (Years 2-3): Scaling plan
3. Infrastructure needs (charging stations, grid capacity)
4. Financial analysis (ROI, payback period, TCO comparison)
5. Risk factors and mitigation

Be specific with vehicle names and numbers."""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "recommendation": message.content[0].text,
        "budget": req.budget,
        "timeline_years": req.timeline_years
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
