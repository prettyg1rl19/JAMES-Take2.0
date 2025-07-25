# List of imports that will help my code function properly
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import pyjokes
import json
import time
import psutil
import random
from dateutil import parser as date_parser

# Here we are setting the properties for JAMES's voice

engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Set British voice because my smart JAMES is British
for voice in voices:
    if "George" in voice.name: #George is Micorsoft's British voice
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 165)     # Slightly slower for clarity
engine.setProperty('volume', 1.0)   # Max volume

# Dramatic pause 
engine.say("Initializing systems.")
engine.runAndWait()
time.sleep(0.8)  # Pause for effect

# He says this when booting up
engine.say("Systems online, Miss.")
engine.runAndWait()

# This will be the declaratios for him saving my assignments
session_memory = []
assignment_due_dates = {}

# This will be the file where JAMES saves my assignments & the memory of the chat
ASSIGNMENT_FILE = "assignments.json"
MEMORY_FILE = "session_memory.json"

# Load session memory from file if it exists
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        session_memory = json.load(f)
else:
    session_memory = []

# Here we are creating JAMES's personality, heavily based off JARVIS from Iron Man
WITTY_RESPONSES = {
    # If you don't haave a watch, he can tell you the time
    'time': [
        "The time is currently {time}, Miss.",
        "My chronometer reads {time} precisely.",
        "The clocks indicate it's {time}."
    ],
    # If my boy has a database, he'll search stuff for you
    'search': [
        "Searching my databases for {query}.",
        "Compiling results for {query}.",
        "Accessing global records regarding {query}."
    ],
    # Prints an error message if JAMES cannot understand the user
    'error': [
        "My audio receptors seem to be malfunctioning momentarily.",
        "How peculiar - my interpretation circuits appear to be offline.",
        "I seem to be experiencing selective auditory perception."
    ],
    # My boy will respond with a witty lil joke
    'joke': [
        "Why don't scientists trust atoms? Because they make up everything.",
        "I was going to tell you a time travel joke, but you didn't like it yet.",
        "What do you call a fake noodle? An impasta."
    ],
    # He greets you based on the time of day
    'greeting': {
        'morning': ["Good morning, Miss. Systems operational.", "Morning, Miss. All systems nominal."],
        'afternoon': ["Good afternoon, Miss. How may I assist?", "Afternoon, Miss. Ready for your commands."],
        'evening': ["Good evening, Miss. Systems standing by.", "Evening, Miss. At your service."]
    },
    # And of course, the classy farewell from my AI
    'farewell': [
        "Shutting down systems. Do call if you require assistance.",
        "Powering down. Until next time, Miss.",
        "Deactivating primary systems. Goodbye."
    ]
}

# Here, JAMES will be allowed to speak for the first time!
def speak(text):
    print("JAMES:", text)
    engine.say(text)
    engine.runAndWait()

# This function will be used to save the chat to JAMES's memory
def save_session_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(session_memory, f)

def load_session_memory():
    global session_memory
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            session_memory = json.load(f)
    else:
        session_memory = []

# You can ask him about your current system status
def system_status():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    speak(f"System status: CPU at {cpu}%, Memory at {memory}%")

# Reminders
def set_reminder():
    speak("What should I remind you about?")
    reminder = listen()
    speak("When should I remind you?")
    time_str = listen()
    # Parse and schedule reminder

def get_witty_response(response_type, **kwargs):
    """Returns a context-appropriate witty response"""
    if response_type in WITTY_RESPONSES:
        choices = WITTY_RESPONSES[response_type]
        if isinstance(choices, dict):
            sub_type = kwargs.get('sub_type', '')
            if sub_type in choices:
                return random.choice(choices[sub_type])
        else:
            template = random.choice(choices)
            return template.format(**kwargs)
    return ""

# JAMES can't work without listening to you, so this function will listen to your commands
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            return command.lower()
        except sr.UnknownValueError:
            speak("I couldn't understand that, Miss.")
        except sr.WaitTimeoutError:
            speak("I didn't detect any audio input, Miss.")
        except sr.RequestError:
            speak("Speech recognition service is unavailable.")
    return ""

# Here, my boy will greet you based on the time of day
def greet():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        speak(get_witty_response('greeting', sub_type='morning') or "Good morning, Miss.")
    elif 12 <= hour < 18:
        speak(get_witty_response('greeting', sub_type='afternoon') or "Good afternoon, Miss.")
    else:
        speak(get_witty_response('greeting', sub_type='evening') or "Good evening, Miss.")
    speak("How may I be of service?")

