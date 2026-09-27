import requests
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city = request.form.get("city")
        updated_time = datetime.now().strftime("%H:%M:%S")

        url = f"https://wttr.in/{city}?format=j1"

        response = requests.get(url)
        data = response.json()

        temperature = data["current_condition"][0]["temp_C"]
        feels_like = data["current_condition"][0]["FeelsLikeC"]
        wind_speed = data["current_condition"][0]["windspeedKmph"]
        humidity = data["current_condition"][0]["humidity"]
        sunrise = data["weather"][0]["astronomy"][0]["sunrise"]
        sunset = data["weather"][0]["astronomy"][0]["sunset"]
        condition = data["current_condition"][0]["weatherDesc"][0]["value"]

        # Choose emoji
        if "Sunny" in condition:
            emoji = "☀️"
        elif "Cloudy" in condition:
            emoji = "☁️"
        elif "Rain" in condition:
            emoji = "🌧️"
        elif "Fog" in condition:
            emoji = "🌫️"
        elif "Overcast" in condition:
            emoji = "☁️"
        else:
            emoji = "🌤️"

        # Choose advice based on temperature
        if int(temperature) >= 30:
            advice = "It's hot! Stay hydrated. 🥤"
        elif int(temperature) >= 20:
            advice = "The weather looks comfortable. 😎"
        else:
            advice = "It's cool outside. You might want a coat. 🧥"

        # Add weather-specific advice
        if "Rain" in condition:
            advice += " Don't forget your umbrella! ☔"
        elif "Fog" in condition:
            advice += " Visibility may be low. Be careful outside. 🌫️"

        return render_template(
            "index.html",
            city=city,
            temperature=temperature,
            feels_like=feels_like,
            condition=condition,
            wind_speed=wind_speed,
            humidity=humidity,
            sunrise=sunrise,
            sunset=sunset,
            updated_time=updated_time,
            advice=advice,
            emoji=emoji
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
