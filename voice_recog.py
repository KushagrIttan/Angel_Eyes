import speech_recognition as sr
import json
from datetime import datetime
import location

LOG_FILE = "cd_zn_final/file_log.json"
loc=location.device_location()

def load_log():
    """Loads the help log from the JSON file."""
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_log(log):
    """Saves the help log to the JSON file."""
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def log_help_alert():
    """Logs a help alert event."""
    log = load_log()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.append({"type": "help", "timestamp": timestamp,"location":loc})
    save_log(log)
    print(f"Help alert logged: {timestamp} location:{loc}")
    display_log()

def display_log():
    """Displays the help log in the console."""
    log = load_log()
    print("\n--- Help Alert Log ---")
    for entry in log:
        print(f"{entry['timestamp']}")
    print("----------------------\n")

def recognize_speech():
    """Continuously listens for speech and triggers an alert on 'help'."""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)

    while True:
        try:
            print("Listening...")
            with microphone as source:
                audio = recognizer.listen(source, timeout=5)  # Listen for 5 seconds

            print("Recognizing...")
            try:
                text = recognizer.recognize_google(audio).lower()
                print(f"You said: {text}")

                if "help" in text:
                    print("ALERT: 'Help' detected!")
                    log_help_alert()  # Log the alert
                    # Optionally, you might want to break or add a delay here
                    #time.sleep(10) # wait 10 seconds before listening again.

            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except sr.WaitTimeoutError:
                print("Listening timed out. Listening again...")

        except KeyboardInterrupt:
            print("Stopping...")
            break

if __name__ == "__main__":
    recognize_speech()