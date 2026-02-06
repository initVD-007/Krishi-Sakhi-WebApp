import sqlite3
import datetime
import os
import tensorflow as tf # For TFLite (checking if needed here or just pure inference)
import numpy as np
from PIL import Image
import io
import logging
from config import Config

logger = logging.getLogger(__name__)

def get_db_connection():
    conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Farmers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS farmers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, 
    phone TEXT UNIQUE NOT NULL, email TEXT UNIQUE,
    location TEXT NOT NULL, crop TEXT NOT NULL, land_size REAL, soil_type TEXT, irrigation TEXT)
    ''')
    # Activities table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (id INTEGER PRIMARY KEY, farmer_phone TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    content TEXT NOT NULL, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    ''')
    
    # --- MIGRATION: Check if email column exists (for existing DBs) ---
    try:
        cursor.execute("SELECT email FROM farmers LIMIT 1")
    except sqlite3.OperationalError:
        print("Migrating Database: Adding 'email' column to farmers table...")
        cursor.execute("ALTER TABLE farmers ADD COLUMN email TEXT")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_farmers_email ON farmers(email)")
    # ------------------------------------------------------------------
    # Crop events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crop_events (id INTEGER PRIMARY KEY, farmer_phone TEXT NOT NULL,
    crop TEXT NOT NULL, sowing_date DATE NOT NULL, UNIQUE(farmer_phone, crop))
    ''')
    # Crop schedules table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crop_schedules (id INTEGER PRIMARY KEY, crop_name TEXT NOT NULL,
    activity TEXT NOT NULL, days_after_sowing INTEGER NOT NULL)
    ''')
    conn.commit()
    conn.close()

def populate_schedules():
    conn = get_db_connection()
    cursor = conn.cursor()
    if cursor.execute("SELECT COUNT(*) FROM crop_schedules").fetchone()[0] == 0:
        schedules = [
            ('Rice', 'First Weeding', 20), ('Rice', 'Fertilizer Application', 35), ('Rice', 'Harvesting', 120),
            ('Tomato', 'Staking/Support', 25), ('Tomato', 'First Fertilizer', 30), ('Tomato', 'Harvesting Begins', 70),
            ('Banana', 'Fertilizer (Month 2)', 60), ('Banana', 'De-suckering', 150), ('Banana', 'Harvesting Begins', 300),
            ('Potato', 'First Earthing Up', 25), ('Potato', 'Fertilizer Application', 30), ('Potato', 'Harvesting', 90)
        ]
        cursor.executemany("INSERT INTO crop_schedules (crop_name, activity, days_after_sowing) VALUES (?, ?, ?)", schedules)
        conn.commit()
    conn.close()

# --- Model Loading ---
# We load this globally or lazily. Let's do a class or global var in utils? 
# Better to have a function to get the interpreter.

interpreter = None
labels = []
input_details = None
output_details = None

def load_model():
    global interpreter, labels, input_details, output_details
    try:
        interpreter = tf.lite.Interpreter(model_path=Config.MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        if os.path.exists(Config.LABELS_PATH):
            with open(Config.LABELS_PATH, 'r') as f:
                labels = f.read().splitlines()
        else:
            print(f"Warning: Labels file not found at {Config.LABELS_PATH}")
    except Exception as e:
        print(f"CRITICAL: Error loading TFLite model or labels: {e}")

def process_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
    return img_array

def run_inference(img_bytes):
    global interpreter
    if interpreter is None:
        load_model()
    
    if interpreter is None:
        return None, 0.0 # Model failed to load
        
    processed_image = process_image(img_bytes)
    interpreter.set_tensor(input_details[0]['index'], processed_image)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    probabilities = output_data[0]
    max_index = np.argmax(probabilities)
    max_prob = probabilities[max_index]
    
    label = labels[max_index] if max_index < len(labels) else "Unknown"
    return label, max_prob

def check_for_reminders():
    print(f"\n--- Running Daily Reminder Check: {datetime.date.today()} ---")
    conn = get_db_connection()
    cursor = conn.cursor()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    cursor.execute("SELECT farmer_phone, crop, sowing_date FROM crop_events")
    events = cursor.fetchall()
    
    for event in events:
        farmer_phone, crop, sowing_date_str = event
        sowing_date = datetime.datetime.strptime(sowing_date_str, '%Y-%m-%d').date()
        
        cursor.execute("SELECT activity, days_after_sowing FROM crop_schedules WHERE crop_name = ?", (crop,))
        schedule_rules = cursor.fetchall()
        
        for rule in schedule_rules:
            activity, days_after = rule
            activity_date = sowing_date + datetime.timedelta(days=days_after)
            
            if activity_date == tomorrow:
                reminder_message = f"REMINDER for farmer {farmer_phone}: Tomorrow is the day for '{activity}' on your {crop} crop."
                print(reminder_message)
    
    conn.close()
    print("--- Reminder Check Finished ---\n")
