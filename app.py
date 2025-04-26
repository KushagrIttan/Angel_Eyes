from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

# Mock database or detection logic (you can replace this with actual logic)
status = {
    "threatLevel": "None detected",
    "peopleCount": "Scanning inactive",
    "environment": "Unknown",
    "lastUpdated": "Never",
    "logs": []
}

def log_event(log_type, message):
    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    status["logs"].append({
        "time": timestamp,
        "type": log_type,
        "message": message
    })

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_detection', methods=['POST'])
def start_detection():
    status["threatLevel"] = "Low"
    status["peopleCount"] = "2 nearby"
    status["environment"] = "Urban"
    status["lastUpdated"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_event("info", "Detection started")
    return jsonify(status)

@app.route('/send_alert', methods=['POST'])
def send_alert():
    log_event("danger", "Alert sent to emergency contacts!")
    return jsonify({"message": "Alert sent successfully!"})

@app.route('/record_evidence', methods=['POST'])
def record_evidence():
    log_event("success", "Evidence recorded successfully")
    return jsonify({"message": "Recording complete!"})

@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    status["logs"].clear()
    return jsonify({"message": "Logs cleared."})

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True)
