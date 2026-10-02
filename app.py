
import requests
from flask import Flask, render_template, request

app = Flask(__name__)


def get_emoji(condition):
    condition = condition.lower()

    if "thunder" in condition:
        return "⛈️"
    elif "rain" in condition:
        return "🌧️"
    elif "snow" in condition:
        return "❄️"
    elif "fog" in condition or "mist" in condition:
        return "🌫️"
    elif "cloud" in condition or "overcast" in condition:
        return "☁️"
    elif "sunny" in condition or "clear" in condition:
        return "☀️"
    else:
        return "🌤️"


@app.route("/", methods=["GET", "POST"])
def home():
    context = {"forecast": [], "temperature": None, "city": ""}

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        context["city"] = city

        try:
            url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
            data = requests.get(url, timeout=15).json()

            current = data["current_condition"][0]
            days = data.get("weather", [])

            condition = current["weatherDesc"][0]["value"]
            temperature = current["temp_C"]

            context.update({
                "temperature": temperature,
                "condition": condition,
                "emoji": get_emoji(condition),
                "feels_like": current["FeelsLikeC"],
                "humidity": current["humidity"],
                "wind_speed": current["windspeedKmph"],
                "advice": "Drink water if it is hot!" if float(temperature) >= 30
                          else "Have a great day!",
                "sunrise": days[0]["astronomy"][0]["sunrise"],
                "sunset": days[0]["astronomy"][0]["sunset"],
                "forecast": []
            })

            for day in days[:5]:
                details = day.get("hourly", [{}])[0]
                description = details.get(
                    "weatherDesc", [{"value": "Unknown"}])[0]["value"]

                context["forecast"].append({
                    "date": day["date"],
                    "condition": description,
                    "emoji": get_emoji(description),
                    "max_temp": day["maxtempC"],
                    "min_temp": day["mintempC"]
                })

        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
            context["error"] = "Could not get weather. Check the city or internet."

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
