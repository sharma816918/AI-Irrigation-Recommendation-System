import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


# ==========================================
# STRUCTURED AI DATA
# ==========================================

class IrrigationData(BaseModel):

    crop: str = Field(
        description="Name of the crop"
    )

    soil_moisture: float = Field(
        description="Soil moisture percentage from 0 to 100"
    )

    temperature: float = Field(
        description="Temperature in Celsius from 0 to 50"
    )

    humidity: float = Field(
        description="Humidity percentage from 0 to 100"
    )

    rain_probability: float = Field(
        description="Rain probability percentage from 0 to 100"
    )


# ==========================================
# GEMINI MODEL
# ==========================================

def get_gemini_model(temperature=0):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set."
        )

    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        temperature=temperature
    )


# ==========================================
# AI DATA EXTRACTION
# ==========================================

def extract_irrigation_data(user_text):

    llm = get_gemini_model(
        temperature=0
    )

    structured_llm = llm.with_structured_output(
        IrrigationData
    )

    prompt = ChatPromptTemplate.from_messages([

        (
            "system",
            """
You are an agricultural data extraction assistant.

Extract these five values from the user's
natural-language description:

- crop
- soil_moisture
- temperature
- humidity
- rain_probability

Rules:

1. Return exactly the required structured fields.

2. soil_moisture must be between 0 and 100.

3. temperature must be between 0 and 50 Celsius.

4. humidity must be between 0 and 100.

5. rain_probability must be between 0 and 100.

6. If the user says "dry soil",
   estimate a reasonable low soil-moisture value.

7. If the user uses descriptive words such as
   hot, humid, dry, or rainy,
   estimate reasonable numerical values.

8. Do not provide explanations.
   Only return the structured information.
"""
        ),

        (
            "human",
            "{user_text}"
        )

    ])

    chain = prompt | structured_llm

    result = chain.invoke({
        "user_text": user_text
    })

    return result.model_dump()


# ==========================================
# AI EXPLANATION
# ==========================================

def generate_irrigation_explanation(
    crop,
    soil_moisture,
    temperature,
    humidity,
    rain_probability,
    score,
    level
):

    llm = get_gemini_model(
        temperature=0.3
    )

    prompt = ChatPromptTemplate.from_template(
        """
You are an agricultural irrigation assistant.

Explain the irrigation recommendation
in simple language.

The irrigation decision has already been
calculated by a Fuzzy Logic system.

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

2. Which environmental factors affected
   the result.

3. Give one simple practical suggestion.

Keep the explanation short and easy
to understand.
"""
    )

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

    return response.content