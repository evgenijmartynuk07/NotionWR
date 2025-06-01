from flask import Flask, render_template_string, request, jsonify
import requests, datetime, calendar

app = Flask(__name__)

NOTION_TOKEN = "ntn_U53315387196pUMxngXz32HUuxMknO5xPowO2AH5g0ia8P"
DATABASE_ID = "1d813dc8d31f80379870c744821bf2f8"
DATABASE_TABLE_ID = "1a013dc8d31f80bda5fef70d4bb1f070"

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
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>Stats</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
    <style>
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            background: linear-gradient(0deg,rgba(2, 0, 36, 1) 0%, rgba(9, 9, 121, 1) 20%, rgba(0, 212, 255, 1) 100%);
            font-family: 'Poppins', sans-serif;
            color: white;
            box-sizing: border-box;
        }

        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: flex-start;
            gap: 40px;
            padding: 40px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .form-container {
            background-color: rgba(45, 26, 198, 0.4);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            flex: 1 1 450px;
            max-width: 600px;
            min-width: 420px;
            color: #333;
        }

        form {
            background: white;
            padding: 20px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        form label {
            font-weight: 600;
            color: #222;
        }

        form h3 {
            text-align: center;
            color: #2196f3;
            margin-bottom: 10px;
        }

        input, select, textarea {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            width: 100%;
            box-sizing: border-box;
        }

        input[type="checkbox"] {
            width: auto;
            transform: scale(1.5);
            accent-color: green;
            cursor: pointer;
        }

        textarea {
            resize: none;
            overflow: hidden;
            min-height: 40px;
        }

        input[type="submit"] {
            background-color: #03a9f4;
            color: white;
            border: none;
            padding: 12px;
            font-size: 16px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.3s;
        }

        input[type="submit"]:hover {
            background-color: #0288d1;
        }

        .charts {
            display: flex;
            flex-direction: row;   /* ← тепер горизонтально */
            gap: 50px;             /* відстань між кружечками */
            align-items: flex-start; 
            justify-content: center;
            flex-wrap: wrap;       /* щоб на малих екранах падало вниз */
            flex: 1 1 200px;
        }

        .circle-container {
            position: relative;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            overflow: visible;
            box-shadow: 0 10px 20px rgba(0,0,0,0.4); /* тінь навколо */
            transition: transform 0.3s ease;
        }

        .circle-container:hover {
            transform: scale(1.05);
        }

        .circle {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: conic-gradient(
                #4caf50 0% var(--percent),
                #f44336 var(--percent) 100%
            );
            position: relative;
            mask: radial-gradient(circle at center, transparent 35%, black 36%);
            -webkit-mask: radial-gradient(circle at center, transparent 35%, black 36%);
        }

        .circle.rr {
            background: radial-gradient(circle at center, #2196f3, #1976d2);
            mask: none;
            -webkit-mask: none;
        }

        .text-center {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-weight: 600;
            font-size: 26px;
            pointer-events: none;
            text-align: center;
            text-shadow: 0 2px 5px rgba(0,0,0,0.5);
            z-index: 2;
        }

        .label {
            margin-top: 12px;
            text-align: center;
            color: white;
            font-size: 16px;
            line-height: 1.4;
            font-family: 'Poppins', sans-serif;
            text-shadow: 0 2px 4px rgba(0,0,0,0.7);
        }

        form .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .field {
            display: flex;
            flex-direction: column;
        }

        .field.checkbox-field {
            flex-direction: row;
            align-items: center;
            gap: 12px;
        }
        
        #stats-box {
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 20px;
            border-radius: 10px;
            max-width: 600px;
            width: 100%;
            margin-top: 30px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.3);
            backdrop-filter: blur(5px);
            text-align: left;
        }
        .stats-wrapper {
            display: flex;
            justify-content: center;
            width: 100%;
        }

        @media (max-width: 768px) {
            .circle-container {
                width: 160px;
                height: 160px;
            }

            .text-center {
                font-size: 20px;
            }

            .label {
                font-size: 14px;
            }

            .charts {
                gap: 40px;
            }
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Ліва колонка — форма -->
        <div class="form-container">
            <form action="/add" method="post">
                <h3>Додати новий трейд</h3>

                <div class="grid">
                    <div class="field">
                        <label for="pair">Pair:</label>
                        <select name="pair" id="pair">
                            <option value="GER40">GER40</option>
                        </select>
                    </div>

                    <div class="field">
                        <label for="position">Position:</label>
                        <select name="position" id="position">
                            <option value="long">long</option>
                            <option value="short">short</option>
                        </select>
                    </div>

                    <div class="field">
                        <label>Trade Date:</label>
                        <input type="date" name="trade_date">
                    </div>

                    <div class="field">
                        <label>Risk (%):</label>
                        <input type="number" name="risk" step="0.01">
                    </div>

                    <div class="field">
                        <label>RR:</label>
                        <input type="number" name="rr" step="0.01">
                    </div>

                    <div class="field">
                        <label>Profit (%):</label>
                        <input type="number" name="profit" step="0.01">
                    </div>

                    <div class="field">
                        <label>Trade Notes:</label>
                        <textarea name="trade_notes" rows="1"></textarea>
                    </div>

                    <div class="field">
                        <label>Problem:</label>
                        <textarea name="problem" rows="1"></textarea>
                    </div>

                    <div class="field">
                        <label>Time Open:</label>
                        <input type="time" name="time_open">
                    </div>

                    <div class="field checkbox-field">
                        <label for="result">Result (positive?):</label>
                        <input type="checkbox" name="result" id="result">
                    </div>

                    <div class="field">
                        <label>Screen URL:</label>
                        <input type="url" name="screen">
                    </div>
                </div>

                <input type="submit" value="Надіслати">
            </form>
        </div>

        <!-- Права колонка — кружечки -->
        <div class="charts">
    <div class="circle-container" style="--percent: 52%;">
        <div class="circle"></div>
        <div class="text-center">{{ percent }}%</div>
        <div class="label">Загальний Win Rate<br>Кількість угод: {{ total }}</div>
    </div>

    <div class="circle-container rr-circle">
        <div class="circle rr"></div>
        <div class="text-center">{{ avg_rr }}</div>
        <div class="label">Середній RR</div>
    </div>

    <!-- Додано: блок статистики під кружечками -->
    <div class="stats-wrapper" style="width: 100%; justify-content: center; display: flex;">
    <div id="stats-box" style="position: relative; padding-right: 30px;">
        <div id="stats-content">Оновлення статистики...</div>

        <!-- Відсотки -->
        <div id="percent-display" style="
            position: absolute;
            top: 50%;
            right: 100px;
            transform: translateY(-50%);
            font-size: 24px;
            font-weight: bold;
            color: while;
        ">
            0%
        </div>
    </div>
</div>
</div>
</div>
</div>
        
    </div>




    <script>
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        });

        document.addEventListener('DOMContentLoaded', function() {
            const positionSelect = document.getElementById('position');

            positionSelect.addEventListener('change', function() {
                positionSelect.style.border = '2px solid initial';

                if (this.value === 'long') {
                    positionSelect.style.border = '2px solid green';
                } else if (this.value === 'short') {
                    positionSelect.style.border = '2px solid red';
                } else {
                    positionSelect.style.border = '1px solid #ccc';
                }
            });
        });
        
