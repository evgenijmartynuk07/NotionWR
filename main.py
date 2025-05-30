from flask import Flask, render_template_string
import requests

app = Flask(__name__)

NOTION_TOKEN = "ntn_U53315387196pUMxngXz32HUuxMknO5xPowO2AH5g0ia8P"
DATABASE_ID = "1d813dc8d31f80379870c744821bf2f8"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def query_database(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

def calculate_checked_percent(data, checkbox_field_name):
    total = 0
    checked_count = 0
    
    for page in data.get("results", []):
        properties = page.get("properties", {})
        checkbox_prop = properties.get(checkbox_field_name)
        
        if checkbox_prop and checkbox_prop.get("type") == "checkbox":
            total += 1
            if checkbox_prop.get("checkbox") is True:
                checked_count += 1
                
    if total == 0:
        return 0, 0

    return (checked_count / total) * 100, total

def calculate_average_rr(data, rr_field_name):
    values = []
    for page in data.get("results", []):
        properties = page.get("properties", {})
        rr_prop = properties.get(rr_field_name)
        
        if rr_prop and rr_prop.get("type") == "number":
            value = rr_prop.get("number")
            if value is not None:
                values.append(value)
    
    if not values:
        return 0
    return sum(values) / len(values)

@app.route('/')
def index():
    data = query_database(DATABASE_ID)
    percent, total_trades = calculate_checked_percent(data, "Positive")
    avg_rr = calculate_average_rr(data, "RR")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Stats</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            background: transparent;
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .wrapper {
            display: flex;
            flex-direction: row;
            justify-content: center;
            align-items: center;
            gap: 60px;
        }
        .circle-container {
            position: relative;
            width: 200px;
            height: 200px;
        }
        .circle {
            width: 200px;
            height: 200px;
            border-radius: 50%;
        }
        .circle.winrate {
            background: conic-gradient(
                #4caf50 0% {{ percent }}%,
                #f44336 {{ percent }}% 100%
            );
            mask: radial-gradient(circle at center, transparent 35%, black 36%);
            -webkit-mask: radial-gradient(circle at center, transparent 35%, black 36%);
        }
        .circle.rr {
            background: #2196f3;
        }
        .text-center {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-weight: bold;
            font-size: 22px;
            pointer-events: none;
            text-align: center;
        }
        .label {
            margin-top: 8px;
            text-align: center;
            color: #fff;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="circle-container">
            <div class="circle winrate"></div>
            <div class="text-center">{{ percent }}%</div>
            <div class="label">Загальний Win Rate<br>Кількість угод: {{ total }}</div>
        </div>
        <div class="circle-container">
            <div class="circle rr"></div>
            <div class="text-center">{{ avg_rr }}</div>
            <div class="label">Середній RR</div>
        </div>
    </div>
</body>
</html>
""", percent=f"{percent:.0f}", total=total_trades, avg_rr=f"{avg_rr:.2f}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
