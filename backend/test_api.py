import sys
import time
import requests

BASE_URL = "http://localhost:8000/api"


def run_tests():
    print("--- STARTING END-TO-END BACKEND API VALIDATION ---")

    # 1. Health check
    try:
        r = requests.get("http://localhost:8000/")
        print(f"[*] Health Check Response: {r.status_code} -> {r.json()}")
    except requests.exceptions.ConnectionError:
        print("[!] Error: Could not connect to FastAPI server. Please verify it is running on port 8000.")
        sys.exit(1)

    # Generate unique emails and phones for this run
    timestamp = int(time.time())
    victim_email = f"victim_{timestamp}@gmail.com"
    victim_phone = f"+919876{str(timestamp)[-6:]}"

    contact_email = f"contact_{timestamp}@gmail.com"
    contact_phone = f"+918876{str(timestamp)[-6:]}"

    # 2. Register Victim User
    victim_reg_payload = {
        "name": "John Doe (Victim)",
        "email": victim_email,
        "phone": victim_phone,
        "password": "securepassword123",
        "fcm_token": "fcm_victim_mock_token_123"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=victim_reg_payload)
    print(f"[*] Register Victim: {r.status_code}")
    assert r.status_code == 201, f"Failed registration: {r.text}"

    # 3. Register Emergency Contact User (so they have an FCM token to receive notifications)
    contact_reg_payload = {
        "name": "Jane Doe (Contact)",
        "email": contact_email,
        "phone": contact_phone,
        "password": "securepassword123",
        "fcm_token": "fcm_contact_mock_token_888"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=contact_reg_payload)
    print(f"[*] Register Contact User: {r.status_code}")
    assert r.status_code == 201

    # 4. Login Victim
    login_payload = {
        "email_or_phone": victim_email,
        "password": "securepassword123"
    }
    r = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    print(f"[*] Login Victim: {r.status_code}")
    assert r.status_code == 200
    tokens = r.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 5. Add Jane Doe as John Doe's Emergency Contact in the DB
    add_contact_payload = {
        "name": "Jane Doe (Wife)",
        "phone": contact_phone,
        "relationship": "Wife"
    }
    r = requests.post(f"{BASE_URL}/contacts", json=add_contact_payload, headers=headers)
    print(f"[*] Add Emergency Contact: {r.status_code} -> {r.json()}")
    assert r.status_code == 201

    # Verify Contacts list
    r = requests.get(f"{BASE_URL}/contacts", headers=headers)
    print(f"[*] Get Contacts: {r.status_code} -> {len(r.json())} item(s)")
    assert r.status_code == 200
    assert len(r.json()) == 1

    # 6. Report Accident (Runs AI + updates DB + pushes mock notifications to Jane's token)
    accident_payload = {
        "latitude": 12.971598,
        "longitude": 77.594566,
        "impact_force": 9.5,  # G-force -> should trigger critical/high severity
        "speed": 85.0,
        "orientation_change": 45.0
    }
    r = requests.post(f"{BASE_URL}/accident/report", json=accident_payload, headers=headers)
    print(f"[*] Report Accident: {r.status_code} -> {r.json()}")
    assert r.status_code == 201
    accident = r.json()
    accident_id = accident["id"]
    assert accident["severity"] == "critical"
    assert accident["risk_score"] > 70

    # Fetch Accident Detail
    r = requests.get(f"{BASE_URL}/accident/{accident_id}", headers=headers)
    print(f"[*] Get Accident Details: {r.status_code}")
    assert r.status_code == 200

    # 7. Query AI Severity prediction manually
    ai_payload = {
        "impact_force": 3.0,
        "speed": 25.0,
        "orientation_change": 15.0,
        "response_delay": 5.0
    }
    r = requests.post(f"{BASE_URL}/ai/severity", json=ai_payload, headers=headers)
    print(f"[*] AI Prediction (Manual): {r.status_code} -> {r.json()}")
    assert r.status_code == 200
    assert "severity" in r.json()
    assert "score" in r.json()

    # 8. Hospital Recommendation
    # Test best hospital recommendation
    r = requests.get(f"{BASE_URL}/best-hospital?latitude=12.971598&longitude=77.594566", headers=headers)
    print(f"[*] Get Best Hospital: {r.status_code} -> {r.json()['hospital']['name']}")
    assert r.status_code == 200

    # Test nearby hospitals
    r = requests.get(f"{BASE_URL}/hospitals/nearby?latitude=12.971598&longitude=77.594566", headers=headers)
    print(f"[*] Get Nearby Hospitals: {r.status_code} -> {len(r.json())} hospitals found")
    assert r.status_code == 200
    assert len(r.json()) > 0

    # 9. Update Live Location (Saves to SQL, updates Redis cache, publishes to channel)
    loc_payload = {
        "latitude": 12.972000,
        "longitude": 77.595000
    }
    r = requests.post(f"{BASE_URL}/location/update", json=loc_payload, headers=headers)
    print(f"[*] Update Live Location: {r.status_code} -> {r.json()}")
    assert r.status_code == 200

    # Get Live Location for User
    r = requests.get(f"{BASE_URL}/location/{victim_reg_payload['fcm_token'] if False else r.json()['user_id']}", headers=headers)
    print(f"[*] Get User Location: {r.status_code} -> {r.json()}")
    assert r.status_code == 200
    assert r.json()["latitude"] == 12.972000

    # 10. SOS System
    sos_payload = {
        "accident_id": accident_id
    }
    r = requests.post(f"{BASE_URL}/sos", json=sos_payload, headers=headers)
    print(f"[*] Activate manual SOS: {r.status_code} -> {r.json()}")
    assert r.status_code == 201

    # Check Active SOS Requests
    r = requests.get(f"{BASE_URL}/sos/active", headers=headers)
    print(f"[*] Get Active SOS Alerts: {r.status_code} -> {len(r.json())} active")
    assert r.status_code == 200
    assert len(r.json()) > 0

    # 11. Police / Authority Alerts
    authority_payload = {
        "accident_id": accident_id,
        "authority_type": "Police"
    }
    r = requests.post(f"{BASE_URL}/authority-alert", json=authority_payload, headers=headers)
    print(f"[*] Dispatch Authority Alert (Police): {r.status_code} -> {r.json()}")
    assert r.status_code == 201

    # 12. Volunteers Matching
    vol_reg_payload = {
        "name": "Sam Rescuer",
        "phone": f"+919000{str(timestamp)[-6:]}",
        "latitude": 12.972500,  # Near John Doe
        "longitude": 77.595500,
        "training_level": "EMT",
        "is_available": True
    }
    r = requests.post(f"{BASE_URL}/volunteers/register", json=vol_reg_payload, headers=headers)
    print(f"[*] Register Volunteer: {r.status_code} -> {r.json()}")
    assert r.status_code == 201

    r = requests.get(f"{BASE_URL}/volunteers/nearby?latitude=12.971598&longitude=77.594566", headers=headers)
    print(f"[*] Get Nearby Volunteers: {r.status_code} -> {len(r.json())} found")
    assert r.status_code == 200
    assert len(r.json()) > 0

    # 13. Ambulance dispatch & ETA
    amb_reg_payload = {
        "name": "Ambulance #4",
        "license_plate": f"KA-01-EM-{str(timestamp)[-4:]}",
        "latitude": 12.981000,
        "longitude": 77.601000,
        "status": "available"
    }
    r = requests.post(f"{BASE_URL}/ambulances/register", json=amb_reg_payload, headers=headers)
    print(f"[*] Register Ambulance: {r.status_code} -> {r.json()}")
    assert r.status_code == 201
    amb_id = r.json()["id"]

    # Dispatch ambulance
    dispatch_payload = {
        "ambulance_id": amb_id,
        "accident_id": accident_id
    }
    r = requests.post(f"{BASE_URL}/ambulances/dispatch", json=dispatch_payload, headers=headers)
    print(f"[*] Dispatch Ambulance: {r.status_code} -> {r.json()}")
    assert r.status_code == 200

    # Get ETA
    r = requests.get(f"{BASE_URL}/ambulances/eta/{accident_id}", headers=headers)
    print(f"[*] Get Ambulance ETA: {r.status_code} -> {r.json()}")
    assert r.status_code == 200

    # 14. First Aid AI Prompts
    fa_payload = {"query": "victim is bleeding severely"}
    r = requests.post(f"{BASE_URL}/ai/first-aid", json=fa_payload, headers=headers)
    print(f"[*] AI First Aid: {r.status_code} -> {r.json()['title']}")
    assert r.status_code == 200
    assert r.json()["found"] is True

    # 15. Government Dashboard Analytics
    r = requests.get(f"{BASE_URL}/gov/dashboard", headers=headers)
    print(f"[*] Get Gov Dashboard Stats: {r.status_code} -> {r.json()['active_incidents']} active incidents")
    assert r.status_code == 200

    r = requests.get(f"{BASE_URL}/gov/heatmaps", headers=headers)
    print(f"[*] Get Heatmap Coordinates: {r.status_code} -> {len(r.json())} incidents mapped")
    assert r.status_code == 200

    print("--- ALL END-TO-END VALIDATIONS SUCCESSFUL ---")


if __name__ == "__main__":
    run_tests()
