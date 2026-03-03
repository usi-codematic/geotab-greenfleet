"""
Geotab API Client - Test and validate all API endpoints needed for GreenFleet Commander.
Run directly: python backend/services/geotab_client.py
"""
import os
import sys
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

load_dotenv()

GEOTAB_DATABASE = os.getenv("GEOTAB_DATABASE")
GEOTAB_USERNAME = os.getenv("GEOTAB_USERNAME")
GEOTAB_PASSWORD = os.getenv("GEOTAB_PASSWORD")
GEOTAB_SERVER = os.getenv("GEOTAB_SERVER", "my.geotab.com")

API_URL = f"https://{GEOTAB_SERVER}/apiv1"


def authenticate():
    """Authenticate with Geotab API and return credentials."""
    resp = requests.post(API_URL, json={
        "method": "Authenticate",
        "params": {
            "database": GEOTAB_DATABASE,
            "userName": GEOTAB_USERNAME,
            "password": GEOTAB_PASSWORD
        }
    })
    resp.raise_for_status()
    result = resp.json()
    if "result" not in result:
        raise Exception(f"Auth failed: {result.get('error', result)}")
    return result["result"]["credentials"]


def api_call(method, params, creds):
    """Make an authenticated Geotab API call."""
    payload = {
        "method": method,
        "params": {**params, "credentials": creds}
    }
    resp = requests.post(API_URL, json=payload)
    resp.raise_for_status()
    result = resp.json()
    if "error" in result:
        raise Exception(f"API error: {result['error']}")
    return result.get("result")


def api_multicall(calls, creds):
    """Make a batch of API calls in a single request."""
    payload = {
        "method": "ExecuteMultiCall",
        "params": {
            "calls": [{"method": m, "params": p} for m, p in calls],
            "credentials": creds
        }
    }
    resp = requests.post(API_URL, json=payload)
    resp.raise_for_status()
    result = resp.json()
    if "error" in result:
        raise Exception(f"MultiCall error: {result['error']}")
    return result.get("result")


def fetch_devices(creds):
    """Get all vehicles/devices."""
    return api_call("Get", {"typeName": "Device"}, creds)


def fetch_trips(creds, from_date=None, to_date=None):
    """Get trips for a date range."""
    if not from_date:
        from_date = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
    if not to_date:
        to_date = datetime.utcnow().isoformat() + "Z"
    return api_call("Get", {
        "typeName": "Trip",
        "search": {"fromDate": from_date, "toDate": to_date}
    }, creds)


def fetch_status_data(creds, device_id, diagnostic_id, from_date=None, to_date=None):
    """Get status data (e.g., fuel consumption) for a device."""
    if not from_date:
        from_date = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
    if not to_date:
        to_date = datetime.utcnow().isoformat() + "Z"
    return api_call("Get", {
        "typeName": "StatusData",
        "search": {
            "deviceSearch": {"id": device_id},
            "diagnosticSearch": {"id": diagnostic_id},
            "fromDate": from_date,
            "toDate": to_date
        }
    }, creds)


