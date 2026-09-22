import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# ==============================
# INPUT VARIABLES
# ==============================

soil_moisture = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'soil_moisture'
)

temperature = ctrl.Antecedent(
    np.arange(0, 51, 1),
    'temperature'
)

humidity = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'humidity'
)

rain_probability = ctrl.Antecedent(
    np.arange(0, 101, 1),
    'rain_probability'
)


# ==============================
# OUTPUT VARIABLE
# ==============================

irrigation = ctrl.Consequent(
    np.arange(0, 101, 1),
    'irrigation'
)


# ==============================
# MEMBERSHIP FUNCTIONS
# ==============================

# Soil Moisture
soil_moisture['low'] = fuzz.trimf(
    soil_moisture.universe, [0, 0, 40]
)

soil_moisture['medium'] = fuzz.trimf(
    soil_moisture.universe, [30, 50, 70]
)

soil_moisture['high'] = fuzz.trimf(
    soil_moisture.universe, [60, 100, 100]
)


# Temperature
temperature['low'] = fuzz.trimf(
    temperature.universe, [0, 0, 20]
)

temperature['medium'] = fuzz.trimf(
    temperature.universe, [15, 25, 35]
)

temperature['high'] = fuzz.trimf(
    temperature.universe, [30, 50, 50]
)


# Humidity
humidity['low'] = fuzz.trimf(
    humidity.universe, [0, 0, 40]
)

humidity['medium'] = fuzz.trimf(
    humidity.universe, [30, 50, 70]
)

humidity['high'] = fuzz.trimf(
    humidity.universe, [60, 100, 100]
)


# Rain Probability
rain_probability['low'] = fuzz.trimf(
    rain_probability.universe, [0, 0, 30]
)

rain_probability['medium'] = fuzz.trimf(
    rain_probability.universe, [20, 50, 80]
)

rain_probability['high'] = fuzz.trimf(
    rain_probability.universe, [70, 100, 100]
)


# Irrigation Output
irrigation['none'] = fuzz.trimf(
    irrigation.universe, [0, 0, 20]
)

irrigation['low'] = fuzz.trimf(
    irrigation.universe, [10, 30, 50]
)

irrigation['medium'] = fuzz.trimf(
    irrigation.universe, [40, 60, 80]
)

irrigation['high'] = fuzz.trimf(
    irrigation.universe, [70, 100, 100]
)


# ==============================
# FUZZY RULES
# ==============================

# Dry soil + hot + low rain = high irrigation
rule1 = ctrl.Rule(
    soil_moisture['low'] &
    temperature['high'] &
    rain_probability['low'],
    irrigation['high']
)


# Dry soil + low humidity + low rain = high irrigation
rule2 = ctrl.Rule(
    soil_moisture['low'] &
    humidity['low'] &
    rain_probability['low'],
    irrigation['high']
)


# Dry soil + medium rain = medium irrigation
rule3 = ctrl.Rule(
    soil_moisture['low'] &
    rain_probability['medium'],
    irrigation['medium']
)


# Dry soil + high rain = low irrigation
rule4 = ctrl.Rule(
    soil_moisture['low'] &
    rain_probability['high'],
    irrigation['low']
)


# Medium soil + hot + low rain = medium irrigation
rule5 = ctrl.Rule(
    soil_moisture['medium'] &
    temperature['high'] &
    rain_probability['low'],
    irrigation['medium']
)


# Medium soil + high humidity + high rain = none
rule6 = ctrl.Rule(
    soil_moisture['medium'] &
    humidity['high'] &
    rain_probability['high'],
    irrigation['none']
)


# Medium soil + high rain = low irrigation
rule7 = ctrl.Rule(
    soil_moisture['medium'] &
    rain_probability['high'],
    irrigation['low']
)


# Wet soil + high rain = none
rule8 = ctrl.Rule(
    soil_moisture['high'] &
    rain_probability['high'],
    irrigation['none']
)


# Wet soil + medium rain = none
rule9 = ctrl.Rule(
    soil_moisture['high'] &
    rain_probability['medium'],
    irrigation['none']
)


# Wet soil + low rain = low irrigation
rule10 = ctrl.Rule(
    soil_moisture['high'] &
    rain_probability['low'],
    irrigation['low']
)


# Low humidity + high temperature = higher irrigation
rule11 = ctrl.Rule(
    humidity['low'] &
    temperature['high'],
    irrigation['high']
)


# High humidity + medium soil = low irrigation
rule12 = ctrl.Rule(
    humidity['high'] &
    soil_moisture['medium'],
    irrigation['low']
)


# High humidity + wet soil = none
rule13 = ctrl.Rule(
    humidity['high'] &
    soil_moisture['high'],
    irrigation['none']
)


# Fallback rules based on soil moisture
rule14 = ctrl.Rule(
    soil_moisture['low'],
    irrigation['medium']
)

rule15 = ctrl.Rule(
    soil_moisture['medium'],
    irrigation['low']
)

rule16 = ctrl.Rule(
    soil_moisture['high'],
    irrigation['none']
)


# ==============================
# CONTROL SYSTEM
# ==============================

irrigation_control = ctrl.ControlSystem([
    rule1, rule2, rule3, rule4,
    rule5, rule6, rule7, rule8,
    rule9, rule10, rule11, rule12,
    rule13, rule14, rule15, rule16
])


# ==============================
# FUNCTION
# ==============================

def get_irrigation_recommendation(
    soil_value,
    temperature_value,
    humidity_value,
    rain_value
):

    simulation = ctrl.ControlSystemSimulation(
        irrigation_control
    )

    simulation.input['soil_moisture'] = soil_value
    simulation.input['temperature'] = temperature_value
    simulation.input['humidity'] = humidity_value
    simulation.input['rain_probability'] = rain_value

    simulation.compute()

    result = simulation.output['irrigation']

    if result < 20:
        level = "NONE"
    elif result < 50:
        level = "LOW"
    elif result < 75:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return result, level


# ==============================
# TEST
# ==============================

if __name__ == "__main__":

    value, level = get_irrigation_recommendation(
        soil_value=25,
        temperature_value=34,
        humidity_value=45,
        rain_value=10
    )

    print("Irrigation Score:", round(value, 2))
    print("Irrigation Level:", level)