from flask import Flask, render_template, request

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

    food_data = {
        "Rice": 130,
        "Egg": 70,
        "Banana": 105,
        "Apple": 95,
        "Chicken": 239
    }

    if request.method == "POST":

        food = request.form["food"]
        quantity = int(request.form["quantity"])

        calories = food_data[food] * quantity

    return render_template(
    "dashboard.html",
    calories=calories,
    selected_food=food if request.method == "POST" else None,
    quantity=quantity if request.method == "POST" else None
)
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

if __name__ == "__main__":
    app.run(debug=True)
