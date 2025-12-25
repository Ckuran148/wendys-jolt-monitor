import requests
import os

# --- CONFIG (Loads from GitHub Secrets) ---
JOLT_URL = "https://api.jolt.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "jolt_auth_token": os.environ.get("JOLT_TOKEN"),
    "jolt_companyid": os.environ.get("COMPANY_ID")
}
VARIABLES = {
    "mode": {
        "mode": "CONTENT_GROUP",
        "id": "Q29udGVudEdyb3VwOjAwMDU4NzViMjYwZDRjNmI2NDdhNjBjZDAxNDFlZDU2"
    }
}
QUERY = """
query GetLocations($mode: ModeInput!) {
    locations(mode: $mode) {
        id
        name
    }
}
"""

# --- HTML TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Wendy's Location Snapshot</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f0f2f5; }
        .card { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .timestamp { color: #666; font-size: 0.8em; margin-bottom: 20px; }
        .badge { background: #E22B32; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; }
    </style>
</head>
<body>
    <h1>Wendy's Locations</h1>
    <div class="timestamp">Last Updated: DATA_TIMESTAMP UTC</div>
    
    <div id="list">
        CONTENT_PLACEHOLDER
    </div>
</body>
</html>
"""

print("Fetching Jolt Data...")
try:
    response = requests.post(JOLT_URL, headers=HEADERS, json={'query': QUERY, 'variables': variables})
    data = response.json()
    
    if 'errors' in data:
        print("API Error:", data['errors'])
        exit(1)

    locations = data['data']['locations']
    locations.sort(key=lambda x: x['name']) # Sort A-Z
    
    # Generate HTML Content
    html_items = ""
    for loc in locations:
        html_items += f'<div class="card"><strong>{loc["name"]}</strong> <span class="badge">{loc["id"]}</span></div>\n'
    
    # Import datetime for timestamp
    from datetime import datetime
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    final_html = HTML_TEMPLATE.replace("CONTENT_PLACEHOLDER", html_items).replace("DATA_TIMESTAMP", now)

    # Save to file
    with open("index.html", "w") as f:
        f.write(final_html)
    
    print("Dashboard generated successfully.")

except Exception as e:
    print(f"Error: {e}")
    exit(1)
