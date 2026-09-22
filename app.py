from flask import Flask, render_template, request
from fuzzy_logic import get_irrigation_recommendation

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    level = None
    crop = None
    if request.method == "POST":

        soil_moisture = float(request.form["soil_moisture"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        rain_probability = float(request.form["rain_probability"])
        crop = request.form["crop"]
        

        result, level = get_irrigation_recommendation(
            soil_value=soil_moisture,
            temperature_value=temperature,
            humidity_value=humidity,
            rain_value=rain_probability
        )

    return render_template(
    "index.html",
    result=result,
    level=level,
    crop=crop
)

if __name__ == "__main__":
    app.run(debug=True)