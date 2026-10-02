
import requests
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)


def get_weather_emoji(condition, day_night):
    condition = condition.lower()

    # Check more specific conditions before general ones
    if "thunder" in condition or "lightning" in condition:
        return "⛈️"

    elif "freezing rain" in condition:
        return "🌧️🥶"

    elif "blizzard" in condition:
        return "🌨️"

    elif "heavy rain" in condition or "torrential rain" in condition:
        return "🌧️"

    elif "drizzle" in condition:
        return "🌦️"

    elif "rain" in condition or "shower" in condition:
        return "🌧️"

    elif "snow" in condition or "ice pellets" in condition:
        return "❄️"

    elif "sleet" in condition:
        return "🌨️"

    elif "fog" in condition or "mist" in condition:
        return "🌫️"

    elif "haze" in condition:
        return "🌁"

    elif "partly cloudy" in condition:
        return "⛅"

    elif "overcast" in condition or "cloudy" in condition:
        return "☁️"

    elif "windy" in condition:
        return "💨"

    elif "sunny" in condition:
        return "☀️"

    elif "clear" in condition:
        return "🌙" if day_night == "Nighttime" else "☀️"

    else:
        return "🌤️"


def get_weather_advice(condition, temperature):
    condition = condition.lower()
    temp = int(temperature)

    if "thunder" in condition or "lightning" in condition:
        return (
            "Thunderstorm conditions! Stay indoors, away from "
            "windows, and avoid exposed outdoor areas. ⛈️"
        )

    elif "blizzard" in condition:
        return "Severe snowy weather is possible. Stay warm and check local travel advice. 🌨️"

    elif "freezing rain" in condition or "sleet" in condition:
        return "Surfaces may be slippery. Take extra care outdoors. 🧊"

    elif "heavy rain" in condition or "torrential rain" in condition:
        return "Heavy rain is possible. Carry an umbrella and watch for flooding. ☔"

    elif "drizzle" in condition:
        return "Light rain is possible. A light raincoat or umbrella may help. 🌦️"

    elif "rain" in condition or "shower" in condition:
        return "Rain is expected. Remember your umbrella and avoid flooded roads. ☔"

    elif "snow" in condition or "ice pellets" in condition:
        return "Dress warmly and check local travel conditions. ❄️"

    elif "fog" in condition or "mist" in condition:
        return "Visibility may be reduced. Take extra care when travelling. 🌫️"

    elif "haze" in condition:
        return "If visibility or air quality is poor, consider limiting strenuous outdoor activity. 🌁"

    elif "wind" in condition:
        return "It's windy. Secure loose outdoor items and take care outside. 💨"

    elif temp >= 30:
        return "It's hot! Drink plenty of water and seek shade when needed. 🥤"

    elif "sunny" in condition or "clear" in condition:
        return "Enjoy the clear weather and remember sun protection when needed. ☀️"

    elif "cloud" in condition or "overcast" in condition:
        return "It's cloudy. Consider carrying a light jacket if needed. ☁️"

    elif temp >= 20:
        return "The weather looks comfortable. Enjoy your day! 😎"

    else:
        return "It's cool outside. Dress comfortably for the weather. 🧥"


@app.route("/", methods=["GET", "POST"])
def home():
    context = {
        "city": "",
        "error": None,
        "temperature": None,
        "forecast": []
    }

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        context["city"] = city

        if not city:
            context["error"] = "Please enter a city name."
            return render_template("index.html", **context)

        url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"

        try:
            response = requests.get(
                url,
                headers={"User-Agent": "WeatherForecastApp/1.0"},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            current = data["current_condition"][0]
            weather = data["weather"]

            temperature = current["temp_C"]
            condition = current["weatherDesc"][0]["value"]

            feels_like = current["FeelsLikeC"]
            wind_speed = current["windspeedKmph"]
            humidity = current["humidity"]

            astronomy = weather[0]["astronomy"][0]
            sunrise = astronomy["sunrise"]
            sunset = astronomy["sunset"]

            # Determine daytime or nighttime
            # Uses the computer's local time.
            now = datetime.now().strftime("%H:%M")
            day_night = (
                "Daytime" if sunrise <= now <= sunset
                else "Nighttime"
            )

            emoji = get_weather_emoji(condition, day_night)
            advice = get_weather_advice(condition, temperature)

            # Prepare forecast cards
            forecast = []

            for day in weather[:5]:
                hourly = day.get("hourly", [])
                description = "No description available"

                if hourly:
                    descriptions = hourly[0].get("weatherDesc", [])
                    if descriptions:
                        description = descriptions[0].get(
                            "value", description
                        )

                forecast.append({
                    "date": day.get("date", ""),
                    "maxtempC": day.get("maxtempC", "N/A"),
                    "mintempC": day.get("mintempC", "N/A"),
                    "description": description,
                    "emoji": get_weather_emoji(description, day_night)
                })

            context.update({
                "temperature": temperature,
                "feels_like": feels_like,
                "wind_speed": wind_speed,
                "humidity": humidity,
                "sunrise": sunrise,
                "sunset": sunset,
                "condition": condition,
                "emoji": emoji,
                "advice": advice,
                "day_night": day_night,
                "forecast": forecast,
                "updated_time": datetime.now().strftime("%H:%M:%S")
            })

        except requests.RequestException:
            context["error"] = (
                "Unable to connect to the weather service. "
                "Check your internet connection and try again."
            )

        except (ValueError, KeyError, IndexError, TypeError):
            context["error"] = (
                "Weather data could not be read. "
                "Please try again or search for another city."
            )

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
