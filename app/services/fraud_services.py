from detetime import datetime, timedelta

ATEMPT_STORE = {}


def check_ip_velocity(ip_address):
    now = datetime.now()
    if ip_address in ATEMPT_STORE:
        attempts = ATEMPT_STORE[ip_address]
        # Remove attempts older than 1 hour
        attempts = [attempt for attempt in attempts if now - attempt < timedelta(hours=1)]
        ATEMPT_STORE[ip_address] = attempts
        if len(attempts) >= 5:  # Threshold for blocking
            return True
    else:
        ATEMPT_STORE[ip_address] = []
    return False


def check_device_reuse(device_id):
    now = datetime.now()
    if device_id in ATEMPT_STORE:
        attempts = ATEMPT_STORE[device_id]
        # Remove attempts older than 1 hour
        attempts = [attempt for attempt in attempts if now - attempt < timedelta(hours=1)]
        ATEMPT_STORE[device_id] = attempts
        if len(attempts) >= 5:  # Threshold for blocking
            return True
    else:
        ATEMPT_STORE[device_id] = []
    return False


def check_geo_risk(location):
    # Placeholder for geo risk check, e.g., using a third-party service
    high_risk_countries = ["CountryA", "CountryB"]
    return location in high_risk_countries


def calculate_fraud_score(ip_address, device_id, location):
    score = 0
    if ip_address and check_ip_velocity(ip_address):
        score += 50
    if device_id and check_device_reuse(device_id):
        score += 30
    if ip_address and check_geo_risk(location):
        score += 20
    return score


def create_fraud_event(user_id, ip_address, device_id, location):
    score = calculate_fraud_score(ip_address, device_id, location)
    event = {
        "user_id": user_id,
        "ip_address": ip_address,
        "device_id": device_id,
        "location": location,
        "score": score,
        "timestamp": datetime.now()
    }
    # Store or log the event as needed
    return event
