import requests
from flask import Flask, render_template, request

app = Flask(__name__)


def get_emoji(condition, night=False):
    c = condition.lower()
    if "thunder" in c:
        return "⛈️"
    if "rain" in c or "drizzle" in c or "shower" in c:
        return "🌧️"
    if "snow" in c or "ice" in c or "sleet" in c:
        return "❄️"
    if "fog" in c or "mist" in c:
        return "🌫️"
    if "overcast" in c:
        return "☁️"
    if "cloud" in c:
        return "☁️" if night else "⛅"
    if "sunny" in c or "clear" in c:
        return "🌙" if night else "☀️"
    return "🌙" if night else "🌤️"


def get_hour(hourly, target):
    """Pick the hourly entry closest to the target time (1200 = noon, 2100 = 9 PM)."""
    if not hourly:
        return {}
    return min(hourly, key=lambda h: abs(int(h.get("time", "0")) - target))


def get_desc(entry):
    try:
        return entry["weatherDesc"][0]["value"]
    except (KeyError, IndexError, TypeError):
        return "Unknown"


@app.route("/", methods=["GET", "POST"])
def home():
    context = {"forecast": [], "temperature": None, "city": ""}

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        context["city"] = city

        if not city:
            context["error"] = "Please enter a city name."
            return render_template("index.html", **context)

        try:
            url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            current = data["current_condition"][0]
            days = data.get("weather", [])
            if not days:
                raise ValueError("No forecast data available")

            condition = current["weatherDesc"][0]["value"]
            temperature = current["temp_C"]

            context.update({
                "temperature": temperature,
                "condition": condition,
                "emoji": get_emoji(condition),
                "feels_like": current["FeelsLikeC"],
                "humidity": current["humidity"],
                "wind_speed": current["windspeedKmph"],
                "advice": "Drink water if it is hot!" if float(temperature) >= 30 else "Have a great day!",
                "sunrise": days[0]["astronomy"][0]["sunrise"],
                "sunset": days[0]["astronomy"][0]["sunset"],
                "forecast": [],
            })

            for day in days[:5]:
                hourly = day.get("hourly", [])
                day_cond = get_desc(get_hour(hourly, 1200))
                night_cond = get_desc(get_hour(hourly, 2100))

                context["forecast"].append({
                    "date": day["date"],
                    "max_temp": day["maxtempC"],
                    "min_temp": day["mintempC"],
                    "day_condition": day_cond,
                    "day_emoji": get_emoji(day_cond),
                    "night_condition": night_cond,
                    "night_emoji": get_emoji(night_cond, night=True),
                })

        except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
            context["error"] = "Could not get weather. Check the city or internet."

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
