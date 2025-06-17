from flask import Flask, render_template, request, session, redirect, url_for
import json
import random

app = Flask(__name__)
app.secret_key = "GerardDiaz"

# Load country data
with open('data/countries_unified_svg.json', encoding='utf-8') as f:
    countries = json.load(f)

def add_streak_to_records(username, streak):
    records = session.get('top5', [])
    records.append({'user': username, 'streak': streak})
    # Sort and keep only top 5
    records = sorted(records, key=lambda x: x['streak'], reverse=True)[:5]
    session['top5'] = records

@app.route("/start", methods=["POST"])
def start():
    username = request.form.get("username", "Player")
    top5 = session.get("top5", [])  # Save current top5
    session.clear()                 # Clear everything else
    session["top5"] = top5          # Restore top5
    session["username"] = username
    session["streak"] = 0
    session["asked_countries"] = []
    return redirect(url_for("quiz"))

@app.route("/", methods=["GET"])
def index():
    top5 = session.get("top5", [])
    return render_template("index.html", top5=top5)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    all_capitals = sorted({c["capital"] for c in countries if c.get("capital")}, key=str.lower)

    # Initialize session variables
    if "asked_countries" not in session:
        session["asked_countries"] = []
    if "streak" not in session:
        session["streak"] = 0
    if "username" not in session:
        session["username"] = "Player"

    if request.method == "POST":
        user_answer = request.form.get("user_answer", "").strip().lower()
        correct_answer = request.form.get("correct_answer", "").strip().lower()
        country_name = request.form.get("country_name", "")

        asked = session.get("asked_countries", [])
        if country_name and country_name not in asked:
            asked.append(country_name)
            session["asked_countries"] = asked

        is_correct = user_answer == correct_answer

        # Streak logic
        if is_correct:
            session["streak"] += 1
        else:
            # Add to records if streak > 0
            if session["streak"] > 0:
                add_streak_to_records(session["username"], session["streak"])
            # Do NOT reset or redirect yet; show result and offer reset button

        country = next((c for c in countries if c["name"] == country_name), random.choice(countries))

        return render_template(
            "quiz.html",
            country=country,
            all_capitals=all_capitals,
            show_result=True,
            is_correct=is_correct,
            user_answer=user_answer,
            correct_answer=correct_answer,
            country_name=country_name,
            streak=session["streak"],
            top5=session.get("top5", [])
        )

    # GET request: choose a country not already asked
    asked = session.get("asked_countries", [])
    unasked_countries = [c for c in countries if c["name"] not in asked]

    if not unasked_countries:
        session["asked_countries"] = []
        unasked_countries = countries

    country = random.choice(unasked_countries)

    return render_template(
        "quiz.html",
        country=country,
        all_capitals=all_capitals,
        show_result=False,
        streak=session.get("streak", 0),
        top5=session.get("top5", [])
    )

@app.route("/reset", methods=["POST"])
def reset():
    # Reset streak and asked_countries, but keep top5 and username
    top5 = session.get("top5", [])
    username = session.get("username", "Player")
    session.clear()
    session["top5"] = top5
    session["username"] = username
    session["streak"] = 0
    session["asked_countries"] = []
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)
