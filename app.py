
import requests
from flask import Flask, render_template, request

app = Flask(__name__)


def get_emoji(condition):
    condition = condition.lower()

    if "thunder" in condition:
        return "⛈️"
    elif "rain" in condition or "drizzle" in condition:
        return "🌧️"
    elif "snow" in condition or "ice" in condition:
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
    context = {
        "forecast": [],
        "temperature": None,
        "city": ""
    }

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        context["city"] = city

        if not city:
            context["error"] = "Please enter a city name."
            return render_template("index.html", **context)

        try:
            url = (
                f"https://wttr.in/"
                f"{requests.utils.quote(city)}?format=j1"
            )

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
                "advice": (
                    "Drink water if it is hot!"
                    if float(temperature) >= 30
                    else "Have a great day!"
                ),
                "sunrise": days[0]["astronomy"][0]["sunrise"],
                "sunset": days[0]["astronomy"][0]["sunset"],
                "forecast": []
            })

            for day in days[:5]:
                hourly = day.get("hourly", [])

                # Find daytime and nighttime entries
                day_data = next(
                    (h for h in hourly
                     if int(h.get("time", "0")) == 1200),
                    hourly[0] if hourly else {}
                )

                night_data = next(
                    (h for h in hourly
                     if int(h.get("time", "0")) in (0, 2100)),
                    hourly[-1] if hourly else {}
                )

                day_condition = day_data.get(
                    "weatherDesc", [{"value": "Unknown"}]
                )[0]["value"]

                night_condition = night_data.get(
                    "weatherDesc", [{"value": "Unknown"}]
                )[0]["value"]

                context["forecast"].append({
                    "date": day["date"],
                    "condition": day_condition,
                    "emoji": get_emoji(day_condition),
                    "max_temp": day["maxtempC"],
                    "min_temp": day["mintempC"],
                    "day_condition": day_condition,
                    "day_emoji": get_emoji(day_condition),
                    "night_condition": night_condition,
                    "night_emoji": get_emoji(night_condition)
                })

        except (
            requests.RequestException,
            ValueError,
            KeyError,
            IndexError,
            TypeError
        ):
            context["error"] = (
                "Could not get weather. Check the city or internet."
            )

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
