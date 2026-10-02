import requests
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city = request.form.get("city")

        if not city:
            return render_template("index.html", error="Please enter a city.")

        try:
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            return render_template(
                "index.html",
                error="Could not get weather data. Please try again."
            )
        forecast = data["weather"][:5]

        # Current weather
        current_weather = data["current_condition"][0]

        temperature = current_weather["temp_C"]
        feels_like = current_weather["FeelsLikeC"]
        wind_speed = current_weather["windspeedKmph"]
        humidity = current_weather["humidity"]
        condition = current_weather["weatherDesc"][0]["value"]

        # Sunrise and sunset
        sunrise = data["weather"][0]["astronomy"][0]["sunrise"]
        sunset = data["weather"][0]["astronomy"][0]["sunset"]

        sunrise_time = datetime.strptime(
            sunrise, "%I:%M %p"
        ).strftime("%H:%M")

        sunset_time = datetime.strptime(
            sunset, "%I:%M %p"
        ).strftime("%H:%M")

        current_time = datetime.now().strftime("%H:%M")

        # Determine day/night
        if sunrise_time <= current_time <= sunset_time:
            day_night = "☀️ Daytime"
        else:
            day_night = "🌙 Nighttime"

        # Choose emoji
        condition_lower = condition.lower()

        if "sunny" in condition_lower:
            emoji = "☀️"
        elif "clear" in condition_lower:
            emoji = "🌙"
        elif "cloudy" in condition_lower:
            emoji = "☁️"
        elif "overcast" in condition_lower:
            emoji = "☁️"
        elif "rain" in condition_lower:
            emoji = "🌧️"
        elif "drizzle" in condition_lower:
            emoji = "🌦️"
        elif "thunder" in condition_lower:
            emoji = "⛈️"
        elif "snow" in condition_lower:
            emoji = "❄️"
        elif "fog" in condition_lower or "mist" in condition_lower:
            emoji = "🌫️"
        else:
            emoji = "🌤️"

        # Choose advice based on temperature
        temperature_int = int(temperature)

        if temperature_int >= 30:
            advice = "It's hot! Stay hydrated. 🥤"
        elif temperature_int >= 20:
            advice = "The weather looks comfortable. 😎"
        else:
            advice = "It's cool outside. You might want a coat. 🧥"

        # Add weather-specific advice
        if "rain" in condition_lower:
            advice += " Don't forget your umbrella! ☔"
        elif "fog" in condition_lower or "mist" in condition_lower:
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
            day_night=day_night,
            advice=advice,
            emoji=emoji,
            forecast=forecast
        )

    # GET request
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
