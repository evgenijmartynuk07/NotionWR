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
        return 0

    return (checked_count / total) * 100

@app.route('/')
def index():
    data = query_database(DATABASE_ID)
    percent = calculate_checked_percent(data, "Positive")
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Checked Percentage</title>
        <style>
            body {
                font-family: sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: transparent; /* прозорий фон для body */
            }
            .circle-wrap {
                width: 200px;
                height: 200px;
                background: conic-gradient(
                    #4caf50 0% {{ percent }}%, 
                    #f44336 {{ percent }}% 100%
                );
                border-radius: 50%;
                position: relative;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .circle-inner {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 140px;
                height: 140px;
                background: transparent; /* прозорий фон всередині круга */
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }
        </style>
    </head>
    <body>
        <div class="circle-wrap">
            <div class="circle-inner">{{ percent }}%</div>
        </div>
    </body>
    </html>
    """, percent=f"{percent:.0f}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