#Here will be his code for the assignment handling
def parse_due_date(text):
    try:
        return date_parser.parse(text, fuzzy=True)
    except Exception:
        return None

    #The assignments will be added via voice
def add_assignment_via_voice():
    speak("What is the assignment name?")
    name = listen()
    speak("When is it due?")
    due_text = listen()
    due_date = parse_due_date(due_text)

    if due_date:
        assignment_due_dates[name] = {
            "due_date": due_date,
            "status": "not started"
        }
        "status": "not started"  # default
        save_assignments()  # Save the data to file
        speak(f"Assignment '{name}' due on {due_date.strftime('%A, %B %d')} has been saved, Miss.")
    else:
        speak("I couldn't understand the due date, Miss. Please try again later.")

def list_assignments_due_soon():
    today = datetime.date.today()
    upcoming = {
        name: data for name, data in assignment_due_dates.items()
        if 0 <= (data["due_date"].date() - today).days <= 7
    }
    if upcoming:
        for name, data in sorted(upcoming.items(), key=lambda x: x[1]["due_date"]):
            days_left = (data["due_date"].date() - today).days
            if days_left == 0:
                speak(f"The assignment '{name}' is due today.")
            elif days_left == 1:
                speak(f"The assignment '{name}' is due tomorrow.")
            else:
                speak(f"The assignment '{name}' is due in {days_left} days, on {data['due_date'].strftime('%A')}.")
    else:
        speak("You have no assignments due within the next 7 days, Miss.")

def save_assignments():
    try:
        with open(ASSIGNMENT_FILE, "w") as f:
            # Save in ISO format for easy date restoration
            serializable_data = {
                k: {
                    "due_date": v["due_date"].isoformat(),
                    "status": v["status"]
                }
                for k, v in assignment_due_dates.items()
            }
            json.dump(serializable_data, f)
    except Exception as e:
        print("Failed to save assignments:", e)

def delete_assignment_via_voice():
    speak("Which assignment should I delete, Miss?")
    name = listen()
    if name in assignment_due_dates:
        del assignment_due_dates[name]
        save_assignments()
        speak(f"Assignment '{name}' has been removed, Miss.")
    else:
        speak(f"I couldn’t find any assignment named '{name}', Miss.")

def load_assignments():
    global assignment_due_dates
    try:
        if os.path.exists(ASSIGNMENT_FILE):
            with open(ASSIGNMENT_FILE, "r") as f:
                data = json.load(f)
                assignment_due_dates = {
                    k: {
                        "due_date": date_parser.parse(v["due_date"]),
                        "status": v.get("status", "not started")
                    }
                    for k, v in data.items()
                }
    except Exception as e:
        print("Failed to load assignments:", e)
        assignment_due_dates = {}

def update_assignment_status_via_voice():
    speak("Which assignment would you like to update, Miss?")
    name = listen()

    if name in assignment_due_dates:
        speak("What is the new status? For example, completed, in progress, or not started.")
        new_status = listen()
        assignment_due_dates[name]["status"] = new_status
        save_assignments()
        speak(f"The status of '{name}' has been updated to '{new_status}', Miss.")
    else:
        speak(f"I couldn't find any assignment named '{name}', Miss.")

# Implemented CRUD for assignment handling
def respond(command):
    if not command:
        return

    session_memory.append(command)

    #CREATE: Add an assignment
    if "assignment" in command and any(word in command for word in ["add", "remember"]):
        add_assignment_via_voice()
        return

    # READ: List assignments due soon
    if "due soon" in command or "anything due" in command:
        list_assignments_due_soon()
        return

    # READ: List or show all assignments
    if "list assignments" in command or "show assignments" in command:
        if assignment_due_dates:
            speak("Here are your current assignments, Miss:")
            for name, data in assignment_due_dates.items():
                due = data["due_date"]
                status = data.get("status", "not started")
                speak(f"{name} is due on {due.strftime('%A, %B %d')} and is currently {status}.")
        else:
            speak("There are no assignments recorded yet, Miss.")
        return

    #UPDATE: Change assignment status
    if "update assignment" in command or "change status" in command:
        update_assignment_status_via_voice()
        return

    # DELETE: Remove an assignment
    if "delete assignment" in command or "remove assignment" in command:
        delete_assignment_via_voice()
        return