import requests
import os
import json
from datetime import datetime

# --- 1. CONFIGURATION ---
# We use 'os.environ.get' so it works on GitHub Actions, 
# but we add a default value for when you run it on your own computer.
JOLT_TOKEN = os.environ.get("JOLT_TOKEN", "__775aea000eec4f5d945926919036a2ae") 
COMPANY_ID = os.environ.get("COMPANY_ID", "0005875b260d4c6a9c965f4e5e59b569")
JOLT_URL = "https://api.jolt.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "jolt_auth_token": JOLT_TOKEN,
    "jolt_companyid": COMPANY_ID
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

# --- 2. THE HTML TEMPLATE ---
# This is the "Shell" of your website. Python will fill in the 'CONTENT_PLACEHOLDER'.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wendy's Location Dashboard</title>
    <style>
        :root { --wendys-red: #E22B32; --dark-gray: #333; --light-gray: #f4f4f4; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: var(--light-gray); margin: 0; padding: 20px; }
        
        /* Header Styling */
        .header { background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header h1 { margin: 0; color: var(--wendys-red); font-size: 1.5rem; }
        .timestamp { color: #888; font-size: 0.9rem; }
        
        /* Search Bar */
        .search-box { margin-bottom: 20px; }
        .search-box input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; box-sizing: border-box; }

        /* Grid Layout */
        .grid-container { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }
        
        /* Card Styling */
        .card { background: white; border-left: 5px solid var(--wendys-red); border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.2s; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .card-title { font-weight: bold; font-size: 1.1rem; margin-bottom: 5px; color: var(--dark-gray); }
        .card-id { color: #666; font-size: 0.85rem; background: #eee; padding: 2px 6px; border-radius: 4px; display: inline-block; }
    </style>
</head>
<body>

    <div class="header">
        <h1>Wendy's Locations</h1>
        <div class="timestamp">Last Updated: DATA_TIMESTAMP</div>
    </div>

    <div class="search-box">
        <input type="text" id="searchInput" onkeyup="filterGrid()" placeholder="Search locations...">
    </div>

    <div class="grid-container" id="locationGrid">
        CONTENT_PLACEHOLDER
    </div>

    <script>
        // Simple search filter script included directly in the HTML
        function filterGrid() {
            var input, filter, grid, cards, title, i, txtValue;
            input = document.getElementById('searchInput');
            filter = input.value.toUpperCase();
            grid = document.getElementById("locationGrid");
            cards = grid.getElementsByClassName('card');

            for (i = 0; i < cards.length; i++) {
                title = cards[i].getElementsByClassName("card-title")[0];
                if (title) {
                    txtValue = title.textContent || title.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        cards[i].style.display = "";
                    } else {
                        cards[i].style.display = "none";
                    }
                }
            }
        }
    </script>
</body>
</html>
"""

# --- 3. FETCH AND GENERATE ---
print("Fetching Jolt Data...")

try:
    response = requests.post(JOLT_URL, headers=HEADERS, json={'query': QUERY, 'variables': VARIABLES})
    
    if response.status_code != 200:
        print(f"Error: Server returned {response.status_code}")
        exit(1)

    data = response.json()
    
    if 'errors' in data:
        print("API Error:", data['errors'])
        exit(1)

    locations = data['data']['locations']
    locations.sort(key=lambda x: x['name']) # Sort A-Z by name
    
    print(f"Success! Found {len(locations)} locations.")

    # --- 4. BUILD THE HTML FRAGMENTS ---
    # We loop through the data and create a string of HTML for each location
    html_cards = ""
    for loc in locations:
        card_html = f"""
        <div class="card">
            <div class="card-title">{loc['name']}</div>
            <div class="card-id">ID: {loc['id']}</div>
        </div>
        """
        html_cards += card_html

    # --- 5. COMBINE AND SAVE ---
    # Get current time
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Replace placeholders in the template
    final_html = HTML_TEMPLATE.replace("CONTENT_PLACEHOLDER", html_cards)
    final_html = final_html.replace("DATA_TIMESTAMP", now_str)

    # Write to file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print("index.html has been generated successfully.")

except Exception as e:
    print(f"Script Error: {e}")
