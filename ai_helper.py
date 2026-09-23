import os
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class IrrigationData(BaseModel):
    crop: str = Field(description="Name of the crop")
    soil_moisture: float
    temperature: float
    humidity: float
    rain_probability: float


def get_gemini_model(temperature=0):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        temperature=temperature
    )


def extract_irrigation_data(user_text):
    llm = get_gemini_model(temperature=0)

    structured_llm = llm.with_structured_output(IrrigationData)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are an agricultural data extraction assistant.

Extract:
- crop
- soil_moisture
- temperature
- humidity
- rain_probability

Rules:
- soil_moisture: 0 to 100
- temperature: 0 to 50 Celsius
- humidity: 0 to 100
- rain_probability: 0 to 100
- If the user says dry soil, estimate a reasonable low value.
- If descriptive words such as hot, humid, dry or rainy are used,
  estimate reasonable numerical values.
- Return only structured information.
"""),
        ("human", "{user_text}")
    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "user_text": user_text
    })

    return result.model_dump()


def extract_irrigation_data_local(user_text):
    """
    Local fallback extraction.
    Used when Gemini quota is exhausted.
    """

    text = user_text.lower()

    # Crop
    crop = "Unknown"

    crops = [
        "tomato",
        "potato",
        "rice",
        "wheat",
        "cotton",
        "sugarcane",
        "maize",
        "corn",
        "onion",
        "carrot",
        "soybean",
        "groundnut",
        "chilli",
        "chili"
    ]

    for item in crops:
        if item in text:
            crop = item.title()
            break

    # Soil moisture
    soil_moisture = None

    soil_match = re.search(
        r"(?:soil moisture|soil moisture is|moisture)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)\s*%?",
        text
    )

    if soil_match:
        soil_moisture = float(soil_match.group(1))

    elif "dry soil" in text:
        soil_moisture = 20.0

    elif "very dry soil" in text:
        soil_moisture = 10.0

    elif "wet soil" in text:
        soil_moisture = 75.0

    elif "very wet soil" in text:
        soil_moisture = 90.0

    # Temperature
    temperature = None

    temp_match = re.search(
        r"(?:temperature|temp)\s*(?:is|of)?\s*(-?\d+(?:\.\d+)?)\s*°?\s*c",
        text
    )

    if temp_match:
        temperature = float(temp_match.group(1))

    # Humidity
    humidity = None

    humidity_match = re.search(
        r"(?:humidity)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)\s*%",
        text
    )

    if humidity_match:
        humidity = float(humidity_match.group(1))

    # Rain probability
    rain_probability = None

    rain_match = re.search(
        r"(?:rain chance|rain probability|rain possibility|rain)\s*(?:is|of)?\s*(\d+(?:\.\d+)?)\s*%",
        text
    )

    if rain_match:
        rain_probability = float(rain_match.group(1))

    # Descriptive rain
    if rain_probability is None:

        if "heavy rain" in text:
            rain_probability = 90.0

        elif "rainy" in text:
            rain_probability = 75.0

        elif "likely rain" in text:
            rain_probability = 70.0

        elif "no rain" in text:
            rain_probability = 5.0

        elif "no chance of rain" in text:
            rain_probability = 5.0

    # Default values if a value is missing
    if soil_moisture is None:
        soil_moisture = 30.0

    if temperature is None:
        temperature = 25.0

    if humidity is None:
        humidity = 50.0

    if rain_probability is None:
        rain_probability = 20.0

    # Keep values inside valid ranges
    soil_moisture = max(0, min(100, soil_moisture))
    temperature = max(0, min(50, temperature))
    humidity = max(0, min(100, humidity))
    rain_probability = max(0, min(100, rain_probability))

    return {
        "crop": crop,
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity,
        "rain_probability": rain_probability
    }


def generate_irrigation_explanation(
    crop,
    soil_moisture,
    temperature,
    humidity,
    rain_probability,
    score,
    level
):

    llm = get_gemini_model(temperature=0.3)

    prompt = ChatPromptTemplate.from_template("""
You are an agricultural irrigation assistant.

Explain the irrigation recommendation in simple language.

The irrigation decision has already been calculated by Fuzzy Logic.

DO NOT change the irrigation level or score.

Crop: {crop}
Soil Moisture: {soil_moisture}%
Temperature: {temperature}°C
Humidity: {humidity}%
Rain Probability: {rain_probability}%
Fuzzy Irrigation Score: {score}
Fuzzy Irrigation Level: {level}

Explain:
1. Why the fuzzy system gave this level.
2. Which environmental factors affected the result.
3. Give one simple practical suggestion.

Keep the explanation short and easy to understand.
""")

    chain = prompt | llm

    response = chain.invoke({
        "crop": crop,
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity,
        "rain_probability": rain_probability,
        "score": round(score, 2),
        "level": level
    })

    # Convert Gemini response to normal text
    if hasattr(response, "content"):
        content = response.content
    else:
        content = str(response)

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])

        content = "".join(text_parts)

    elif isinstance(content, dict):

        if "text" in content:
            content = content["text"]

        else:
            content = str(content)

    return content


def generate_local_explanation(
    crop,
    soil_moisture,
    temperature,
    humidity,
    rain_probability,
    score,
    level
):

    reasons = []

    if soil_moisture < 40:
        reasons.append("soil moisture is low")

    elif soil_moisture >= 60:
        reasons.append("soil moisture is high")

    else:
        reasons.append("soil moisture is moderate")

    if temperature >= 30:
        reasons.append("temperature is high")

    elif temperature <= 20:
        reasons.append("temperature is relatively low")

    if humidity < 40:
        reasons.append("humidity is low")

    elif humidity >= 70:
        reasons.append("humidity is high")

    if rain_probability >= 70:
        reasons.append("rain probability is high")

    elif rain_probability <= 30:
        reasons.append("rain probability is low")

    reason_text = ", ".join(reasons)

    if level == "HIGH":

        suggestion = (
            "Irrigation should be considered soon because "
            "the field conditions indicate a higher water requirement."
        )

    elif level == "MEDIUM":

        suggestion = (
            "Moderate irrigation may be appropriate "
            "based on the current field conditions."
        )

    elif level == "LOW":

        suggestion = (
            "Only a small amount of irrigation may be required."
        )

    else:

        suggestion = (
            "Irrigation may not be required at the moment."
        )

    return (
        f"For the {crop} crop, the fuzzy system calculated "
        f"an irrigation score of {score:.2f}, resulting in a "
        f"{level} irrigation level. "
        f"The main factors were {reason_text}. "
        f"{suggestion}"
    )