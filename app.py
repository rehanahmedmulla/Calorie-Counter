from flask import Flask, render_template, request,redirect
import sqlite3
from datetime import date
import os
from dotenv import load_dotenv
import requests

load_dotenv(override=True)

# Load key from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key="rynx_premium_super_secret_key"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    calories = None
    food = None
    quantity = None
    food_details = None

    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT 
        food_name,
        calories,
        protein,
        carbs,
        fat,
        fiber
    FROM foods
    ORDER BY food_name
    """)

    foods = cursor.fetchall()

    conn.close()

    if request.method == "POST":

        food = request.form["food"]
        quantity = int(request.form["quantity"])

        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()

        cursor.execute(
            """ 
            SELECT
                calories,
                protein,
                carbs,
                fat,
                fiber
            FROM foods
            WHERE food_name = ?
            """, (food,)
        )
        food_details = cursor.fetchone()

        protein =food_details[1]
        carbs =food_details[2]
        fat = food_details[3]
        fiber =food_details[4]

        protein = protein*quantity
        carbs=carbs*quantity
        fat=fat*quantity
        fiber=fiber*quantity

        calories_per_serving = food_details[0]

        calories = calories_per_serving * quantity

        #conn = sqlite3.connect("calories.db")
        #cursor = conn.cursor()

        today = date.today()

        cursor.execute(
            "INSERT INTO food_history (food, quantity, calories,date) VALUES (?, ?, ?, ?)",
            (food, quantity, calories, str(today))
        )

        conn.commit()
        conn.close()
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()

    today =str(date.today())

    cursor.execute("""
        SELECT id,food, quantity, calories
        FROM food_history
        WHERE date = ?
        ORDER BY id DESC
    """,(today,))

    history = cursor.fetchall()
    total_calories=0
    for item in history:
        total_calories += item[3]

    conn.close()
    goal = 2500

    consumed = total_calories

    remaining = goal - consumed

    if goal > 0:
        progress = round((consumed / goal) * 100)
    else:
        progress = 0

    return render_template(
       "dashboard.html",
       calories=calories,
       selected_food=food if request.method == "POST" else None,
       quantity=quantity if request.method == "POST" else None,
       history=history,
       total_calories=total_calories,
       goal=goal,
       consumed=consumed,
       remaining=remaining,
       progress=progress,
       foods=foods,

       protein=protein if request.method == "POST" else None,
       carbs=carbs if request.method == "POST" else None,
       fat=fat if request.method == "POST" else None,
       fiber=fiber if request.method == "POST" else None,
 )

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()

    if request.method =="POST":

        quantity = int(request.form["quantity"])

        cursor.execute(
            "SELECT food FROM food_history WHERE id = ?",
            (id,)
        )

        food_name = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT calories
            FROM foods
            WHERE food_name = ?
            """,
            (food_name,)
        )

        calories_per_serving = cursor.fetchone()[0]
        calories = calories_per_serving * quantity

        cursor.execute(
            """
            UPDATE food_history
            SET quantity = ?, calories = ?
            WHERE id = ?
            """,
            (quantity, calories, id)
        )
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    cursor.execute(
        "SELECT * FROM food_history WHERE id = ?",
        (id,)
    )

    food = cursor.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        food=food
    )


@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM food_history WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/bmi", methods=["GET", "POST"])
def bmi():

    result = None

    if request.method == "POST":

        weight = float(request.form["weight"])
        height = float(request.form["height"])

        height = height / 100

        bmi = weight / (height * height)

        if bmi < 18.5:
            status = "Underweight"
        elif bmi < 25:
            status = "Normal Weight"
        elif bmi < 30:
            status = "Overweight"
        else:
            status = "Obese"

        result = {
            "bmi": round(bmi, 2),
            "status": status
        }

    return render_template(
        "bmi.html",
        result=result
    )

@app.route("/goal", methods=["GET", "POST"])
def goal():

    result = None

    if request.method == "POST":

        age = int(request.form["age"])
        weight = float(request.form["weight"])
        height = float(request.form["height"])
        gender = request.form["gender"]

        if gender == "Male":
            maintenance = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            maintenance = 10 * weight + 6.25 * height - 5 * age - 161

        result = {
            "maintenance": round(maintenance),
            "fat_loss": round(maintenance - 500),
            "muscle_gain": round(maintenance + 300)
        }

    return render_template("goal.html", result=result)

@app.route("/manage_foods", methods=["GET", "POST"])
def manage_foods():
    if request.method == "POST":
        # 1. Grab the data from the HTML form
        food_name = request.form["food_name"]
        calories = int(request.form["calories"])
        protein = float(request.form["protein"])
        carbs = float(request.form["carbs"])
        fat = float(request.form["fat"])
        fiber = float(request.form["fiber"])

        # 2. Connect to the database and insert the new food safely
        conn = sqlite3.connect("calories.db")
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO foods (food_name, calories, protein, carbs, fat, fiber)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (food_name, calories, protein, carbs, fat, fiber)
        )
        
        conn.commit()
        conn.close()

        # 3. Redirect back to the same page to see the updated list
        return redirect("/manage_foods")

    # If it's a GET request, just load the page and show all current foods
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, food_name, calories, protein FROM foods ORDER BY food_name")
    all_foods = cursor.fetchall()
    conn.close()

    return render_template("manage_foods.html", all_foods=all_foods)
