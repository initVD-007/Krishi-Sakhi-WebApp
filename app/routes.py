from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from .utils import get_db_connection, run_inference, check_for_reminders
from config import Config
import google.generativeai as genai
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import datetime
import io
from PIL import Image

main = Blueprint('main', __name__)

# Config Gemini
llm_model = None
if Config.GEMINI_API_KEY and 'YOUR_GEMINI_API_KEY' not in Config.GEMINI_API_KEY:
    genai.configure(api_key=Config.GEMINI_API_KEY)
    llm_model = genai.GenerativeModel('gemini-3-flash-preview')

@main.route('/')
def home():
    if 'phone' in session:
        return render_template('index.html')
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmers WHERE phone = ?", (phone,))
        farmer = cursor.fetchone()
        conn.close()
        
        if farmer:
            session['phone'] = farmer['phone']
            session['name'] = farmer['name']
            session['location'] = farmer['location']
            session['crop'] = farmer['crop']
            if 'email' in farmer.keys() and farmer['email']: 
                 session['email'] = farmer['email']
            return redirect(url_for('main.home'))
        else:
            return render_template('login.html', error="Phone number not found.")
    return render_template('login.html')

@main.route('/google_auth', methods=['POST'])
def google_auth():
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'success': False, 'error': 'No token provided'})

    try:
        r = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
        if r.status_code != 200:
            return jsonify({'success': False, 'error': 'Invalid Token'})
        
        google_data = r.json()
        email = google_data.get('email')
        name = google_data.get('name')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email not found in token'})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM farmers WHERE email = ?", (email,))
        farmer = cursor.fetchone()
        conn.close()

        if farmer:
            session['phone'] = farmer['phone']
            session['name'] = farmer['name']
            return jsonify({'success': True, 'redirect': url_for('main.home')})
        else:
            session['register_prefill'] = {'email': email, 'name': name}
            return jsonify({'success': True, 'redirect': url_for('main.register')})

    except Exception as e:
        print(f"Google Auth Error: {e}")
        return jsonify({'success': False, 'error': 'Server Error'})

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        location = request.form.get('location')
        crop = request.form.get('crop')
        land_size = request.form.get('land_size')
        soil_type = request.form.get('soil_type')
        irrigation = request.form.get('irrigation')
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO farmers (name, phone, email, location, crop, land_size, soil_type, irrigation) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, phone, email, location, crop, land_size, soil_type, irrigation))
            conn.commit()
            conn.close()
            return redirect(url_for('main.login'))
        except sqlite3.IntegrityError:
            return render_template('register.html', error="This phone number is already registered.")
            
    prefill = session.pop('register_prefill', {})
    return render_template('register.html', prefill=prefill)

@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main.route('/diagnose', methods=['GET', 'POST'])
def diagnose():
    if 'phone' not in session: return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '':
            return render_template('diagnose.html', prediction_text='No image selected.')
        
        img_bytes = file.read()
        
        prediction_text = "Analysis Failed"
        care_instructions = None
        disease_name = "Unknown"
        
        gemini_success = False
        if llm_model:
            def call_gemini():
                img = Image.open(io.BytesIO(img_bytes))
                prompt = """
                Analyze this plant image. 
                1. Identify the plant name.
                2. Determine if it is Healthy or has a Disease/Pest/Deficiency.
                3. If diseased, name the disease specifically.
                4. Provide a confidence level (High/Medium/Low).
                
                Format the answer as:
                "Diagnosis: [Plant Name] - [Disease Name/Healthy] ([Confidence])"

                Then provide two distinct sections for care:
                
                **🍃 Natural/Organic Control:**
                - [Bullet point 1]
                - [Bullet point 2]
                
                **🧪 Chemical Control:**
                - [Bullet point 1]
                - [Bullet point 2]
                """
                response = llm_model.generate_content([prompt, img])
                return response.text

            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(call_gemini)
                    full_text = future.result(timeout=5)
                
                lines = full_text.split('\n')
                prediction_text = lines[0].replace('Diagnosis:', '').strip()
                if "Diagnosis:" in lines[0]:
                    prediction_text = lines[0].strip()
                else:
                    prediction_text = "Diagnosis: " + lines[0].strip()

                care_instructions = "\n".join(lines[1:]).strip()
                disease_name = prediction_text
                gemini_success = True
                
            except TimeoutError:
                print("Gemini Timeout: Switching to TFLite model...")
            except Exception as e:
                print(f"Gemini Vision Error: {e}")
        
        if not gemini_success:
            print("Falling back to TFLite...")
            label, max_prob = run_inference(img_bytes)
            
            CONFIDENCE_THRESHOLD = 0.5
            
            if max_prob > CONFIDENCE_THRESHOLD:
                disease_name = label.replace("___", " ").replace("_", " ")
                prediction_text = f"Diagnosis (Offline Model): {disease_name} ({max_prob:.2%})"
                care_instructions = "AI assistant unavailable for care instructions."
            else:
                prediction_text = "Unknown or Not a Plant Leaf"
                care_instructions = None

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activities (farmer_phone, activity_type, content, response) VALUES (?, ?, ?, ?)",
                       (session['phone'], 'Diagnosis', file.filename, prediction_text))
        conn.commit()
        conn.close()
        
        return render_template('diagnose.html', prediction_text=prediction_text, care_instructions=care_instructions)

    return render_template('diagnose.html')