function getMonthName(monthNumber) {
    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    return monthNames[parseInt(monthNumber, 10) - 1] || '';
}

document.addEventListener('DOMContentLoaded', function () {
    fetch('/get_stats', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error(data.error);
            return;
        }

        const statsContent = document.getElementById('stats-content');
        statsContent.innerHTML = `
            <p><strong>Статистика ${getMonthName(data.month)}</strong></p>
            <p><strong>Всього угод:</strong> ${data.total_trades}</p>
            <p><strong>Take profit:</strong> ${data.wins}</p>
            <p><strong>Stop-loss:</strong> ${data.losses}</p>
        `;
        const percentDisplay = document.getElementById('percent-display');
        percentDisplay.textContent = `${data.percent}%`;
    })
    .catch(error => {
        console.error('Помилка при запиті:', error);
    });
});
    </script>  
</body>
</html>






""", percent=f"{percent:.0f}", total=total_trades, avg_rr=f"{avg_rr:.2f}")


@app.route('/add', methods=['POST'])
def add_trade():
    data = {
        "parent": {"database_id": DATABASE_TABLE_ID},
        "properties": {
            "Pair": { "select": { "name": request.form['pair'] } },
            "Position": { "select": { "name": request.form['position'] } },
            "Trade Date": {"date": {"start": request.form['trade_date']}},
            "Risk": {"number": float(request.form['risk']) / 100},
            "RR": {"number": float(request.form['rr'])},
            "Profit": {"number": float(request.form['profit']) / 100},
            "Trade notes": {"rich_text": [{"text": {"content": request.form['trade_notes']}}]},
            "problem": {"rich_text": [{"text": {"content": request.form['problem']}}]},
            "time open": {"rich_text": [{"text": {"content": request.form['time_open']}}]},
            "Result": {"checkbox": 'result' in request.form},
            "Screen": {
                "files": [
                    {
                        "type": "external",
                        "name": "screen",
                        "external": {
                            "url": request.form.get('screen', '')
                        }
                    }
                ]
            }
        }
    }
    
    datarr = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Positive": {"checkbox": 'result' in request.form},
            "RR": {"number": float(request.form['rr'])},
            "Date": {"date": {"start": request.form['trade_date']}}
            
        }
    }

    res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
    if res.status_code == 200 or res.status_code == 201:
        requests.post("https://api.notion.com/v1/pages", headers=headers, json=datarr)
        return "✅ Трейд успішно додано! <a href='/'>Назад</a>"
    else:
        return f"❌ Помилка: {res.status_code} — {res.text} <a href='/'>Назад</a>"
        
        
@app.route('/get_stats', methods=['POST'])
def get_stats():
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    start_date = f"{year}-{month:02d}-01"
    # отримуємо останній день місяця
    last_day = calendar.monthrange(year, month)[1]
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    query = {
        "filter": {
            "and": [
                { "property": "Trade Date", "date": { "on_or_after": start_date } },
                { "property": "Trade Date", "date": { "on_or_before": end_date } }
            ]
        }
    }

    notion_url = f"https://api.notion.com/v1/databases/{DATABASE_TABLE_ID}/query"
    response = requests.post(notion_url, headers=headers, json=query)
    data = response.json()

    if 'results' not in data:
        return jsonify({ "error": "Помилка при отриманні даних" })

    trades = data['results']
    total_trades = len(trades)
    wins = 0
    total_rr = 0
    percent = 0

    for trade in trades:
        props = trade['properties']
        if props['Result']['checkbox']:
            wins += 1
        total_rr += props['RR']['number']
        
        percent += trade['properties']['Profit']['number']

    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    avg_rr = (total_rr / wins) if wins > 0 else 0

    return jsonify({
        "month": month,
        "total_trades": total_trades,
        "wins": wins,
        "losses": total_trades - wins,
        "win_rate": round(win_rate, 2),
        "avg_rr": round(avg_rr, 2),
        "percent": round(percent * 100, 2)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
