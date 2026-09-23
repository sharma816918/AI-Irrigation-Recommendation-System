import streamlit as st
import json

from ai_helper import (
    extract_irrigation_data,
    extract_irrigation_data_local,
    generate_irrigation_explanation,
    generate_local_explanation
)

from fuzzy_logic import get_irrigation_recommendation


st.set_page_config(
    page_title="AI Irrigation System",
    page_icon="🌱",
    layout="centered"
)


st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #e8f5e9,
        #f1f8e9,
        #ffffff
    );
}

.main-title {
    text-align: center;
    color: #1b5e20;
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #4e6e50;
    font-size: 17px;
    margin-bottom: 30px;
}

.input-card,
.result-card {
    background-color: #ffffff !important;
    color: #222222 !important;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.input-card *,
.result-card * {
    color: #222222;
}

.section-title {
    color: #2e7d32 !important;
    font-size: 24px;
    font-weight: 700;
}

div[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border-radius: 12px;
    padding: 10px;
}

div[data-testid="stMetricLabel"] {
    color: #555555 !important;
}

div[data-testid="stMetricValue"] {
    color: #1b5e20 !important;
}

textarea {
    color: #222222 !important;
}

label {
    color: #222222 !important;
}

p {
    color: #222222;
}

.footer {
    text-align: center;
    color: #607d60;
    margin-top: 40px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="main-title">🌱 AI Irrigation Recommendation System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI + LangChain + Fuzzy Logic for Smart Irrigation</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="input-card">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-title">🌾 Enter Field Conditions</div>',
    unsafe_allow_html=True
)

st.write(
    "Describe your crop and field conditions in normal language."
)

st.info(
    "💡 Example: My tomato crop has dry soil, temperature is 34°C, "
    "humidity is 45% and rain chance is 10%."
)

user_input = st.text_area(
    "📝 Describe your field",
    height=130,
    placeholder=(
        "Example: My tomato crop has dry soil, "
        "temperature is 34°C, humidity is 45% "
        "and rain chance is 10%."
    )
)

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


button = st.button(
    "🌱 Get Irrigation Recommendation",
    type="primary",
    use_container_width=True
)


if button:

    if not user_input.strip():

        st.warning(
            "⚠️ Please enter your field conditions."
        )

    else:

        # =================================================
        # STEP 1 - AI EXTRACTION
        # =================================================

        try:

            with st.spinner(
                "🤖 AI is understanding your field conditions..."
            ):

                extracted_data = extract_irrigation_data(
                    user_input
                )

        except Exception:

            # Silent local fallback
            extracted_data = extract_irrigation_data_local(
                user_input
            )


        # =================================================
        # STEP 2 - PROCESS DATA
        # =================================================

        try:

            if isinstance(
                extracted_data,
                str
            ):

                data = json.loads(
                    extracted_data
                )

            else:

                data = extracted_data


            if isinstance(
                data,
                list
            ):

                data = data[0]


            crop = data["crop"]

            soil_moisture = float(
                data["soil_moisture"]
            )

            temperature = float(
                data["temperature"]
            )

            humidity = float(
                data["humidity"]
            )

            rain_probability = float(
                data["rain_probability"]
            )


        except Exception as data_error:

            st.error(
                "❌ Could not process field data."
            )

            st.write(
                str(data_error)
            )

            st.stop()


        # =================================================
        # STEP 3 - FUZZY LOGIC
        # =================================================

        score, level = get_irrigation_recommendation(

            soil_value=soil_moisture,

            temperature_value=temperature,

            humidity_value=humidity,

            rain_value=rain_probability

        )


        st.success(
            "✅ Irrigation recommendation generated!"
        )


        # =================================================
        # STEP 4 - EXTRACTED INFORMATION
        # =================================================

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '🤖 Extracted Information'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "🌾 Crop",
                crop
            )

            st.metric(
                "💧 Soil Moisture",
                f"{soil_moisture}%"
            )

            st.metric(
                "🌡️ Temperature",
                f"{temperature}°C"
            )

        with col2:

            st.metric(
                "💦 Humidity",
                f"{humidity}%"
            )

            st.metric(
                "🌧️ Rain Probability",
                f"{rain_probability}%"
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        # =================================================
        # STEP 5 - FUZZY LOGIC RESULT
        # =================================================

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '🧠 Fuzzy Logic Result'
            '</div>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Irrigation Score",
                f"{score:.2f}"
            )

        with col2:

            st.metric(
                "Irrigation Level",
                level
            )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


        # =================================================
        # STEP 6 - STATUS
        # =================================================

        if level == "HIGH":

            st.error(
                "🔴 Status: High Irrigation Required"
            )

        elif level == "MEDIUM":

            st.warning(
                "🟡 Status: Moderate Irrigation Required"
            )

        elif level == "LOW":

            st.info(
                "🔵 Status: Low Irrigation Required"
            )

        else:

            st.success(
                "🟢 Status: No Irrigation Required"
            )


        # =================================================
        # STEP 7 - EXPLANATION
        # =================================================

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            '💡 AI Explanation'
            '</div>',
            unsafe_allow_html=True
        )


        try:

            with st.spinner(
                "💡 Preparing explanation..."
            ):

                explanation = generate_irrigation_explanation(

                    crop=crop,

                    soil_moisture=soil_moisture,

                    temperature=temperature,

                    humidity=humidity,

                    rain_probability=rain_probability,

                    score=score,

                    level=level

                )


            st.write(
                explanation
            )


        except Exception:

            # Silent local explanation fallback

            explanation = generate_local_explanation(

                crop=crop,

                soil_moisture=soil_moisture,

                temperature=temperature,

                humidity=humidity,

                rain_probability=rain_probability,

                score=score,

                level=level

            )

            st.write(
                explanation
            )


        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer">'
    '🌱 AI Irrigation Recommendation System | '
    'LangChain + Gemini + Fuzzy Logic'
    '</div>',
    unsafe_allow_html=True
)