@main.route('/ask', methods=['GET', 'POST'])
def ask():
    if 'phone' not in session: return redirect(url_for('main.login'))
    if request.method == 'POST':
        if llm_model is None:
            return render_template('ask.html', llm_answer="LLM is not configured.")
        question = request.form.get('question')
        if not question:
            return render_template('ask.html', llm_answer="Please ask a question.")

        location = session.get('location', 'N/A')
        crop = session.get('crop', 'N/A')
        prompt = f"You are Krishi Sakhi, an expert AI assistant for farmers in Kerala, India. Provide a clear, concise, and helpful answer. Farmer's Context: Location: {location}, Main Crop: {crop}. Farmer's Question: \"{question}\"\nAnswer:"
        
        try:
            response = llm_model.generate_content(prompt)
            answer = response.text
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO activities (farmer_phone, activity_type, content, response) VALUES (?, ?, ?, ?)",
                           (session['phone'], 'Question', question, answer))
            conn.commit()
            conn.close()
        except Exception as e:
            answer = "Sorry, I could not process your request at the moment."
        
        return render_template('ask.html', llm_answer=answer)
    return render_template('ask.html')

@main.route('/my_farm', methods=['GET', 'POST'])
def my_farm():
    if 'phone' not in session: return redirect(url_for('main.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        crop = request.form['crop']
        sowing_date = request.form['sowing_date']
        cursor.execute("INSERT OR REPLACE INTO crop_events (farmer_phone, crop, sowing_date) VALUES (?, ?, ?)",
                       (session['phone'], crop, sowing_date))
        conn.commit()

    cursor.execute("SELECT crop, sowing_date FROM crop_events WHERE farmer_phone = ?", (session['phone'],))
    events = cursor.fetchall()
    
    schedules = {}
    for crop, sowing_date_str in events:
        sowing_date = datetime.datetime.strptime(sowing_date_str, '%Y-%m-%d').date()
        cursor.execute("SELECT activity, days_after_sowing FROM crop_schedules WHERE crop_name = ?", (crop,))
        schedule_rules = cursor.fetchall()
        
        calculated_schedule = []
        for activity, days in schedule_rules:
            activity_date = sowing_date + datetime.timedelta(days=days)
            calculated_schedule.append({'activity': activity, 'date': activity_date.strftime('%d %B, %Y')})
        schedules[crop] = calculated_schedule

    conn.close()
    return render_template('my_farm.html', schedules=schedules)

@main.route('/activity_log')
def activity_log():
    if 'phone' not in session: return redirect(url_for('main.login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, activity_type, content, response FROM activities WHERE farmer_phone = ? ORDER BY timestamp DESC",
                   (session['phone'],))
    activities = cursor.fetchall()
    conn.close()
    
    return render_template('activity_log.html', activities=activities)

@main.route('/get_advisory', methods=['POST'])
def get_advisory():
    data = request.get_json()
    lat = data.get('latitude')
    lon = data.get('longitude')

    if not lat or not lon:
        return jsonify({'error': 'Location not provided'}), 400

    weather_advisory = "Weather data unavailable."
    description = "clear sky" 
    
    if Config.WEATHER_API_KEY and 'YOUR_OPENWEATHERMAP_API_KEY' not in Config.WEATHER_API_KEY:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={Config.WEATHER_API_KEY}&units=metric"
        try:
            weather_res = requests.get(weather_url).json()
            if weather_res.get("cod") == 200:
                main_weather = weather_res['main']
                weather = weather_res['weather'][0]
                temp = main_weather['temp']
                description = weather['description']
                
                weather_advisory = f"🌦️ Weather: Current temperature is {temp}°C with {description}."
                if 'rain' in description or 'storm' in description:
                    weather_advisory += "\nRecommendation: Avoid spraying pesticides or applying fertilizer today."
        except Exception as e:
            print(f"Weather API Error: {e}")

    pest_advisory = ""
    if llm_model:
        location = session.get('location', 'N/A')
        crop = session.get('crop', 'N/A')
        prompt = f"""
        Based on the current weather ({description}) in {location} for a farmer growing {crop},
        what is one proactive pest or disease warning you can give for today?
        Keep the advice short and actionable (1-2 sentences).
        """
        try:
            response = llm_model.generate_content(prompt)
            pest_advisory = f"\n\n🦟 AI Advisory: {response.text}"
        except Exception as e:
            print(f"Gemini Pest Advisory Error: {e}")

    full_advisory = weather_advisory + pest_advisory
    return jsonify({'advisory': full_advisory})