@app.route("/delete_food/<int:id>")
def delete_food(id):
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()

    # Database se food item delete karna
    cursor.execute(
        "DELETE FROM foods WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    # Delete hone ke baad wapas manage_foods page par bhej dena
    return redirect("/manage_foods")
@app.route("/edit_food/<int:id>", methods=["GET", "POST"])
def edit_food(id):
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()

    if request.method == "POST":
        # Form se naya updated data lena
        food_name = request.form["food_name"]
        calories = int(request.form["calories"])
        protein = float(request.form["protein"])
        carbs = float(request.form["carbs"])
        fat = float(request.form["fat"])
        fiber = float(request.form["fiber"])

        # Database mein us specific id wale food ko update karna
        cursor.execute(
            """
            UPDATE foods
            SET food_name = ?, calories = ?, protein = ?, carbs = ?, fat = ?, fiber = ?
            WHERE id = ?
            """,
            (food_name, calories, protein, carbs, fat, fiber, id)
        )
        conn.commit()
        conn.close()

        # Update hone ke baad wapas list par bhej dena
        return redirect("/manage_foods")

    # Agar request GET hai, toh database se purana data nikal kar form mein dikhana
    cursor.execute("SELECT * FROM foods WHERE id = ?", (id,))
    food = cursor.fetchone()
    conn.close()

    return render_template("edit_food.html", food=food)

@app.route("/ai_coach", methods=["POST"])
def ai_coach():
    # THE PROFESSIONAL METHOD: Fetch securely from .env
    api_key = os.getenv("GOOGLE_API_KEY") 
    
    if not api_key:
         # Agar key load na ho, toh crash hone ke bajaye error dikhao
         print("SECURITY ALERT: API Key is missing or not loading from .env!")
         return redirect("/dashboard")

    user_query = request.form.get("query")
    if not user_query:
        return redirect("/dashboard")
        
    prompt = f"You are a professional fitness coach. Answer this diet question shortly: {user_query}"
    
    # Direct API Call using the secure key
    # THE FINAL FIX: Using the exact model name from your terminal list
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        resp_data = resp.json()
        
        if 'candidates' in resp_data:
            ai_text = resp_data['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in resp_data:
            error_msg = resp_data['error']['message']
            
            # Smart Fallback: Agar Google overload ho jaye
            if "high demand" in error_msg.lower() or "overloaded" in error_msg.lower():
                ai_text = "🤖 AI Coach: I'm currently helping a lot of users at the gym! Please take a quick water break and ask me again in 30 seconds. 💧"
            else:
                ai_text = "🤖 AI Coach is taking a quick rest. Please try again shortly."
            
    except Exception as e:
        ai_text = f"System Error: {str(e)}"
    
    # --- Dashboard Data Logic ---
    conn = sqlite3.connect("calories.db")
    cursor = conn.cursor()
    cursor.execute("SELECT food_name, calories, protein, carbs, fat, fiber FROM foods ORDER BY food_name")
    foods = cursor.fetchall()
    
    today = str(date.today())
    cursor.execute("SELECT id, food, quantity, calories FROM food_history WHERE date = ? ORDER BY id DESC", (today,))
    history = cursor.fetchall()
    
    total_calories = sum(item[3] for item in history)
    goal = 2500
    progress = round((total_calories / goal) * 100) if goal > 0 else 0
    remaining = goal - total_calories
    conn.close()
    
    return render_template(
        "dashboard.html",
        ai_response=ai_text,
        history=history,
        total_calories=total_calories,
        goal=goal,
        consumed=total_calories,
        remaining=remaining,
        progress=progress,
        foods=foods
    )

from flask import flash # Sabse upar imports mein add karein

@app.route("/ai_logger", methods=["POST"])
def ai_logger():
    api_key = os.getenv("GOOGLE_API_KEY")
    food_text = request.form.get("food_text")
    
    if not food_text:
        return redirect("/dashboard")

    prompt = f"""
    You are an expert nutritionist. Analyze this meal: '{food_text}'.
    Estimate the total nutritional values. 
    Respond ONLY with a valid JSON object in this exact format, with no markdown, no formatting, and no extra text:
    {{"food_name": "Name of the meal", "calories": 250, "protein": 10.5, "carbs": 30.0, "fat": 5.0, "fiber": 2.0}}
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=15)
        resp_data = resp.json()
        
        if 'candidates' in resp_data:
            ai_text = resp_data['candidates'][0]['content']['parts'][0]['text']
            
            clean_text = ai_text.strip().strip('```json').strip('```')
            nutrition_data = json.loads(clean_text)
            
            conn = sqlite3.connect("calories.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO foods (food_name, calories, protein, carbs, fat, fiber) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nutrition_data["food_name"], nutrition_data["calories"], nutrition_data["protein"], 
                 nutrition_data["carbs"], nutrition_data["fat"], nutrition_data["fiber"])
            )
            conn.commit()
            conn.close()
            
            # SUCCESS MESSAGE JO SCREEN PAR DIKHEGA
            flash(f"✅ AI Saved: {nutrition_data['food_name']} ({nutrition_data['calories']} kcal) to your database!")
            
    except Exception as e:
        # Technical text ke bajaye user ko polite gym-themed message dikhayenge
        flash("🤖 AI Logger: I am currently counting macros for a lot of users in the gym! 🏋️‍♂️ Take a water break and try again in 20 seconds. 💧")
        print(f"AI Logger Error: {str(e)}")
        
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)