def fetch_log_records(creds, device_id, from_date=None, to_date=None):
    """Get GPS log records for a device."""
    if not from_date:
        from_date = (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z"
    if not to_date:
        to_date = datetime.utcnow().isoformat() + "Z"
    return api_call("Get", {
        "typeName": "LogRecord",
        "search": {
            "deviceSearch": {"id": device_id},
            "fromDate": from_date,
            "toDate": to_date
        }
    }, creds)


def fetch_exception_events(creds, from_date=None, to_date=None):
    """Get exception events (speeding, harsh braking, etc.)."""
    if not from_date:
        from_date = (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z"
    if not to_date:
        to_date = datetime.utcnow().isoformat() + "Z"
    return api_call("Get", {
        "typeName": "ExceptionEvent",
        "search": {"fromDate": from_date, "toDate": to_date}
    }, creds)


def test_ace_query(creds, prompt="What are the top 5 vehicles by distance traveled this week?"):
    """Test Geotab Ace AI with the three-step pattern."""
    print(f"\n--- Ace AI Query: '{prompt}' ---")

    # Step 1: Create chat
    print("  Step 1: Creating chat...")
    result = api_call("GetAceResults", {
        "serviceName": "dna-planet-orchestration",
        "functionName": "create-chat",
        "customerData": True,
        "functionParameters": {}
    }, creds)
    chat_id = result.get("data", {}).get("chat_id")
    if not chat_id:
        print(f"  Failed to create chat: {result}")
        return None
    print(f"  Chat ID: {chat_id}")

    # Step 2: Send prompt (wait 8s for rate limiting)
    print("  Step 2: Sending prompt (waiting 8s for rate limit)...")
    time.sleep(8)
    result = api_call("GetAceResults", {
        "serviceName": "dna-planet-orchestration",
        "functionName": "send-prompt",
        "customerData": True,
        "functionParameters": {
            "chat_id": chat_id,
            "prompt": prompt
        }
    }, creds)
    mg_id = result.get("data", {}).get("message_group_id")
    if not mg_id:
        print(f"  Failed to send prompt: {result}")
        return None
    print(f"  Message Group ID: {mg_id}")

    # Step 3: Poll for results
    print("  Step 3: Polling for results...")
    for attempt in range(24):  # Max 2 minutes
        time.sleep(5)
        result = api_call("GetAceResults", {
            "serviceName": "dna-planet-orchestration",
            "functionName": "get-message-group",
            "customerData": True,
            "functionParameters": {
                "chat_id": chat_id,
                "message_group_id": mg_id
            }
        }, creds)
        status = result.get("data", {}).get("status", "UNKNOWN")
        print(f"  Poll {attempt + 1}: {status}")
        if status == "DONE":
            return result
        elif status == "FAILED":
            print(f"  Ace query failed: {result}")
            return None

    print("  Ace query timed out")
    return None


def run_all_tests():
    """Run all API tests and report results."""
    print("=" * 60)
    print("GreenFleet Commander - Geotab API Test Suite")
    print("=" * 60)

    # Check env vars
    missing = []
    for var in ["GEOTAB_DATABASE", "GEOTAB_USERNAME", "GEOTAB_PASSWORD"]:
        if not os.getenv(var):
            missing.append(var)
    if missing:
        print(f"\nMissing environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your Geotab demo credentials.")
        sys.exit(1)

    print(f"\nDatabase: {GEOTAB_DATABASE}")
    print(f"Username: {GEOTAB_USERNAME}")
    print(f"Server:   {GEOTAB_SERVER}")

    # Test 1: Authentication
    print("\n--- Test 1: Authentication ---")
    try:
        creds = authenticate()
        print(f"  OK - Session ID: {creds.get('sessionId', 'N/A')[:20]}...")
    except Exception as e:
        print(f"  FAILED: {e}")
        sys.exit(1)

    # Test 2: Fetch Devices
    print("\n--- Test 2: Fetch Devices ---")
    try:
        devices = fetch_devices(creds)
        print(f"  OK - {len(devices)} devices found")
        if devices:
            d = devices[0]
            print(f"  Sample: {d.get('name', 'N/A')} (ID: {d.get('id', 'N/A')})")
    except Exception as e:
        print(f"  FAILED: {e}")
        devices = []

    # Test 3: Fetch Trips
    print("\n--- Test 3: Fetch Trips (last 7 days) ---")
    try:
        trips = fetch_trips(creds)
        print(f"  OK - {len(trips)} trips found")
        if trips:
            t = trips[0]
            print(f"  Sample: device={t.get('device', {}).get('id', 'N/A')}, "
                  f"distance={t.get('distance', 0):.1f}m, "
                  f"idling={t.get('idlingDuration', 'N/A')}")
    except Exception as e:
        print(f"  FAILED: {e}")

    # Test 4: Fetch StatusData (fuel)
    if devices:
        print("\n--- Test 4: Fetch StatusData (fuel) ---")
        try:
            device_id = devices[0]["id"]
            status = fetch_status_data(creds, device_id, "DiagnosticDeviceTotalFuelId")
            print(f"  OK - {len(status)} fuel readings for {devices[0].get('name', device_id)}")
            if status:
                s = status[0]
                print(f"  Sample: value={s.get('data', 'N/A')}, date={s.get('dateTime', 'N/A')}")
        except Exception as e:
            print(f"  FAILED (may be expected for demo DB): {e}")

    # Test 5: Fetch LogRecords (GPS)
    if devices:
        print("\n--- Test 5: Fetch LogRecords (GPS, last 24h) ---")
        try:
            device_id = devices[0]["id"]
            logs = fetch_log_records(creds, device_id)
            print(f"  OK - {len(logs)} GPS records for {devices[0].get('name', device_id)}")
            if logs:
                l = logs[0]
                print(f"  Sample: lat={l.get('latitude', 'N/A')}, "
                      f"lon={l.get('longitude', 'N/A')}, "
                      f"speed={l.get('speed', 'N/A')}")
        except Exception as e:
            print(f"  FAILED: {e}")

    # Test 6: Fetch ExceptionEvents
    print("\n--- Test 6: Fetch ExceptionEvents (last 7 days) ---")
    try:
        events = fetch_exception_events(creds)
        print(f"  OK - {len(events)} exception events found")
        if events:
            ev = events[0]
            print(f"  Sample: rule={ev.get('rule', {}).get('id', 'N/A')}, "
                  f"device={ev.get('device', {}).get('id', 'N/A')}, "
                  f"duration={ev.get('duration', 'N/A')}")
    except Exception as e:
        print(f"  FAILED: {e}")

    # Test 7: Ace AI (optional, takes 30-60s)
    print("\n--- Test 7: Ace AI Query ---")
    print("  (This takes 30-60 seconds...)")
    try:
        ace_result = test_ace_query(creds)
        if ace_result:
            data = ace_result.get("data", {})
            messages = data.get("messages", [])
            print(f"  OK - {len(messages)} messages in response")
            for msg in messages[:3]:
                content = msg.get("content", "")
                if isinstance(content, str):
                    print(f"  > {content[:200]}...")
        else:
            print("  Ace returned no results (may need Ace-enabled database)")
    except Exception as e:
        print(f"  FAILED: {e}")

    print("\n" + "=" * 60)
    print("Test suite complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
