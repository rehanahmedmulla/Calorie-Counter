from flask import Flask, render_template, request,redirect
import sqlite3
from datetime import date

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)
